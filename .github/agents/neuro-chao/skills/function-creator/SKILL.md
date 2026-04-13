---
name: function-creator
description: Higher-order skill transformation engine that maps existing skills into analogous domains. Use when transforming a skill to a new domain/context, generating skill families from a single source, composing transformation chains, parameterizing skills into reusable templates, or packaging templates for community sharing. Composes with skill-creator for final packaging.
---

# Function Creator

Transform existing skills into analogous domains by decomposing them into abstract templates, parameterizing domain-specific bindings, and applying new domain mappings. A **functor** over the skill space.

```
F: Skill_A → Skill_B
F(skill) = structure(skill) ⊕ new_bindings
```

## Core Workflow

Skill transformation involves these steps:

1. **Decompose** the source skill into template + domain bindings
2. **Map** source domain terms to target domain terms
3. **Transform** the template with new bindings to generate the target skill
4. **Review** the generated skill for domain accuracy
5. **Package** with skill-creator for delivery or sharing

## Step 1: Decompose the Source Skill

Analyze a skill to separate its invariant structure from domain-specific content:

```bash
python /home/ubuntu/skills/function-creator/scripts/decompose_skill.py <skill_path> --output <output_dir>
```

**Input**: Path to any skill directory containing SKILL.md.

**Output** (three files):
- `template_manifest.yaml` — Parameterized template with slots for domain values
- `domain_bindings.yaml` — Extracted domain-specific terms, APIs, formats, services
- `structure_map.yaml` — Structural analysis (sections, workflow steps, code blocks)

**Example:**
```bash
python scripts/decompose_skill.py /home/ubuntu/skills/stock-analysis --output ./stock_template
```

Review the manifest to understand what slots are available for transformation.

## Step 2: Create the Domain Mapping

Create a transform specification that maps source domain concepts to target domain concepts.

**Copy and edit the template:**
```bash
cp /home/ubuntu/skills/function-creator/templates/transform_spec.yaml my_transform.yaml
```

The transform spec has three sections:

| Section | Purpose | Example |
|---------|---------|--------|
| `slot_mappings` | Fill parameterized slots (name, description, domain) | `name: crypto-analysis` |
| `term_mappings` | Explicit old→new term replacements | `stock: crypto` |
| `file_mappings` | Rename resource files | `fnb_extract.py: capitec_extract.py` |

**For common domain mappings**, consult `references/domain-patterns.md` which provides ready-made mapping tables for financial, data sync, document processing, investigation, and platform integration domain families.

**For the formal model**, consult `references/transformation-theory.md` for functor composition laws and template algebra.

## Step 3: Transform

Apply the mapping to generate the new skill:

```bash
python /home/ubuntu/skills/function-creator/scripts/transform_skill.py \
    <template_manifest> <transform_spec> [--output <skill_dir>]
```

**Example:**
```bash
python scripts/transform_skill.py ./stock_template/template_manifest.yaml my_transform.yaml
```

The script transforms SKILL.md and all resource files (scripts, references, templates), applying term replacements while preserving structure. Output defaults to `/home/ubuntu/skills/<new_name>/`.

**Interactive mode** (builds the transform spec through prompts):
```bash
python scripts/transform_skill.py ./stock_template/template_manifest.yaml --interactive
```

## Step 4: Review

The generated skill includes a `TRANSFORM_REPORT.md` documenting all replacements made. Review:

1. **SKILL.md** — Verify frontmatter description triggers correctly for the new domain
2. **Scripts** — Update domain-specific logic that term replacement alone cannot handle
3. **References** — Add target-domain documentation
4. **Templates** — Adjust output formats for the target domain

## Step 5: Package

Use skill-creator to validate and deliver:

```bash
python /home/ubuntu/skills/skill-creator/scripts/quick_validate.py <new_skill_name>
```

## Transformation Chains

Generate a **family of skills** from a single source using chain specifications.

**Copy and edit the template:**
```bash
cp /home/ubuntu/skills/function-creator/templates/chain_spec.yaml my_chain.yaml
```

**Chain types:**

| Pattern | Description | Example |
|---------|-------------|--------|
| **Parallel fork** | Same source → multiple domains | stock-analysis → [crypto, forex, commodities] |
| **Sequential chain** | Output of one feeds next | raw-extract → validated-extract → enriched-extract |
| **Dependency graph** | Arbitrary DAG with `depends_on` | Complex multi-stage pipelines |

**Commands:**
```bash
# Validate chain spec
python scripts/chain_transforms.py my_chain.yaml --validate

# Visualize as Mermaid diagram
python scripts/chain_transforms.py my_chain.yaml --visualize

# Dry run (show plan without executing)
python scripts/chain_transforms.py my_chain.yaml --dry-run

# Execute
python scripts/chain_transforms.py my_chain.yaml --output /home/ubuntu/skills/
```

## Community Sharing

Package a decomposed template for others to instantiate in their own domains:

```bash
python /home/ubuntu/skills/function-creator/scripts/share_template.py \
    <decomposed_dir> --format dir --output <share_path>
```

This generates a shareable bundle with:
- Template manifest and domain bindings
- Auto-generated README with slot documentation
- Instructions for community members to apply their own transform specs

## Quick Reference

| Task | Command |
|------|--------|
| Decompose a skill | `python scripts/decompose_skill.py <skill_path> -o <dir>` |
| Transform to new domain | `python scripts/transform_skill.py <manifest> <spec>` |
| Interactive transform | `python scripts/transform_skill.py <manifest> --interactive` |
| Validate chain | `python scripts/chain_transforms.py <chain> --validate` |
| Visualize chain | `python scripts/chain_transforms.py <chain> --visualize` |
| Execute chain | `python scripts/chain_transforms.py <chain> -o <dir>` |
| Share template | `python scripts/share_template.py <dir> --format dir` |

## Composition with Other Skills

| Skill | Composition |
|-------|------------|
| **skill-creator** | Package transformed skills for delivery |
| **skill-nn** | Treat transformations as forward passes in a skill network |
| **topology-weaver** | Map domain terminology to architectural specifications |
| **promise-lambda-attention** | Use promises to constrain valid transformations |

## References

- **Transformation Theory**: `references/transformation-theory.md` — Formal model, functor laws, template algebra
- **Domain Patterns**: `references/domain-patterns.md` — Ready-made mapping tables for common domain families
