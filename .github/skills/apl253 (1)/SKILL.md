---
name: apl253
description: Christopher Alexander's "A Pattern Language" (253 patterns) for design across domains. Use for pattern-based design thinking, applying architectural patterns to software/organizations/communities, navigating pattern hierarchies, finding related patterns, and domain transformations.
---

# APL253 - A Pattern Language

253 interconnected design patterns from Christopher Alexander's seminal work, organized for multi-domain application.

## Quick Start

### Get a Pattern

Read pattern file directly:
```
patterns/apl0/dim0/cat{1-3}/seq{01-36}/apl{NNN}.md
```

Or use query script:
```bash
python3 scripts/query_patterns.py get 107
```

### Find Related Patterns

```bash
# Get parent patterns (broader context)
python3 scripts/query_patterns.py broader 107

# Get child patterns (narrower detail)
python3 scripts/query_patterns.py narrower 107

# Find path between patterns
python3 scripts/query_patterns.py path 1 253
```

### Search Patterns

```bash
python3 scripts/query_patterns.py search "light"
python3 scripts/query_patterns.py search "community"
```

## Pattern Organization

| Category | Range | Scale |
|----------|-------|-------|
| cat1 | 1-94 | Towns |
| cat2 | 95-204 | Buildings |
| cat3 | 205-253 | Construction |

**Dimensions** (6 perspectives): dim0=Archetypal, dim2=Physical, dim3=Social, dim4=Conceptual, dim5=Interpersonal

## Key Entry Points

| ID | Pattern | Reaches |
|----|---------|---------|
| 1 | INDEPENDENT REGIONS | 94% |
| 18 | NETWORK OF LEARNING | 68% |
| 24 | SACRED SITES | 65% |
| 95 | BUILDING COMPLEX | 61% |

## Hub Patterns (Most Connected)

| ID | Pattern | Connections |
|----|---------|-------------|
| 30 | ACTIVITY NODES | 24 |
| 142 | SEQUENCE OF SITTING SPACES | 23 |
| 107 | WINGS OF LIGHT | 21 |
| 100 | PEDESTRIAN STREET | 20 |

## Common Workflows

### Apply Patterns to Software Architecture

1. Identify the design problem
2. Start from Pattern 1 (INDEPENDENT REGIONS) → microservices
3. Follow narrower refs for detail: 8 (MOSAIC) → polyglot, 52 (NETWORK OF PATHS) → communication
4. See [domain-transformations.md](references/domain-transformations.md) for mappings

### Apply Patterns to Organizations

1. Start from Pattern 1 → autonomous teams
2. Pattern 12 (COMMUNITY OF 7000) → team sizing
3. Pattern 37 (HOUSE CLUSTER) → cross-functional pods
4. See [domain-transformations.md](references/domain-transformations.md) for mappings

### Navigate Pattern Hierarchy

1. Start at root patterns (1, 18, 24, 95)
2. Follow narrower refs depth-first
3. Use hub patterns (30, 142, 107) as waypoints
4. See [dependency-graph.md](references/dependency-graph.md) for full analysis

### Find Patterns for a Problem

1. Search by keyword: `python3 scripts/query_patterns.py search "privacy"`
2. Check broader patterns for context
3. Check narrower patterns for implementation detail
4. Cross-reference across dimensions for domain-specific views

## References

- **[pattern-structure.md](references/pattern-structure.md)** - Directory layout, file formats, statistics
- **[dependency-graph.md](references/dependency-graph.md)** - Graph analysis, traversal strategies, critical paths
- **[domain-transformations.md](references/domain-transformations.md)** - Software/organization mappings, dimension usage

## File Structure

```
apl253/
├── SKILL.md                    # This file
├── scripts/
│   └── query_patterns.py       # Pattern query tool
├── references/
│   ├── pattern-structure.md    # Directory layout
│   ├── dependency-graph.md     # Graph analysis
│   └── domain-transformations.md # Domain mappings
└── patterns/apl0/
    ├── dim{0-5}.md             # Dimension descriptions
    └── dim{0-5}/cat{1-3}/seq{01-36}/
        ├── apl{NNN}.md         # Pattern content
        └── apl{NNN}/
            ├── broader.md      # Parent patterns
            └── narrower.md     # Child patterns
```
