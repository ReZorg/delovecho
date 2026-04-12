# LLaMA ARM64 Minimal Template

A minimal GGML implementation for LLaMA-family models on ARM64 (NEON).

## What's Included

This template provides the absolute minimum code to run LLaMA inference:

```
llama-arm64-minimal/
├── README.md           # This file
├── ggml-minimal.h      # Core types and macros
├── ggml-quants.h       # Quantization types (Q4_0, Q4_K)
├── ggml-quants-neon.c  # NEON-optimized quantization
├── ggml-ops.h          # Operation declarations
├── ggml-ops-neon.c     # NEON-optimized operations
├── gguf-minimal.h      # GGUF file reading
├── gguf-minimal.c      # GGUF implementation
├── llama-minimal.h     # LLaMA model structure
├── llama-minimal.c     # LLaMA forward pass
└── main.c              # Example usage
```

## Supported Operations

Only the 11 operations required for LLaMA inference:

| Operation | Implementation |
|-----------|----------------|
| GET_ROWS | Scalar |
| MUL_MAT | NEON (F32×F32, Q4_0×F32, Q4_K×F32) |
| RMS_NORM | NEON |
| ROPE | NEON |
| SOFT_MAX | NEON |
| SILU | NEON |
| ADD | NEON |
| MUL | NEON |
| RESHAPE | View (no copy) |
| PERMUTE | View (no copy) |
| CONT | Copy if needed |

## Supported Types

- F32 (full precision)
- F16 (storage, converted to F32 for compute)
- Q4_0 (4-bit symmetric)
- Q4_K (4-bit K-quant)

## Build

```bash
# Simple build
cc -O3 -march=armv8-a -o llama-minimal main.c llama-minimal.c \
   ggml-ops-neon.c ggml-quants-neon.c gguf-minimal.c -lm

# With Apple Accelerate (macOS)
cc -O3 -march=armv8-a -DGGML_USE_ACCELERATE -framework Accelerate \
   -o llama-minimal main.c llama-minimal.c \
   ggml-ops-neon.c ggml-quants-neon.c gguf-minimal.c -lm

# Android NDK
$NDK/toolchains/llvm/prebuilt/*/bin/aarch64-linux-android28-clang \
   -O3 -o llama-minimal main.c llama-minimal.c \
   ggml-ops-neon.c ggml-quants-neon.c gguf-minimal.c -lm
```

## Usage

```c
#include "llama-minimal.h"

int main() {
    // Load model
    llama_model model;
    llama_load_model(&model, "model.gguf");
    
    // Create context
    llama_context ctx;
    llama_init_context(&ctx, &model, 2048);  // 2K context
    
    // Tokenize (simplified)
    int tokens[] = {1, 15043, 29892, 825, 338, 278, 6368, 310, 2834, 29973};
    int n_tokens = 10;
    
    // Generate
    for (int i = 0; i < 100; i++) {
        float* logits = llama_forward(&ctx, tokens, n_tokens);
        int next_token = sample_token(logits, model.n_vocab);
        
        if (next_token == 2) break;  // EOS
        
        tokens[n_tokens++] = next_token;
        printf("%s", llama_token_to_str(&model, next_token));
    }
    
    llama_free_context(&ctx);
    llama_free_model(&model);
    return 0;
}
```

## Memory Requirements

```
Model weights: ~4GB for 7B Q4_K
KV cache: 2 × n_layer × n_kv_head × head_dim × 2 × context_len
  = 2 × 32 × 8 × 128 × 2 × 2048 = 256 MB for 7B with 2K context

Total: ~4.3 GB for 7B Q4_K with 2K context
```

## Extending

To add new operations:

1. Add declaration to `ggml-ops.h`
2. Add NEON implementation to `ggml-ops-neon.c`
3. Update `llama-minimal.c` if needed for model variants

To add new quantization types:

1. Add block structure to `ggml-quants.h`
2. Add dequantize/vec_dot functions to `ggml-quants-neon.c`
3. Update `gguf-minimal.c` to handle the type

## Limitations

- Single-threaded (add OpenMP for multi-threading)
- No batching (single sequence only)
- No speculative decoding
- No Flash Attention (standard attention only)
- No MoE support (no MUL_MAT_ID)

## License

MIT (same as GGML)
