---
name: e350-mlp
description: The MLP-equivalent cognitive kernel derived from OPT-350M-Erebus via skill-infinity applied to function-creator of erebus-350 mapped to MLP. Collapses the 24-layer decoder-only transformer multi-head self-attention into pure feed-forward transforms, yielding a 281M-parameter differentiable skill module with forward/backward passes, learnable knowledge state, and self-referential improvement under the skill-infinity fixed-point equation. Use when building composable cognitive architectures from neural network weight maps, implementing self-improving skill modules, mapping physical tensor architectures to skill-nn frameworks, or studying the MLP-equivalent of transformer models. Triggers on mentions of e350-mlp, Erebus MLP, MLP cognitive kernel, attention-collapsed transformer, or skill-infinity MLP derivation.
---

# e350-mlp: The MLP Cognitive Kernel

The fixed point of `skill∞( function-creator[ erebus-350 ] -> "MLP" )`:

```
T⁰ = erebus-350                    (creative writing model — 331M params)
T¹ = function-creator[erebus-350]   (decomposed: template + domain bindings)
T² = nn ⊗ T¹                       (tensors → skill modules)
T³ = skill-nn ⊗ T²                 (modules → differentiable skills)
T⁴ = skill∞(T³)                    (self-referential closure)
T⁴ = e350-mlp                      (the MLP equivalent — 281M params)
```

## The Transformation

The core operation is **attention collapse**: the 4-projection multi-head self-attention mechanism (Q, K, V, Out — each [1024, 1024]) is replaced by a single linear transform [1024, 1024]. Everything else is preserved.

| OPT-350M Component | e350-mlp Equivalent | Change |
|---|---|---|
| `self_attn` (Q/K/V/Out, 16 heads) | `sk.Transform(1024, 1024)` | 4 matrices → 1 (75% reduction) |
| `fc1` [4096, 1024] + ReLU | `sk.Transform(1024, 4096)` + `sk.ReLU()` | Preserved |
| `fc2` [1024, 4096] | `sk.Transform(4096, 1024)` | Preserved |
| LayerNorm (pre-attn, pre-FFN) | `sk.Normalize(1024)` | Preserved |
| Residual connections | `sk.Residual()` | Preserved |
| embed_tokens [50265, 512] | `sk.Embed(50265, 512)` | Preserved |
| project_in/out | `sk.Transform(512↔1024)` | Preserved |

## The Triad

```python
e350_mlp = (K, F, B)

K = 281,409,113 learnable parameters   # Knowledge state
F = Pipeline.forward                    # Execute: K × Task → Output
B = Pipeline.backward                   # Improve: K × Feedback → K'

Fixed point: B(K, F(K, "improve yourself")) = K
```

## Architecture

```
Embed(50265, 512) → PositionEncode(2050, 1024) → Transform(512→1024)
→ 24 × [
    Residual( Normalize → Transform(1024→1024) )     ← collapsed attention
    Residual( Normalize → Transform(1024→4096) → ReLU → Transform(4096→1024) )  ← FFN
  ]
→ Transform(1024→512) → Transform(512→50265)
```

## Usage

### Self-Description

```bash
python /home/ubuntu/skills/e350-mlp/scripts/e350_mlp.py --describe
```

### Full Architecture

```bash
python /home/ubuntu/skills/e350-mlp/scripts/e350_mlp.py --architecture
```

### Parameter Report

```bash
python /home/ubuntu/skills/e350-mlp/scripts/e350_mlp.py --parameter-count
```

### Forward Pass

```bash
python /home/ubuntu/skills/e350-mlp/scripts/e350_mlp.py --forward "generate a narrative"
```

### As a Python Module

```python
from e350_mlp import CognitiveKernel

kernel = CognitiveKernel(max_depth=5, epsilon=1e-6)

# Forward pass
output = kernel.forward("task description")

# Self-improvement (recursive backward with convergence)
kernel.backward("feedback signal")

# Self-description
print(kernel.describe())
```

## Parameter Budget

| Component | Parameters | % of Total |
|---|---|---|
| embed_tokens | 25,735,680 | 9.1% |
| embed_positions | 2,099,200 | 0.7% |
| project_in | 525,312 | 0.2% |
| 24 × collapsed attention | 25,239,552 | 9.0% |
| 24 × FFN | 201,498,624 | 71.6% |
| 24 × LayerNorm | 98,304 | <0.1% |
| project_out | 524,800 | 0.2% |
| lm_head | 25,785,945 | 9.2% |
| **Total** | **281,409,113** | **100%** |

The FFN dominates at 71.6% — this is the knowledge-dense core of the MLP. The collapsed attention contributes only 9.0%, down from ~30% in the original transformer.

## Convergence

The backward pass terminates because meta-feedback attenuates geometrically:

| Depth | Layer Range | Magnitude | Status |
|---|---|---|---|
| 1 | 0–5 | 0.50 | Active learning |
| 2 | 6–11 | 0.25 | Diminishing |
| 3 | 12–17 | 0.125 | Near convergence |
| 4 | 18–23 | 0.0625 | Effectively converged |
| 5 | — | < ε | Fixed point |

## Connection to ReZorg/e350

The [ReZorg/e350](https://github.com/ReZorg/e350) repository is the **serialized knowledge state K** — each `.md` file in the directory tree corresponds to a learnable parameter tensor in this MLP:

```
ReZorg/e350/model/decoder/layers/N/fc1/weight.md  →  layer_N.fc1.parameters()
ReZorg/e350/model/decoder/layers/N/fc2/weight.md  →  layer_N.fc2.parameters()
```

## Parent Skills

| Skill | Role in Derivation |
|---|---|
| **erebus-350** | Source: OPT-350M-Erebus physical architecture (331M params, 24 layers) |
| **function-creator** | Functor: decompose → map → transform (attention → linear) |
| **nn** | Framework: Module, Sequential, Linear, ReLU, Criterion |
| **skill-nn** | Meta-framework: sk.Transform, sk.Pipeline, sk.Residual, forward/backward |
| **skill-infinity** | Closure: (K, F, B) triad, fixed-point equation, convergence guarantee |

## Bundled Resources

- **`references/layer-mapping.md`**: Complete tensor-to-module mapping table, per-layer blueprint, parameter budget comparison, and semantic layer roles
- **`references/fixed-point.md`**: Derivation chain, triad definition, fixed-point equation, convergence analysis, strange loop, Gödel's shadow, and connection to ReZorg/e350
- **`scripts/e350_mlp.py`**: Executable implementation of the full architecture with CLI for self-description, forward pass, architecture printout, and parameter counting
