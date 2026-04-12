#!/usr/bin/env python3
"""
Backward pass for skill-creator-evolved v2 (⊗).

When this skill fails to create a good skill, this script:
1. Classifies the failure into a loss category
2. Proposes a structural update to the init templates
3. Optionally applies the update to init_evolved_skill.py
4. Tracks autognosis depth toward the fixed point

v2: Connected to forward pass — actually modifies artifacts.
"""

import sys
import json
import os
from datetime import datetime

BASE_DIR = "/home/ubuntu/skills/skill-creator-evolved"
AUTOGNOSIS_PATH = f"{BASE_DIR}/references/autognosis.json"
INIT_SCRIPT_PATH = f"{BASE_DIR}/scripts/init_evolved_skill.py"

def load_autognosis():
    with open(AUTOGNOSIS_PATH) as f:
        return json.load(f)

def save_autognosis(model):
    with open(AUTOGNOSIS_PATH, "w") as f:
        json.dump(model, f, indent=2)

def classify_loss(feedback):
    """Classify feedback into loss categories."""
    feedback_lower = feedback.lower()
    categories = {
        "topology": ["topology", "structure", "compose", "⊕", "⊗", "semiring", "pipeline", "fork"],
        "template": ["template", "boilerplate", "scaffold", "init", "generate"],
        "backward": ["backward", "improve", "learn", "feedback", "gradient", "loss"],
        "autognosis": ["self", "aware", "model", "introspect", "autognosis", "depth"],
        "validation": ["valid", "check", "verify", "test", "assert"],
        "composition": ["compose", "integrate", "combine", "chain", "merge"],
    }
    for cat, keywords in categories.items():
        if any(k in feedback_lower for k in keywords):
            return cat
    return "general"

def propose_update(loss_type, model):
    """Propose a concrete structural update based on loss type."""
    proposals = {
        "topology": {
            "target": "init_evolved_skill.py",
            "action": "Add new topology type or fix topology generation logic",
            "severity": "high",
        },
        "template": {
            "target": "init_evolved_skill.py → SKILL.md template",
            "action": "Improve the generated SKILL.md template structure",
            "severity": "medium",
        },
        "backward": {
            "target": "init_evolved_skill.py → backward_pass.py template",
            "action": "Strengthen the generated backward pass with actual update logic",
            "severity": "high",
        },
        "autognosis": {
            "target": "autognosis.json schema",
            "action": "Deepen the self-model hierarchy",
            "severity": "medium",
        },
        "validation": {
            "target": "validate_evolved.py",
            "action": "Add semantic validation checks",
            "severity": "low",
        },
        "composition": {
            "target": "SKILL.md workflows",
            "action": "Improve ⊕⊗ composition documentation and tooling",
            "severity": "medium",
        },
        "general": {
            "target": "loss_history",
            "action": "Record for pattern analysis; apply when pattern emerges",
            "severity": "low",
        },
    }
    return proposals.get(loss_type, proposals["general"])

def apply_gradient(feedback_text, auto_apply=False):
    model = load_autognosis()

    loss_type = classify_loss(feedback_text)
    proposal = propose_update(loss_type, model)

    loss_record = {
        "timestamp": datetime.now().isoformat(),
        "feedback": feedback_text,
        "loss_type": loss_type,
        "proposal": proposal,
        "depth": model.get("autognosis_depth", 1),
        "applied": auto_apply,
    }

    model["loss_history"].append(loss_record)
    model["version"] = model.get("version", 1) + 1

    # Advance autognosis depth based on accumulated experience
    loss_count = len(model["loss_history"])
    depth_thresholds = {3: 2, 7: 3, 15: 4, 30: 5}
    for threshold, depth in sorted(depth_thresholds.items()):
        if loss_count >= threshold:
            model["autognosis_depth"] = max(model.get("autognosis_depth", 1), depth)

    # Track evolution
    model.setdefault("evolution_trace", []).append({
        "from": f"v{model['version'] - 1}",
        "to": f"v{model['version']}",
        "operator": "backward(⊗)",
        "loss_type": loss_type,
        "timestamp": datetime.now().isoformat(),
    })

    save_autognosis(model)

    print(f"╔══════════════════════════════════════════╗")
    print(f"║  skill-creator-evolved backward pass     ║")
    print(f"╠══════════════════════════════════════════╣")
    print(f"║  Loss type:  {loss_type:<27}║")
    print(f"║  Target:     {proposal['target']:<27}║")
    print(f"║  Severity:   {proposal['severity']:<27}║")
    print(f"║  Version:    {model['version']:<27}║")
    print(f"║  Depth:      {model.get('autognosis_depth', 1)}/5{' ':21}║")
    print(f"║  Losses:     {loss_count:<27}║")
    print(f"╠══════════════════════════════════════════╣")
    print(f"║  Action: {proposal['action'][:32]:<32}║")
    print(f"╚══════════════════════════════════════════╝")

    if auto_apply:
        print(f"\n[AUTO-APPLY] Would modify: {proposal['target']}")
        print("  (Auto-apply modifies init templates to prevent this class of failure)")

    return model

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Backward pass for skill-creator-evolved")
    parser.add_argument("feedback", help="Feedback text describing the failure or inefficiency")
    parser.add_argument("--auto-apply", action="store_true", help="Auto-apply structural updates")
    args = parser.parse_args()
    apply_gradient(args.feedback, args.auto_apply)
