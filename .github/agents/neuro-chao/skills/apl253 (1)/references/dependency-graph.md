# Pattern Dependency Graph Reference

## Graph Overview

The 253 patterns form a directed acyclic graph (DAG):
- **BROADER** → parent patterns (context providers)
- **NARROWER** → child patterns (detail providers)

## Root Patterns (Entry Points)

| ID | Name | Reaches | % |
|----|------|---------|---|
| 1 | INDEPENDENT REGIONS | 238 | 94.1% |
| 18 | NETWORK OF LEARNING | 173 | 68.4% |
| 24 | SACRED SITES | 165 | 65.2% |
| 95 | BUILDING COMPLEX | 153 | 60.5% |
| 253 | THINGS FROM YOUR LIFE | 0 | 0% |

## Critical Hub Patterns

| ID | Name | In | Out | Total |
|----|------|----|-----|-------|
| 30 | ACTIVITY NODES | 6 | 18 | 24 |
| 249 | ORNAMENT | 22 | 2 | 24 |
| 142 | SEQUENCE OF SITTING SPACES | 10 | 13 | 23 |
| 107 | WINGS OF LIGHT | 11 | 10 | 21 |
| 100 | PEDESTRIAN STREET | 10 | 10 | 20 |

## Depth Distribution

| Depth | Count | Description |
|-------|-------|-------------|
| 0 | 5 | Root patterns |
| 1 | 25 | First level |
| 2 | 77 | Core patterns |
| 3 | 80 | Core patterns |
| 4 | 47 | Detail patterns |
| 5 | 6 | Leaf patterns |

## Category Flow

```
Towns (94) ──206──> Buildings (110) ──142──> Construction (49)
   │                    │                         │
   └──289──┐            └──453──┐                 └──124──┐
           ↓                    ↓                         ↓
        (self)              (self)                     (self)
```

## Traversal Strategy

1. **Start**: Pattern 1 (INDEPENDENT REGIONS) - reaches 94%
2. **Follow**: narrower references depth-first
3. **Secondary**: Pattern 95 for building-specific patterns
4. **Waypoints**: Patterns 30, 142, 107, 100 as convergence points

## Longest Chains

1. Pattern 1 → ... → Pattern 253 (20 steps)
2. Pattern 24 → ... → Pattern 253 (19 steps)
3. Pattern 95 → ... → Pattern 253 (19 steps)
