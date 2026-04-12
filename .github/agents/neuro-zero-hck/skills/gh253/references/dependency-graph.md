# Pattern Dependency Graph Reference

## Graph Overview

The gh253 patterns form a directed acyclic graph (DAG) of 253 interconnected patterns:

- **BROADER** → parent patterns (context providers)
- **NARROWER** → child patterns (detail providers)

## Root Patterns (Entry Points)

These patterns have no broader context and serve as primary entry points:

| ID | Name | Reaches | Description |
|----|------|---------|-------------|
| 1 | INDEPENDENT ENTERPRISES | 94% | Foundational pattern for autonomous software ecosystems |
| 18 | NETWORK OF LEARNING | 68% | Knowledge sharing and continuous improvement |
| 24 | SACRED REPOSITORIES | 65% | Preserving important code and documentation |
| 95 | REPOSITORY COMPLEX | 61% | Foundational pattern for repository architecture |
| 253 | PERSONAL TOUCHES | 0% | Terminal pattern (leaf node) |

## Critical Hub Patterns

These patterns have the most connections and serve as convergence points:

| ID | Name | In | Out | Total | Description |
|----|------|----|-----|-------|-------------|
| 30 | ACTIVITY NODES | 6 | 18 | 24 | Key integration points in the codebase |
| 107 | MODULAR DESIGN | 11 | 10 | 21 | Transparency and maintainability |
| 100 | CONTRIBUTOR PATH | 10 | 10 | 20 | Main pathways through the codebase |
| 142 | SEQUENCE OF REVIEW STAGES | 10 | 13 | 23 | Code review workflow |

## Depth Distribution

| Depth | Count | Description |
|-------|-------|-------------|
| 0 | 5 | Root patterns (entry points) |
| 1 | 25 | First-level patterns |
| 2 | 77 | Core patterns |
| 3 | 80 | Core patterns |
| 4 | 47 | Detail patterns |
| 5 | 19 | Leaf patterns |

## Category Flow

```
Enterprises (94) ──206──> Organisations (110) ──142──> Repositories (49)
   │                         │                            │
   └──289──┐                 └──453──┐                    └──124──┐
           ↓                         ↓                            ↓
        (self)                    (self)                       (self)
```

Patterns flow from high-level enterprise concerns down through organisation structure to repository implementation details.

## Traversal Strategies

### Top-Down (Design)

1. **Start**: Pattern 1 (INDEPENDENT ENTERPRISES) - reaches 94% of patterns
2. **Follow**: narrower references depth-first
3. **Waypoints**: Patterns 30, 107, 100 as convergence points
4. **End**: Construction patterns (205-253) for implementation

### Bottom-Up (Analysis)

1. **Start**: Identify the specific pattern relevant to your problem
2. **Follow**: broader references to understand context
3. **Iterate**: Continue until reaching root patterns
4. **Apply**: Work back down with full context

### Lateral (Exploration)

1. **Start**: Any pattern of interest
2. **Explore**: Both broader and narrower references
3. **Search**: Use keyword search to find related patterns
4. **Connect**: Find paths between patterns of interest

## Key Chains

### Enterprise → Repository Chain

```
1 INDEPENDENT ENTERPRISES
└── 8 MOSAIC OF TECH STACKS
    └── 37 REPOSITORY CLUSTER
        └── 95 REPOSITORY COMPLEX
            └── 107 MODULAR DESIGN
                └── 205 STRUCTURE FOLLOWS TEAM SPACES
                    └── 212 CORE MODULES
```

### Contributor Experience Chain

```
1 INDEPENDENT ENTERPRISES
└── 12 COMMUNITY OF DEVELOPERS
    └── 57 NEWCOMERS IN THE PROJECT
        └── 91 CONTRIBUTOR ONBOARDING
            └── 112 ONBOARDING FLOW
                └── 149 README WELCOMES YOU
```

### API Design Chain

```
28 API GATEWAY
└── 53 MAIN GATEWAYS
    └── 110 MAIN ENTRY POINT
        └── 122 PUBLIC INTERFACES
            └── 165 OPEN API
                └── 234 PUBLIC API
```

## Graph Metrics

| Metric | Value |
|--------|-------|
| Total nodes | 253 |
| Total broader edges | 1,167 |
| Total narrower edges | 1,270 |
| Average connections per pattern | 9.6 |
| Maximum depth | 6 levels |
| Longest chain | 20 steps (1 → 253) |

## Using the Graph

### Find Context for a Pattern

```bash
python3 scripts/query_patterns.py broader 107
```

### Find Implementation Details

```bash
python3 scripts/query_patterns.py narrower 107
```

### Find Path Between Patterns

```bash
python3 scripts/query_patterns.py path 1 253
```

### Explore by Keyword

```bash
python3 scripts/query_patterns.py search "api"
```
