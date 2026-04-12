# org-oc Dependency Graph Reference

> Auto-generated from build model (iteration 5). Last updated: 2026-03-10T01:44:32.382920+00:00

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
| 0 | Foundation | blender_api_msgs, cogutil, link-grammar, moses | 0✓ 4✗ |
| 1 | Core | atomspace, atomspace-agents, atomspace-bridge, atomspace-cog, atomspace-dht, atomspace-ipfs, atomspace-metta, atomspace-pgres, atomspace-restful, atomspace-rocks, atomspace-rpc, atomspace-storage, atomspace-websockets | 0✓ 10✗ |
| 2 | Logic | unify, ure | 0✓ 2✗ |
| 3 | Cognitive | attention, cogserver, dimensional-embedding, pattern-index, spacetime | 0✓ 4✗ |
| 4 | Advanced | asmoses, benchmark, miner, pln | 0✓ 1✗ |
| 5 | Learning | generate, learn | 0✓ 1✗ |
| 6 | Language | lg-atomese | 0✓ 1✗ |
| 7 | Robotics | sensory, vision | 0✓ 2✗ |
| 8 | Integration | TinyCog, opencog | 0✓ 1✗ |
| 9 | Specialized | agi-bio, atomese-simd, cheminformatics, ghost_bridge, matrix, python-attic, visualization | 0✓ 7✗ |

## Build Tiers (Optimized)

Components within each tier build **concurrently**; tiers execute **sequentially**.

**Tier 0** (~12 min): blender_api_msgs, cogutil, link-grammar, moses
**Tier 1** (~15 min): atomspace, atomspace-agents, atomspace-bridge, atomspace-dht, atomspace-ipfs, atomspace-metta, atomspace-pgres, atomspace-rocks, atomspace-rpc, atomspace-storage, atomspace-websockets
**Tier 2** (~8 min): unify, ure
**Tier 3** (~8 min): cogserver, dimensional-embedding, pattern-index, spacetime
**Tier 4** (~12 min): asmoses, benchmark, miner, pln
**Tier 5** (~6 min): generate, learn
**Tier 6** (~5 min): lg-atomese
**Tier 7** (~6 min): atomspace-cog, sensory, vision
**Tier 8** (~5 min): TinyCog, atomspace-restful
**Tier 9** (~15 min): agi-bio, atomese-simd, attention, cheminformatics, ghost_bridge, matrix, opencog, python-attic, visualization

## Critical Build Path

The longest dependency chain determining minimum build time:

```
cogutil (5m) → atomspace (15m) → unify (6m) → ure (8m) → pln (10m) → opencog (15m)
Total: 59 min minimum
```

## Component Catalog

| Component | Layer | Deps | Sys Deps | Est. Time | Status |
|-----------|-------|------|----------|-----------|--------|
| TinyCog | 8 | — | — | 5m | skipped_dep_failed |
| agi-bio | 9 | cogutil, atomspace | — | 4m | skipped_dep_failed |
| asmoses | 4 | cogutil, atomspace, ure | libopenmpi-dev | 12m | untested |
| atomese-simd | 9 | cogutil, atomspace | — | 4m | skipped_dep_failed |
| atomspace | 1 | cogutil | guile-3.0-dev, libboost-all-dev, cxxtest, cython3 | 15m | skipped_dep_failed |
| atomspace-agents | 1 | cogutil, atomspace | — | 5m | skipped_dep_failed |
| atomspace-bridge | 1 | cogutil, atomspace | — | 5m | skipped_dep_failed |
| atomspace-cog | 1 | cogutil, atomspace, cogserver | — | 5m | untested |
| atomspace-dht | 1 | cogutil, atomspace | — | 5m | skipped_dep_failed |
| atomspace-ipfs | 1 | cogutil, atomspace | — | 5m | skipped_dep_failed |
| atomspace-metta | 1 | cogutil, atomspace | — | 5m | skipped_dep_failed |
| atomspace-pgres | 1 | cogutil, atomspace | libpqxx-dev, unixodbc-dev | 6m | skipped_dep_failed |
| atomspace-restful | 1 | cogutil, atomspace, cogserver | — | 5m | untested |
| atomspace-rocks | 1 | cogutil, atomspace | librocksdb-dev | 6m | skipped_dep_failed |
| atomspace-rpc | 1 | cogutil, atomspace | — | 4m | skipped_dep_failed |
| atomspace-storage | 1 | cogutil, atomspace | — | 8m | untested |
| atomspace-websockets | 1 | cogutil, atomspace | — | 4m | skipped_dep_failed |
| attention | 3 | cogutil, atomspace, cogserver | — | 7m | untested |
| benchmark | 4 | cogutil, atomspace, ure | — | 6m | skipped_dep_failed |
| blender_api_msgs | 0 | — | — | 2m | skipped_dep_failed |
| cheminformatics | 9 | cogutil, atomspace | — | 4m | skipped_dep_failed |
| cogserver | 3 | cogutil, atomspace | libssl-dev | 8m | skipped_dep_failed |
| cogutil | 0 | — | libboost-all-dev, cmake, cxxtest, binutils-dev, libiberty-dev | 5m | skipped_dep_failed |
| dimensional-embedding | 3 | cogutil, atomspace | — | 4m | skipped_dep_failed |
| generate | 5 | cogutil, atomspace | — | 5m | skipped_dep_failed |
| ghost_bridge | 9 | — | — | 3m | skipped_dep_failed |
| learn | 5 | cogutil, atomspace, cogserver | — | 6m | untested |
| lg-atomese | 6 | cogutil, atomspace | — | 5m | skipped_dep_failed |
| link-grammar | 0 | — | autoconf, automake, libtool, swig | 8m | skipped_dep_failed |
| matrix | 9 | cogutil, atomspace | — | 3m | skipped_dep_failed |
| miner | 4 | cogutil, atomspace, ure, unify | — | 8m | untested |
| moses | 0 | — | libboost-all-dev, cmake, cxxtest, libopenmpi-dev | 12m | skipped_dep_failed |
| opencog | 8 | cogutil, atomspace, cogserver, attention, ure, pln | — | 15m | untested |
| pattern-index | 3 | cogutil, atomspace | — | 5m | skipped_dep_failed |
| pln | 4 | cogutil, atomspace, ure, spacetime | — | 10m | untested |
| python-attic | 9 | cogutil, atomspace, cogserver, ure, pln | — | 5m | skipped_dep_failed |
| sensory | 7 | cogutil, atomspace | — | 3m | skipped_dep_failed |
| spacetime | 3 | cogutil, atomspace | liboctomap-dev | 5m | skipped_dep_failed |
| unify | 2 | cogutil, atomspace | — | 6m | skipped_dep_failed |
| ure | 2 | cogutil, atomspace, unify | — | 8m | skipped_dep_failed |
| vision | 7 | cogutil, atomspace | libopencv-dev | 6m | skipped_dep_failed |
| visualization | 9 | cogutil, atomspace | — | 4m | skipped_dep_failed |

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
| liboctomap-dev | spacetime |
| libopencv-dev | vision |
| libopenmpi-dev | asmoses, moses |
| libpqxx-dev | atomspace-pgres |
| librocksdb-dev | atomspace-rocks |
| libssl-dev | cogserver |
| libtool | link-grammar |
| swig | link-grammar |
| unixodbc-dev | atomspace-pgres |

## Accumulated Fixes

Fixes discovered and applied through iterative diagnosis:

**asmoses**:
- [asmoses] sys_dep libmpi-dev → libopenmpi-dev

**moses**:
- [moses] sys_dep libmpi-dev → libopenmpi-dev

