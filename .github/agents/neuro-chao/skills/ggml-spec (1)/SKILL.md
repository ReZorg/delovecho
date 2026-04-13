---
name: ggml-spec
description: Build minimal GGML tensor library implementations from formal specifications. Use when creating custom ML inference engines, porting GGML to new architectures, implementing subset of operations for specific models (LLaMA, Whisper), or optimizing quantized inference for target hardware (ARM64, x86-64, WASM).
---

# GGML Specification Skill

Build minimal, efficient GGML implementations by selecting only the operations, types, and architecture-specific code needed for your use case.

## Quick Start

### 1. Generate Scaffold

```bash
python scripts/generate_minimal.py \
    --arch arm64 \
    --model llama \
    --quants q4_k,f16 \
    --output ./my-llama-impl
```

### 2. Implement Core Operations

The scaffold generates stubs. Implement using patterns from:
- `references/op-catalog.md` - Operation semantics
- `references/arch-profiles/arm64-v8a.md` - SIMD patterns

### 3. Build and Test

```bash
cd my-llama-impl && make
./llama-minimal model.gguf "Hello"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Application                          │
├─────────────────────────────────────────────────────────────┤
│  Model Layer (llama-minimal.c, whisper-minimal.c)           │
├─────────────────────────────────────────────────────────────┤
│  Operations (ggml-ops-*.c)    │  Types (ggml-quants-*.c)    │
├───────────────────────────────┴─────────────────────────────┤
│  Core Spec (ggml-minimal.h)   │  GGUF (gguf-minimal.c)      │
└─────────────────────────────────────────────────────────────┘
```

## Parameter Space

| Dimension | Options |
|-----------|---------|
| **Architecture** | `arm64`, `x86-64`, `x86-64-avx512`, `wasm`, `scalar` |
| **Model** | `llama`, `whisper`, `bert`, `custom` |
| **Quantization** | `f32`, `f16`, `q4_0`, `q4_k`, `q5_k`, `q6_k`, `q8_0` |

## Reference Files

Read these based on your task:

| Task | Reference |
|------|-----------|
| Understanding GGML core | `references/formal-spec.md` |
| Implementing operations | `references/op-catalog.md` |
| Adding quantization | `references/type-system.md` |
| ARM64 optimization | `references/arch-profiles/arm64-v8a.md` |
| x86-64 optimization | `references/arch-profiles/x86-64.md` |
| LLaMA implementation | `references/model-patterns/llama-family.md` |
| Whisper implementation | `references/model-patterns/whisper.md` |

## Common Workflows

### Minimal LLaMA on ARM64

```bash
# Generate scaffold
python scripts/generate_minimal.py --arch arm64 --model llama --quants q4_k --output ./llama-arm64

# Key files to implement:
# - ggml-ops-neon.c: MUL_MAT, RMS_NORM, ROPE, SOFT_MAX, SILU
# - ggml-quants-neon.c: Q4_K dequantize, vec_dot
```

Required ops (11): GET_ROWS, MUL_MAT, RMS_NORM, ROPE, SOFT_MAX, SILU, ADD, MUL, RESHAPE, PERMUTE, CONT

### Whisper on x86-64

```bash
python scripts/generate_minimal.py --arch x86-64 --model whisper --quants q5_k,f16 --output ./whisper-x64
```

Required ops (15): CONV_1D, GET_ROWS, MUL_MAT, NORM, SOFT_MAX, GELU, ADD, MUL, RESHAPE, PERMUTE, TRANSPOSE, CONT, DIAG_MASK_INF, PAD, SCALE

### Custom Model

```bash
python scripts/generate_minimal.py --arch arm64 --model custom --quants f32 --output ./my-model

# Then manually add required ops to ggml-ops.h and implement
```

## Operation Priority

For LLM inference, implement in this order:

1. **Critical** (blocks inference): MUL_MAT, GET_ROWS
2. **Required** (model-specific): RMS_NORM/NORM, ROPE, SOFT_MAX, SILU/GELU
3. **Shape ops** (usually zero-copy): RESHAPE, PERMUTE, VIEW, CONT
4. **Optimization** (performance): FLASH_ATTN_EXT, fused kernels

## Quantization Selection

| Type | Bits/Weight | Quality | Speed | Use Case |
|------|-------------|---------|-------|----------|
| F16 | 16 | Best | Slow | Reference, small models |
| Q8_0 | 8.5 | Excellent | Medium | Quality-critical |
| Q6_K | 6.6 | Very Good | Medium | Balanced |
| Q5_K | 5.5 | Good | Fast | Recommended default |
| Q4_K | 4.5 | Acceptable | Fastest | Memory-constrained |
| Q4_0 | 4.5 | Lower | Fastest | Simplest to implement |

## Templates

Pre-built templates in `templates/`:

- `llama-arm64-minimal/` - LLaMA on ARM64 with NEON
- `llama-x64-avx2-minimal/` - LLaMA on x86-64 with AVX2
- `scaffold-custom/` - Empty starting point

## Memory Estimation

```
Model weights ≈ n_params × bits_per_weight / 8
KV cache ≈ 2 × n_layer × n_kv_heads × head_dim × 2 × context_len

Example (7B Q4_K, 4K context):
  Weights: 7B × 4.5 / 8 ≈ 4 GB
  KV cache: 2 × 32 × 8 × 128 × 2 × 4096 ≈ 512 MB
```

## Validation

Test your implementation:

```c
// 1. Load reference GGUF model
// 2. Run forward pass
// 3. Compare logits to reference (llama.cpp output)
// 4. Check: max_diff < 0.01 for Q4_K, < 0.001 for F16
```
