# P9Fstyx Architecture Reference

## Table of Contents

1. Overview
2. Module → RTSA Component Mapping
3. Cloudflare Worker Binding Mapping (verified)
4. Environment Variable → Component Metadata Mapping
5. CogOps Test Endpoints
6. Topological Constraints

## Overview

P9Fstyx (Plan 9 Filesystem Styx Protocol) is a cognitive power-scribe framework implementing distributed micro-kernel networks via the 9P/Styx filesystem protocol. When composed with RTSA, each P9Fstyx module becomes a topological component whose connections are monitored via Betti numbers and persistence diagrams.

Source repositories: `orgitcog/mad9ml` (Marduk cognitive architecture), `orgitcog/p9fstyx` (OpenCog + 9P kernel).

## Module → RTSA Component Mapping

### P9Fstyx Modules

| P9Fstyx Module | Component ID | Port Types | Layer |
|---|---|---|---|
| StyxProtocol | `styx_server` | 9p (BIDI), kv (SOURCE) | infra |
| PowerScribe | `powerscribe` | module (SINK), schedule (SOURCE), 9p (BIDI) | orchestration |
| MicroKernelNetwork | `micro_kernel_network` | kernel (SINK), field (SOURCE), 9p (BIDI) | compute |
| WaveEquations | `wave_field` | field (SINK), field (SOURCE) | compute |
| GaugeKernel | `gauge_kernel` | field (SINK), vector (SOURCE), tensor (SOURCE) | compute |
| DifferentialEngine | `differential_engine` | domain (SINK), kernel (SOURCE) | compute |
| GripOptimizer | `grip_optimizer` | topology (SINK), vector (SOURCE) | optimization |
| PowerSkill | `powerskill` | field (SINK), pathway (SOURCE) | optimization |
| LambdaPromises | `lambda_promises` | constraint (SINK), solution (SOURCE), 9p (BIDI) | orchestration |

### OpenCog Modules

| OpenCog Module | Component ID | Port Types | Layer |
|---|---|---|---|
| AtomSpace | `atomspace` | pattern (SINK), atom (SOURCE), kv (BIDI) | core |
| PatternMatcher | `pattern_matcher` | pattern (SINK), atom (SOURCE/BIDI) | core |
| ECAN | `ecan_attention` | atom (SINK/SOURCE/BIDI) | core |

### Marduk Cognitive Modules

| Marduk Module | Component ID | Port Types | Layer |
|---|---|---|---|
| Memory Store | `marduk_memory` | memory (SINK/SOURCE), kv (BIDI) | core |
| MOSES Evolution | `moses_evolution` | genome (SINK/SOURCE), metric (BIDI) | optimization |

## Cloudflare Worker Binding Mapping (verified)

All bindings verified via cogops test worker on 2026-03-02.

| Component | KV Binding | Namespace ID | CogOps Verified |
|---|---|---|---|
| `atomspace` | `ATOMSPACE_KV` | `5b5c50565a984a85b0967bd06683b27d` | yes |
| `styx_server` | `P9FSTYX_STATE` | `12d928e7197a4799bb57b68fd9975198` | yes |
| `marduk_memory` | `MARDUK_KV` | `bed8f7fba72f4101bf7cf5fdfa43fbd3` | yes |
| `moses_evolution` | `TASK_METRICS` | `94599ec5a4af49a4bc66c8815e85a1d8` | yes |
| `marduk_memory` | `MardukStore` | `1ecc1e3d85c745d387c675dd7bfd4d93` | yes |

Additional bindings:

| Resource | Binding | ID |
|---|---|---|
| D1 Database | `DB` | `7e2e03fa-1b31-4355-a4ee-4a6e3d5ff60e` |
| R2 Bucket | `TEMPLATES` | `marduk-ml-sdk-templates` |
| Dispatch NS | `DISPATCHER` | `marduk-ml-sdk-namespace` |

## Environment Variable → Component Metadata Mapping

### Marduk Cognitive Vars

```
MARDUK_MEMORY_CAPACITY          → marduk_memory.metadata.capacity (1000)
MARDUK_EVOLUTION_MUTATION_RATE   → moses_evolution.metadata.mutation_rate (0.05)
MARDUK_EVOLUTION_DRIFT_FACTOR    → moses_evolution.metadata.drift_factor (0.01)
MARDUK_EVOLUTION_FITNESS_THRESH  → moses_evolution.metadata.fitness_threshold (0.7)
MARDUK_ATTENTION_TOTAL_RESOURCES → ecan_attention.metadata.total_resources (100)
MARDUK_ATTENTION_DECAY_RATE      → ecan_attention.metadata.decay_rate (0.05)
MARDUK_ATTENTION_SPREADING_FACTOR→ ecan_attention.metadata.spreading_factor (0.8)
```

### P9Fstyx Vars

```
P9FSTYX_STYX_MOUNT_POINT        → styx_server.metadata.mount (/n/cognitive)
P9FSTYX_WAVE_SPEED               → wave_field.metadata.wave_speed (1.0)
P9FSTYX_WAVE_DAMPING              → wave_field.metadata.damping (0.01)
P9FSTYX_GAUGE_GROUP               → gauge_kernel.metadata.gauge_group (U1)
P9FSTYX_GAUGE_DIMENSION           → gauge_kernel.metadata.dimension (3)
P9FSTYX_GRIP_LEARNING_RATE        → grip_optimizer.metadata.learning_rate (0.01)
P9FSTYX_GRIP_MOMENTUM             → grip_optimizer.metadata.momentum (0.9)
P9FSTYX_KERNEL_NETWORK_DIMENSIONS → micro_kernel_network.metadata.dimensions (3)
P9FSTYX_POWERSCRIBE_AUTO          → powerscribe.metadata.auto_orchestrate (true)
P9FSTYX_POWERSKILL_POPULATION     → powerskill.metadata.population_size (10)
```

### AtomSpace Vars

```
ATOMSPACE_MAX_ATOMS              → atomspace.metadata.max_atoms (100000)
ATOMSPACE_PATTERN_CACHE_SIZE     → pattern_matcher.metadata.cache_size (1000)
ATOMSPACE_ADVANCED_PATTERNS      → pattern_matcher.metadata.advanced (true)
```

## CogOps Test Endpoints

Live test worker: `https://marduk-cogops-test.dan-cdc.workers.dev`

| Endpoint | Method | Tests |
|---|---|---|
| `/cogops/topology` | GET | All 5 KV + D1 connectivity, cross-namespace refs, β₀ verification |
| `/cogops/memory` | GET | 4 memory types (declarative, episodic, procedural, semantic), read-back |
| `/cogops/atomspace` | GET | ConceptNodes, InheritanceLinks, EvaluationLinks, BindLink pattern match |
| `/cogops/p9fstyx` | GET | Styx mount, PowerScribe registry, micro-kernel mesh, lambda-promises |
| `/cogops/ecan` | GET | Attention bank allocation, spreading activation, decay |
| `/cogops/wave` | GET | Wave field initialization, 5-step evolution, energy dissipation |
| `/cogops/gauge` | GET | U1(3) connection, curvature tensor, parallel transport holonomy |
| `/cogops/metrics` | GET | Task metrics, MOSES evolution step, autonomy heartbeat |
| `/cogops/run-all` | POST | Full 8-phase cognitive cycle |
| `/cogops/status` | GET | Health check with last cycle summary |

## Topological Constraints

| Constraint | Dimension | Operator | Value | Description |
|---|---|---|---|---|
| `connected` | β₀ | == | 1 | Single connected mesh, no orphaned modules |
| `redundant_paths` | β₁ | >= | 3 | Fault-tolerant cognitive processing paths |

Verified results: β₀ = 1, β₁ = 5, 3 triangles (2-simplices), χ = -4.
