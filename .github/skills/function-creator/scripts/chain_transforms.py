#!/usr/bin/env python3
"""
chain_transforms.py — Compose multiple skill transformations into chains and pipelines.

Supports sequential chains (A→B→C), parallel forks (A→[B,C]→D), and
transformation graphs for complex skill family generation.

Usage:
    python chain_transforms.py <chain_spec> [--output <output_dir>] [--validate]

Arguments:
    chain_spec    Path to chain specification YAML
    --output      Output directory for all generated skills (default: /home/ubuntu/skills/)
    --validate    Validate the chain spec without executing
    --visualize   Output a Mermaid diagram of the chain

Chain Spec Format:
    See templates/chain_spec.yaml for the full schema.

Example:
    python chain_transforms.py my_chain.yaml --output /home/ubuntu/skills/
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime

try:
    import yaml
    def load_yaml(path):
        with open(path) as f:
            return yaml.safe_load(f)
    def dump_yaml(data, path):
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
except ImportError:
    def load_yaml(path):
        with open(path) as f:
            return json.load(f)
    def dump_yaml(data, path):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


SCRIPTS_DIR = Path(__file__).parent


def validate_chain(chain: dict) -> list:
    """Validate a chain specification, return list of errors."""
    errors = []

    if "chain" not in chain:
        errors.append("Missing 'chain' key in specification")
        return errors

    meta = chain.get("meta", {})
    if not meta.get("name"):
        errors.append("Missing meta.name")

    steps = chain["chain"]
    if not isinstance(steps, list) or len(steps) == 0:
        errors.append("'chain' must be a non-empty list of steps")
        return errors

    step_ids = set()
    for i, step in enumerate(steps):
        step_id = step.get("id", f"step_{i}")
        if step_id in step_ids:
            errors.append(f"Duplicate step id: {step_id}")
        step_ids.add(step_id)

        if "source" not in step and i == 0:
            errors.append(f"Step {step_id}: first step must have 'source' (skill path or template manifest)")

        if "transform" not in step:
            errors.append(f"Step {step_id}: missing 'transform' specification")

        # Check dependencies
        deps = step.get("depends_on", [])
        for dep in deps:
            if dep not in step_ids:
                errors.append(f"Step {step_id}: dependency '{dep}' not found in prior steps")

    return errors


def resolve_execution_order(steps: list) -> list:
    """Topological sort of steps based on dependencies."""
    # Build adjacency
    step_map = {s.get("id", f"step_{i}"): s for i, s in enumerate(steps)}
    in_degree = {sid: 0 for sid in step_map}
    graph = {sid: [] for sid in step_map}

    for sid, step in step_map.items():
        for dep in step.get("depends_on", []):
            graph[dep].append(sid)
            in_degree[sid] += 1

    # Kahn's algorithm
    queue = [sid for sid, deg in in_degree.items() if deg == 0]
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(step_map):
        raise ValueError("Circular dependency detected in chain")

    return [(sid, step_map[sid]) for sid in order]


def generate_mermaid(chain: dict) -> str:
    """Generate a Mermaid diagram of the transformation chain."""
    lines = ["graph TD"]
    steps = chain["chain"]
    step_ids = []

    for i, step in enumerate(steps):
        sid = step.get("id", f"step_{i}")
        step_ids.append(sid)
        label = step.get("label", step.get("transform", {}).get("slot_mappings", {}).get("name", sid))
        lines.append(f'    {sid}["{label}"]')

    for i, step in enumerate(steps):
        sid = step.get("id", f"step_{i}")
        deps = step.get("depends_on", [])
        if deps:
            for dep in deps:
                lines.append(f"    {dep} --> {sid}")
        elif i > 0:
            prev_sid = step_ids[i - 1]
            source = step.get("source", "")
            if source == "previous":
                lines.append(f"    {prev_sid} --> {sid}")

    # Style
    lines.append("")
    lines.append("    classDef source fill:#e1f5fe,stroke:#01579b")
    lines.append("    classDef transform fill:#f3e5f5,stroke:#4a148c")
    if step_ids:
        lines.append(f"    class {step_ids[0]} source")
        for sid in step_ids[1:]:
            lines.append(f"    class {sid} transform")

    return "\n".join(lines)


def execute_chain(chain: dict, output_base: Path, dry_run: bool = False):
    """Execute a transformation chain."""
    import subprocess

    steps = chain["chain"]
    ordered = resolve_execution_order(steps)
    results = {}

    print(f"🔗 Executing chain: {chain.get('meta', {}).get('name', 'unnamed')}")
    print(f"   Steps: {len(ordered)}")
    print(f"   Output: {output_base}")
    print()

    for sid, step in ordered:
        print(f"⚙️  Step: {sid}")

        # Resolve source
        source = step.get("source", "")
        if source == "previous":
            # Use output of the dependency
            deps = step.get("depends_on", [])
            if deps:
                source = results[deps[0]]["manifest_path"]
            else:
                print(f"   ⚠️  'previous' source but no depends_on — skipping")
                continue
        elif source in results:
            source = results[source]["manifest_path"]

        # Step 1: Decompose if source is a skill path (not a manifest)
        source_path = Path(source)
        if source_path.is_dir() and (source_path / "SKILL.md").exists():
            decompose_output = output_base / f"_decomposed_{sid}"
            cmd = [
                sys.executable,
                str(SCRIPTS_DIR / "decompose_skill.py"),
                str(source_path),
                "--output", str(decompose_output),
            ]
            if dry_run:
                print(f"   [DRY RUN] Would decompose: {source_path}")
                manifest_path = str(decompose_output / "template_manifest.yaml")
            else:
                print(f"   Decomposing: {source_path}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"   ❌ Decompose failed: {result.stderr}")
                    continue
                manifest_path = str(decompose_output / "template_manifest.yaml")
        else:
            manifest_path = str(source_path)

        # Step 2: Write transform spec
        transform_spec = step.get("transform", {})
        spec_path = output_base / f"_spec_{sid}.yaml"
        if not dry_run:
            dump_yaml(transform_spec, spec_path)

        # Step 3: Transform
        new_name = transform_spec.get("slot_mappings", {}).get("name", f"{sid}_output")
        skill_output = output_base / new_name

        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "transform_skill.py"),
            manifest_path,
            str(spec_path),
            "--output", str(skill_output),
        ]

        if dry_run:
            print(f"   [DRY RUN] Would transform → {new_name}")
        else:
            print(f"   Transforming → {new_name}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"   ❌ Transform failed: {result.stderr}")
                print(f"   stdout: {result.stdout}")
                continue
            print(f"   ✅ Generated: {skill_output}")

        results[sid] = {
            "skill_path": str(skill_output),
            "manifest_path": manifest_path,
            "name": new_name,
        }

    # Summary
    print(f"\n📦 Chain execution complete!")
    print(f"   Generated {len(results)} skills:")
    for sid, info in results.items():
        print(f"   - {info['name']} ({info['skill_path']})")

    return results


def main():
    parser = argparse.ArgumentParser(description="Compose skill transformation chains")
    parser.add_argument("chain_spec", help="Path to chain specification YAML")
    parser.add_argument("--output", "-o", default="/home/ubuntu/skills/", help="Output base directory")
    parser.add_argument("--validate", action="store_true", help="Validate only")
    parser.add_argument("--visualize", action="store_true", help="Output Mermaid diagram")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show plan without executing")
    args = parser.parse_args()

    chain = load_yaml(args.chain_spec)

    # Validate
    errors = validate_chain(chain)
    if errors:
        print("❌ Validation errors:")
        for err in errors:
            print(f"   - {err}")
        sys.exit(1)
    else:
        print("✅ Chain specification is valid")

    if args.validate:
        return

    # Visualize
    if args.visualize:
        mermaid = generate_mermaid(chain)
        output_path = Path(args.chain_spec).with_suffix(".mmd")
        output_path.write_text(mermaid, encoding="utf-8")
        print(f"📊 Mermaid diagram: {output_path}")
        print(mermaid)
        return

    # Execute
    output_base = Path(args.output)
    execute_chain(chain, output_base, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
