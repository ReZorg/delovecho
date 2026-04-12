# Dependency Graph: opencog/* ⊕ openclaw/*

## Circled-Operators Semiring

The repository ecosystem forms a semiring (R, ⊕, ⊗, 0, 1) where:

| Element | Meaning |
|---------|---------|
| R | Set of 112 repositories across opencog (90) and openclaw (23) |
| ⊕ | Disjoint union — independent repos coexist without interaction |
| ⊗ | Dependency integration — repo A requires repo B to build |
| 0 | Empty/orphan repos (no code, no deps, no dependents) |
| 1 | cogutil — the identity element (42 dependents, everything depends on it) |

## Tier Assignments (Topological Sort)

| Tier | Count | Key Components |
|------|-------|----------------|
| 0 | 62 | cogutil, all openclaw repos, standalone opencog repos |
| 1 | 12 | atomspace, moses, asmoses, attention, matrix, relex |
| 2 | 29 | cogserver, pln, ure, unify, miner, generate, sensory |
| 3 | 7 | learn, ure, atomspace-viz, ocpkg, opencog-nix |
| 4 | 2 | docker, opencog-debian (meta-packages) |

## ⊕-Components (Independent Subgraphs)

60 independent components, largest has 51 repos (all opencog core).
The two organizations form a **pure ⊕ (disjoint union)** — no cross-org dependencies.

## ⊗-Chains (Longest Dependency Pipelines)

```
cogutil → atomspace → unify → ure → opencog-debian     (len=5)
cogutil → atomspace → cogserver → learn → docker        (len=5)
cogutil → atomspace → cogserver → learn → opencog-debian (len=5)
```

## Identity Element Analysis

| Component | Dependents | Role |
|-----------|-----------|------|
| cogutil | 42 | Foundation library (1 element) |
| atomspace | 37 | Core knowledge representation |
| cogserver | 4 | Network server |
| atomspace-rocks | 2 | Persistent storage |
| unify | 2 | Unification engine |

## Cross-Org Bridge

The bridge matrix B[2×2] after training:

```
         opencog  openclaw
opencog  [ 2.547   0.000 ]
openclaw [ 0.000   1.029 ]
```

The orgs are fully independent (⊕). The opencog self-connection is stronger
because it has a denser dependency graph (112 edges vs 2 for openclaw).
