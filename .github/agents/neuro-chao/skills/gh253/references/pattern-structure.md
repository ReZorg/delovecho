# Pattern Structure Reference

## Directory Layout

```
gh253/
├── README.md                           # Main documentation
├── gh253_domain_mappings.json          # Complete APL→GitHub mappings
├── patterns/
│   ├── cat1-enterprises/               # Patterns 1-94: Enterprise-level
│   │   ├── gh{NNN}-{slug}.md           # Pattern content
│   │   └── gh{NNN}/                    # Relationship directory
│   │       ├── broader.md              # Parent patterns
│   │       └── narrower.md             # Child patterns
│   ├── cat2-organisations/             # Patterns 95-204: Organisation-level
│   │   └── ...
│   └── cat3-repositories/              # Patterns 205-253: Repository-level
│       └── ...
├── references/
│   ├── domain-transformations.md       # APL→GitHub concept mappings
│   ├── dependency-graph.md             # Graph analysis
│   └── pattern-structure.md            # This file
└── scripts/
    ├── query_patterns.py               # Pattern query tool
    ├── transform_patterns.py           # APL→gh253 transformer
    └── build_relationships.py          # Relationship builder
```

## Categories (3 Scales)

| Code | Name | Pattern Range | Count | GitHub Analog |
|------|------|---------------|-------|---------------|
| cat1-enterprises | Enterprises | 1-94 | 94 | GitHub Enterprises |
| cat2-organisations | Organisations | 95-204 | 110 | GitHub Organisations |
| cat3-repositories | Repositories | 205-253 | 49 | GitHub Repositories |

## Pattern File Format

```markdown
---
name: gh{NNN}
description: "{ID} - {PATTERN NAME}"
---

# {PATTERN NAME}

## Problem
{Problem description in GitHub context}

## Discussion
{Extended discussion with GitHub-specific examples}

## Solution
{Solution description}

## Related Patterns
- [{PATTERN NAME} ({ID})]
```

## Relationship File Format

### broader.md

```markdown
---
name: broader
description: Broader Patterns for gh{NNN}
---

# BROADER Instructions

These patterns provide context and are typically applied before this pattern:

- gh{NNN}: {Pattern Name}
```

### narrower.md

```markdown
---
name: narrower
description: Narrower Patterns for gh{NNN}
---

# NARROWER Instructions

These patterns provide detail and are typically applied after this pattern:

- gh{NNN}: {Pattern Name}
```

## Key Statistics

| Metric | Value |
|--------|-------|
| Total patterns | 253 |
| Enterprise patterns (cat1) | 94 |
| Organisation patterns (cat2) | 110 |
| Repository patterns (cat3) | 49 |
| Broader relationship files | 248 |
| Narrower relationship files | 244 |
| Root patterns (no broader) | 5 |
| Leaf patterns (no narrower) | 9 |

## Root Patterns (Entry Points)

These patterns have no broader context—they are the starting points:

| ID | Pattern | Category |
|----|---------|----------|
| 1 | INDEPENDENT ENTERPRISES | cat1-enterprises |
| 18 | NETWORK OF LEARNING | cat1-enterprises |
| 24 | SACRED REPOSITORIES | cat1-enterprises |
| 95 | REPOSITORY COMPLEX | cat2-organisations |
| 253 | PERSONAL TOUCHES | cat3-repositories |

## Naming Conventions

### Pattern Files

- Format: `gh{NNN}-{slug}.md`
- NNN: Zero-padded 3-digit pattern number (001-253)
- slug: Lowercase, hyphenated pattern name
- Example: `gh107-modular-design.md`

### Relationship Directories

- Format: `gh{NNN}/`
- Contains: `broader.md` and/or `narrower.md`
- Example: `gh107/broader.md`

## Query Tool Usage

```bash
# Get a specific pattern
python3 scripts/query_patterns.py get 107

# Search by keyword
python3 scripts/query_patterns.py search "api"

# Get broader patterns
python3 scripts/query_patterns.py broader 107

# Get narrower patterns
python3 scripts/query_patterns.py narrower 107

# Find path between patterns
python3 scripts/query_patterns.py path 1 253

# List all patterns
python3 scripts/query_patterns.py list

# List by category
python3 scripts/query_patterns.py list enterprises
```
