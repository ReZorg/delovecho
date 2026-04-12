#!/usr/bin/env python3
"""
infer_sequence.py — Generate action sequence ASTs from natural language goals.

Uses the Skillm vocabulary and training corpus to synthesize procedural programs.

Usage:
  python infer_sequence.py "Find the latest invoice and save it to the database"
  python infer_sequence.py --goal "Sync all email accounts" --connector neon
  python infer_sequence.py --goal "Create a campaign report" --format mermaid
  python infer_sequence.py --corpus /path/to/corpus.jsonl --goal "..."
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ── Vocabulary ──────────────────────────────────────────────────────────────

VERBS = [
    "DISCOVER", "INSPECT", "CREATE", "MUTATE", "DESTROY",
    "NAVIGATE", "COMPOSE", "OBSERVE", "ORCHESTRATE", "CLASSIFY",
]

# Goal keywords → verb mapping (used for rule-based inference)
GOAL_VERB_MAP = {
    "find": "DISCOVER", "search": "DISCOVER", "list": "DISCOVER", "get": "DISCOVER",
    "look": "DISCOVER", "show": "DISCOVER", "what": "DISCOVER",
    "read": "INSPECT", "check": "INSPECT", "describe": "INSPECT", "examine": "INSPECT",
    "detail": "INSPECT", "fetch": "INSPECT",
    "create": "CREATE", "add": "CREATE", "new": "CREATE", "make": "CREATE",
    "build": "CREATE", "generate": "CREATE", "write": "CREATE",
    "update": "MUTATE", "edit": "MUTATE", "change": "MUTATE", "modify": "MUTATE",
    "set": "MUTATE", "fix": "MUTATE", "rename": "MUTATE",
    "delete": "DESTROY", "remove": "DESTROY", "drop": "DESTROY", "clean": "DESTROY",
    "go": "NAVIGATE", "open": "NAVIGATE", "visit": "NAVIGATE", "navigate": "NAVIGATE",
    "move": "NAVIGATE", "browse": "NAVIGATE",
    "run": "COMPOSE", "execute": "COMPOSE", "send": "COMPOSE", "deploy": "COMPOSE",
    "apply": "COMPOSE", "install": "COMPOSE",
    "monitor": "OBSERVE", "measure": "OBSERVE", "report": "OBSERVE",
    "analyze": "OBSERVE", "track": "OBSERVE", "insight": "OBSERVE",
    "migrate": "ORCHESTRATE", "prepare": "ORCHESTRATE", "provision": "ORCHESTRATE",
    "sync": "ORCHESTRATE", "coordinate": "ORCHESTRATE",
    "label": "CLASSIFY", "tag": "CLASSIFY", "categorize": "CLASSIFY",
    "organize": "CLASSIFY", "sort": "CLASSIFY",
}

# Connector keywords → connector mapping (ordered by priority)
# When a word maps to multiple connectors, the first match wins.
# Use a list of (keyword, connector, weight) tuples for weighted matching.
CONNECTOR_KEYWORDS = [
    # Notion (high-specificity keywords)
    ("notion", "notion", 3),
    ("wiki", "notion", 2),
    # Gmail
    ("email", "gmail", 3), ("emails", "gmail", 3),
    ("mail", "gmail", 2), ("inbox", "gmail", 2),
    ("label", "gmail", 2), ("labels", "gmail", 2),
    ("thread", "gmail", 2), ("threads", "gmail", 2),
    # Calendar
    ("calendar", "google-calendar", 3),
    ("event", "google-calendar", 2), ("events", "google-calendar", 2),
    ("meeting", "google-calendar", 2), ("schedule", "google-calendar", 2),
    # Meta Marketing
    ("campaign", "meta-marketing", 3), ("campaigns", "meta-marketing", 3),
    ("ad", "meta-marketing", 2), ("ads", "meta-marketing", 2),
    ("marketing", "meta-marketing", 2),
    ("facebook", "meta-marketing", 3), ("meta", "meta-marketing", 2),
    ("instagram", "meta-marketing", 3), ("insight", "meta-marketing", 1),
    # Neon
    ("sql", "neon", 3), ("postgres", "neon", 3), ("neon", "neon", 3),
    ("migration", "neon", 2), ("migrate", "neon", 2),
    ("branch", "neon", 2), ("schema", "neon", 2),
    ("table", "neon", 1), ("database", "neon", 1),
    ("query", "neon", 1),
    # Playwright
    ("browser", "playwright", 3), ("playwright", "playwright", 3),
    ("click", "playwright", 2), ("screenshot", "playwright", 2),
    ("form", "playwright", 1), ("web", "playwright", 1),
    # Notion (lower-specificity — page can be Notion or Playwright)
    ("page", "notion", 1), ("pages", "notion", 1),
    ("message", "gmail", 1), ("messages", "gmail", 1),
]

CONNECTOR_MAP = {}  # kept for backward compat
for _kw, _conn, _w in CONNECTOR_KEYWORDS:
    CONNECTOR_MAP[_kw] = _conn

# Sequence templates keyed by (primary_verb, connector)
TEMPLATES = {
    ("DISCOVER", "notion"): [
        {"verb": "DISCOVER", "tool": "notion-search", "description": "Search Notion workspace"},
        {"verb": "INSPECT", "tool": "notion-fetch", "description": "Fetch full page content"},
    ],
    ("DISCOVER", "gmail"): [
        {"verb": "DISCOVER", "tool": "gmail_search_messages", "description": "Search Gmail messages"},
        {"verb": "INSPECT", "tool": "gmail_read_threads", "description": "Read matching threads"},
    ],
    ("DISCOVER", "meta-marketing"): [
        {"verb": "DISCOVER", "tool": "meta_marketing_get_ad_accounts", "description": "List ad accounts"},
        {"verb": "DISCOVER", "tool": "meta_marketing_get_campaigns", "description": "List campaigns"},
        {"verb": "OBSERVE", "tool": "meta_marketing_get_insights", "description": "Get performance insights"},
    ],
    ("CREATE", "notion"): [
        {"verb": "DISCOVER", "tool": "notion-search", "description": "Find parent page or database"},
        {"verb": "INSPECT", "tool": "notion-fetch", "description": "Fetch schema or template"},
        {"verb": "CREATE", "tool": "notion-create-pages", "description": "Create new page"},
    ],
    ("CREATE", "google-calendar"): [
        {"verb": "DISCOVER", "tool": "google_calendar_search_events", "description": "Check for conflicts"},
        {"verb": "CREATE", "tool": "google_calendar_create_events", "description": "Create event"},
    ],
    ("ORCHESTRATE", "neon"): [
        {"verb": "DISCOVER", "tool": "list_projects", "description": "Find target project"},
        {"verb": "INSPECT", "tool": "get_database_tables", "description": "Inspect current schema"},
        {"verb": "CREATE", "tool": "create_branch", "description": "Create safety branch"},
        {"verb": "ORCHESTRATE", "tool": "prepare_database_migration", "description": "Prepare migration"},
        {"verb": "COMPOSE", "tool": "run_sql", "description": "Test on branch"},
        {"verb": "ORCHESTRATE", "tool": "complete_database_migration", "description": "Commit migration"},
    ],
    ("COMPOSE", "neon"): [
        {"verb": "DISCOVER", "tool": "list_projects", "description": "Find project"},
        {"verb": "INSPECT", "tool": "get_database_tables", "description": "List tables"},
        {"verb": "COMPOSE", "tool": "run_sql", "description": "Execute SQL query"},
    ],
    ("NAVIGATE", "playwright"): [
        {"verb": "NAVIGATE", "tool": "browser_navigate", "description": "Navigate to URL"},
        {"verb": "OBSERVE", "tool": "browser_snapshot", "description": "Capture page state"},
        {"verb": "MUTATE", "tool": "browser_click", "description": "Interact with page"},
        {"verb": "OBSERVE", "tool": "browser_wait_for", "description": "Wait for result"},
    ],
    ("COMPOSE", "gmail"): [
        {"verb": "DISCOVER", "tool": "gmail_search_messages", "description": "Find relevant threads"},
        {"verb": "INSPECT", "tool": "gmail_read_threads", "description": "Read thread content"},
        {"verb": "COMPOSE", "tool": "gmail_send_messages", "description": "Compose and send reply"},
    ],
    ("CLASSIFY", "gmail"): [
        {"verb": "DISCOVER", "tool": "gmail_search_messages", "description": "Find messages to classify"},
        {"verb": "CLASSIFY", "tool": "gmail_manage_labels", "description": "Apply labels"},
    ],
    ("OBSERVE", "meta-marketing"): [
        {"verb": "DISCOVER", "tool": "meta_marketing_get_ad_accounts", "description": "List accounts"},
        {"verb": "DISCOVER", "tool": "meta_marketing_get_campaigns", "description": "List campaigns"},
        {"verb": "DISCOVER", "tool": "meta_marketing_get_adsets", "description": "List ad sets"},
        {"verb": "OBSERVE", "tool": "meta_marketing_get_insights", "description": "Get detailed insights"},
    ],
}


# ── Inference Engine ────────────────────────────────────────────────────────

def infer_verbs(goal: str) -> list[str]:
    """Extract verb categories from a natural language goal."""
    words = goal.lower().split()
    verbs = []
    for word in words:
        # Strip punctuation
        clean = word.strip(".,;:!?\"'()[]")
        if clean in GOAL_VERB_MAP:
            verb = GOAL_VERB_MAP[clean]
            if verb not in verbs:
                verbs.append(verb)
    return verbs or ["COMPOSE"]


def infer_connector(goal: str) -> str:
    """Infer the primary connector from a natural language goal using weighted matching."""
    words = goal.lower().split()
    connector_scores = {}
    for word in words:
        clean = word.strip(".,;:!?\"'()[]")
        for kw, conn, weight in CONNECTOR_KEYWORDS:
            if clean == kw:
                connector_scores[conn] = connector_scores.get(conn, 0) + weight
    if connector_scores:
        return max(connector_scores, key=connector_scores.get)
    return "neon"  # Default


def build_ast(goal: str, connector: str = None, corpus_path: str = None) -> dict:
    """Generate an action sequence AST from a goal description."""
    verbs = infer_verbs(goal)
    if connector is None:
        connector = infer_connector(goal)

    primary_verb = verbs[0]

    # Look up template
    template_key = (primary_verb, connector)
    if template_key in TEMPLATES:
        steps = TEMPLATES[template_key]
    else:
        # Fallback: generic DISCOVER → primary_verb pattern
        steps = [
            {"verb": "DISCOVER", "tool": f"{connector}:discover", "description": f"Find relevant entities in {connector}"},
            {"verb": primary_verb, "tool": f"{connector}:{primary_verb.lower()}", "description": f"Execute {primary_verb} action"},
        ]

    # Build AST
    ast = {
        "version": "1.0.0",
        "goal": goal,
        "context": {
            "connectors": [connector],
            "variables": {},
        },
        "root": {
            "type": "pipeline",
            "steps": [
                {
                    "type": "action",
                    "verb": step["verb"],
                    "tool": step["tool"],
                    "params": {},
                    "description": step["description"],
                }
                for step in steps
            ],
        },
    }

    # If multiple verbs detected, wrap in a guard for error handling
    if len(verbs) > 1:
        original_root = ast["root"]
        ast["root"] = {
            "type": "guard",
            "try": original_root,
            "catch": {
                "type": "action",
                "verb": "OBSERVE",
                "tool": "log_error",
                "params": {},
                "description": "Log failure and report to user",
            },
        }

    return ast


def ast_to_mermaid(ast: dict) -> str:
    """Convert an AST to a Mermaid flowchart diagram."""
    lines = ["graph TD"]
    counter = [0]

    def node_id():
        counter[0] += 1
        return f"N{counter[0]}"

    def render(node, parent_id=None):
        nid = node_id()
        if node["type"] == "action":
            label = f'{node["verb"]}\\n{node.get("description", node["tool"])}'
            lines.append(f'    {nid}["{label}"]')
        elif node["type"] == "pipeline":
            lines.append(f'    {nid}(["⊗ Pipeline"])')
            prev = nid
            for step in node["steps"]:
                child = render(step, nid)
                lines.append(f"    {prev} --> {child}")
                prev = child
            return prev  # Return last step for chaining
        elif node["type"] == "choice":
            lines.append(f'    {nid}{{"⊕ Choice"}}')
            for branch in node["branches"]:
                child = render(branch["node"], nid)
                label = branch.get("label", "")
                lines.append(f"    {nid} -->|{label}| {child}")
        elif node["type"] == "guard":
            lines.append(f'    {nid}["🛡 Guard"]')
            try_child = render(node["try"], nid)
            lines.append(f"    {nid} -->|try| {try_child}")
            if "catch" in node:
                catch_child = render(node["catch"], nid)
                lines.append(f"    {nid} -->|catch| {catch_child}")
        elif node["type"] == "loop":
            until_val = node.get('until', '')
            lines.append(f'    {nid}["🔄 Loop: {until_val}"]')
            body_child = render(node["body"], nid)
            lines.append(f"    {nid} --> {body_child}")
            lines.append(f"    {body_child} -.->|repeat| {nid}")

        if parent_id and node["type"] == "action":
            pass  # Parent handles connection

        return nid

    render(ast["root"])
    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate Skillm action sequence AST")
    parser.add_argument("goal", nargs="?", help="Natural language goal")
    parser.add_argument("--goal", dest="goal_flag", help="Natural language goal (flag form)")
    parser.add_argument("--connector", help="Override connector detection")
    parser.add_argument("--corpus", help="Path to training corpus JSONL")
    parser.add_argument("--format", choices=["json", "mermaid", "summary"], default="json")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    goal = args.goal or args.goal_flag
    if not goal:
        print("Error: provide a goal as positional argument or --goal flag", file=sys.stderr)
        sys.exit(1)

    ast = build_ast(goal, connector=args.connector, corpus_path=args.corpus)

    if args.format == "json":
        output = json.dumps(ast, indent=2)
    elif args.format == "mermaid":
        output = ast_to_mermaid(ast)
    elif args.format == "summary":
        steps = []
        root = ast["root"]
        if root["type"] == "guard":
            root = root["try"]
        if root["type"] == "pipeline":
            for i, step in enumerate(root["steps"], 1):
                steps.append(f"{i}. [{step['verb']}] {step.get('description', step['tool'])}")
        output = f"Goal: {ast['goal']}\nConnector: {ast['context']['connectors'][0]}\n\nAction Sequence:\n" + "\n".join(steps)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Output written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
