# gh253: A Pattern Language for GitHub

A comprehensive pattern language for designing and understanding healthy, sustainable, and effective software development ecosystems on GitHub. This project adapts Christopher Alexander's seminal work *A Pattern Language* (APL253) to the domain of GitHub, providing 253 interconnected patterns for enterprises, organisations, and repositories.

## Overview

Just as Alexander's original patterns describe how to build living, human-centered physical spaces, gh253 describes how to build living, developer-centered digital spaces on GitHub. The patterns range from high-level enterprise governance down to the atomic elements of individual repositories.

## Scale Mappings

| APL253 Scale | gh253 Scale | Pattern Range | Description |
|--------------|-------------|---------------|-------------|
| Regions | Enterprises | 1-94 | Autonomous spheres of culture, governance, and collaboration |
| Towns | Organisations | 95-204 | Collections of repositories forming a cohesive whole |
| Buildings | Repositories | 205-253 | The fundamental units of code, documentation, and collaboration |

## Quick Start

### Get a Pattern

```bash
python3 scripts/query_patterns.py get 107
```

### Search Patterns

```bash
python3 scripts/query_patterns.py search "api"
python3 scripts/query_patterns.py search "team"
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

### List Patterns

```bash
# List all patterns
python3 scripts/query_patterns.py list

# List by category
python3 scripts/query_patterns.py list enterprises
python3 scripts/query_patterns.py list organisations
python3 scripts/query_patterns.py list repositories
```

## Pattern Organization

```
gh253/
├── README.md                           # This file
├── gh253_domain_mappings.json          # APL→GitHub concept mappings
├── patterns/
│   ├── cat1-enterprises/               # Patterns 1-94
│   │   ├── gh001-independent-enterprises.md
│   │   ├── gh001/
│   │   │   ├── broader.md
│   │   │   └── narrower.md
│   │   └── ...
│   ├── cat2-organisations/             # Patterns 95-204
│   │   └── ...
│   └── cat3-repositories/              # Patterns 205-253
│       └── ...
├── references/
│   ├── domain-transformations.md       # APL→GitHub mappings
│   ├── dependency-graph.md             # Graph analysis
│   └── pattern-structure.md            # Directory layout
└── scripts/
    ├── query_patterns.py               # Pattern query tool
    ├── transform_patterns.py           # APL→gh253 transformer
    └── build_relationships.py          # Relationship builder
```

## Key Entry Points

| ID | Pattern | Reaches | Description |
|----|---------|---------|-------------|
| 1 | INDEPENDENT ENTERPRISES | 94% | Autonomous software ecosystems |
| 18 | NETWORK OF LEARNING | 68% | Knowledge sharing and continuous improvement |
| 24 | SACRED REPOSITORIES | 65% | Preserving important code and documentation |
| 95 | REPOSITORY COMPLEX | 61% | Repository architecture patterns |

## Hub Patterns (Most Connected)

| ID | Pattern | Connections | Description |
|----|---------|-------------|-------------|
| 30 | ACTIVITY NODES | 24 | Key integration points |
| 107 | MODULAR DESIGN | 21 | Transparency and maintainability |
| 100 | CONTRIBUTOR PATH | 20 | Main pathways through the codebase |

## Common Workflows

### Design a New Enterprise

1. Start with Pattern 1 (INDEPENDENT ENTERPRISES)
2. Follow narrower patterns for organisation structure
3. Apply Pattern 12 (COMMUNITY OF DEVELOPERS) for team sizing
4. Use Pattern 37 (REPOSITORY CLUSTER) for repo organisation

### Architect a Repository

1. Start with Pattern 95 (REPOSITORY COMPLEX)
2. Apply Pattern 107 (MODULAR DESIGN) for structure
3. Use Pattern 205 (STRUCTURE FOLLOWS TEAM SPACES) for alignment
4. Follow construction patterns (206-253) for implementation details

### Improve Developer Experience

1. Search for relevant patterns: `search "contributor"`
2. Apply Pattern 100 (CONTRIBUTOR PATH) for onboarding
3. Use Pattern 112 (ONBOARDING FLOW) for transitions
4. Implement Pattern 149 (README WELCOMES YOU) for first impressions

## Concept Mappings

The gh253 patterns transform architectural concepts to GitHub concepts:

| Architecture | GitHub |
|--------------|--------|
| Region | Enterprise |
| Town | Organisation |
| Building | Repository |
| Room | Directory |
| Door | API Endpoint |
| Window | Interface |
| Path | Workflow |
| Street | Integration Pipeline |
| Garden | Documentation |
| Entrance | README |
| Column | Core Module |
| Foundation | Framework |

## References

- **[domain-transformations.md](references/domain-transformations.md)** - Complete APL→GitHub mappings
- **[dependency-graph.md](references/dependency-graph.md)** - Graph analysis and traversal strategies
- **[pattern-structure.md](references/pattern-structure.md)** - Directory layout and file formats

## Credits

This pattern language is based on Christopher Alexander's *A Pattern Language* (1977), adapted for the GitHub domain. The original work provides timeless insights into creating spaces that support human flourishing—insights that translate remarkably well to the digital spaces where developers collaborate.

---

*"Each pattern describes a problem which occurs over and over again in our environment, and then describes the core of the solution to that problem, in such a way that you can use this solution a million times over, without ever doing it the same way twice."* — Christopher Alexander
