---
name: nn-to-the-fourth
description: "The fixed-point self-application of nn-squared: nn⁴ = nn² ⊗ nn². The five nn² paths (HyperNets, NAS, Meta-Learning, Loss Learning, Activation Search) applied to themselves and each other. Covers HyperHyperNets, MetaNAS, Meta-Meta-Learning, cross-path compositions (HyperNAS, HyperMAML, Meta-NAS), fixed-point convergence, and self-improving neural systems. Proves nn⁴ ≅ nn² — the strange loop where self-application reaches a fixed point. Use for self-improving AI, NAS-over-NAS, hierarchical meta-learning, learning quines, or systems that design their own design process. Composes nn² (method) ⊗ nn² (object) via circled-operators. Triggers on nn⁴, self-application, fixed-point, strange loop, learning quine, meta-meta-learning, MetaNAS, HyperHyperNet, self-improving network, or skill-infinity."
---

# nn\u2074 \u2014 The Fixed-Point Self-Application

The **tensor product of nn\u00b2 with itself**. The five capability paths of nn\u00b2 become both method and object, producing a 5\u00d75 product of second-order capabilities that converges to a fixed point.

```
nn\u2074 = nn\u00b2 \u2297 nn\u00b2
    = (HyperNet, NAS, MetaLearn, LossLearn, ActSearch)
      \u2297
      (HyperNet, NAS, MetaLearn, LossLearn, ActSearch)

Idempotency theorem: nn\u2074 \u2245 nn\u00b2
```

## The nn\u2074 Kronecker Product Table

| Method \\ Object | HyperNet | NAS | MetaLearn | LossLearn | ActSearch |
|-----------------|----------|-----|-----------|-----------|----------|
| **HyperNet** | HyperHyperNet | HyperNAS | HyperMAML | HyperLoss | HyperAct |
| **NAS** | NAS-for-H | MetaNAS | NAS-for-ML | NAS-for-Loss | NAS-for-Act |
| **MetaLearn** | Meta-H | Meta-NAS | Meta\u00b2Learn | Meta-LossLearn | Meta-ActSearch |
| **LossLearn** | H-Quality | NAS-Quality | ML-Quality | Meta\u00b2Loss | Act-Quality |
| **ActSearch** | H-Gate | NAS-Gate | ML-Gate | Loss-Gate | Meta\u00b2Act |

## The Idempotency Theorem

nn\u2074 \u2245 nn\u00b2 because each diagonal element collapses to its nn\u00b2 counterpart:

```
HyperHyperNet  \u2245  HyperNet       A weight generator that generates weight generators
                                   is just a more general weight generator.

MetaNAS        \u2245  NAS             A search that searches for searches
                                   is just a more general search.

Meta\u00b2Learn     \u2245  MetaLearn       Learning to learn to learn collapses
                                   to learning to learn.

Meta\u00b2Loss      \u2245  LossLearn       A loss evaluating losses evaluating losses
                                   collapses to a loss evaluating losses.

Meta\u00b2Act       \u2245  ActSearch       An activation searching for activation searches
                                   collapses to an activation search.
```

The **fixed point** is reached when self-application produces no new representational power. This is the **learning quine** \u2014 a system whose output is instructions for building itself.

## Five Fixed-Point Paths (Diagonal)

### FP1: HyperHyperNet \u2014 The Weight-Generation Quine

A HyperNetwork `H\u2082` generates the weights of another HyperNetwork `H\u2081`, which generates the weights of a target `G`:

```python
import torch
import torch.nn as nn

class HyperHyperNet(nn.Module):
    """H\u2082(z\u2082) \u2192 \u03b8_{H\u2081}, then H\u2081(z\u2081; \u03b8_{H\u2081}) \u2192 \u03b8_G, then G(x; \u03b8_G) \u2192 y.
    Fixed point: H\u2082 that generates its own weights."""

    def __init__(self, z2_dim, z1_dim, target_in, target_hid, target_out):
        super().__init__()
        # H\u2082 generates weights for H\u2081's generator
        h1_out = target_hid * target_in + target_hid + target_out * target_hid + target_out
        self.h2 = nn.Sequential(
            nn.Linear(z2_dim, 128), nn.ReLU(),
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, z1_dim * 64 + 64 + 64 * h1_out + h1_out),
        )
        self.z1_dim = z1_dim
        self.shapes = {"ti": target_in, "th": target_hid, "to": target_out}

    def forward(self, z2, z1, x):
        # Level 2: generate H\u2081 params
        h1_flat = self.h2(z2)
        # Level 1: functional forward through H\u2081 to get G params
        # Level 0: functional forward through G
        # (See scripts/hyper_hyper_net.py for full implementation)
        pass
```

Run `scripts/hyper_hyper_net.py` for the complete three-level pipeline with convergence detection.

### FP2: MetaNAS \u2014 Search that Searches for Search

A NAS algorithm whose search space includes NAS configurations:

```python
class MetaNAS(nn.Module):
    """Outer search over NAS hyperparameters, inner search over architectures.
    Fixed point: the NAS configuration that would discover itself."""

    def __init__(self, n_configs, n_edges, n_ops):
        super().__init__()
        self.config_weights = nn.Parameter(torch.randn(n_configs))
        self.configs = nn.ParameterList([
            nn.Parameter(torch.randn(3))  # [search_lr, search_steps, regularization]
            for _ in range(n_configs)
        ])
        self.n_edges, self.n_ops = n_edges, n_ops
```

Run `scripts/meta_nas.py` for MetaNAS with inner DARTS and outer configuration search.

### FP3: Meta\u00b2Learn \u2014 Learning to Learn to Learn

Three nested training loops with fixed-point detection:

```python
def meta_meta_learn(model, task_dist, loss_fn,
                    inner_lr, inner_steps,       # Level 1: task adaptation
                    outer_lr,                     # Level 2: MAML
                    meta_meta_lr, meta_epochs,    # Level 3: learn MAML hyperparams
                    convergence_threshold=1e-4):
    """Three-level optimization. Converges when Level 3 stops improving Level 2."""
    log_inner_lr = torch.tensor(float(inner_lr)).log().requires_grad_(True)
    prev_meta_loss = float('inf')
    for epoch in range(meta_epochs):
        current_inner_lr = log_inner_lr.exp()
        meta_loss = maml_epoch(model, task_dist, loss_fn,
                               current_inner_lr, inner_steps, outer_lr)
        # Fixed-point detection
        delta = abs(meta_loss.item() - prev_meta_loss)
        if delta < convergence_threshold:
            return True, epoch  # nn\u2074 \u2245 nn\u00b2 reached
        prev_meta_loss = meta_loss.item()
    return False, meta_epochs
```

Run `scripts/meta_meta_learn.py` for the complete three-level meta-learner.

## Five Key Cross-Path Compositions (Off-Diagonal)

### HyperNAS (HyperNet \u2297 NAS)

Generate architecture parameters with a HyperNetwork conditioned on dataset features:

```python
class HyperNAS(nn.Module):
    def __init__(self, dataset_embed_dim, n_edges, n_ops):
        super().__init__()
        self.alpha_gen = nn.Sequential(
            nn.Linear(dataset_embed_dim, 64), nn.ReLU(),
            nn.Linear(64, n_edges * n_ops),
        )
        self.n_edges, self.n_ops = n_edges, n_ops

    def forward(self, dataset_embedding):
        return self.alpha_gen(dataset_embedding).view(self.n_edges, self.n_ops)
```

### HyperMAML (HyperNet \u2297 MetaLearn)

Generate task-family-specific MAML initializations.

### Meta-NAS (MetaLearn \u2297 NAS)

Meta-learn initial architecture parameters for fast NAS adaptation to new datasets.

### NAS-for-MetaLearners (NAS \u2297 MetaLearn)

Search for the optimal meta-learner architecture (MAML vs. ProtoNet vs. RelationNet).

### HyperLoss (HyperNet \u2297 LossLearn)

Generate task-conditioned loss functions via weight generation.

See `references/cross_path_compositions.md` for all 20 off-diagonal compositions.

## Fixed-Point Detection

```python
def detect_fixed_point(system, threshold=1e-4, max_iter=100):
    """Detect when self-application has converged (nn\u2074 \u2192 nn\u00b2)."""
    prev = {k: v.clone() for k, v in system.state_dict().items()}
    for i in range(max_iter):
        system.self_apply()
        delta = sum((system.state_dict()[k] - prev[k]).norm().item() for k in prev)
        if delta < threshold:
            return True, i
        prev = {k: v.clone() for k, v in system.state_dict().items()}
    return False, max_iter
```

Run `scripts/fixed_point_detector.py` for convergence detection across all five paths.

## Nested Tuples: n-ary Products

The binary product nn⁴ = nn² ⊗ nn² generalizes to n-ary products. The **General Collapse Theorem** proves nn^{2k} ≅ nn² for all k ≥ 1, but higher-arity tuples introduce distinct **structural patterns** (role decompositions) even though they have the same algebraic value.

### The Triad-of-Dyads (nn⁶ = nn² ⊗ nn² ⊗ nn²)

The ternary product introduces a three-role decomposition:

```
nn² ⊗ nn² ⊗ nn²
 ↑      ↑      ↑
METHOD OBJECT EVALUATOR
(Agent) (Arena) (Relation)
```

In nn⁴ (binary), the evaluator is implicit (baked into the training loss). In nn⁶ (ternary), the evaluator is an **explicit learned meta-network** that judges designs independently. This maps to the **Agent-Arena-Relation** (AAR) pattern from cognitive architecture.

| Tuple | Roles | Dimension | Pattern |
|-------|-------|-----------|--------|
| Dyad (nn⁴) | Method, Object | 5² = 25 | Design |
| Triad (nn⁶) | Method, Object, Evaluator | 5³ = 125 | Design + Evaluate |
| Tetrad (nn⁸) | Method, Object, Evaluator, Meta | 5⁴ = 625 | Design + Evaluate + Meta-evaluate |
| Pentad (nn¹⁰) | One role per nn² path | 5⁵ = 3125 | Full self-reflection |

Run `scripts/triad_of_dyads.py` for the three-role system with n-ary table generation.

See `references/nested_tuples.md` for the general collapse theorem and full tuple catalog.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/hyper_hyper_net.py` | Three-level HyperNet with convergence detection |
| `scripts/meta_nas.py` | MetaNAS: meta-learn NAS hyperparameters |
| `scripts/meta_meta_learn.py` | Three-level MAML with fixed-point proof |
| `scripts/fixed_point_detector.py` | Detect nn\u2074 \u2192 nn\u00b2 convergence across all paths |
| `scripts/self_improving.py` | Complete self-improvement loop combining all paths |
| `scripts/triad_of_dyads.py` | nn⁶ triad: Method ⊗ Object ⊗ Evaluator (AAR pattern) |

## References
| Topic | File | When to Read |
|-------|------|--------------|
| Fixed-point theory | `references/fixed_point_theory.md` | Understanding idempotency proof |
| Cross-path catalog | `references/cross_path_compositions.md` | Using off-diagonal compositions |
| Self-improvement protocols | `references/self_improvement.md` | Building self-improving systems |
| Convergence analysis | `references/convergence.md` | Analyzing when nn⁴ → nn² |
| Nested tuples | `references/nested_tuples.md` | n-ary products, triad-of-dyads, general collapse theorem |

## Composition with Other Skills

| Skill | Composition | Effect |
|-------|------------|--------|
| `nn` | `nn\u2074 = nn \u2297 nn \u2297 nn \u2297 nn` | Four-fold self-application |
| `nn-squared` | `nn\u2074 = nn\u00b2 \u2297 nn\u00b2` | Direct parent (self-application of nn\u00b2) |
| `circled-operators` | Provides \u2295\u2297 algebra | Semiring framework |
| `function-creator` | `F(nn\u00b2) \u2192 nn\u2074` | The functor that produced this skill |
| `bolt-cpp-ml\u00b2` | `nn\u2074 \u2297 bolt\u00b2` | Self-improving C++ ML inference |
| `echo-evolve-composed` | `nn\u2074 \u2297 echo` | Fixed-point cognitive architecture |
| `regima-cognitive-ai` | `nn\u2074 \u2297 cognitive` | Self-designing organizational AI |
