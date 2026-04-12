# GGML Operation Catalog

This catalog defines all GGML operations with their formal signatures, shape inference rules, and mathematical semantics. Operations are grouped by category for easy reference.

## Operation Index

Use this index to find operations by use case:

| Use Case | Operations |
|----------|------------|
| **LLM Core** | MUL_MAT, RMS_NORM, ROPE, SOFT_MAX, SILU, GET_ROWS |
| **Attention** | FLASH_ATTN_EXT, DIAG_MASK_INF, SCALE |
| **Elementwise** | ADD, SUB, MUL, DIV, SQR, SQRT, EXP, LOG |
| **Activations** | RELU, GELU, SILU, TANH, SIGMOID, SOFTPLUS |
| **Normalization** | NORM, RMS_NORM, GROUP_NORM, L2_NORM |
| **Reduction** | SUM, SUM_ROWS, MEAN, ARGMAX |
| **Shape** | RESHAPE, VIEW, PERMUTE, TRANSPOSE, CONT |
| **Convolution** | CONV_1D, CONV_2D, IM2COL, POOL_1D, POOL_2D |

---

## 1. Matrix Operations

### MUL_MAT (Matrix Multiplication)

**Signature:** `(A: [m, k, ...], B: [n, k, ...]) → C: [m, n, ...]`

**Semantics:** `C = A @ B^T` (B is transposed)

```
for batch dimensions:
    C[i, j] = Σ_k A[i, k] * B[j, k]
```

**Shape inference:**
```
C.ne[0] = A.ne[0]  // m
C.ne[1] = B.ne[0]  // n
C.ne[2] = max(A.ne[2], B.ne[2])  // batch
C.ne[3] = max(A.ne[3], B.ne[3])  // batch
```

**Type constraints:**
- A can be quantized (Q4_0, Q4_K, etc.)
- B must be F32 or F16
- C is F32

**Critical for:** All linear layers, attention QKV projections

---

### MUL_MAT_ID (Mixture of Experts)

**Signature:** `(A: [m, k, n_experts], B: [n, k], ids: [n_tokens]) → C: [m, n_tokens]`

**Semantics:** Per-token expert selection
```
for each token t:
    expert = ids[t]
    C[:, t] = A[:, :, expert] @ B[:, t]
```

**Critical for:** MoE models (Mixtral, etc.)

---

### OUT_PROD (Outer Product)

**Signature:** `(A: [m], B: [n]) → C: [m, n]`

**Semantics:** `C[i, j] = A[i] * B[j]`

---

## 2. Normalization Operations

### RMS_NORM (Root Mean Square Normalization)

**Signature:** `(x: [n, ...], eps: float) → y: [n, ...]`

**Semantics:**
```
rms = sqrt(mean(x²) + eps)
y = x / rms
```

**Parameters:** `eps` stored in op_params as float (default: 1e-5)

**Critical for:** LLaMA, Mistral (replaces LayerNorm)

---

### NORM (Layer Normalization)

**Signature:** `(x: [n, ...], eps: float) → y: [n, ...]`

**Semantics:**
```
mean = mean(x)
var = mean((x - mean)²)
y = (x - mean) / sqrt(var + eps)
```

---

### GROUP_NORM

**Signature:** `(x: [c, h, w, n], n_groups: int, eps: float) → y`

**Semantics:** Normalize within groups of channels

---

### L2_NORM

**Signature:** `(x: [n, ...], eps: float) → y: [n, ...]`

**Semantics:** `y = x / (||x||_2 + eps)`

---

## 3. Positional Encoding

### ROPE (Rotary Position Embedding)

**Signature:** `(x: [head_dim, n_heads, seq_len, batch], pos: [seq_len], ...) → y`

**Parameters:**
```c
struct rope_params {
    int32_t n_dims;       // Dimensions to rotate (usually head_dim)
    int32_t mode;         // 0=normal, 2=neox, 8=mrope, 24=vision
    int32_t n_ctx_orig;   // Original context length
    float   freq_base;    // Base frequency (10000.0)
    float   freq_scale;   // Frequency scaling
    float   ext_factor;   // Extension factor
    float   attn_factor;  // Attention factor
    float   beta_fast;    // YaRN parameter
    float   beta_slow;    // YaRN parameter
};
```

**Semantics (simplified):**
```
for each position p, dimension pair (2i, 2i+1):
    θ = p / (freq_base ^ (2i / n_dims))
    y[2i]   = x[2i] * cos(θ) - x[2i+1] * sin(θ)
    y[2i+1] = x[2i] * sin(θ) + x[2i+1] * cos(θ)
```

**Critical for:** All modern LLMs with rotary embeddings

---

## 4. Attention Operations

### SOFT_MAX

**Signature:** `(x: [n, ...], scale: float, mask: optional) → y: [n, ...]`

**Semantics:**
```
x_scaled = x * scale
if mask: x_scaled += mask
y = softmax(x_scaled, dim=0)
```

**Parameters:** `scale` in op_params

---

### DIAG_MASK_INF (Causal Mask)

**Signature:** `(x: [n, n, ...], n_past: int) → y`

**Semantics:** Set upper triangle to -inf for causal attention
```
y[i, j] = -inf if j > i + n_past else x[i, j]
```

---

### FLASH_ATTN_EXT (Flash Attention)

**Signature:** `(Q, K, V, mask) → O`

**Semantics:** Memory-efficient fused attention
```
O = softmax(Q @ K^T / sqrt(d_k) + mask) @ V
```

**Critical for:** Efficient attention computation

---

## 5. Activation Functions

### Unary Activations

All have signature: `(x: [n, ...]) → y: [n, ...]`

| Op | Formula |
|----|---------|
| RELU | `max(0, x)` |
| GELU | `0.5 * x * (1 + tanh(sqrt(2/π) * (x + 0.044715 * x³)))` |
| GELU_QUICK | `x * sigmoid(1.702 * x)` |
| SILU (SwiGLU) | `x * sigmoid(x)` |
| SIGMOID | `1 / (1 + exp(-x))` |
| TANH | `(exp(x) - exp(-x)) / (exp(x) + exp(-x))` |
| EXP | `exp(x)` |
| SOFTPLUS | `log(1 + exp(x))` |
| HARDSIGMOID | `clip((x + 3) / 6, 0, 1)` |
| HARDSWISH | `x * hardsigmoid(x)` |

---

### GLU Operations (Gated Linear Units)

**Signature:** `(x: [2n, ...]) → y: [n, ...]`

Split input in half, apply gating:

| Op | Formula |
|----|---------|
| REGLU | `x[:n] * relu(x[n:])` |
| GEGLU | `x[:n] * gelu(x[n:])` |
| SWIGLU | `x[:n] * silu(x[n:])` |

---

## 6. Elementwise Operations

### Binary Operations

**Signature:** `(a, b) → c` with broadcasting

| Op | Formula |
|----|---------|
| ADD | `a + b` |
| SUB | `a - b` |
| MUL | `a * b` |
| DIV | `a / b` |

### Unary Operations

| Op | Formula |
|----|---------|
| SQR | `x²` |
| SQRT | `√x` |
| LOG | `ln(x)` |
| SIN | `sin(x)` |
| COS | `cos(x)` |
| ABS | `|x|` |
| NEG | `-x` |
| SGN | `sign(x)` |

---

## 7. Reduction Operations

### SUM

**Signature:** `(x: [n, ...]) → y: scalar`

**Semantics:** `y = Σ x[i]`

---

### SUM_ROWS

**Signature:** `(x: [n, m, ...]) → y: [1, m, ...]`

**Semantics:** Sum along dimension 0

---

### MEAN

**Signature:** `(x: [n, ...]) → y: scalar`

**Semantics:** `y = mean(x)`

---

### ARGMAX

**Signature:** `(x: [n, ...]) → y: [1, ...]`

**Semantics:** Index of maximum value along dim 0

---

## 8. Shape Operations

### RESHAPE

**Signature:** `(x, new_shape) → y`

**Semantics:** Change shape without copying data (view)

**Constraint:** `product(new_shape) == product(x.shape)`

---

### VIEW

**Signature:** `(x, offset, new_ne, new_nb) → y`

**Semantics:** Create view with custom strides

---

### PERMUTE

**Signature:** `(x, axes: [4]) → y`

**Semantics:** Reorder dimensions
```
y.ne[i] = x.ne[axes[i]]
y.nb[i] = x.nb[axes[i]]
```

---

### TRANSPOSE

**Signature:** `(x) → y`

**Semantics:** Swap dimensions 0 and 1 (equivalent to permute([1,0,2,3]))

---

### CONT (Contiguous)

**Signature:** `(x) → y`

**Semantics:** Copy to contiguous memory if needed

---

### CONCAT

**Signature:** `(a, b, dim) → c`

**Semantics:** Concatenate along dimension

---

## 9. Indexing Operations

### GET_ROWS (Embedding Lookup)

**Signature:** `(emb: [vocab, dim], idx: [n]) → y: [n, dim]`

**Semantics:** `y[i] = emb[idx[i]]`

**Critical for:** Token embedding lookup

---

### SET_ROWS

**Signature:** `(dst, src, idx) → dst`

**Semantics:** Scatter: `dst[idx[i]] = src[i]`

---

## 10. Convolution Operations

### IM2COL

**Signature:** `(x: [c, h, w, n], kernel_h, kernel_w, stride, pad, dilation) → y`

**Semantics:** Image to column transformation for efficient convolution

---

### CONV_2D

**Signature:** `(input, kernel, stride, padding) → output`

---

### POOL_2D

**Signature:** `(x, kernel_size, stride, padding, pool_type) → y`

**pool_type:** MAX or AVG

---

## 11. Special Operations

### SCALE

**Signature:** `(x, scale: float) → y`

**Semantics:** `y = x * scale`

---

### CLAMP

**Signature:** `(x, min, max) → y`

**Semantics:** `y = clip(x, min, max)`

---

### ARANGE

**Signature:** `(start, stop, step) → y`

**Semantics:** Generate range tensor

---

### FILL

**Signature:** `(x, value) → y`

**Semantics:** Fill tensor with constant value

---

## 12. Custom Operations

### MAP_CUSTOM1/2/3

**Signature:** User-defined

**Semantics:** Apply custom function with 1/2/3 inputs

```c
typedef void (*ggml_custom1_op_t)(
    struct ggml_tensor * dst,
    const struct ggml_tensor * a,
    int ith, int nth, void * userdata);
```

---

## Operation Implementation Checklist

For a minimal implementation, implement operations in this priority order:

### Priority 1: Core LLM (Required)
- [ ] MUL_MAT (with quantized A support)
- [ ] RMS_NORM
- [ ] ROPE
- [ ] SOFT_MAX
- [ ] SILU
- [ ] GET_ROWS
- [ ] ADD
- [ ] MUL

### Priority 2: Attention
- [ ] DIAG_MASK_INF
- [ ] SCALE
- [ ] PERMUTE
- [ ] RESHAPE
- [ ] VIEW
- [ ] CONT

### Priority 3: Extended
- [ ] FLASH_ATTN_EXT
- [ ] MUL_MAT_ID (for MoE)
- [ ] GELU, RELU (for other architectures)
- [ ] NORM (for GPT-style models)
