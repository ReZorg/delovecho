# Glyph-Noetic Inferno Kernel Architecture

## Table of Contents

1. [Composition Formula](#composition-formula)
2. [System Components](#system-components)
3. [Glyph Categories](#glyph-categories)
4. [Temporal Hierarchy](#temporal-hierarchy)
5. [Topology Model](#topology-model)
6. [Kernel Promises](#kernel-promises)
7. [Autognosis Self-Image](#autognosis-self-image)

## Composition Formula

```
/glyph-noetic-inferno-engine = /neuro-symbolic-engine(
    /time-crystal-nn(/time-crystal-neuron)
    [/time-crystal-daemon]
) ( /plan9-file-server [/p9fstyx-topology] )
```

Composes: `glyph-noetic-engine` + `manuscog-cognitive-devkernel` + `opencog-inferno-kernel` + `p9fstyx-topology` + `promise-lambda-attention`.

## System Components

| Component | File | Kernel Service | 9P Path |
|-----------|------|----------------|---------|
| Glyph Engine | `glyph.c` | Sentence dispatch | `/dev/glyph` |
| Temporal Scheduler | `temporal.c` | 12-level time-crystal | `/n/glyph/temporal/` |
| AtomSpace | `atomspace.c` | Hypergraph knowledge | `/n/glyph/atomspace/` |
| Topology | `p9topo.c` | RTSA cluster model | `/n/glyph/topology/` |
| Promises | `promises.c` | PLA validation | `/n/glyph/promises/` |
| Autognosis | `promises.c` | Self-awareness | `/n/glyph/autognosis/` |
| Device Driver | `devglyph.c` | File I/O interface | `/dev/glyph` |

## Glyph Categories

| Category | Code | Color | Examples |
|----------|------|-------|----------|
| Kernel | `K:` | Red | `[K:STATUS]`, `[K:GLYPHS]`, `[K:PROMISES]` |
| Temporal | `T` | Blue | `[T-HIERARCHY]`, `[T~q]`..`[T~h]` |
| Cognitive | `C:` | Purple | `[C:PLN]`, `[C:MOSES]`, `[C:PATTERN]`, `[C:ATTN]` |
| Structural | `S:` | Green | `[S:ATOMSPACE]` |
| Noetic | `N:` | Orange | `[N:DECISION]` |
| Protocol | `P:` | Cyan | `[P:FS]`, `[P:CPU]`, `[P:NS]` |
| Topology | `T:` | Cyan | `[T:ASSEMBLY]`, `[T:BETA0]`, `[T:BETA1]`, `[T:PERSIST]` |

Operators: `?` (query), `!` (action), `->` (flow), `|` (pipe).

## Temporal Hierarchy

12 levels from Nanobrain time-crystal model:

| Level | Name | Period | Kernel Service |
|-------|------|--------|----------------|
| 0 | quantum_resonance | 1μs | AtomSpace CRUD |
| 1 | protein_dynamics | 8ms | Pattern matching |
| 2 | ion_channel_gating | 26ms | PLN inference |
| 3 | membrane_dynamics | 52ms | ECAN attention |
| 4 | axon_initial_segment | 110ms | MOSES learning |
| 5 | dendritic_integration | 160ms | Namespace sync |
| 6 | synaptic_plasticity | 250ms | Cluster heartbeat |
| 7 | soma_processing | 330ms | Autognosis observe |
| 8 | network_sync | 500ms | Self-image rebuild |
| 9 | global_rhythm | 1000ms | Global coordination |
| 10 | circadian_modulation | 60s | Circadian adaptation |
| 11 | homeostatic_regulation | 3600s | Homeostatic regulation |

## Topology Model

The Plan 9 cluster is modeled as a simplicial complex with 5 components:

- `fs` (file server, storage layer)
- `auth` (auth server, storage layer)
- `cpu1`, `cpu2` (CPU servers, compute layer)
- `glyph-engine` (cognitive engine, compute layer)

Topological invariants:
- **β₀ = 1** — Single connected component (all nodes reachable)
- **β₁ = 2** — Two independent redundant cycles (fs↔cpu1↔glyph, fs↔cpu2↔glyph)
- **Euler characteristic χ = β₀ - β₁ + β₂ = -1**

Constraints:
- `connected_cluster`: β₀ == 1 (required)
- `storage_redundancy`: β₁ >= 1 (required)

## Kernel Promises

11 promises from Promise-Lambda Attention (PLA):

| ID | Name | Description |
|----|------|-------------|
| 0 | INFERNO_BINARY | Inferno kernel binary exists |
| 1 | LIMBO_COMPILER | Limbo compiler available |
| 2 | 9P_LISTENER | 9P protocol listener active |
| 3 | CLUSTER_COMPOSE | Cluster composition valid |
| 4 | COGNITIVE_NS | Cognitive namespace mounted |
| 5 | DEVCONTAINER | Devcontainer running |
| 6 | AUTOGNOSIS | Autognosis loop active |
| 7 | TEMPORAL_LEVELS | All 12 temporal levels active |
| 8 | GLYPH_DEVICE | /dev/glyph device exists |
| 9 | TOPO_CONNECTED | β₀ == 1 |
| 10 | TOPO_REDUNDANT | β₁ >= 1 |

## Autognosis Self-Image

3-level hierarchical self-awareness:

1. **Level 0 — Operational**: Promise validation, temporal tick counts, error rates
2. **Level 1 — Cognitive**: AtomSpace health, module activity, attention distribution
3. **Level 2 — Reflective**: Self-image coherence, convergence detection, awareness score

Awareness score formula: `(satisfied_promises / total_promises) * 0.5 + (active_modules / total_modules) * 0.3 + (topology_healthy ? 0.2 : 0.0)`
