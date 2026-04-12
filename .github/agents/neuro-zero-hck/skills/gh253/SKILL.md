---
name: gh253
description: A Pattern Language for GitHub - 253 interconnected patterns for designing enterprises, organisations, and repositories. Use for GitHub architecture design, repository structure planning, team organization, developer experience optimization, and applying Christopher Alexander's pattern language to software development ecosystems.
---

# gh253 - A Pattern Language for GitHub

253 interconnected design patterns adapted from Christopher Alexander's *A Pattern Language* for the GitHub domain.

## Quick Start

### Get a Pattern

```bash
python3 /home/ubuntu/skills/gh253/scripts/query_patterns.py get 107
```

### Search Patterns

```bash
python3 /home/ubuntu/skills/gh253/scripts/query_patterns.py search "api"
python3 /home/ubuntu/skills/gh253/scripts/query_patterns.py search "team"
```

### Find Related Patterns

```bash
# Get parent patterns (broader context)
python3 /home/ubuntu/skills/gh253/scripts/query_patterns.py broader 107

# Get child patterns (narrower detail)
python3 /home/ubuntu/skills/gh253/scripts/query_patterns.py narrower 107

# Find path between patterns
python3 /home/ubuntu/skills/gh253/scripts/query_patterns.py path 1 253
```

## Scale Mappings

| APL253 Scale | gh253 Scale | Pattern Range | Description |
|--------------|-------------|---------------|-------------|
| Regions | Enterprises | 1-94 | Autonomous spheres of governance |
| Towns | Organisations | 95-204 | Collections of repositories |
| Buildings | Repositories | 205-253 | Fundamental code units |

## Key Entry Points

| ID | Pattern | Use When |
|----|---------|----------|
| 1 | INDEPENDENT ENTERPRISES | Designing autonomous software ecosystems |
| 12 | COMMUNITY OF DEVELOPERS | Sizing and structuring teams |
| 95 | REPOSITORY COMPLEX | Architecting multi-repo projects |
| 107 | MODULAR DESIGN | Creating maintainable code structure |
| 205 | STRUCTURE FOLLOWS TEAM SPACES | Aligning code with team organization |

## Common Workflows

### Design a New Enterprise

1. Start with Pattern 1 (INDEPENDENT ENTERPRISES)
2. Apply Pattern 12 (COMMUNITY OF DEVELOPERS) for team sizing
3. Use Pattern 37 (REPOSITORY CLUSTER) for repo organization

### Architect a Repository

1. Start with Pattern 95 (REPOSITORY COMPLEX)
2. Apply Pattern 107 (MODULAR DESIGN) for structure
3. Use Pattern 205 (STRUCTURE FOLLOWS TEAM SPACES)
4. Follow construction patterns (206-253) for implementation

### Improve Developer Experience

1. Search: `search "contributor"`
2. Apply Pattern 100 (CONTRIBUTOR PATH)
3. Use Pattern 112 (ONBOARDING FLOW)
4. Implement Pattern 149 (README WELCOMES YOU)

## Pattern Organization

```
gh253/
├── patterns/
│   ├── cat1-enterprises/    # Patterns 1-94
│   ├── cat2-organisations/  # Patterns 95-204
│   └── cat3-repositories/   # Patterns 205-253
├── references/
│   ├── domain-transformations.md
│   ├── dependency-graph.md
│   └── pattern-structure.md
└── scripts/
    └── query_patterns.py
```

## References

- **[domain-transformations.md](references/domain-transformations.md)** - APL→GitHub concept mappings
- **[dependency-graph.md](references/dependency-graph.md)** - Graph analysis and traversal
- **[pattern-structure.md](references/pattern-structure.md)** - Directory layout and file formats
