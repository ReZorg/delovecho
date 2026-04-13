#!/usr/bin/env python3
"""
transform_skill.py — Transform a decomposed skill template into a new domain.

Takes a template manifest (from decompose_skill.py) and a transform specification,
then generates a new skill in the target domain while preserving the invariant structure.

Usage:
    python transform_skill.py <template_manifest> <transform_spec> [--output <output_dir>]

Arguments:
    template_manifest   Path to template_manifest.yaml from decompose_skill.py
    transform_spec      Path to transform specification YAML (or use --interactive)
    --output            Output directory for the new skill (default: /home/ubuntu/skills/<new_name>)
    --interactive       Interactively build the transform spec
    --dry-run           Show what would be generated without writing files

Output:
    A new skill directory with transformed SKILL.md, scripts, references, and templates.

Example:
    # Transform fnb-statement-extract into capitec-statement-extract
    python transform_skill.py ./fnb_template/template_manifest.yaml ./capitec_transform.yaml

    # Interactive mode
    python transform_skill.py ./fnb_template/template_manifest.yaml --interactive
"""

import argparse
import os
import re
import sys
import shutil
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
    import json
    def load_yaml(path):
        """Fallback: parse simple YAML as key-value pairs."""
        data = {}
        with open(path) as f:
            content = f.read()
        # Try JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        # Simple YAML parser
        current_key = None
        current_dict = data
        for line in content.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" in stripped:
                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip()
                if value:
                    current_dict[key] = value
                else:
                    current_dict[key] = {}
                    current_key = key
        return data

    def dump_yaml(data, path):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


def build_replacement_map(manifest: dict, transform: dict) -> dict:
    """Build a comprehensive term replacement map from manifest slots and transform spec."""
    replacements = {}

    # Map parameterized slots to new values
    slots = manifest.get("parameterized_slots", {})
    mappings = transform.get("slot_mappings", {})

    for slot_name, slot_info in slots.items():
        current = slot_info.get("current", "")
        new_value = mappings.get(slot_name, current)

        if isinstance(current, str) and isinstance(new_value, str) and current != new_value:
            replacements[current] = new_value
        elif isinstance(current, list) and isinstance(new_value, list):
            for old, new in zip(current, new_value):
                if old != new:
                    replacements[str(old)] = str(new)

    # Add explicit term mappings
    term_map = transform.get("term_mappings", {})
    replacements.update(term_map)

    # Add file rename mappings
    file_map = transform.get("file_mappings", {})
    replacements.update(file_map)

    return replacements


def transform_text(text: str, replacements: dict, case_sensitive: bool = True) -> str:
    """Apply all replacements to text, preserving case patterns when possible."""
    result = text
    # Sort by length descending to avoid partial replacements
    sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)

    for old, new in sorted_replacements:
        if not old:
            continue
        if case_sensitive:
            result = result.replace(old, new)
        else:
            # Case-insensitive with case preservation
            pattern = re.compile(re.escape(old), re.IGNORECASE)
            def case_repl(match):
                matched = match.group(0)
                if matched.isupper():
                    return new.upper()
                elif matched.islower():
                    return new.lower()
                elif matched[0].isupper():
                    return new[0].upper() + new[1:] if len(new) > 1 else new.upper()
                return new
            result = pattern.sub(case_repl, result)

    return result


def transform_file(src_path: Path, dst_path: Path, replacements: dict, file_type: str = "text"):
    """Transform a single file by applying replacements."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    if file_type == "binary":
        shutil.copy2(src_path, dst_path)
        return

    try:
        content = src_path.read_text(encoding="utf-8")
        transformed = transform_text(content, replacements, case_sensitive=False)
        dst_path.write_text(transformed, encoding="utf-8")
    except UnicodeDecodeError:
        shutil.copy2(src_path, dst_path)


def transform_filename(name: str, replacements: dict) -> str:
    """Transform a filename using the replacement map."""
    result = name
    for old, new in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        if old.lower() in result.lower():
            result = re.sub(re.escape(old), new, result, flags=re.IGNORECASE)
    return result


def generate_transform_spec_interactive(manifest: dict) -> dict:
    """Interactively build a transform specification."""
    print("\n🎯 Interactive Transform Specification Builder")
    print("=" * 50)

    spec = {
        "meta": {
            "source_skill": manifest["meta"]["source_skill"],
            "created": datetime.now().isoformat(),
        },
        "slot_mappings": {},
        "term_mappings": {},
        "file_mappings": {},
    }

    slots = manifest.get("parameterized_slots", {})

    print(f"\nSource skill: {manifest['meta']['source_skill']}")
    print(f"Primary domain: {slots.get('primary_domain', {}).get('current', 'unknown')}")
    print(f"\nProvide new values for each slot (press Enter to keep current):\n")

    for slot_name, slot_info in slots.items():
        current = slot_info.get("current", "")
        desc = slot_info.get("description", "")
        display_current = current if isinstance(current, str) else str(current)[:60]
        new_value = input(f"  {slot_name} [{display_current}]: ").strip()
        if new_value:
            spec["slot_mappings"][slot_name] = new_value

    print("\nAdditional term mappings (empty line to finish):")
    while True:
        old = input("  Old term: ").strip()
        if not old:
            break
        new = input(f"  New term for '{old}': ").strip()
        if new:
            spec["term_mappings"][old] = new

    return spec


def generate_transform_report(manifest: dict, transform: dict, replacements: dict, output_dir: Path) -> str:
    """Generate a human-readable transformation report."""
    lines = [
        "# Transformation Report",
        "",
        f"**Source skill**: {manifest['meta']['source_skill']}",
        f"**Target skill**: {transform.get('slot_mappings', {}).get('name', 'unknown')}",
        f"**Generated**: {datetime.now().isoformat()}",
        "",
        "## Replacement Map",
        "",
        "| Original | Replacement |",
        "|----------|-------------|",
    ]
    for old, new in sorted(replacements.items()):
        lines.append(f"| `{old}` | `{new}` |")

    lines.extend([
        "",
        "## Structure Preserved",
        "",
    ])
    inv = manifest.get("invariant_structure", {})
    for section in inv.get("sections", []):
        lines.append(f"- {section}")

    lines.extend([
        "",
        "## Next Steps",
        "",
        "1. Review the generated SKILL.md for accuracy",
        "2. Update scripts with domain-specific logic",
        "3. Add domain-specific references and templates",
        "4. Test with real tasks in the target domain",
        "5. Validate with skill-creator's quick_validate.py",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Transform a skill template into a new domain")
    parser.add_argument("template_manifest", help="Path to template_manifest.yaml")
    parser.add_argument("transform_spec", nargs="?", help="Path to transform specification YAML")
    parser.add_argument("--output", "-o", help="Output directory for the new skill")
    parser.add_argument("--interactive", "-i", action="store_true", help="Build transform spec interactively")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show plan without writing files")
    args = parser.parse_args()

    # Load manifest
    manifest = load_yaml(args.template_manifest)
    source_path = Path(manifest["meta"]["source_path"])
    print(f"🔄 Transforming skill: {manifest['meta']['source_skill']}")

    # Load or build transform spec
    if args.interactive:
        transform = generate_transform_spec_interactive(manifest)
    elif args.transform_spec:
        transform = load_yaml(args.transform_spec)
    else:
        print("ERROR: Provide a transform_spec path or use --interactive", file=sys.stderr)
        sys.exit(1)

    # Determine output directory
    new_name = transform.get("slot_mappings", {}).get("name", manifest["meta"]["source_skill"] + "-transformed")
    output_dir = Path(args.output) if args.output else Path(f"/home/ubuntu/skills/{new_name}")

    # Build replacement map
    replacements = build_replacement_map(manifest, transform)
    print(f"✅ Built replacement map: {len(replacements)} mappings")

    if args.dry_run:
        print("\n📋 Dry run — would apply these replacements:")
        for old, new in sorted(replacements.items()):
            print(f"   {old} → {new}")
        print(f"\n   Output: {output_dir}")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"   Target: {output_dir}")

    # Transform SKILL.md
    skill_md_src = source_path / "SKILL.md"
    if skill_md_src.exists():
        transform_file(skill_md_src, output_dir / "SKILL.md", replacements)
        print(f"✅ Transformed SKILL.md")

    # Transform all resource files
    for category in ["scripts", "references", "templates"]:
        src_dir = source_path / category
        if not src_dir.exists():
            continue
        for src_file in src_dir.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(source_path)
                new_filename = transform_filename(rel_path.name, replacements)
                new_rel = rel_path.parent / new_filename
                dst_file = output_dir / new_rel

                ext = src_file.suffix.lower()
                file_type = "binary" if ext in {".png", ".jpg", ".gif", ".ico", ".woff", ".ttf"} else "text"
                transform_file(src_file, dst_file, replacements, file_type)
                print(f"   ✅ {rel_path} → {new_rel}")

    # Generate transformation report
    report = generate_transform_report(manifest, transform, replacements, output_dir)
    (output_dir / "TRANSFORM_REPORT.md").write_text(report, encoding="utf-8")
    print(f"✅ Generated TRANSFORM_REPORT.md")

    # Save the transform spec for reproducibility
    dump_yaml(transform, output_dir / "transform_spec.yaml")
    print(f"✅ Saved transform_spec.yaml")

    print(f"\n📦 Transformation complete!")
    print(f"   New skill: {output_dir}")
    print(f"\nNext steps:")
    print(f"   1. Review {output_dir / 'SKILL.md'}")
    print(f"   2. Update domain-specific scripts and references")
    print(f"   3. Validate: python /home/ubuntu/skills/skill-creator/scripts/quick_validate.py {new_name}")


if __name__ == "__main__":
    main()
