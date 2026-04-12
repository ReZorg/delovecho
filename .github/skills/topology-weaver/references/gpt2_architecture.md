# GPT-2 Architecture Reference

Detailed component specifications for GPT-2 topology generation.

## Architecture Variants

| Variant | d_model | n_layers | n_heads | d_head | d_mlp | Parameters |
|---------|---------|----------|---------|--------|-------|------------|
| GPT-2 | 768 | 12 | 12 | 64 | 3072 | 117M |
| GPT-2 Medium | 1024 | 24 | 16 | 64 | 4096 | 345M |
| GPT-2 Large | 1280 | 36 | 20 | 64 | 5120 | 762M |
| GPT-2 XL | 1600 | 48 | 25 | 64 | 6400 | 1.5B |

## Layer Structure

Each transformer layer consists of:

```
Layer[i]:
├── Attention Block
│   ├── LayerNorm (pre-norm)
│   ├── Multi-Head Attention
│   │   ├── Q projection: d_model → d_model
│   │   ├── K projection: d_model → d_model
│   │   ├── V projection: d_model → d_model
│   │   ├── Attention computation
│   │   └── O projection: d_model → d_model
│   └── Residual connection
│
└── MLP Block
    ├── LayerNorm (pre-norm)
    ├── c_fc: d_model → 4*d_model (expansion)
    ├── GELU activation
    ├── c_proj: 4*d_model → d_model (contraction)
    └── Residual connection
```

## MLP Block Details

### c_fc (First Projection)

```python
# Expansion projection
c_fc = nn.Linear(d_model, 4 * d_model)

# Contextual tags:
# - particle_creation: Creates 4x more "particles" (features)
# - field_expansion: Expands the field to higher dimension
```

**Dimensions:**
- Input: `(batch, seq_len, d_model)`
- Output: `(batch, seq_len, 4 * d_model)`

**Parameters:**
- Weight: `(4 * d_model, d_model)`
- Bias: `(4 * d_model,)`

### GELU Activation

```python
# Gaussian Error Linear Unit
def gelu(x):
    return 0.5 * x * (1 + tanh(sqrt(2/π) * (x + 0.044715 * x³)))

# Contextual tags:
# - measurement_gate: Collapses superposition
# - nonlinear_vertex: Interaction point
```

**Properties:**
- Smooth approximation to ReLU
- Non-zero gradient for negative inputs
- Probabilistic interpretation: gates by cumulative Gaussian

### c_proj (Second Projection)

```python
# Contraction projection
c_proj = nn.Linear(4 * d_model, d_model)

# Contextual tags:
# - particle_annihilation: Reduces back to d_model particles
# - field_contraction: Contracts field to original dimension
```

**Dimensions:**
- Input: `(batch, seq_len, 4 * d_model)`
- Output: `(batch, seq_len, d_model)`

## Integration Points

### Pre-MLP Integration

```yaml
point: pre_mlp
location: After attention residual, before MLP LayerNorm
type: wave_input

connects_from:
  - attention_output (via residual add)
  - previous_layer_output (via residual stream)

connects_to:
  - mlp_layer_norm
  
contextual_tag: wave_entry
description: Wave function enters MLP processing
```

### Post-FC Integration

```yaml
point: post_fc
location: After c_fc, before GELU
type: superposition_state

connects_from:
  - c_fc output

connects_to:
  - gelu activation
  - (optional) gating mechanism
  - (optional) skip connection to c_proj

contextual_tag: superposition_peak
description: Maximum superposition in expanded space
```

### Post-MLP Integration

```yaml
point: post_mlp
location: After c_proj, at residual add
type: wave_output

connects_from:
  - c_proj output

connects_to:
  - residual_add (with pre-mlp input)
  - next_layer_input

contextual_tag: wave_exit
description: Wave function exits MLP, rejoins residual stream
```

## Attention Block Details

### Query/Key/Value Projections

```python
# All projections: d_model → d_model
# Split into n_heads of dimension d_head each

c_attn = nn.Linear(d_model, 3 * d_model)  # Combined QKV
# or separate:
W_Q = nn.Linear(d_model, d_model)
W_K = nn.Linear(d_model, d_model)
W_V = nn.Linear(d_model, d_model)
```

### Attention Computation

```python
# Scaled dot-product attention
def attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = Q @ K.transpose(-2, -1) / sqrt(d_k)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -inf)
    weights = softmax(scores, dim=-1)  # Salience landscape
    return weights @ V

# Contextual tags:
# - query_wave: Q projection output
# - key_wave: K projection output  
# - value_particle: V projection output
# - salience_field: Attention weights (S(i,j))
```

### Output Projection

```python
c_proj = nn.Linear(d_model, d_model)

# Contextual tags:
# - attention_collapse: Projects multi-head back to d_model
# - wave_interference: Combines head outputs
```

## Residual Stream

The residual stream is the "information highway" through the model:

```
x_0 = embed(tokens) + pos_embed

for layer in layers:
    x = x + attention(layer_norm(x))  # Attention residual
    x = x + mlp(layer_norm(x))        # MLP residual

output = layer_norm(x)
```

**Contextual interpretation:**
- Residual stream = Standing wave that accumulates information
- Each layer adds interference patterns
- Final output = Collapsed measurement of accumulated wave

## Weight Initialization

GPT-2 uses specific initialization:

```python
# Linear layers
nn.init.normal_(weight, mean=0.0, std=0.02)
nn.init.zeros_(bias)

# Output projections (scaled by depth)
nn.init.normal_(weight, mean=0.0, std=0.02 / sqrt(2 * n_layers))
```

## Topology YAML Template

```yaml
name: gpt2_topology
architecture: gpt2
d_model: 768
n_layers: 12
n_heads: 12
d_head: 64
d_mlp: 3072

mlp_block:
  components:
    - name: c_fc
      type: linear
      in_features: ${d_model}
      out_features: ${d_mlp}
      tag: particle_creation
      
    - name: gelu
      type: activation
      tag: measurement_gate
      
    - name: c_proj
      type: linear
      in_features: ${d_mlp}
      out_features: ${d_model}
      tag: particle_annihilation

  integration_points:
    - name: pre_mlp
      type: wave_input
      connects_to: [attention_output, residual]
      
    - name: post_fc
      type: superposition_state
      connects_to: [gating, skip]
      
    - name: post_mlp
      type: wave_output
      connects_to: [next_layer, residual]

attention_block:
  meshwork_anchors:
    - name: query_anchor
      type: query_field
      tag: query_wave
      
    - name: key_anchor
      type: key_field
      tag: key_wave
      
    - name: value_anchor
      type: value_field
      tag: value_particle
      
    - name: output_anchor
      type: output_field
      tag: wave_interference
```
