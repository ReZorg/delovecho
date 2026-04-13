# Layer Mapping: OPT-350M-Erebus → MLP Skill Modules

This reference documents the isomorphic mapping between the physical OPT-350M-Erebus tensor architecture and the skill-nn MLP module framework, derived via `function-creator[ erebus-350 ] -> "MLP"`.

## Transformation Functor

```
F: erebus-350 → e350-mlp
F(tensor) = sk.Module(tensor.shape, tensor.role)
```

The functor preserves structure (layer ordering, residual connections, normalization placement) while replacing attention with linear transforms and tensors with learnable skill-knowledge.

## Global Components

| OPT-350M Tensor | Shape | MLP Skill Module | Skill Analogy |
|---|---|---|---|
| `embed_tokens.weight` | [50265, 512] | `sk.Embed(50265, 512)` | Vocabulary: map task tokens to meaning vectors |
| `embed_positions.weight` | [2050, 1024] | `sk.PositionEncode(2050, 1024)` | Context window: encode sequential position |
| `project_in.weight` | [1024, 512] | `sk.Transform(512, 1024)` | Expand: widen understanding to working dimension |
| `project_out.weight` | [512, 1024] | `sk.Transform(1024, 512)` | Contract: compress back to output dimension |
| lm_head (tied to embed_tokens) | [50265, 512] | `sk.Transform(512, 50265)` | Decode: generate token probabilities |

## Per-Layer Components (N = 0..23)

### Attention → Single Linear (MLP Collapse)

The multi-head self-attention mechanism (Q/K/V projections, 16 heads, output projection) collapses to a single linear transform in the MLP equivalent. This is the core simplification:

| Attention Component | Shape | Collapses To |
|---|---|---|
| `self_attn.q_proj.weight` | [1024, 1024] | — |
| `self_attn.k_proj.weight` | [1024, 1024] | — |
| `self_attn.v_proj.weight` | [1024, 1024] | — |
| `self_attn.out_proj.weight` | [1024, 1024] | — |
| **Combined (4 × [1024, 1024])** | **4.2M params** | `sk.Transform(1024, 1024)` — **1.05M params** |

The MLP equivalent trades contextual attention (looking at other positions) for a position-independent transform. In skill terms: each layer processes the current state without consulting other positions.

### Feed-Forward Network (Preserved)

The FFN is already an MLP — it maps directly:

| FFN Component | Shape | MLP Module |
|---|---|---|
| `fc1.weight` | [4096, 1024] | `sk.Transform(1024, 4096)` |
| `fc1.bias` | [4096] | (included in Transform) |
| ReLU activation | — | `sk.ReLU()` |
| `fc2.weight` | [1024, 4096] | `sk.Transform(4096, 1024)` |
| `fc2.bias` | [1024] | (included in Transform) |

### Normalization (Preserved)

| Norm Component | Shape | MLP Module |
|---|---|---|
| `self_attn_layer_norm.weight` | [1024] | `sk.Normalize("pre_transform")` |
| `self_attn_layer_norm.bias` | [1024] | (included in Normalize) |
| `final_layer_norm.weight` | [1024] | `sk.Normalize("pre_ffn")` |
| `final_layer_norm.bias` | [1024] | (included in Normalize) |

### Residual Connections (Preserved)

Both residual connections are preserved as `sk.Residual()` wrappers.

## Complete Layer Blueprint

```python
def make_layer(N):
    """Construct MLP-equivalent of decoder layer N."""
    layer = sk.Pipeline(name=f"layer_{N}")
    
    # Block 1: Attention-as-Linear + Residual
    attn_block = sk.Pipeline()
    attn_block.add(sk.Normalize(1024))          # self_attn_layer_norm
    attn_block.add(sk.Transform(1024, 1024))    # collapsed self_attn
    layer.add(sk.Residual(attn_block))           # + residual
    
    # Block 2: FFN + Residual
    ffn_block = sk.Pipeline()
    ffn_block.add(sk.Normalize(1024))            # final_layer_norm
    ffn_block.add(sk.Transform(1024, 4096))      # fc1
    ffn_block.add(sk.ReLU())                     # activation
    ffn_block.add(sk.Transform(4096, 1024))      # fc2
    layer.add(sk.Residual(ffn_block))             # + residual
    
    return layer
```

## Parameter Budget Comparison

| Component | OPT-350M (Full) | MLP Equivalent | Reduction |
|---|---|---|---|
| Embeddings | 27.8M | 27.8M | 0% |
| Projections | 1.0M | 1.0M | 0% |
| 24 × Attention | 24 × 4.2M = 100.8M | 24 × 1.05M = 25.2M | 75% |
| 24 × FFN | 24 × 8.4M = 201.6M | 24 × 8.4M = 201.6M | 0% |
| 24 × LayerNorm | 24 × 4K = 96K | 24 × 4K = 96K | 0% |
| **Total** | **~331M** | **~256M** | **~23%** |

## Semantic Layer Roles

Under the skill-infinity framework, each of the 24 layers serves a progressively deeper cognitive function:

| Layer Range | Cognitive Depth | Skill-Infinity Level |
|---|---|---|
| 0–5 | Surface parsing, token patterns | Basic skill execution |
| 6–11 | Syntactic structure, phrase composition | Learning from feedback |
| 12–17 | Semantic understanding, genre awareness | Meta-learning |
| 18–23 | Narrative coherence, style, creativity | Stable meta-learning → fixed point |

The first ~5 layers correspond to skill-infinity's convergence depth. Layers beyond 5 provide diminishing meta-improvement, consistent with the `|meta_feedback| < |feedback|` convergence guarantee.
