#ifndef GGML_QUANTS_H
#define GGML_QUANTS_H

#include "ggml-minimal.h"

#ifdef __cplusplus
extern "C" {
#endif

// =============================================================================
// Q4_0: 4-bit symmetric quantization
// Block size: 32 elements
// Storage: 18 bytes per block (2 + 16)
// =============================================================================

typedef struct {
    ggml_fp16_t d;       // scale (delta)
    uint8_t qs[QK4_0/2]; // 4-bit quantized values (packed)
} block_q4_0;

static_assert(sizeof(block_q4_0) == 18, "block_q4_0 size mismatch");

// =============================================================================
// Q4_K: 4-bit K-quant (super-block quantization)
// Block size: 256 elements (8 sub-blocks of 32)
// Storage: 144 bytes per block
// =============================================================================

typedef struct {
    ggml_fp16_t d;          // super-block scale
    ggml_fp16_t dmin;       // super-block min
    uint8_t scales[12];     // 8 × 6-bit scale/min pairs
    uint8_t qs[QK4_K/2];    // 4-bit quantized values
} block_q4_k;

static_assert(sizeof(block_q4_k) == 144, "block_q4_k size mismatch");

// =============================================================================
// Dequantization Functions
// =============================================================================

// Dequantize Q4_0 block to float
void dequantize_row_q4_0(const block_q4_0* x, float* y, int64_t k);

// Dequantize Q4_K block to float
void dequantize_row_q4_k(const block_q4_k* x, float* y, int64_t k);

// =============================================================================
// Vector Dot Product Functions
// These are the critical hot path for quantized matrix multiplication
// =============================================================================

// Q4_0 × F32 dot product
void ggml_vec_dot_q4_0_f32(int n, float* s, const void* vx, const float* vy);

// Q4_K × F32 dot product
void ggml_vec_dot_q4_k_f32(int n, float* s, const void* vx, const float* vy);

// =============================================================================
// Quantization Functions (for completeness, not always needed for inference)
// =============================================================================

// Quantize float row to Q4_0
void quantize_row_q4_0(const float* x, block_q4_0* y, int64_t k);

// Quantize float row to Q4_K
void quantize_row_q4_k(const float* x, block_q4_k* y, int64_t k);

#ifdef __cplusplus
}
#endif

#endif // GGML_QUANTS_H
