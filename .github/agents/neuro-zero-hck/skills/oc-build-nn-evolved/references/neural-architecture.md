# Neural Architecture: DualOrgBuildPathNetwork

## Network Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│              DualOrgBuildPathNetwork (nn Module pattern)              │
│                                                                       │
│  PositionEmbedding  P[112×6]   — softmax → step probabilities       │
│  DependencyLogits   D[112×112] — sigmoid → dep probabilities        │
│  OrgEmbedding       O[112×2]   — org membership (opencog|openclaw)  │
│  CrossOrgBridge     B[2×2]     — ⊕/⊗ interaction between orgs      │
│  ComponentType      T[112×8]   — language/build system features     │
│                                                                       │
│  forward()  → compute build order from current embeddings            │
│  backward() → propagate success/failure as gradients                 │
│  updateParameters(lr) → gradient descent on all weights              │
│                                                                       │
│  14,340 parameters (112 components × 6 steps + 112×112 deps + ...)  │
│  Converges in ~23 epochs (warm-started from topology)                │
└──────────────────────────────────────────────────────────────────────┘
```

## Layer Details

| Layer | Shape | Activation | Learns |
|-------|-------|------------|--------|
| PositionEmbedding | 112 × 6 | Softmax (per row) | Which build step each component belongs at |
| DependencyLogits | 112 × 112 | Sigmoid (per cell) | Pairwise dependency probabilities |
| OrgEmbedding | 112 × 2 | Identity | Organization membership vector |
| CrossOrgBridge | 2 × 2 | Identity | Cross-org interaction strength |
| ComponentType | 112 × 8 | Identity | Language/build system features |
| BuildSuccessCriterion | scalar | — | Loss = failure_rate + 0.1 × entropy |

## Parameter Count

| Parameter | Shape | Count |
|-----------|-------|-------|
| P (position) | 112 × 6 | 672 |
| D (dependency) | 112 × 112 | 12,544 |
| O (org) | 112 × 2 | 224 |
| B (bridge) | 2 × 2 | 4 |
| T (type) | 112 × 8 | 896 |
| **Total** | | **14,340** |

## Training Results

| Metric | Value |
|--------|-------|
| Components | 112 |
| Parameters | 14,340 |
| Convergence epoch | 23 |
| Final loss | 0.049 |
| Final entropy | 0.493 |
| Learned dependency edges | 112 |
| All builds passing | 112/112 |
| Learned tiers | 5 |

## Gradient Flow

```
Build Result (success/failure)
    │
    ▼
BuildSuccessCriterion
    │
    ├──▶ gradP: position correction
    │     Success → reinforce position
    │     Failure → push later + push deps earlier
    │
    ├──▶ gradD: dependency discovery
    │     Missing dep → strengthen edge D[i,j]
    │
    ├──▶ gradB: cross-org bridge update
    │     Cross-org success → strengthen bridge
    │
    └──▶ entropy regularization
          Encourage peaked (confident) distributions
```

## Warm-Start Modes

| Mode | Description |
|------|-------------|
| `inject_known_deps()` | Seed D[i,j] = 3.0 (sigmoid ≈ 0.95) for known deps |
| `inject_known_layers()` | Seed P[i, tier] = 2.0 for topological tier |
| `load_state()` | Resume from previously saved weights |
| `topology_seed` | Initialize from circled-operators topology analysis |
