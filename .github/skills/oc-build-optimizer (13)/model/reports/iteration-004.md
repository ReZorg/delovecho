# Iteration 4 Report

**Date**: 2026-03-10T01:37:49.599105+00:00
**Convergence**: iterating

## Build Sequence

- **Tiers**: 10
- **Makespan**: 70 min
- **Speedup**: 3.66x
- **Critical path**: cogutil → atomspace → unify → ure → pln → opencog

## Tier Breakdown

| Tier | Components | Max Time | Width |
|------|-----------|----------|-------|
| T0 | blender_api_msgs, cogutil, link-grammar, moses | 12m | 4 |
| T1 | atomspace, atomspace-agents, atomspace-bridge, atomspace-dht, atomspace-ipfs, atomspace-metta, atomspace-pgres, atomspace-rocks, atomspace-rpc, atomspace-storage, atomspace-websockets | 15m | 11 |
| T2 | unify, ure | 8m | 2 |
| T3 | cogserver, dimensional-embedding, pattern-index, spacetime | 8m | 4 |
| T4 | asmoses, benchmark, miner, pln | 12m | 4 |
| T5 | generate, learn | 6m | 2 |
| T6 | lg-atomese | 5m | 1 |
| T7 | atomspace-cog, sensory, vision | 6m | 3 |
| T8 | TinyCog, atomspace-restful | 5m | 2 |
| T9 | agi-bio, atomese-simd, attention, cheminformatics, ghost_bridge, matrix, opencog, python-attic, visualization | 15m | 9 |

## Component Status

| Component | Status | Errors | Fixes |
|-----------|--------|--------|-------|
| TinyCog | skipped_dep_failed | 1 | 0 |
| agi-bio | skipped_dep_failed | 1 | 0 |
| asmoses | untested | 0 | 1 |
| atomese-simd | skipped_dep_failed | 1 | 0 |
| atomspace | skipped_dep_failed | 1 | 0 |
| atomspace-agents | skipped_dep_failed | 1 | 0 |
| atomspace-bridge | skipped_dep_failed | 1 | 0 |
| atomspace-cog | untested | 0 | 0 |
| atomspace-dht | skipped_dep_failed | 1 | 0 |
| atomspace-ipfs | skipped_dep_failed | 1 | 0 |
| atomspace-metta | skipped_dep_failed | 1 | 0 |
| atomspace-pgres | skipped_dep_failed | 1 | 0 |
| atomspace-restful | untested | 0 | 0 |
| atomspace-rocks | skipped_dep_failed | 1 | 0 |
| atomspace-rpc | skipped_dep_failed | 1 | 0 |
| atomspace-storage | untested | 0 | 0 |
| atomspace-websockets | skipped_dep_failed | 1 | 0 |
| attention | untested | 0 | 0 |
| benchmark | skipped_dep_failed | 1 | 0 |
| blender_api_msgs | skipped_dep_failed | 1 | 0 |
| cheminformatics | skipped_dep_failed | 1 | 0 |
| cogserver | skipped_dep_failed | 1 | 0 |
| cogutil | skipped_dep_failed | 1 | 0 |
| dimensional-embedding | skipped_dep_failed | 1 | 0 |
| generate | skipped_dep_failed | 1 | 0 |
| ghost_bridge | skipped_dep_failed | 1 | 0 |
| learn | untested | 0 | 0 |
| lg-atomese | skipped_dep_failed | 1 | 0 |
| link-grammar | skipped_dep_failed | 1 | 0 |
| matrix | skipped_dep_failed | 1 | 0 |
| miner | untested | 0 | 0 |
| moses | skipped_dep_failed | 1 | 1 |
| opencog | untested | 0 | 0 |
| pattern-index | skipped_dep_failed | 1 | 0 |
| pln | untested | 0 | 0 |
| python-attic | skipped_dep_failed | 1 | 0 |
| sensory | skipped_dep_failed | 1 | 0 |
| spacetime | skipped_dep_failed | 1 | 0 |
| unify | skipped_dep_failed | 1 | 0 |
| ure | skipped_dep_failed | 1 | 0 |
| vision | skipped_dep_failed | 1 | 0 |
| visualization | skipped_dep_failed | 1 | 0 |

## Iteration History

| Iter | Tiers | Makespan | Fixes | Diagnoses | OK | Fail |
|------|-------|----------|-------|-----------|-----|------|
| 0 | 6 | 70m | 0 | 0 | 0 | 0 |
| 1 | 6 | 70m | 0 | 2 | 0 | 0 |
| 2 | 6 | 70m | 0 | 0 | 0 | 0 |
| 3 | 6 | 70m | 2 | 1 | 0 | 33 |
