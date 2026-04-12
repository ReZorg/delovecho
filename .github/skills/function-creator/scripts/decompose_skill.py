#!/usr/bin/env python3
"""
decompose_skill.py — Decompose a skill into its abstract template and domain bindings.

Analyzes a skill directory, identifies invariant structure vs. domain-specific elements,
and outputs a parameterized skill template manifest (YAML) ready for transformation.

Usage:
    python decompose_skill.py <skill_path> [--output <output_dir>]

Arguments:
    skill_path    Path to the skill directory (must contain SKILL.md)
    --output      Output directory for the template manifest (default: ./output)

Output:
    <output_dir>/template_manifest.yaml   — Parameterized skill template
    <output_dir>/domain_bindings.yaml     — Extracted domain-specific bindings
    <output_dir>/structure_map.yaml       — Structural analysis of the skill

Example:
    python decompose_skill.py /home/ubuntu/skills/fnb-statement-extract --output ./fnb_template
"""

import argparse
import os
import re
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    # Inline minimal YAML emitter for environments without PyYAML
    class yaml:
        @staticmethod
        def dump(data, stream=None, default_flow_style=False, sort_keys=False, allow_unicode=True):
            result = _minimal_yaml_dump(data)
            if stream:
                stream.write(result)
                return None
            return result

def _minimal_yaml_dump(data, indent=0):
    """Minimal YAML serializer for when PyYAML is unavailable."""
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{k}:")
                lines.append(_minimal_yaml_dump(v, indent + 1))
            else:
                lines.append(f"{prefix}{k}: {_format_value(v)}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.append(_minimal_yaml_dump(item, indent + 1))
            else:
                lines.append(f"{prefix}- {_format_value(item)}")
    else:
        lines.append(f"{prefix}{_format_value(data)}")
    return "\n".join(lines)

def _format_value(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        if "\n" in v or ":" in v or "#" in v:
            return f'"{v}"'
        return v
    return str(v)


# --- Domain Detection Patterns ---

DOMAIN_INDICATORS = {
    "finance": [
        r"\b(bank|statement|transaction|balance|debit|credit|ledger|account|payment)\b",
        r"\b(FNB|ABSA|Nedbank|Capitec|Standard Bank|Investec)\b",
        r"\b(SWIFT|IBAN|BIC|forex|currency|interest|dividend)\b",
    ],
    "email": [
        r"\b(mailbox|inbox|message|email|SMTP|IMAP|POP3|Exchange|Graph API)\b",
        r"\b(sender|recipient|subject|attachment|folder|draft|sent)\b",
    ],
    "skincare": [
        r"\b(skin|formulation|ingredient|SPF|retinol|peptide|serum|moisturizer)\b",
        r"\b(Zone Concept|anti-inflammatory|anti-oxidant|rejuvenation)\b",
    ],
    "legal": [
        r"\b(case|court|affidavit|filing|evidence|plaintiff|defendant|judgment)\b",
        r"\b(interdict|perjury|disclosure|burden of proof|litigation)\b",
    ],
    "stock_market": [
        r"\b(stock|ticker|SEC|filing|insider|portfolio|market cap|P/E ratio)\b",
        r"\b(bull|bear|dividend|earnings|IPO|NASDAQ|NYSE)\b",
    ],
    "devops": [
        r"\b(deploy|CI/CD|pipeline|container|Docker|Kubernetes|Terraform)\b",
        r"\b(AWS|Azure|GCP|Cloudflare|serverless|Lambda|Function)\b",
    ],
    "data_sync": [
        r"\b(sync|backup|delta|incremental|batch|ETL|migration|replicate)\b",
        r"\b(PostgreSQL|MySQL|Neon|database|schema|table|query)\b",
    ],
}

# Structural element patterns
STRUCTURAL_PATTERNS = {
    "workflow_steps": r"^\d+\.\s+\*\*(.+?)\*\*",
    "section_headers": r"^#{1,4}\s+(.+)",
    "script_references": r"(?:python|bash)\s+[\w/]+/scripts/(\w+\.(?:py|sh))",
    "file_references": r"(?:references|templates)/[\w.-]+",
    "code_blocks": r"```(\w+)?\n(.*?)```",
    "table_rows": r"\|(.+)\|",
    "yaml_frontmatter": r"^---\n(.*?)\n---",
}


def parse_skill_md(skill_path: Path) -> dict:
    """Parse SKILL.md into frontmatter and body sections."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"ERROR: No SKILL.md found at {skill_md}", file=sys.stderr)
        sys.exit(1)

    content = skill_md.read_text(encoding="utf-8")

    # Extract frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
    if fm_match:
        frontmatter_raw = fm_match.group(1)
        body = fm_match.group(2)
        # Parse simple YAML frontmatter
        frontmatter = {}
        for line in frontmatter_raw.strip().split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                frontmatter[key.strip()] = value.strip()
    else:
        frontmatter = {}
        body = content

    return {"frontmatter": frontmatter, "body": body, "raw": content}


def detect_domains(text: str) -> dict:
    """Detect domain indicators in text, return domain scores."""
    scores = {}
    text_lower = text.lower()
    for domain, patterns in DOMAIN_INDICATORS.items():
        matches = 0
        matched_terms = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches += len(found)
            matched_terms.extend(found)
        if matches > 0:
            scores[domain] = {
                "score": matches,
                "matched_terms": list(set(matched_terms))[:10],
            }
    return scores


def extract_structure(body: str) -> dict:
    """Extract structural elements from the skill body."""
    structure = {}

    # Sections
    sections = []
    for match in re.finditer(r"^(#{1,4})\s+(.+)", body, re.MULTILINE):
        sections.append({
            "level": len(match.group(1)),
            "title": match.group(2).strip(),
            "position": match.start(),
        })
    structure["sections"] = sections

    # Workflow steps
    steps = re.findall(r"^\d+\.\s+\*\*(.+?)\*\*", body, re.MULTILINE)
    structure["workflow_steps"] = steps

    # Script references
    scripts = re.findall(r"[\w/]+/scripts/([\w.-]+)", body)
    structure["script_references"] = list(set(scripts))

    # Reference file mentions
    refs = re.findall(r"(?:references|templates)/([\w.-]+)", body)
    structure["reference_files"] = list(set(refs))

    # Code blocks with language
    code_blocks = []
    for match in re.finditer(r"```(\w+)?\n(.*?)```", body, re.DOTALL):
        code_blocks.append({
            "language": match.group(1) or "unknown",
            "length": len(match.group(2).strip().split("\n")),
        })
    structure["code_blocks"] = code_blocks

    # Tables
    tables = re.findall(r"(\|.+\|(?:\n\|.+\|)+)", body)
    structure["table_count"] = len(tables)

    return structure


def inventory_resources(skill_path: Path) -> dict:
    """Inventory all bundled resources in the skill directory."""
    resources = {"scripts": [], "references": [], "templates": [], "other": []}

    for root, dirs, files in os.walk(skill_path):
        rel_root = Path(root).relative_to(skill_path)
        for f in files:
            if f == "SKILL.md":
                continue
            rel_path = str(rel_root / f)
            entry = {
                "path": rel_path,
                "size": (Path(root) / f).stat().st_size,
                "extension": Path(f).suffix,
            }
            if "scripts" in rel_path:
                resources["scripts"].append(entry)
            elif "references" in rel_path:
                resources["references"].append(entry)
            elif "templates" in rel_path:
                resources["templates"].append(entry)
            else:
                resources["other"].append(entry)

    return resources


def extract_domain_bindings(parsed: dict, domains: dict, structure: dict) -> dict:
    """Extract domain-specific bindings that would need to change in a transformation."""
    body = parsed["body"]
    bindings = {
        "name": parsed["frontmatter"].get("name", ""),
        "description": parsed["frontmatter"].get("description", ""),
        "primary_domain": max(domains, key=lambda d: domains[d]["score"]) if domains else "general",
        "domain_terms": [],
        "api_references": [],
        "tool_references": [],
        "data_formats": [],
        "external_services": [],
    }

    # Collect all domain-specific terms
    for domain_info in domains.values():
        bindings["domain_terms"].extend(domain_info["matched_terms"])
    bindings["domain_terms"] = list(set(bindings["domain_terms"]))

    # Detect API references
    api_patterns = re.findall(r"(?:API|endpoint|URL|https?://\S+)", body, re.IGNORECASE)
    bindings["api_references"] = list(set(api_patterns))[:10]

    # Detect data format references
    format_patterns = re.findall(r"\b(JSON|YAML|CSV|XML|PDF|XLSX|HTML|SQL)\b", body, re.IGNORECASE)
    bindings["data_formats"] = list(set(f.upper() for f in format_patterns))

    # Detect external service references
    service_patterns = re.findall(
        r"\b(Microsoft Graph|Exchange Online|Neon|PostgreSQL|MySQL|Cloudflare|GitHub|Slack|Notion)\b",
        body, re.IGNORECASE
    )
    bindings["external_services"] = list(set(service_patterns))

    return bindings


def build_template_manifest(parsed: dict, structure: dict, bindings: dict, resources: dict, skill_path: Path) -> dict:
    """Build the parameterized skill template manifest."""
    name = bindings["name"]
    manifest = {
        "meta": {
            "template_version": "1.0",
            "source_skill": name,
            "source_path": str(skill_path),
            "created": datetime.now().isoformat(),
            "checksum": hashlib.sha256(parsed["raw"].encode()).hexdigest()[:16],
        },
        "invariant_structure": {
            "sections": [s["title"] for s in structure["sections"]],
            "workflow_steps": structure["workflow_steps"],
            "code_block_languages": list(set(cb["language"] for cb in structure["code_blocks"])),
            "has_tables": structure["table_count"] > 0,
            "script_count": len(resources["scripts"]),
            "reference_count": len(resources["references"]),
            "template_count": len(resources["templates"]),
        },
        "parameterized_slots": {
            "name": {"current": name, "slot": "{{skill_name}}", "description": "Skill name"},
            "description": {
                "current": bindings["description"],
                "slot": "{{skill_description}}",
                "description": "Skill description with domain-specific triggers",
            },
            "primary_domain": {
                "current": bindings["primary_domain"],
                "slot": "{{target_domain}}",
                "description": "Primary domain context",
            },
            "domain_terms": {
                "current": bindings["domain_terms"],
                "slot": "{{domain_terms}}",
                "description": "Domain-specific terminology to replace",
            },
            "api_references": {
                "current": bindings["api_references"],
                "slot": "{{api_references}}",
                "description": "API endpoints and external service references",
            },
            "data_formats": {
                "current": bindings["data_formats"],
                "slot": "{{data_formats}}",
                "description": "Data formats used by the skill",
            },
            "external_services": {
                "current": bindings["external_services"],
                "slot": "{{external_services}}",
                "description": "External services the skill integrates with",
            },
        },
        "resource_inventory": resources,
        "composition_interface": {
            "inputs": structure["workflow_steps"][:1] if structure["workflow_steps"] else ["task"],
            "outputs": structure["workflow_steps"][-1:] if structure["workflow_steps"] else ["result"],
            "chainable": True,
            "parallelizable": len(structure["workflow_steps"]) > 3,
        },
    }
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Decompose a skill into template + domain bindings")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--output", "-o", default="./output", help="Output directory")
    args = parser.parse_args()

    skill_path = Path(args.skill_path).resolve()
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🔍 Decomposing skill: {skill_path.name}")
    print(f"   Source: {skill_path}")
    print(f"   Output: {output_dir}")

    # Step 1: Parse SKILL.md
    parsed = parse_skill_md(skill_path)
    print(f"✅ Parsed SKILL.md ({len(parsed['body'])} chars)")

    # Step 2: Detect domains
    domains = detect_domains(parsed["body"])
    primary = max(domains, key=lambda d: domains[d]["score"]) if domains else "general"
    print(f"✅ Detected domains: {', '.join(domains.keys()) or 'general'} (primary: {primary})")

    # Step 3: Extract structure
    structure = extract_structure(parsed["body"])
    print(f"✅ Extracted structure: {len(structure['sections'])} sections, {len(structure['workflow_steps'])} workflow steps")

    # Step 4: Inventory resources
    resources = inventory_resources(skill_path)
    total = sum(len(v) for v in resources.values())
    print(f"✅ Inventoried resources: {total} files")

    # Step 5: Extract domain bindings
    bindings = extract_domain_bindings(parsed, domains, structure)
    print(f"✅ Extracted bindings: {len(bindings['domain_terms'])} domain terms")

    # Step 6: Build template manifest
    manifest = build_template_manifest(parsed, structure, bindings, resources, skill_path)
    print(f"✅ Built template manifest")

    # Write outputs
    with open(output_dir / "template_manifest.yaml", "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    with open(output_dir / "domain_bindings.yaml", "w") as f:
        yaml.dump(bindings, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    with open(output_dir / "structure_map.yaml", "w") as f:
        yaml.dump({"structure": structure, "domains": domains}, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n📦 Decomposition complete!")
    print(f"   template_manifest.yaml  — Parameterized skill template")
    print(f"   domain_bindings.yaml    — Extracted domain-specific bindings")
    print(f"   structure_map.yaml      — Structural analysis")
    print(f"\nNext: Use transform_skill.py to map this template to a new domain.")


if __name__ == "__main__":
    main()
