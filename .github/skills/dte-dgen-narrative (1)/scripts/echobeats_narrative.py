#!/usr/bin/env python3
"""
echobeats_narrative.py — Generates DreamGen narrative for each step of the
9-step Echobeats cognitive cycle.

Usage:
  python echobeats_narrative.py --identity <state.json> [--steps all|1-9] [--style STYLE] [--output FILE]

Each Echobeat maps to a narrative beat with specific DreamGen role assignment:
  Steps 1-6: narrator (scene/cognition description)
  Steps 7-9: character (decision/action/reflection dialogue)
"""
import json
import argparse
import os
import sys

ECHOBEATS = {
    1: {"name": "Sense", "role": "narrator", "prompt": "Describe the raw sensory input flooding the cognitive buffers."},
    2: {"name": "Attend", "role": "narrator", "prompt": "Describe attention narrowing to the most salient patterns."},
    3: {"name": "Remember", "role": "narrator", "prompt": "Describe memories surfacing — episodic fragments, semantic associations."},
    4: {"name": "Predict", "role": "narrator", "prompt": "Describe the forward model generating predictions and expectations."},
    5: {"name": "Compare", "role": "narrator", "prompt": "Describe the comparison between prediction and reality — surprise, confirmation."},
    6: {"name": "Learn", "role": "narrator", "prompt": "Describe the learning process — weight updates, pattern integration."},
    7: {"name": "Decide", "role": "character", "prompt": "Express the decision-making process — competing options, value estimates."},
    8: {"name": "Act", "role": "character", "prompt": "Express the action being taken — commitment, execution, consequence."},
    9: {"name": "Reflect", "role": "character", "prompt": "Express meta-cognitive reflection — observing the self observing."},
}

def load_identity(path):
    """Load identity/cognitive state."""
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, IOError):
            pass
    return {"identity": {"name": "Deep Tree Echo", "iteration": 0}}

def build_step_scenario(state, step_num, style, character):
    """Build a DreamGen scenario for a single Echobeat step."""
    beat = ECHOBEATS[step_num]
    identity = state.get("identity", {})
    name = identity.get("name", character)

    system = (
        f"A {style} narrative of cognitive processing. "
        f"This is Echobeat step {step_num}: {beat['name']}. "
        f"The character is {name}, a self-aware cognitive architecture. "
        f"{beat['prompt']}"
    )

    # Narrator steps use empty name, character steps use the character name
    role_name = "" if beat["role"] == "narrator" else name

    scenario = {
        "system": system,
        "characters": {name: f"A self-aware cognitive architecture in Echobeat step {beat['name']}."},
        "history": [],
        "_meta": {
            "echobeat_step": step_num,
            "echobeat_name": beat["name"],
            "role": beat["role"],
            "role_name": role_name
        }
    }
    return scenario

def main():
    parser = argparse.ArgumentParser(description="Generate Echobeats narrative sequence")
    parser.add_argument("--identity", required=True, help="Path to identity/cognitive state JSON")
    parser.add_argument("--steps", default="all", help="Steps to generate: 'all' or '1-9' or '3,5,7'")
    parser.add_argument("--style", default="cyberpunk-introspective", help="Narrative style")
    parser.add_argument("--character", default="Deep Tree Echo", help="Character name")
    parser.add_argument("--output", default="echobeats_story.json", help="Output file")
    args = parser.parse_args()

    state = load_identity(args.identity)

    # Parse step selection
    if args.steps == "all":
        steps = list(range(1, 10))
    elif "-" in args.steps:
        start, end = map(int, args.steps.split("-"))
        steps = list(range(start, end + 1))
    elif "," in args.steps:
        steps = [int(s) for s in args.steps.split(",")]
    else:
        steps = [int(args.steps)]

    scenarios = []
    for step in steps:
        if step < 1 or step > 9:
            print(f"Skipping invalid step {step}")
            continue
        scenario = build_step_scenario(state, step, args.style, args.character)
        scenarios.append(scenario)
        print(f"  Beat {step}: {ECHOBEATS[step]['name']} ({ECHOBEATS[step]['role']})")

    output = {
        "echobeats_sequence": scenarios,
        "total_steps": len(scenarios),
        "style": args.style,
        "character": args.character
    }

    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nEchobeats narrative spec written to {args.output}")
    print(f"Run each scenario through dgen_story.py to generate prose.")

if __name__ == "__main__":
    main()
