# Iteration 2 Report

**Date**: 2026-03-09T23:58:10.211259+00:00
**Convergence**: converged

## Build Sequence

- **Tiers**: 6
- **Makespan**: 70 min
- **Speedup**: 3.66x
- **Critical path**: cogutil → atomspace → unify → ure → pln → opencog

## Tier Breakdown

| Tier | Components | Max Time | Width |
|------|-----------|----------|-------|
| T0 | moses, link-grammar, TinyCog, cogutil, ghost_bridge, blender_api_msgs | 12m | 6 |
| T1 | atomspace | 15m | 1 |
| T2 | atomspace-storage, cogserver, atomspace-pgres, atomspace-rocks, unify, vision, atomspace-agents, atomspace-bridge, atomspace-dht, atomspace-ipfs, atomspace-metta, generate, lg-atomese, pattern-index, spacetime, agi-bio, atomese-simd, atomspace-rpc, atomspace-websockets, cheminformatics, dimensional-embedding, visualization, matrix, sensory | 8m | 24 |
| T3 | attention, learn, ure, atomspace-cog, atomspace-restful | 8m | 5 |
| T4 | asmoses, pln, miner, benchmark | 12m | 4 |
| T5 | opencog, python-attic | 15m | 2 |

## Component Status

| Component | Status | Errors | Fixes |
|-----------|--------|--------|-------|
| TinyCog | untested | 0 | 0 |
| agi-bio | untested | 0 | 0 |
| asmoses | untested | 0 | 0 |
| atomese-simd | untested | 0 | 0 |
| atomspace | untested | 0 | 0 |
| atomspace-agents | untested | 0 | 0 |
| atomspace-bridge | untested | 0 | 0 |
| atomspace-cog | untested | 0 | 0 |
| atomspace-dht | untested | 0 | 0 |
| atomspace-ipfs | untested | 0 | 0 |
| atomspace-metta | untested | 0 | 0 |
| atomspace-pgres | untested | 0 | 0 |
| atomspace-restful | untested | 0 | 0 |
| atomspace-rocks | untested | 0 | 0 |
| atomspace-rpc | untested | 0 | 0 |
| atomspace-storage | untested | 0 | 0 |
| atomspace-websockets | untested | 0 | 0 |
| attention | untested | 0 | 0 |
| benchmark | untested | 0 | 0 |
| blender_api_msgs | untested | 0 | 0 |
| cheminformatics | untested | 0 | 0 |
| cogserver | untested | 0 | 0 |
| cogutil | untested | 0 | 0 |
| dimensional-embedding | untested | 0 | 0 |
| generate | untested | 0 | 0 |
| ghost_bridge | untested | 0 | 0 |
| learn | untested | 0 | 0 |
| lg-atomese | untested | 0 | 0 |
| link-grammar | untested | 0 | 0 |
| matrix | untested | 0 | 0 |
| miner | untested | 0 | 0 |
| moses | untested | 0 | 0 |
| opencog | untested | 0 | 0 |
| pattern-index | untested | 0 | 0 |
| pln | untested | 0 | 0 |
| python-attic | untested | 0 | 0 |
| sensory | untested | 0 | 0 |
| spacetime | untested | 0 | 0 |
| unify | untested | 0 | 0 |
| ure | untested | 0 | 0 |
| vision | untested | 0 | 0 |
| visualization | untested | 0 | 0 |

## Iteration History

| Iter | Tiers | Makespan | Fixes | Diagnoses | OK | Fail |
|------|-------|----------|-------|-----------|-----|------|
| 0 | 6 | 70m | 0 | 0 | 0 | 0 |
| 1 | 6 | 70m | 0 | 2 | 0 | 0 |
