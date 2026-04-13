#!/usr/bin/env python3
"""
train_skillm.py — Harvest action sequences from MCP connectors, Neon databases,
and existing skills to build a Skillm training corpus.

Usage:
  python train_skillm.py --source connectors   # Parse MCP tool result files
  python train_skillm.py --source skills        # Parse SKILL.md workflow steps
  python train_skillm.py --source all           # All sources
  python train_skillm.py --source all --output /path/to/corpus.jsonl
"""

import argparse
import glob
import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

# ── Vocabulary ──────────────────────────────────────────────────────────────

VERB_MAP = {
    # Notion
    "notion-search": "DISCOVER",
    "notion-fetch": "INSPECT",
    "notion-create-pages": "CREATE",
    "notion-update-page": "MUTATE",
    "notion-move-pages": "NAVIGATE",
    "notion-duplicate-page": "NAVIGATE",
    "notion-create-database": "CREATE",
    "notion-update-data-source": "MUTATE",
    "notion-create-comment": "CREATE",
    "notion-get-comments": "INSPECT",
    "notion-get-teams": "DISCOVER",
    "notion-get-users": "DISCOVER",
    "notion-create-view": "CLASSIFY",
    "notion-update-view": "CLASSIFY",
    # Gmail
    "gmail_search_messages": "DISCOVER",
    "gmail_read_threads": "INSPECT",
    "gmail_send_messages": "COMPOSE",
    "gmail_manage_labels": "CLASSIFY",
    # Calendar
    "google_calendar_search_events": "DISCOVER",
    "google_calendar_create_events": "CREATE",
    "google_calendar_get_event": "INSPECT",
    "google_calendar_update_events": "MUTATE",
    "google_calendar_delete_events": "DESTROY",
    # Meta Marketing
    "meta_marketing_get_ad_accounts": "DISCOVER",
    "meta_marketing_get_campaigns": "DISCOVER",
    "meta_marketing_get_adsets": "DISCOVER",
    "meta_marketing_get_ads": "DISCOVER",
    "meta_marketing_get_insights": "OBSERVE",
    "meta_marketing_get_object": "INSPECT",
    # Neon
    "list_projects": "DISCOVER",
    "list_organizations": "DISCOVER",
    "create_project": "CREATE",
    "delete_project": "DESTROY",
    "describe_project": "INSPECT",
    "run_sql": "COMPOSE",
    "run_sql_transaction": "COMPOSE",
    "describe_table_schema": "INSPECT",
    "get_database_tables": "INSPECT",
    "create_branch": "CREATE",
    "prepare_database_migration": "ORCHESTRATE",
    "complete_database_migration": "ORCHESTRATE",
    "describe_branch": "INSPECT",
    "delete_branch": "DESTROY",
    "reset_from_parent": "ORCHESTRATE",
    "explain_sql_statement": "OBSERVE",
    "prepare_query_tuning": "ORCHESTRATE",
    "complete_query_tuning": "ORCHESTRATE",
    "list_slow_queries": "OBSERVE",
    "search": "DISCOVER",
    "fetch": "INSPECT",
    # Playwright
    "browser_navigate": "NAVIGATE",
    "browser_navigate_back": "NAVIGATE",
    "browser_snapshot": "OBSERVE",
    "browser_take_screenshot": "OBSERVE",
    "browser_click": "MUTATE",
    "browser_fill_form": "MUTATE",
    "browser_type": "MUTATE",
    "browser_evaluate": "COMPOSE",
    "browser_run_code": "COMPOSE",
    "browser_select_option": "MUTATE",
    "browser_close": "DESTROY",
    "browser_tabs": "NAVIGATE",
    "browser_wait_for": "OBSERVE",
    "browser_hover": "NAVIGATE",
    "browser_drag": "MUTATE",
    "browser_file_upload": "CREATE",
    "browser_press_key": "MUTATE",
    "browser_handle_dialog": "COMPOSE",
    "browser_console_messages": "OBSERVE",
    "browser_network_requests": "OBSERVE",
    "browser_resize": "MUTATE",
    "browser_install": "CREATE",
}

CONNECTOR_FROM_TOOL = {}
for tool, verb in VERB_MAP.items():
    if tool.startswith("notion"):
        CONNECTOR_FROM_TOOL[tool] = "notion"
    elif tool.startswith("gmail"):
        CONNECTOR_FROM_TOOL[tool] = "gmail"
    elif tool.startswith("google_calendar"):
        CONNECTOR_FROM_TOOL[tool] = "google-calendar"
    elif tool.startswith("meta_marketing"):
        CONNECTOR_FROM_TOOL[tool] = "meta-marketing"
    elif tool.startswith("browser"):
        CONNECTOR_FROM_TOOL[tool] = "playwright"
    else:
        CONNECTOR_FROM_TOOL[tool] = "neon"


# ── Source: MCP Connector Logs ──────────────────────────────────────────────

def harvest_connector_logs():
    """Parse MCP tool result files into action sequence training examples."""
    examples = []
    result_dirs = [
        Path.home() / ".mcp" / "tool-results",
        Path("/tmp/manus-mcp"),
    ]

    entries = []
    for d in result_dirs:
        if not d.exists():
            continue
        for f in sorted(d.glob("*")):
            if not f.is_file():
                continue
            name = f.stem
            # Parse timestamp and tool name from filename
            # Format: YYYY-MM-DD_HH-MM-SS_server_tool.json
            parts = name.split("_", 3)
            if len(parts) >= 4:
                ts = parts[0] + "T" + parts[1].replace("-", ":")
                server = parts[2]
                tool = parts[3]
            elif name.startswith("mcp_result_"):
                ts = datetime.now().isoformat()
                server = "unknown"
                tool = "unknown"
            else:
                continue

            # Try to read the result
            try:
                content = f.read_text()
                result = json.loads(content) if content.strip() else {}
            except (json.JSONDecodeError, OSError):
                result = {}

            verb = VERB_MAP.get(tool, "COMPOSE")
            connector = CONNECTOR_FROM_TOOL.get(tool, server)

            params = result.get("params", {}) if isinstance(result, dict) else {}

            entries.append({
                "timestamp": ts,
                "verb": verb,
                "tool": tool,
                "connector": connector,
                "params": params,
                "result_summary": _summarize_result(result),
            })

    # Group entries by connector into sequences
    by_connector = {}
    for e in entries:
        by_connector.setdefault(e["connector"], []).append(e)

    for connector, actions in by_connector.items():
        if len(actions) < 2:
            continue
        examples.append({
            "id": str(uuid.uuid4()),
            "source": "connector",
            "source_id": connector,
            "goal": f"Observed action sequence on {connector} connector",
            "sequence": [
                {
                    "verb": a["verb"],
                    "tool": a["tool"],
                    "params": a["params"],
                    "result_summary": a["result_summary"],
                }
                for a in actions
            ],
            "outcome": "success",
            "weight": 1.0,
            "metadata": {
                "connector": connector,
                "action_count": len(actions),
            },
        })

    return examples


def _summarize_result(result):
    """Create a brief summary of a tool result."""
    if isinstance(result, list):
        return f"returned {len(result)} items"
    if isinstance(result, dict):
        if "error" in result or "Error" in str(result.get("formatted", "")):
            return "error"
        if "results" in result:
            r = result["results"]
            return f"returned {len(r)} results" if isinstance(r, list) else "returned results"
        return "returned object"
    return "returned value"


# ── Source: Skill Workflow Steps ────────────────────────────────────────────

STEP_PATTERN = re.compile(r"^\s*(\d+)\.\s+\*\*(.+?)\*\*\s*[-–:]?\s*(.*)", re.MULTILINE)
STEP_SIMPLE = re.compile(r"^\s*(\d+)\.\s+(.+)", re.MULTILINE)
COMMAND_PATTERN = re.compile(r"`([^`]+)`")


def harvest_skills():
    """Parse SKILL.md files for procedural workflow steps."""
    examples = []
    skills_dir = Path.home() / "skills"

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        try:
            content = skill_md.read_text()
        except OSError:
            continue

        # Extract skill name from frontmatter
        name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        skill_name = name_match.group(1).strip().strip('"\'') if name_match else skill_dir.name

        # Find workflow steps (bold step pattern)
        steps = STEP_PATTERN.findall(content)
        if not steps:
            # Try simple numbered steps
            steps = STEP_SIMPLE.findall(content)
            steps = [(s[0], s[1], "") for s in steps]

        if len(steps) < 2:
            continue

        # Convert steps to action sequence
        sequence = []
        for step_num, step_title, step_detail in steps:
            verb = _infer_verb(step_title + " " + step_detail)
            commands = COMMAND_PATTERN.findall(step_title + " " + step_detail)
            sequence.append({
                "verb": verb,
                "tool": commands[0] if commands else f"skill:{skill_name}:step{step_num}",
                "params": {},
                "result_summary": step_title.strip(),
            })

        # Extract description from frontmatter
        desc_match = re.search(r"^description:\s*(.+?)$", content, re.MULTILINE)
        goal = desc_match.group(1).strip().strip('"\'') if desc_match else f"Execute {skill_name} workflow"

        examples.append({
            "id": str(uuid.uuid4()),
            "source": "skill",
            "source_id": skill_name,
            "goal": goal,
            "sequence": sequence[:20],  # Cap at 20 steps
            "outcome": "success",
            "weight": 2.0,  # Skills are expert-curated, higher weight
            "metadata": {
                "skill_name": skill_name,
                "step_count": len(sequence),
            },
        })

    return examples


def _infer_verb(text):
    """Infer the action verb category from step text."""
    text_lower = text.lower()
    verb_keywords = {
        "DISCOVER": ["search", "find", "list", "scan", "locate", "browse", "explore", "query"],
        "INSPECT": ["read", "fetch", "describe", "examine", "analyze", "review", "check", "verify", "look"],
        "CREATE": ["create", "add", "new", "generate", "build", "init", "setup", "write", "produce"],
        "MUTATE": ["update", "edit", "modify", "change", "set", "configure", "adjust", "fix", "patch"],
        "DESTROY": ["delete", "remove", "drop", "clean", "purge", "destroy"],
        "NAVIGATE": ["navigate", "go", "move", "open", "visit", "switch", "redirect"],
        "COMPOSE": ["run", "execute", "send", "apply", "deploy", "install", "invoke", "call"],
        "OBSERVE": ["observe", "monitor", "measure", "capture", "screenshot", "log", "track", "watch"],
        "ORCHESTRATE": ["prepare", "complete", "migrate", "provision", "orchestrate", "coordinate", "plan"],
        "CLASSIFY": ["label", "tag", "categorize", "classify", "organize", "sort", "group", "filter"],
    }
    for verb, keywords in verb_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return verb
    return "COMPOSE"  # Default


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Harvest Skillm training data")
    parser.add_argument("--source", choices=["connectors", "skills", "all"], default="all")
    parser.add_argument("--output", default=None, help="Output JSONL file path")
    args = parser.parse_args()

    examples = []

    if args.source in ("connectors", "all"):
        print("Harvesting connector logs...")
        examples.extend(harvest_connector_logs())
        print(f"  Found {len(examples)} connector sequences")

    skill_count_before = len(examples)
    if args.source in ("skills", "all"):
        print("Harvesting skill workflows...")
        examples.extend(harvest_skills())
        print(f"  Found {len(examples) - skill_count_before} skill sequences")

    print(f"\nTotal training examples: {len(examples)}")

    # Compute statistics
    verb_counts = {}
    for ex in examples:
        for step in ex["sequence"]:
            verb_counts[step["verb"]] = verb_counts.get(step["verb"], 0) + 1

    print("\nVerb distribution:")
    for verb, count in sorted(verb_counts.items(), key=lambda x: -x[1]):
        print(f"  {verb:15s} {count:5d}")

    # Output
    output_path = args.output or str(Path.home() / "skillm-corpus.jsonl")
    with open(output_path, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")
    print(f"\nCorpus written to: {output_path}")


if __name__ == "__main__":
    main()
