---
name: oc-build-nn
description: Neural build-path optimizer for o9nn/org-oc that learns the optimal build sequence through differentiable position embeddings and dependency logits trained via backpropagation from build success/failure signals. Composes with oc-build-optimizer for combined deterministic + neural optimization. Use when training the build order from real build data, discovering hidden dependencies via gradient descent, or running the neural simulation to predict optimal tier assignments. Triggers on mentions of neural build path, build sequence learning, differentiable build optimizer, build dependency backpropagation, or nn build training.
---

# OC Build NN

Neural build-path optimizer for **o9nn/org-oc** using nn-inspired learnable embeddings. Treats the build sequence as a differentiable optimization problem where build success/failure provides gradient signal via backpropagation, resolving the exact dependency chain package-by-package.

**Complementary skill**: Use alongside **oc-build-optimizer** (deterministic diagnosis + self-updating model). This skill provides the neural learning layer; oc-build-optimizer provides the error diagnosis engine, GHA workflow generation, and self-update mechanism.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              BuildPathNetwork (nn Module pattern)             │
│                                                               │
│  PositionEmbedding P[N×S]  — softmax → step probabilities    │
│  DependencyLogits  D[N×N]  — sigmoid → dep probabilities     │
│                                                               │
│  forward()  → compute build order from current embeddings     │
│  backward() → propagate success/failure as gradients          │
│  updateParameters(lr) → gradient descent on P and D           │
│                                                               │
│  2,184 parameters (42 components × 10 steps + 42×42 deps)    │
│  Converges in ~200 epochs (simulation) or online from builds  │
└──────────────────────────────────────────────────────────────┘
```

### How the Network Learns

Each build attempt is a training step:

1. **Success** at step S → negative gradient on P[comp, S] (reinforce position), slight positive gradient on other steps (push away)
2. **Failure** due to missing dep Y → positive gradient on P[comp, S] (push later) + negative gradient on D[comp, Y] (strengthen dependency edge) + push Y to earlier steps
3. **Entropy regularization** encourages peaked (confident) position distributions

Convergence: all builds pass AND position entropy < 0.5 (confident assignments).

### nn Module Pattern

Every layer implements the Torch7 nn.Module interface:

| Method | Description |
|--------|-------------|
| `forward(input)` | Compute output from current weights |
| `backward(input, gradOutput)` | Compute gradients from build results |
| `zeroGradParameters()` | Zero accumulated gradients |
| `updateParameters(lr)` | Update weights: W -= lr * gradW |
| `parameters()` | Return {weights}, {gradWeights} |

### Network Layers

| Layer | Shape | Activation | Learns |
|-------|-------|------------|--------|
| `PositionEmbedding` | N x S | Softmax (per row) | Which step each component belongs at |
| `DependencyLogits` | N x N | Sigmoid (per cell) | Pairwise dependency probabilities |
| `BuildSuccessCriterion` | scalar | — | Loss = failure_rate + 0.1 * entropy |

## Workflow

### Standalone Neural Training (simulation)

```bash
python3 scripts/neural_build_path.py --epochs 200 --lr 0.1 --apply
```

Trains against the known dependency graph in simulation, then writes learned knowledge back to `model/build_model.json`.

### Integrated with oc-build-optimizer

When `run_iteration.py` from oc-build-optimizer runs, it automatically imports and calls the neural module at step 6/8:

- **With real build results**: Single online learning step (`train_from_real_results()`)
- **Without results (dry-run)**: Full simulation training (~50 epochs)

To use both skills together:

```bash
# 1. Run a full iteration (deterministic + neural)
python3 /path/to/oc-build-optimizer/scripts/run_iteration.py --repo /path/to/org-oc --local

# 2. Or run neural training standalone then apply
python3 scripts/neural_build_path.py --epochs 200 --lr 0.1 --apply

# 3. Then self-update the optimizer skill's references
python3 /path/to/oc-build-optimizer/scripts/self_update.py --report
```

### CLI Options

```bash
python3 scripts/neural_build_path.py \
  --model model/build_model.json \  # Path to build model
  --epochs 200 \                    # Training epochs
  --lr 0.1 \                        # Learning rate
  --no-warm-start \                 # Don't seed from known deps
  --apply \                         # Write learned knowledge back to model
  --output results.json             # Save training results
```

## Key Functions

| Function | Purpose |
|----------|---------|
| `train()` | Full training loop with simulation |
| `train_from_real_results()` | Single online learning step from actual build results |
| `apply_to_model()` | Write learned deps/tiers back to build_model.json |
| `simulate_build()` | Simulate a build attempt against the true dependency graph |

## Neural State Persistence

The network state is stored in `model/build_model.json` under the `neural_state` key:

```json
{
  "neural_state": {
    "components": ["cogutil", "atomspace", "..."],
    "n_steps": 10,
    "position_weight": [["..."]],
    "dependency_weight": [["..."]],
    "history": [{"epoch": 0, "loss": 0.17, "success": 38}]
  },
  "neural_training": [
    {"timestamp": "...", "epochs": 200, "converged": true, "best_loss": 0.02}
  ]
}
```

The model resumes from saved state — if already converged, epoch 0 immediately passes.

## Warm-Start Modes

| Mode | Description |
|------|-------------|
| `inject_known_deps()` | Seed D[i,j] = 3.0 (sigmoid = 0.95) for known deps |
| `inject_known_layers()` | Seed P[i, layer] = 2.0 for known layer assignments |
| `load_state_dict()` | Resume from previously saved weights |

## Tested Results

| Metric | Value |
|--------|-------|
| Components | 42 |
| Parameters | 2,184 |
| Convergence epoch | 197 |
| Final loss | 0.022 |
| Final entropy | 0.497 |
| Learned dependency edges | 89 |
| All builds passing | 42/42 |
| Learned tiers | 10 |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/neural_build_path.py` | Neural build-path optimizer (standalone or integrated) |

All other scripts (diagnosis, self-update, GHA generation) live in oc-build-optimizer.

## Model and Reference Files

Shared with oc-build-optimizer (same `model/build_model.json`):

- **`model/build_model.json`**: Persistent model + neural weights
- **`references/dependency-graph.md`**: Read when debugging dependency failures
- **`references/gha-patterns.md`**: Read when generating CI workflows
