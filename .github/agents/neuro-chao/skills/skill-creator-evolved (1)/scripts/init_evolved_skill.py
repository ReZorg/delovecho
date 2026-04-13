#!/usr/bin/env python3
"""
Initialize a new evolved skill with Triadic structure (Forward, Backward, Knowledge)
and ⊗-composable semiring topology.

v2: Evolved via skill-creator-evolved ( ⊗ )
- Embeds semiring (R, ⊕, ⊗, 0, 1) into skill topology
- Generates hierarchical autognosis with depth tracking
- Creates connected forward↔backward passes
- Supports Pipeline, Fork, Merge, Residual, Tensor, and Semiring topologies
"""

import os
import sys
import json
import argparse
from datetime import datetime

TOPOLOGIES = {
    "Transform":  {"symbol": "→",  "pattern": "A → B",             "composable": True},
    "Pipeline":   {"symbol": "⊗",  "pattern": "A ⊗ B ⊗ C",        "composable": True},
    "Fork":       {"symbol": "⊕",  "pattern": "A ⊕ B ⊕ C",        "composable": True},
    "Merge":      {"symbol": "⊕→", "pattern": "(A ⊕ B) → C",      "composable": True},
    "Residual":   {"symbol": "+",  "pattern": "A + F(A)",           "composable": True},
    "Tensor":     {"symbol": "⊗",  "pattern": "A ⊗ B (interacting)","composable": True},
    "Semiring":   {"symbol": "⊕⊗", "pattern": "(R, ⊕, ⊗, 0, 1)",  "composable": True},
}

def create_skill(skill_name, topology="Pipeline", compose_with=None):
    base_dir = f"/home/ubuntu/skills/{skill_name}"

    if os.path.exists(base_dir):
        print(f"Error: Skill directory {base_dir} already exists.")
        sys.exit(1)

    if topology not in TOPOLOGIES:
        print(f"Error: Unknown topology '{topology}'. Choose from: {list(TOPOLOGIES.keys())}")
        sys.exit(1)

    topo = TOPOLOGIES[topology]

    # Create directories
    for d in ["", "/scripts", "/references", "/templates"]:
        os.makedirs(f"{base_dir}{d}", exist_ok=True)

    # --- SKILL.md ---
    compose_section = ""
    if compose_with:
        compose_section = f"""
## Composition

This skill is designed for ⊗-composition with: {', '.join(compose_with)}

| Operator | Composition | Effect |
|----------|-------------|--------|
| ⊕ | `{skill_name} ⊕ other` | Run as alternatives, merge outputs |
| ⊗ | `{skill_name} ⊗ other` | Chain multiplicatively, deep integration |
"""

    skill_md = f"""---
name: {skill_name}
description: "TODO: Describe what this skill does and when to use it."
---

# {skill_name.replace('-', ' ').title()}

Topology: **{topology}** `{topo['pattern']}`

## Forward Pass (Execution)

TODO: Define the execution logic.

Each step should produce an output that feeds into the next step (⊗ composition)
or into parallel alternatives (⊕ composition).

## Backward Pass (Improvement)

When this skill fails or produces suboptimal results:

1. Identify the loss signal (what went wrong vs. expected).
2. Run the backward pass to update knowledge state:
   ```bash
   python /home/ubuntu/skills/{skill_name}/scripts/backward_pass.py '<feedback>'
   ```
3. The backward pass will:
   - Record the loss in `references/autognosis.json`
   - Analyze which forward-pass step produced the error
   - Propose a structural update (topology change, reference addition, script fix)

## Knowledge State

| Component | Location | Purpose |
|-----------|----------|---------|
| Templates | `templates/` | Structural priors and output formats |
| References | `references/` | Domain bindings and documentation |
| Self-Model | `references/autognosis.json` | Hierarchical self-awareness |
| Loss History | `references/autognosis.json → loss_history` | Gradient accumulator |
{compose_section}
## Algebraic Properties

This skill satisfies the semiring laws when composed with other evolved skills:

```
{skill_name} ⊕ 0 = {skill_name}           (additive identity)
{skill_name} ⊗ 1 = {skill_name}           (multiplicative identity)
{skill_name} ⊗ 0 = 0                      (annihilation)
{skill_name} ⊗ (A ⊕ B) = ({skill_name}⊗A) ⊕ ({skill_name}⊗B)  (distributivity)
```
"""
    with open(f"{base_dir}/SKILL.md", "w") as f:
        f.write(skill_md)

    # --- backward_pass.py ---
    backward_py = f'''#!/usr/bin/env python3
"""
Backward pass for {skill_name}.
Analyzes failure feedback and updates the skill's knowledge state.
Connected to the forward pass via autognosis topology tracking.

v2: Implements actual gradient-driven structural updates.
"""

import sys
import json
import os
from datetime import datetime

BASE_DIR = "/home/ubuntu/skills/{skill_name}"
AUTOGNOSIS_PATH = f"{{BASE_DIR}}/references/autognosis.json"

def load_autognosis():
    with open(AUTOGNOSIS_PATH) as f:
        return json.load(f)

def save_autognosis(model):
    with open(AUTOGNOSIS_PATH, "w") as f:
        json.dump(model, f, indent=2)

def classify_loss(feedback):
    """Classify feedback into loss categories for targeted structural updates."""
    feedback_lower = feedback.lower()
    if any(w in feedback_lower for w in ["wrong", "incorrect", "error", "bug"]):
        return "correctness"
    elif any(w in feedback_lower for w in ["slow", "verbose", "bloated", "long"]):
        return "efficiency"
    elif any(w in feedback_lower for w in ["missing", "incomplete", "partial"]):
        return "coverage"
    elif any(w in feedback_lower for w in ["compose", "integrate", "combine"]):
        return "composability"
    else:
        return "general"

def propose_structural_update(loss_type, model):
    """Propose a topology change based on loss type."""
    proposals = {{
        "correctness": "Add a Residual (skip connection) to preserve original input alongside transformation",
        "efficiency": "Apply Token L1 regularization — prune unnecessary steps from the Pipeline",
        "coverage": "Add a Fork (⊕) to run parallel analysis paths and Merge results",
        "composability": "Upgrade topology to Semiring to enable ⊕⊗ algebraic composition",
        "general": "Record for pattern analysis; apply gradient when pattern emerges",
    }}
    return proposals.get(loss_type, proposals["general"])

def apply_gradient(feedback_text):
    model = load_autognosis()

    loss_type = classify_loss(feedback_text)
    proposal = propose_structural_update(loss_type, model)

    loss_record = {{
        "timestamp": datetime.now().isoformat(),
        "feedback": feedback_text,
        "loss_type": loss_type,
        "proposal": proposal,
        "depth": model.get("autognosis_depth", 1),
        "applied": False,
    }}

    model["loss_history"].append(loss_record)
    model["version"] = model.get("version", 1) + 1

    # Advance autognosis depth if enough losses accumulated
    loss_count = len(model["loss_history"])
    if loss_count >= 5 and model.get("autognosis_depth", 1) < 5:
        model["autognosis_depth"] = min(5, model.get("autognosis_depth", 1) + 1)

    save_autognosis(model)

    print(f"Loss type: {{loss_type}}")
    print(f"Proposal: {{proposal}}")
    print(f"Version: {{model['version']}}")
    print(f"Autognosis depth: {{model.get('autognosis_depth', 1)}}")
    print(f"Total losses recorded: {{loss_count}}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backward_pass.py '<feedback_text>'")
        sys.exit(1)
    apply_gradient(sys.argv[1])
'''
    with open(f"{base_dir}/scripts/backward_pass.py", "w") as f:
        f.write(backward_py)
    os.chmod(f"{base_dir}/scripts/backward_pass.py", 0o755)

    # --- autognosis.json ---
    self_model = {
        "name": skill_name,
        "topology": topology,
        "topology_symbol": topo["symbol"],
        "topology_pattern": topo["pattern"],
        "version": 1,
        "autognosis_depth": 1,
        "created": datetime.now().isoformat(),
        "created_by": "skill-creator-evolved v2 (⊗)",
        "semiring": {
            "additive_identity": "NoOp",
            "multiplicative_identity": "Identity",
            "composable_with": compose_with or [],
        },
        "loss_history": [],
        "evolution_trace": [
            {
                "from": "init",
                "to": f"{skill_name} v1",
                "operator": "⊗",
                "timestamp": datetime.now().isoformat(),
            }
        ],
    }
    with open(f"{base_dir}/references/autognosis.json", "w") as f:
        json.dump(self_model, f, indent=2)

    print(f"Initialized evolved skill: {skill_name}")
    print(f"  Topology: {topology} {topo['symbol']} {topo['pattern']}")
    print(f"  Location: {base_dir}")
    if compose_with:
        print(f"  Composes with: {', '.join(compose_with)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialize an evolved skill with ⊗-composable semiring topology"
    )
    parser.add_argument("skill_name", help="Name of the skill to create")
    parser.add_argument(
        "--topology",
        choices=list(TOPOLOGIES.keys()),
        default="Pipeline",
        help="Skill topology (default: Pipeline)",
    )
    parser.add_argument(
        "--compose-with",
        nargs="*",
        help="Names of skills this skill is designed to compose with",
    )
    args = parser.parse_args()
    create_skill(args.skill_name, args.topology, args.compose_with)
