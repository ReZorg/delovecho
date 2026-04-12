#!/usr/bin/env python3
"""
backward_pass.py — Loss classification and fix routing for dte-dgen-narrative.

Routes failures to the correct layer based on loss type:
  Layer 0: echo-evolve-composed (cognitive state issues)
  Layer 1: clawcog <-> gauge-hypergraph-network (gateway/analysis issues)
  Layer 2: agi-os (OS-level failures)
  Layer 3: avatar channels (expression issues)
  Layer 4: dgen (narrative quality issues)
  Pipeline: workflow-creator (step failures)

Usage:
  python backward_pass.py '<feedback description>'
"""
import json
import os
import sys
import re
from datetime import datetime

AUTOGNOSIS_PATH = os.path.join(os.path.dirname(__file__), "..", "references", "autognosis.json")

LOSS_PATTERNS = {
    "narrative_incoherent": {
        "patterns": [r"incoher", r"doesn.t make sense", r"rambling", r"repetiti", r"nonsense"],
        "layer": 4, "layer_name": "dgen",
        "fix": "Adjust DreamGen sampling: lower temperature (0.5), increase DRY multiplier (1.0), add more system context."
    },
    "character_voice_wrong": {
        "patterns": [r"voice.*wrong", r"out of character", r"doesn.t sound like", r"personality.*off"],
        "layer": 4, "layer_name": "dgen",
        "fix": "Update character description in scenario.json. Check role_config — ensure name matches character."
    },
    "cognitive_state_missing": {
        "patterns": [r"state.*missing", r"no cognitive", r"empty state", r"echobeats.*null", r"identity.*not found"],
        "layer": 0, "layer_name": "echo-evolve-composed",
        "fix": "Run echo-evolve-composed forward pass first. Check echo_state.json exists and is valid."
    },
    "gateway_unreachable": {
        "patterns": [r"gateway.*unreachable", r"clawcog.*down", r"connection.*refused", r"ws://.*fail"],
        "layer": 1, "layer_name": "clawcog",
        "fix": "Check clawcog daemon is running. Verify WebSocket port. Restart with: cd clawcog && python run.py"
    },
    "hypergraph_empty": {
        "patterns": [r"hypergraph.*empty", r"no attention", r"gauge.*fail", r"analysis.*empty"],
        "layer": 1, "layer_name": "gauge-hypergraph-network",
        "fix": "Verify input encoding for gauge-equivariant attention. Check AtomSpace has loaded atoms."
    },
    "os_failure": {
        "patterns": [r"agi.?os", r"atomspace.*fail", r"kernel.*panic", r"9p.*error", r"mig.*fail"],
        "layer": 2, "layer_name": "agi-os",
        "fix": "Check agi-os build status. Verify AtomSpace is initialized. Run: cd agi-os && make check"
    },
    "avatar_flat": {
        "patterns": [r"expression.*flat", r"avatar.*not.*moving", r"au.*zero", r"face.*blank", r"rig.*fail"],
        "layer": 3, "layer_name": "avatar-channels",
        "fix": "Check AU mappings in expression_narrative.py. Verify endocrine state is non-zero. Test with known AU set."
    },
    "workflow_failed": {
        "patterns": [r"workflow.*fail", r"step.*fail", r"pipeline.*error", r"checkpoint.*corrupt"],
        "layer": -1, "layer_name": "workflow-creator",
        "fix": "Check workflow checkpoint. Resume with: python workflow.py --resume. Check step logs."
    },
}

def classify_loss(feedback):
    """Classify the loss type from feedback text."""
    feedback_lower = feedback.lower()
    for loss_type, info in LOSS_PATTERNS.items():
        for pattern in info["patterns"]:
            if re.search(pattern, feedback_lower):
                return loss_type, info
    return "general", {
        "layer": -1, "layer_name": "unknown",
        "fix": "Inspect the full pipeline output. Check each layer's logs in order: L0→L1→L2→L3→L4."
    }

def load_autognosis():
    """Load autognosis state."""
    if os.path.exists(AUTOGNOSIS_PATH):
        with open(AUTOGNOSIS_PATH, 'r') as f:
            return json.load(f)
    return {"depth": 0, "losses": [], "layer_health": {str(i): 1.0 for i in range(5)}}

def save_autognosis(state):
    """Save autognosis state."""
    os.makedirs(os.path.dirname(AUTOGNOSIS_PATH), exist_ok=True)
    with open(AUTOGNOSIS_PATH, 'w') as f:
        json.dump(state, f, indent=2)

def main():
    if len(sys.argv) < 2:
        print("Usage: python backward_pass.py '<feedback>'")
        sys.exit(1)

    feedback = " ".join(sys.argv[1:])
    loss_type, info = classify_loss(feedback)
    autognosis = load_autognosis()

    # Record loss
    loss_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "feedback": feedback,
        "loss_type": loss_type,
        "layer": info["layer"],
        "layer_name": info["layer_name"]
    }
    autognosis.setdefault("losses", []).append(loss_entry)

    # Degrade layer health
    layer_key = str(info["layer"])
    health = autognosis.setdefault("layer_health", {})
    current = health.get(layer_key, 1.0)
    health[layer_key] = max(0.0, current - 0.15)

    # Advance autognosis depth
    loss_count = len(autognosis["losses"])
    autognosis["depth"] = min(loss_count, 10)

    save_autognosis(autognosis)

    # Output diagnosis
    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║  dte-dgen-narrative — BACKWARD PASS                    ║")
    print(f"╠══════════════════════════════════════════════════════════╣")
    print(f"║  Loss Type  : {loss_type:<42} ║")
    print(f"║  Layer      : {info['layer']} ({info['layer_name']:<35}) ║")
    print(f"║  Health     : {health.get(layer_key, 1.0):.0%}{'':<43} ║")
    print(f"║  Depth      : {autognosis['depth']:<42} ║")
    print(f"╠══════════════════════════════════════════════════════════╣")
    print(f"║  FIX: {info['fix'][:50]:<50} ║")
    if len(info['fix']) > 50:
        print(f"║       {info['fix'][50:]:<50} ║")
    print(f"╚══════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    main()
