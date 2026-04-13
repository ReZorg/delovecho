# Cross-Path Compositions Catalog

The 20 off-diagonal elements of the nn⁴ Kronecker product table. Each is a composition of two nn² capability paths.

## Table of Contents

1. HyperNet ⊗ NAS (HyperNAS)
2. HyperNet ⊗ MetaLearn (HyperMAML)
3. HyperNet ⊗ LossLearn (HyperLoss)
4. HyperNet ⊗ ActSearch (HyperActivation)
5. NAS ⊗ HyperNet (NAS-for-HyperNets)
6. NAS ⊗ MetaLearn (NAS-for-MetaLearners)
7. NAS ⊗ LossLearn (NAS-for-Losses)
8. NAS ⊗ ActSearch (NAS-for-Activations)
9. MetaLearn ⊗ HyperNet (Meta-HyperNet)
10. MetaLearn ⊗ NAS (Meta-NAS)
11. MetaLearn ⊗ LossLearn (Meta-LossLearning)
12. MetaLearn ⊗ ActSearch (Meta-ActivationSearch)
13. LossLearn ⊗ HyperNet (HyperNet Quality)
14. LossLearn ⊗ NAS (NAS Quality)
15. LossLearn ⊗ MetaLearn (MetaLearn Quality)
16. LossLearn ⊗ ActSearch (Activation Quality)
17. ActSearch ⊗ HyperNet (HyperNet Gating)
18. ActSearch ⊗ NAS (NAS Gating)
19. ActSearch ⊗ MetaLearn (MetaLearn Gating)
20. ActSearch ⊗ LossLearn (Loss Gating)

## Tier 1: High-Impact Compositions

### 1. HyperNAS (HyperNet ⊗ NAS)

**What**: A HyperNetwork generates the architecture parameters (α) of a DARTS search space, conditioned on dataset features.

**Why**: Instead of searching from scratch for each dataset, generate a good starting architecture instantly.

**Pattern**:
```
dataset_features → HyperNet → α₀ (initial architecture)
α₀ → DARTS → α* (refined architecture)
```

**Use case**: Transfer NAS across datasets. Train the HyperNet on many (dataset, optimal_architecture) pairs, then instantly generate good architectures for new datasets.

### 2. HyperMAML (HyperNet ⊗ MetaLearn)

**What**: A HyperNetwork generates task-family-specific MAML initializations θ₀.

**Why**: Different task families may need different initializations. Instead of one θ₀ for all tasks, generate θ₀ conditioned on the task family.

**Pattern**:
```
task_family_embedding → HyperNet → θ₀
θ₀ → MAML inner loop → θ_adapted
```

**Use case**: Multi-domain few-shot learning where tasks come from very different domains (vision, NLP, tabular).

### 3. Meta-NAS (MetaLearn ⊗ NAS)

**What**: Meta-learn the initial architecture parameters α₀ for fast NAS adaptation.

**Why**: Standard NAS starts from random α. Meta-NAS learns α₀ that adapts quickly to new datasets with just a few search steps.

**Pattern**:
```
Outer loop: learn α₀ across many datasets
Inner loop: adapt α₀ to a specific dataset in K steps
```

**Use case**: Few-shot NAS — find good architectures for new datasets with minimal search budget.

### 4. NAS-for-MetaLearners (NAS ⊗ MetaLearn)

**What**: Use NAS to search for the optimal meta-learner architecture.

**Why**: The architecture of the meta-learner (MAML's base network) significantly affects meta-learning performance. Automate its design.

**Pattern**:
```
Search space: {MAML, ProtoNet, RelationNet, SNAIL, ...}
Search: DARTS-style differentiable selection
Output: optimal meta-learner architecture
```

## Tier 2: Useful Compositions

### 5. HyperLoss (HyperNet ⊗ LossLearn)

**What**: Generate task-specific loss function parameters with a HyperNetwork.

**Pattern**: `task_embedding → HyperNet → [margin, temperature, focal_gamma, label_smoothing]`

### 6. HyperActivation (HyperNet ⊗ ActSearch)

**What**: Generate layer-specific activation function coefficients.

**Pattern**: `layer_embedding → HyperNet → activation_coefficients`

### 7. NAS-for-Losses (NAS ⊗ LossLearn)

**What**: Search over a space of parameterized loss functions.

**Pattern**: `DARTS over {CE, focal, hinge, contrastive, ...} with learnable weights`

### 8. NAS-for-Activations (NAS ⊗ ActSearch)

**What**: Include activation function choice in the NAS search space.

**Pattern**: `Each edge: operation × activation as joint search`

### 9. Meta-HyperNet (MetaLearn ⊗ HyperNet)

**What**: Meta-learn how to train HyperNetworks — learn the optimal HyperNet training procedure.

**Pattern**: `MAML where each "task" is training a HyperNet for a different target network`

### 10. Meta-LossLearning (MetaLearn ⊗ LossLearn)

**What**: Meta-learn the loss function — learn a loss that generalizes across tasks.

**Pattern**: `Outer: learn loss params. Inner: train with that loss on each task.`

## Tier 3: Specialized Compositions

### 11. NAS-for-HyperNets (NAS ⊗ HyperNet)

**What**: Search for the optimal HyperNetwork architecture.

### 12. Meta-ActivationSearch (MetaLearn ⊗ ActSearch)

**What**: Meta-learn activation functions that transfer across tasks.

### 13. HyperNet Quality (LossLearn ⊗ HyperNet)

**What**: A learned criterion for evaluating HyperNetwork quality.

### 14. NAS Quality (LossLearn ⊗ NAS)

**What**: A learned criterion for evaluating NAS search quality (beyond validation accuracy).

### 15. MetaLearn Quality (LossLearn ⊗ MetaLearn)

**What**: A learned criterion for evaluating meta-learner quality.

### 16. Activation Quality (LossLearn ⊗ ActSearch)

**What**: A learned criterion for evaluating activation function quality.

### 17-20. Gating Compositions (ActSearch ⊗ *)

**What**: Use activation/gating mechanisms to select among variants of each path.

- **HyperNet Gating**: Gate between multiple HyperNet variants
- **NAS Gating**: Gate between NAS algorithms based on dataset features
- **MetaLearn Gating**: Gate between meta-learning algorithms
- **Loss Gating**: Gate between loss functions

## Composition Rules

Any two cross-path compositions can themselves be composed:

```
(HyperNAS) ⊗ (Meta-NAS) = HyperNet generates α₀, then Meta-NAS adapts it
(HyperMAML) ⊕ (Meta-NAS) = Choose between HyperMAML and Meta-NAS per task
```

The semiring laws ensure all such compositions are well-defined.
