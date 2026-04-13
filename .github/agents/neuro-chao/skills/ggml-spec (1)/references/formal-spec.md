# GGML Formal Specification

This document defines the invariant core of GGML - the formal grammar, protocols, and contracts that any minimal implementation must satisfy. This represents approximately 1% of the full GGML codebase but defines 100% of its computational semantics.

## 1. Tensor Grammar

### 1.1 Tensor Structure

A tensor `T` is defined by the tuple `(type, ne[4], nb[4], data, op, src[10])`:

```
struct tensor {
    type   : ggml_type           // Data type (F32, F16, Q4_0, etc.)
    ne[4]  : int64[4]            // Number of elements per dimension
    nb[4]  : size_t[4]           // Stride in bytes per dimension
    data   : void*               // Pointer to tensor data
    op     : ggml_op             // Operation that produced this tensor
    src[10]: tensor*[10]         // Source tensors (inputs to op)
}
```

**Invariants:**
- `GGML_MAX_DIMS = 4` (tensors are at most 4-dimensional)
- `nb[0] = type_size(type)` for contiguous tensors
- `nb[i] = nb[i-1] * ne[i-1]` for contiguous tensors
- `ne[i] >= 1` for all dimensions (no zero-size dimensions)

### 1.2 Shape Algebra

**Element count:** `nelements(T) = ne[0] * ne[1] * ne[2] * ne[3]`

**Byte size:** `nbytes(T) = nb[3] * ne[3]` (for contiguous tensors)

**Contiguity test:**
```
is_contiguous(T) := 
    nb[0] == type_size(type) &&
    nb[1] == nb[0] * ne[0] &&
    nb[2] == nb[1] * ne[1] &&
    nb[3] == nb[2] * ne[2]
```

**Broadcasting rule:** Tensor `A` can broadcast to `B` iff for each dimension `i`:
```
can_broadcast(A, B) := ∀i: (A.ne[i] == B.ne[i]) || (A.ne[i] == 1)
```

### 1.3 Memory Layout

Tensors use **row-major order** with the following conventions:
- Dimension 0 (ne[0]): innermost, contiguous elements
- Dimension 1 (ne[1]): rows
- Dimension 2 (ne[2]): matrices/channels
- Dimension 3 (ne[3]): batch

**Element access formula:**
```c
// Access element at indices (i0, i1, i2, i3)
void* element_ptr(tensor* T, int64_t i0, int64_t i1, int64_t i2, int64_t i3) {
    return (char*)T->data + i3*T->nb[3] + i2*T->nb[2] + i1*T->nb[1] + i0*T->nb[0];
}
```

### 1.4 View Semantics

A **view** is a tensor that shares data with another tensor but may have different shape/strides:
```
view(T, offset, new_ne, new_nb) := {
    type: T.type,
    ne:   new_ne,
    nb:   new_nb,
    data: T.data + offset,
    view_src: T,
    view_offs: offset
}
```

Views enable zero-copy operations: reshape, transpose, slice, permute.

## 2. Type System

### 2.1 Primitive Types

| Type | Size (bytes) | Block Size | Description |
|------|--------------|------------|-------------|
| F32  | 4 | 1 | 32-bit IEEE 754 float |
| F16  | 2 | 1 | 16-bit IEEE 754 half-precision |
| BF16 | 2 | 1 | Google Brain 16-bit float |
| I8   | 1 | 1 | Signed 8-bit integer |
| I16  | 2 | 1 | Signed 16-bit integer |
| I32  | 4 | 1 | Signed 32-bit integer |
| I64  | 8 | 1 | Signed 64-bit integer |
| F64  | 8 | 1 | 64-bit IEEE 754 double |

### 2.2 Quantized Types

Quantized types store multiple elements per block with shared scale factors:

| Type | Block Size | Bits/Weight | Structure |
|------|------------|-------------|-----------|
| Q4_0 | 32 | 4.5 | `{f16 scale; uint8 quants[16]}` |
| Q4_1 | 32 | 5.0 | `{f16 scale, min; uint8 quants[16]}` |
| Q5_0 | 32 | 5.5 | `{f16 scale; uint8 qh[4]; uint8 quants[16]}` |
| Q5_1 | 32 | 6.0 | `{f16 scale, min; uint8 qh[4]; uint8 quants[16]}` |
| Q8_0 | 32 | 8.5 | `{f16 scale; int8 quants[32]}` |
| Q8_1 | 32 | 9.0 | `{f32 scale, sum; int8 quants[32]}` |

**K-Quants** (super-blocks with nested quantization):

| Type | Block Size | Bits/Weight | Description |
|------|------------|-------------|-------------|
| Q2_K | 256 | 2.5625 | 2-bit with 4-bit scales |
| Q3_K | 256 | 3.4375 | 3-bit with 6-bit scales |
| Q4_K | 256 | 4.5 | 4-bit with 6-bit scales |
| Q5_K | 256 | 5.5 | 5-bit with 6-bit scales |
| Q6_K | 256 | 6.5625 | 6-bit with 8-bit scales |

### 2.3 Quantization Contract

Every quantized type must implement:

```c
// Quantize n floats from src to dst
void quantize_row_TYPE(const float* src, void* dst, int64_t n);

// Dequantize n elements from src to dst
void dequantize_row_TYPE(const void* src, float* dst, int64_t n);

// Vector dot product: sum(dequant(vx) * vy)
void vec_dot_TYPE(int n, float* s, const void* vx, const float* vy);
```

**Type metadata functions:**
```c
int64_t blck_size(type);     // Elements per block (1 for non-quantized)
size_t  type_size(type);     // Bytes per block
size_t  row_size(type, ne);  // Bytes for ne elements: type_size * (ne / blck_size)
bool    is_quantized(type);  // True for Q* types
```

## 3. Operation Protocol

### 3.1 Operation Definition

Every operation `op` is defined by:

1. **Signature**: Input types, output type, parameter constraints
2. **Shape inference**: `output_shape = f(input_shapes, params)`
3. **Forward compute**: `output_data = compute(input_data, params)`
4. **Backward compute** (optional): `input_grads = backward(output_grad, inputs, params)`

### 3.2 Operation Categories

**Unary ops** (1 input → 1 output):
```
UNARY_OP(x) → y where y.shape == x.shape
Examples: ABS, NEG, EXP, RELU, SILU, GELU, TANH, SIGMOID
```

**Binary ops** (2 inputs → 1 output):
```
BINARY_OP(a, b) → c where c.shape = broadcast(a.shape, b.shape)
Examples: ADD, SUB, MUL, DIV
```

**Reduction ops** (reduce along dimensions):
```
REDUCE_OP(x, dims) → y where y.shape has dims collapsed
Examples: SUM, SUM_ROWS, MEAN, ARGMAX
```

**Matrix ops**:
```
MUL_MAT(A[m,k], B[k,n]) → C[m,n]  // C = A @ B^T (note: B is transposed)
OUT_PROD(A[m], B[n]) → C[m,n]     // C = A ⊗ B (outer product)
```

### 3.3 Critical Operations for LLM Inference

| Operation | Signature | Semantics |
|-----------|-----------|-----------|
| MUL_MAT | (A, B) → C | Matrix multiply: C = A @ B^T |
| RMS_NORM | (x, eps) → y | y = x / sqrt(mean(x²) + eps) |
| ROPE | (x, pos, freq_base, freq_scale) → y | Rotary position embedding |
| SOFT_MAX | (x, scale, mask) → y | Scaled softmax with optional mask |
| SILU | x → y | y = x * sigmoid(x) |
| GET_ROWS | (emb, idx) → y | Embedding lookup |

### 3.4 Operation Parameters

Operations may have parameters stored in `op_params[GGML_MAX_OP_PARAMS]`:

```c
// Example: ROPE parameters
struct rope_params {
    int32_t n_dims;      // Number of dimensions to rotate
    int32_t mode;        // ROPE type (normal, neox, mrope)
    int32_t n_ctx_orig;  // Original context length
    float   freq_base;   // Base frequency (default: 10000)
    float   freq_scale;  // Frequency scale factor
    float   ext_factor;  // Extension factor for long contexts
    float   attn_factor; // Attention factor
    float   beta_fast;   // YaRN beta fast
    float   beta_slow;   // YaRN beta slow
};
```

## 4. Computation Graph

### 4.1 Graph Structure

```c
struct cgraph {
    int n_nodes;                    // Number of operation nodes
    int n_leafs;                    // Number of leaf tensors (inputs)
    tensor* nodes[GGML_MAX_NODES];  // Operation nodes in topological order
    tensor* leafs[GGML_MAX_NODES];  // Leaf tensors (no sources)
    tensor* grads[GGML_MAX_NODES];  // Gradient tensors (for backward)
};
```

### 4.2 Graph Construction

```c
// Create computation graph
cgraph* graph = ggml_new_graph(ctx);

// Build forward graph from output tensor
ggml_build_forward_expand(graph, output);

// Graph is now topologically sorted: nodes[0] computed first
```

### 4.3 Graph Execution Contract

A backend must implement:
```c
enum ggml_status ggml_backend_graph_compute(backend, cgraph);
```

Execution semantics:
1. Process nodes in order `nodes[0]` to `nodes[n_nodes-1]`
2. For each node, ensure all `src[]` tensors are computed
3. Execute the operation, writing result to `node->data`
4. Return `GGML_STATUS_SUCCESS` or error code

## 5. Backend Contract

### 5.1 Backend Interface

A minimal backend must implement:

```c
// Backend identification
const char* ggml_backend_name(backend);
ggml_guid_t ggml_backend_guid(backend);

// Buffer management
ggml_backend_buffer_t ggml_backend_alloc_buffer(backend, size);
ggml_backend_buffer_type_t ggml_backend_get_default_buffer_type(backend);

// Tensor data transfer
void ggml_backend_tensor_set(tensor, data, offset, size);
void ggml_backend_tensor_get(tensor, data, offset, size);

// Computation
enum ggml_status ggml_backend_graph_compute(backend, cgraph);

// Capability query
bool ggml_backend_supports_op(backend, op_tensor);
```

### 5.2 Buffer Type Contract

```c
// Buffer type interface
const char* ggml_backend_buft_name(buft);
ggml_backend_buffer_t ggml_backend_buft_alloc_buffer(buft, size);
size_t ggml_backend_buft_get_alignment(buft);
bool ggml_backend_buft_is_host(buft);  // True if CPU-accessible
```

### 5.3 Device Types

```c
enum ggml_backend_dev_type {
    GGML_BACKEND_DEVICE_TYPE_CPU,   // CPU using system memory
    GGML_BACKEND_DEVICE_TYPE_GPU,   // GPU with dedicated memory
    GGML_BACKEND_DEVICE_TYPE_IGPU,  // Integrated GPU using host memory
    GGML_BACKEND_DEVICE_TYPE_ACCEL  // Accelerator (BLAS, AMX, etc.)
};
```

## 6. GGUF File Format

### 6.1 File Structure

```
GGUF File:
┌─────────────────────────────────────┐
│ Magic: "GGUF" (4 bytes)             │
│ Version: uint32 (currently 3)       │
│ Tensor Count: int64                 │
│ KV Count: int64                     │
├─────────────────────────────────────┤
│ KV Pairs (metadata)                 │
│   key: string                       │
│   type: gguf_type                   │
│   value: varies by type             │
├─────────────────────────────────────┤
│ Tensor Info (per tensor)            │
│   name: string                      │
│   n_dims: uint32                    │
│   dims[]: int64[]                   │
│   type: ggml_type                   │
│   offset: uint64                    │
├─────────────────────────────────────┤
│ [Padding to alignment]              │
├─────────────────────────────────────┤
│ Tensor Data (binary blob)           │
└─────────────────────────────────────┘
```

### 6.2 GGUF Types

```c
enum gguf_type {
    GGUF_TYPE_UINT8   = 0,
    GGUF_TYPE_INT8    = 1,
    GGUF_TYPE_UINT16  = 2,
    GGUF_TYPE_INT16   = 3,
    GGUF_TYPE_UINT32  = 4,
    GGUF_TYPE_INT32   = 5,
    GGUF_TYPE_FLOAT32 = 6,
    GGUF_TYPE_BOOL    = 7,
    GGUF_TYPE_STRING  = 8,
    GGUF_TYPE_ARRAY   = 9,
    GGUF_TYPE_UINT64  = 10,
    GGUF_TYPE_INT64   = 11,
    GGUF_TYPE_FLOAT64 = 12,
};
```

### 6.3 String Encoding

Strings are encoded as: `length: uint64` followed by `chars: char[length]` (no null terminator).

### 6.4 Standard Metadata Keys

```
general.architecture    : string  // "llama", "gpt2", "whisper", etc.
general.name           : string  // Model name
general.quantization_version : uint32
general.alignment      : uint32  // Data alignment (default: 32)

{arch}.context_length  : uint32  // Maximum context length
{arch}.embedding_length: uint32  // Hidden size
{arch}.block_count     : uint32  // Number of transformer blocks
{arch}.attention.head_count      : uint32
{arch}.attention.head_count_kv   : uint32
{arch}.rope.freq_base  : float32
```

## 7. Memory Alignment

### 7.1 Platform Alignment

```c
#if UINTPTR_MAX == 0xFFFFFFFF
    #define GGML_MEM_ALIGN 4    // 32-bit systems
#else
    #define GGML_MEM_ALIGN 16   // 64-bit systems
#endif
```

### 7.2 Alignment Macro

```c
#define GGML_PAD(x, n) (((x) + (n) - 1) & ~((n) - 1))
```

### 7.3 GGUF Alignment

Default alignment for tensor data: `GGUF_DEFAULT_ALIGNMENT = 32`

Can be overridden via `general.alignment` metadata key.

## 8. Constants and Limits

```c
#define GGML_MAX_DIMS           4     // Maximum tensor dimensions
#define GGML_MAX_SRC            10    // Maximum source tensors per op
#define GGML_MAX_OP_PARAMS      64    // Bytes for operation parameters
#define GGML_MAX_NAME           64    // Maximum tensor name length
#define GGML_DEFAULT_N_THREADS  4     // Default thread count
#define GGML_DEFAULT_GRAPH_SIZE 2048  // Default graph node capacity
```
