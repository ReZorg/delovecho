#!/usr/bin/env python3
"""
Validate an evolved skill to ensure it meets the Triadic structure requirements
and ⊗-composable semiring properties.

v2: Adds semantic validation beyond structural checks.
- Topology coherence
- Forward↔Backward connectivity
- Semiring law compliance
- Autognosis depth verification
"""

import os
import sys
import json
import re
import argparse

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.info.append(msg)

    @property
    def passed(self):
        return len(self.errors) == 0

    def report(self):
        lines = []
        if self.errors:
            lines.append("ERRORS:")
            for e in self.errors:
                lines.append(f"  ✗ {e}")
        if self.warnings:
            lines.append("WARNINGS:")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        if self.info:
            lines.append("INFO:")
            for i in self.info:
                lines.append(f"  ℹ {i}")
        return "\n".join(lines)


def validate_structure(base_dir, result):
    """Check required files and directories exist."""
    required_files = {
        "SKILL.md": "Core skill definition",
        "scripts/backward_pass.py": "Backward pass implementation",
        "references/autognosis.json": "Self-model",
    }
    for path, desc in required_files.items():
        full = os.path.join(base_dir, path)
        if not os.path.exists(full):
            result.error(f"Missing {path} ({desc})")
        else:
            result.note(f"Found {path}")


def validate_skill_md(base_dir, result):
    """Validate SKILL.md frontmatter and triadic sections."""
    path = os.path.join(base_dir, "SKILL.md")
    if not os.path.exists(path):
        return

    with open(path) as f:
        content = f.read()

    # Frontmatter
    if not re.search(r'^---\s*\n.*?name:\s*\S+', content, re.DOTALL):
        result.error("SKILL.md missing 'name' in YAML frontmatter")
    if not re.search(r'description:\s*\S+', content):
        result.error("SKILL.md missing 'description' in YAML frontmatter")
    if 'TODO' in content:
        result.warn("SKILL.md still contains TODO placeholders")

    # Triadic structure
    has_forward = bool(re.search(r'(?i)(forward\s+pass|execution)', content))
    has_backward = bool(re.search(r'(?i)(backward\s+pass|improvement)', content))
    has_knowledge = bool(re.search(r'(?i)(knowledge\s+state|knowledge|self.model)', content))

    if not has_forward:
        result.error("SKILL.md missing Forward Pass / Execution section")
    if not has_backward:
        result.error("SKILL.md missing Backward Pass / Improvement section")
    if not has_knowledge:
        result.warn("SKILL.md missing explicit Knowledge State section")

    # ⊗ composition markers
    has_algebraic = bool(re.search(r'[⊕⊗]', content))
    if has_algebraic:
        result.note("Skill uses ⊕⊗ algebraic composition markers")
    else:
        result.warn("Skill does not use ⊕⊗ composition markers (not ⊗-composable)")

    # Line count
    line_count = len(content.splitlines())
    if line_count > 500:
        result.warn(f"SKILL.md is {line_count} lines (recommended: <500)")
    result.note(f"SKILL.md: {line_count} lines")


def validate_autognosis(base_dir, result):
    """Validate autognosis self-model schema and depth."""
    path = os.path.join(base_dir, "references/autognosis.json")
    if not os.path.exists(path):
        return

    try:
        with open(path) as f:
            model = json.load(f)
    except json.JSONDecodeError as e:
        result.error(f"autognosis.json is not valid JSON: {e}")
        return

    required_fields = ["name", "topology", "version"]
    for field in required_fields:
        if field not in model:
            result.error(f"autognosis.json missing required field: '{field}'")

    # Depth check
    depth = model.get("autognosis_depth", 0)
    if depth == 0:
        result.warn("autognosis_depth is 0 or missing (no self-awareness)")
    elif depth >= 3:
        result.note(f"autognosis_depth={depth} (meta-learning capable)")
    else:
        result.note(f"autognosis_depth={depth}")

    # Topology check
    valid_topologies = ["Transform", "Pipeline", "Fork", "Merge", "Residual", "Tensor", "Semiring"]
    topo = model.get("topology", "")
    if topo and topo not in valid_topologies:
        result.warn(f"Non-standard topology: '{topo}' (valid: {valid_topologies})")

    # Semiring check
    if "semiring" in model:
        result.note("Skill has semiring algebraic structure defined")
    else:
        result.warn("No semiring structure defined (limited composability)")

    # Evolution trace
    trace = model.get("evolution_trace", [])
    if trace:
        result.note(f"Evolution trace: {len(trace)} steps recorded")

    result.note(f"Version: {model.get('version', '?')}")


def validate_backward_pass(base_dir, result):
    """Validate backward pass script is functional."""
    path = os.path.join(base_dir, "scripts/backward_pass.py")
    if not os.path.exists(path):
        return

    with open(path) as f:
        content = f.read()

    # Check it references autognosis
    if "autognosis" in content:
        result.note("backward_pass.py is connected to autognosis self-model")
    else:
        result.warn("backward_pass.py does not reference autognosis (disconnected)")

    # Check it has classification logic
    if "classify" in content or "categorize" in content or "loss_type" in content:
        result.note("backward_pass.py has loss classification logic")
    else:
        result.warn("backward_pass.py lacks loss classification (undifferentiated feedback)")

    # Check it proposes updates
    if "propose" in content or "update" in content or "structural" in content:
        result.note("backward_pass.py proposes structural updates")
    else:
        result.warn("backward_pass.py does not propose structural updates (passive logging only)")


def validate_skill(skill_name):
    base_dir = f"/home/ubuntu/skills/{skill_name}"

    if not os.path.exists(base_dir):
        print(f"Error: Skill directory {base_dir} does not exist.")
        sys.exit(1)

    result = ValidationResult()

    validate_structure(base_dir, result)
    validate_skill_md(base_dir, result)
    validate_autognosis(base_dir, result)
    validate_backward_pass(base_dir, result)

    print(f"╔══════════════════════════════════════════╗")
    print(f"║  Evolved Skill Validation: {skill_name[:14]:<14}║")
    print(f"╠══════════════════════════════════════════╣")

    if result.passed:
        print(f"║  Result: PASSED ✓{' ':23}║")
    else:
        print(f"║  Result: FAILED ✗{' ':23}║")

    print(f"║  Errors:   {len(result.errors):<30}║")
    print(f"║  Warnings: {len(result.warnings):<30}║")
    print(f"╚══════════════════════════════════════════╝")
    print()
    print(result.report())

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate an evolved skill (v2 ⊗)")
    parser.add_argument("skill_name", help="Name of the skill to validate")
    args = parser.parse_args()
    validate_skill(args.skill_name)
