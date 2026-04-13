# org-oc Dependency Graph Reference

> Auto-generated from build model (iteration 3). Last updated: 2026-03-10T00:13:35.422421+00:00

## Table of Contents

1. [Layer Architecture](#layer-architecture)
2. [Build Tiers (Optimized)](#build-tiers-optimized)
3. [Critical Build Path](#critical-build-path)
4. [Component Catalog](#component-catalog)
5. [Known Inter-Component Dependencies](#known-inter-component-dependencies)
6. [System-Level Dependencies](#system-level-dependencies)
7. [Accumulated Fixes](#accumulated-fixes)

## Layer Architecture

| Layer | Name | Components | Status |
|-------|------|-----------|--------|
| 0 | Foundation | blender_api_msgs, cogutil, link-grammar, moses | untested |
| 1 | Core | atomspace, atomspace-agents, atomspace-bridge, atomspace-cog, atomspace-dht, atomspace-ipfs, atomspace-metta, atomspace-pgres, atomspace-restful, atomspace-rocks, atomspace-rpc, atomspace-storage, atomspace-websockets | untested |
| 2 | Logic | unify, ure | untested |
| 3 | Cognitive | attention, cogserver, dimensional-embedding, pattern-index, spacetime | untested |
| 4 | Advanced | asmoses, benchmark, miner, pln | untested |
| 5 | Learning | generate, learn | untested |
| 6 | Language | lg-atomese | untested |
| 7 | Robotics | sensory, vision | untested |
| 8 | Integration | TinyCog, opencog | untested |
| 9 | Specialized | agi-bio, atomese-simd, cheminformatics, ghost_bridge, matrix, python-attic, visualization | untested |

## Build Tiers (Optimized)

Components within each tier build **concurrently**; tiers execute **sequentially**.

**Tier 0** (~12 min): moses, link-grammar, TinyCog, cogutil, ghost_bridge, blender_api_msgs
**Tier 1** (~15 min): atomspace
**Tier 2** (~8 min): atomspace-storage, cogserver, atomspace-pgres, atomspace-rocks, unify, vision, atomspace-agents, atomspace-bridge, atomspace-dht, atomspace-ipfs, atomspace-metta, generate, lg-atomese, pattern-index, spacetime, agi-bio, atomese-simd, atomspace-rpc, atomspace-websockets, cheminformatics, dimensional-embedding, visualization, matrix, sensory
**Tier 3** (~8 min): attention, learn, ure, atomspace-cog, atomspace-restful
**Tier 4** (~12 min): asmoses, pln, miner, benchmark
**Tier 5** (~15 min): opencog, python-attic

## Critical Build Path

The longest dependency chain determining minimum build time:

```
cogutil (5m) → atomspace (15m) → unify (6m) → ure (8m) → pln (10m) → opencog (15m)
Total: 59 min minimum
```

## Component Catalog

| Component | Layer | Deps | Sys Deps | Est. Time | Status |
|-----------|-------|------|----------|-----------|--------|
| TinyCog | 8 | — | — | 5m | untested |
| agi-bio | 9 | cogutil, atomspace | — | 4m | untested |
| asmoses | 4 | cogutil, atomspace, ure | libmpi-dev | 12m | untested |
| atomese-simd | 9 | cogutil, atomspace | — | 4m | untested |
| atomspace | 1 | cogutil | guile-3.0-dev, libboost-all-dev, cxxtest, cython3 | 15m | untested |
| atomspace-agents | 1 | cogutil, atomspace | — | 5m | untested |
| atomspace-bridge | 1 | cogutil, atomspace | — | 5m | untested |
| atomspace-cog | 1 | cogutil, atomspace, cogserver | — | 5m | untested |
| atomspace-dht | 1 | cogutil, atomspace | — | 5m | untested |
| atomspace-ipfs | 1 | cogutil, atomspace | — | 5m | untested |
| atomspace-metta | 1 | cogutil, atomspace | — | 5m | untested |
| atomspace-pgres | 1 | cogutil, atomspace | libpqxx-dev, unixodbc-dev | 6m | untested |
| atomspace-restful | 1 | cogutil, atomspace, cogserver | — | 5m | untested |
| atomspace-rocks | 1 | cogutil, atomspace | librocksdb-dev | 6m | untested |
| atomspace-rpc | 1 | cogutil, atomspace | — | 4m | untested |
| atomspace-storage | 1 | cogutil, atomspace | — | 8m | untested |
| atomspace-websockets | 1 | cogutil, atomspace | — | 4m | untested |
| attention | 3 | cogutil, atomspace, cogserver | — | 7m | untested |
| benchmark | 4 | cogutil, atomspace, ure | — | 6m | untested |
| blender_api_msgs | 0 | — | — | 2m | untested |
| cheminformatics | 9 | cogutil, atomspace | — | 4m | untested |
| cogserver | 3 | cogutil, atomspace | libssl-dev | 8m | untested |
| cogutil | 0 | — | libboost-all-dev, cmake, cxxtest, binutils-dev, libiberty-dev | 5m | untested |
| dimensional-embedding | 3 | cogutil, atomspace | — | 4m | untested |
| generate | 5 | cogutil, atomspace | — | 5m | untested |
| ghost_bridge | 9 | — | — | 3m | untested |
| learn | 5 | cogutil, atomspace, cogserver | — | 6m | untested |
| lg-atomese | 6 | cogutil, atomspace | — | 5m | untested |
| link-grammar | 0 | — | autoconf, automake, libtool, swig | 8m | untested |
| matrix | 9 | cogutil, atomspace | — | 3m | untested |
| miner | 4 | cogutil, atomspace, ure, unify | — | 8m | untested |
| moses | 0 | — | libboost-all-dev, cmake, cxxtest, libmpi-dev | 12m | untested |
| opencog | 8 | cogutil, atomspace, cogserver, attention, ure, pln | — | 15m | untested |
| pattern-index | 3 | cogutil, atomspace | — | 5m | untested |
| pln | 4 | cogutil, atomspace, ure, spacetime | — | 10m | untested |
| python-attic | 9 | cogutil, atomspace, cogserver, ure, pln | — | 5m | untested |
| sensory | 7 | cogutil, atomspace | — | 3m | untested |
| spacetime | 3 | cogutil, atomspace | liboctomap-dev | 5m | untested |
| unify | 2 | cogutil, atomspace | — | 6m | untested |
| ure | 2 | cogutil, atomspace, unify | — | 8m | untested |
| vision | 7 | cogutil, atomspace | libopencv-dev | 6m | untested |
| visualization | 9 | cogutil, atomspace | — | 4m | untested |

## Known Inter-Component Dependencies

Verified dependencies (auto-updated from build diagnosis):

```
TinyCog                   → (no org-oc deps)
agi-bio                   → cogutil, atomspace
asmoses                   → cogutil, atomspace, ure
atomese-simd              → cogutil, atomspace
atomspace                 → cogutil
atomspace-agents          → cogutil, atomspace
atomspace-bridge          → cogutil, atomspace
atomspace-cog             → cogutil, atomspace, cogserver
atomspace-dht             → cogutil, atomspace
atomspace-ipfs            → cogutil, atomspace
atomspace-metta           → cogutil, atomspace
atomspace-pgres           → cogutil, atomspace
atomspace-restful         → cogutil, atomspace, cogserver
atomspace-rocks           → cogutil, atomspace
atomspace-rpc             → cogutil, atomspace
atomspace-storage         → cogutil, atomspace
atomspace-websockets      → cogutil, atomspace
attention                 → cogutil, atomspace, cogserver
benchmark                 → cogutil, atomspace, ure
blender_api_msgs          → (no org-oc deps)
cheminformatics           → cogutil, atomspace
cogserver                 → cogutil, atomspace
cogutil                   → (no org-oc deps)
dimensional-embedding     → cogutil, atomspace
generate                  → cogutil, atomspace
ghost_bridge              → (no org-oc deps)
learn                     → cogutil, atomspace, cogserver
lg-atomese                → cogutil, atomspace
link-grammar              → (no org-oc deps)
matrix                    → cogutil, atomspace
miner                     → cogutil, atomspace, ure, unify
moses                     → (no org-oc deps)
opencog                   → cogutil, atomspace, cogserver, attention, ure, pln
pattern-index             → cogutil, atomspace
pln                       → cogutil, atomspace, ure, spacetime
python-attic              → cogutil, atomspace, cogserver, ure, pln
sensory                   → cogutil, atomspace
spacetime                 → cogutil, atomspace
unify                     → cogutil, atomspace
ure                       → cogutil, atomspace, unify
vision                    → cogutil, atomspace
visualization             → cogutil, atomspace
```

## System-Level Dependencies

| Package | Required By |
|---------|------------|
| autoconf | link-grammar |
| automake | link-grammar |
| binutils-dev | cogutil |
| cmake | cogutil, moses |
| cxxtest | atomspace, cogutil, moses |
| cython3 | atomspace |
| guile-3.0-dev | atomspace |
| libboost-all-dev | atomspace, cogutil, moses |
| libiberty-dev | cogutil |
| libmpi-dev | asmoses, moses |
| liboctomap-dev | spacetime |
| libopencv-dev | vision |
| libpqxx-dev | atomspace-pgres |
| librocksdb-dev | atomspace-rocks |
| libssl-dev | cogserver |
| libtool | link-grammar |
| swig | link-grammar |
| unixodbc-dev | atomspace-pgres |

## Accumulated Fixes

Fixes discovered and applied through iterative diagnosis:

No fixes applied yet.
