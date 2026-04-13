# LLaMA Family Model Pattern

Covers: LLaMA, LLaMA 2, LLaMA 3, Mistral, Mixtral, CodeLlama, Vicuna, Alpaca, and derivatives.

## Architecture Overview

```
Input tokens → Embedding → N × Transformer Block → RMS Norm → Output Projection → Logits

Transformer Block:
    x → RMS Norm → Self-Attention → + → RMS Norm → FFN → +
        └─────────────────────────────┘   └──────────────┘
                (residual)                   (residual)
```

## Required Operations

### Minimal Op Set (11 operations)

| Operation | Usage | Priority |
|-----------|-------|----------|
| GET_ROWS | Token embedding lookup | Critical |
| MUL_MAT | All linear projections | Critical |
| RMS_NORM | Pre-attention, pre-FFN norm | Critical |
| ROPE | Rotary position embedding | Critical |
| SOFT_MAX | Attention scores | Critical |
| SILU | FFN activation | Critical |
| ADD | Residual connections | Critical |
| MUL | RMS norm scaling, attention | Critical |
| RESHAPE | Attention head splitting | Required |
| PERMUTE | Attention dimension reorder | Required |
| CONT | Ensure contiguous for matmul | Required |

### Extended Op Set (for variants)

| Operation | Usage | Models |
|-----------|-------|--------|
| MUL_MAT_ID | Expert routing | Mixtral, DeepSeek |
| DIAG_MASK_INF | Causal masking | All (can be fused) |
| FLASH_ATTN_EXT | Fused attention | Performance opt |
| GELU | Alternative activation | Some fine-tunes |

## Tensor Shapes

For a model with:
- `n_vocab`: Vocabulary size
- `n_embd`: Embedding dimension (hidden size)
- `n_head`: Number of attention heads
- `n_head_kv`: Number of KV heads (GQA)
- `n_layer`: Number of transformer blocks
- `n_ff`: FFN intermediate size

### Weight Tensors

```
token_embd.weight    : [n_vocab, n_embd]

blk.{i}.attn_norm.weight : [n_embd]
blk.{i}.attn_q.weight    : [n_embd, n_embd]
blk.{i}.attn_k.weight    : [n_embd, n_embd_head * n_head_kv]
blk.{i}.attn_v.weight    : [n_embd, n_embd_head * n_head_kv]
blk.{i}.attn_output.weight : [n_embd, n_embd]

blk.{i}.ffn_norm.weight  : [n_embd]
blk.{i}.ffn_gate.weight  : [n_embd, n_ff]
blk.{i}.ffn_up.weight    : [n_embd, n_ff]
blk.{i}.ffn_down.weight  : [n_ff, n_embd]

output_norm.weight : [n_embd]
output.weight      : [n_embd, n_vocab]  (or tied to token_embd)
```

### Activation Shapes (per token)

```
Input:  [seq_len]  (token IDs)
Embed:  [seq_len, n_embd]
Q:      [seq_len, n_head, head_dim]
K:      [seq_len, n_head_kv, head_dim]
V:      [seq_len, n_head_kv, head_dim]
Attn:   [n_head, seq_len, seq_len]
FFN:    [seq_len, n_ff]
Output: [seq_len, n_vocab]
```

## Forward Pass Pseudocode

```python
def llama_forward(tokens, weights, kv_cache, pos):
    # Embedding lookup
    x = GET_ROWS(weights.token_embd, tokens)  # [seq, embd]
    
    for layer in range(n_layer):
        w = weights.layers[layer]
        
        # Self-attention
        x_norm = RMS_NORM(x, w.attn_norm)
        
        Q = MUL_MAT(x_norm, w.attn_q)  # [seq, embd]
        K = MUL_MAT(x_norm, w.attn_k)  # [seq, kv_dim]
        V = MUL_MAT(x_norm, w.attn_v)  # [seq, kv_dim]
        
        # Reshape for multi-head attention
        Q = RESHAPE(Q, [seq, n_head, head_dim])
        K = RESHAPE(K, [seq, n_head_kv, head_dim])
        V = RESHAPE(V, [seq, n_head_kv, head_dim])
        
        # Apply rotary embeddings
        Q = ROPE(Q, pos)
        K = ROPE(K, pos)
        
        # Update KV cache
        kv_cache.k[layer] = CONCAT(kv_cache.k[layer], K)
        kv_cache.v[layer] = CONCAT(kv_cache.v[layer], V)
        
        # Attention: Q @ K^T / sqrt(d) -> softmax -> @ V
        K_full = kv_cache.k[layer]
        V_full = kv_cache.v[layer]
        
        # GQA: repeat K,V heads if n_head_kv < n_head
        if n_head_kv < n_head:
            K_full = REPEAT(K_full, n_head // n_head_kv)
            V_full = REPEAT(V_full, n_head // n_head_kv)
        
        scores = MUL_MAT(Q, K_full) * (1/sqrt(head_dim))
        scores = DIAG_MASK_INF(scores)  # Causal mask
        attn = SOFT_MAX(scores)
        attn_out = MUL_MAT(attn, V_full)
        
        # Project back
        attn_out = RESHAPE(attn_out, [seq, embd])
        attn_out = MUL_MAT(attn_out, w.attn_output)
        
        x = ADD(x, attn_out)  # Residual
        
        # FFN (SwiGLU)
        x_norm = RMS_NORM(x, w.ffn_norm)
        gate = MUL_MAT(x_norm, w.ffn_gate)
        up = MUL_MAT(x_norm, w.ffn_up)
        ffn_out = MUL(SILU(gate), up)
        ffn_out = MUL_MAT(ffn_out, w.ffn_down)
        
        x = ADD(x, ffn_out)  # Residual
    
    # Output
    x = RMS_NORM(x, weights.output_norm)
    logits = MUL_MAT(x, weights.output)
    
    return logits
```

## Model Variants

### LLaMA 1/2

```yaml
architecture: llama
n_head_kv: n_head  # Full attention (no GQA)
rope_type: normal
activation: silu
norm: rms_norm
```

### LLaMA 3

```yaml
architecture: llama
n_head_kv: 8  # GQA with 8 KV heads
rope_type: normal
rope_freq_base: 500000  # Extended context
activation: silu
norm: rms_norm
```

### Mistral

```yaml
architecture: llama
n_head_kv: 8  # GQA
rope_type: normal
sliding_window: 4096  # Sliding window attention
activation: silu
```

### Mixtral (MoE)

```yaml
architecture: llama
n_head_kv: 8
n_expert: 8
n_expert_used: 2  # Top-2 routing
# Requires MUL_MAT_ID for expert selection
```

## GGUF Metadata Keys

```
general.architecture = "llama"
general.name = "LLaMA-2-7B"

llama.context_length = 4096
llama.embedding_length = 4096
llama.block_count = 32
llama.attention.head_count = 32
llama.attention.head_count_kv = 32
llama.attention.layer_norm_rms_epsilon = 1e-5
llama.rope.freq_base = 10000.0
llama.feed_forward_length = 11008
```

## Quantization Strategy

| Layer Type | Recommended Quant | Notes |
|------------|-------------------|-------|
| token_embd | Q4_K, Q6_K | Large, benefits from quant |
| attn_q/k/v | Q4_K | Main memory savings |
| attn_output | Q4_K | |
| ffn_gate/up | Q4_K | Largest layers |
| ffn_down | Q6_K | Slightly higher quality |
| output | F16, Q6_K | Keep higher precision |
| *_norm | F32 | Small, keep full precision |

## Memory Estimation

```
Model memory ≈ n_params × bits_per_weight / 8

KV cache per token ≈ 2 × n_layer × n_head_kv × head_dim × sizeof(float16)

Example (LLaMA-2-7B, Q4_K):
  Weights: 7B × 4.5 bits / 8 ≈ 4 GB
  KV cache (4K ctx): 2 × 32 × 32 × 128 × 2 × 4096 ≈ 2 GB
  Total: ~6 GB
```

## Minimal Implementation Checklist

```
[ ] Token embedding lookup (GET_ROWS)
[ ] RMS normalization
[ ] Q/K/V projections (MUL_MAT)
[ ] Rotary position embedding (ROPE)
[ ] Attention score computation
[ ] Softmax with causal mask
[ ] Attention output projection
[ ] SwiGLU FFN (SILU + MUL)
[ ] Residual connections (ADD)
[ ] Output projection
[ ] KV cache management
```

## Performance Hotspots

| Operation | % Time | Optimization |
|-----------|--------|--------------|
| MUL_MAT (Q/K/V) | 30-40% | Quantized matmul |
| MUL_MAT (FFN) | 40-50% | Quantized matmul |
| SOFT_MAX | 5-10% | Fused attention |
| ROPE | 2-5% | SIMD vectorization |
| RMS_NORM | 1-2% | SIMD vectorization |
