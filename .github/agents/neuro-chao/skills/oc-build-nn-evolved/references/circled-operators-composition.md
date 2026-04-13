# Circled-Operators Composition for Build Optimization

## Algebraic Structure

This skill applies the semiring (R, ⊕, ⊗, 0, 1) to multi-org build optimization:

```
⊕  = Disjoint union (repos/orgs that build independently)
⊗  = Dependency chain (repos that must build sequentially)
0  = Empty/orphan repo (no build output)
1  = cogutil (identity — everything depends on it)
```

## Composition Patterns

### ⊕-Dominant (Polynomial Pattern)

Repos in the same tier build concurrently:

```
Tier_k = comp_1 ⊕ comp_2 ⊕ ... ⊕ comp_n
```

Each component is independent within its tier. GHA matrix strategy exploits this.

### ⊗-Dominant (Tensorial Pattern)

Tiers build sequentially:

```
Build = Tier_0 ⊗ Tier_1 ⊗ Tier_2 ⊗ Tier_3 ⊗ Tier_4
```

Each tier depends on all previous tiers completing.

### Hybrid (Polynomial of Tensors)

The full build is a polynomial of tensors:

```
Build = (T0_1 ⊕ T0_2 ⊕ ... ⊕ T0_62) ⊗ (T1_1 ⊕ ... ⊕ T1_12) ⊗ ... ⊗ (T4_1 ⊕ T4_2)
```

Distributivity (Law 7) allows refactoring between these forms.

### Cross-Org Composition

```
opencog/* ⊕ openclaw/* = pure disjoint union
```

No ⊗ edges cross the org boundary. Both orgs can build entirely in parallel.

## Neural Network as ⊗-Composition

The network itself is a ⊗-composition of layers:

```
Network = PositionEmbedding ⊗ DependencyLogits ⊗ OrgEmbedding ⊗ CrossOrgBridge ⊗ TypeFeatures
```

Each layer transforms the build-order representation multiplicatively.

## Skill Composition

This skill composes with others via ⊕⊗:

| Composition | Pattern | Effect |
|-------------|---------|--------|
| `oc-build-nn-evolved ⊕ oc-build-optimizer` | Fork | Run neural + deterministic in parallel |
| `oc-build-nn-evolved ⊗ generate_gha` | Pipeline | Train → generate workflow |
| `oc-build-nn-evolved ⊗ backward_pass` | Pipeline | Train → improve from feedback |
| `analyze_topology ⊗ neural_build_path` | Pipeline | Scan → train |
