#ifndef GGML_MINIMAL_H
#define GGML_MINIMAL_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// =============================================================================
// Constants
// =============================================================================

#define GGML_MAX_DIMS    4
#define GGML_MAX_SRC     10
#define GGML_MAX_NAME    64
#define GGML_MEM_ALIGN   16

// Quantization block sizes
#define QK4_0  32
#define QK4_K  256

// =============================================================================
// Data Types
// =============================================================================

typedef uint16_t ggml_fp16_t;

enum ggml_type {
    GGML_TYPE_F32  = 0,
    GGML_TYPE_F16  = 1,
    GGML_TYPE_Q4_0 = 2,
    GGML_TYPE_Q4_K = 12,
    GGML_TYPE_I32  = 26,
    GGML_TYPE_COUNT
};

// =============================================================================
// Type Metadata
// =============================================================================

static inline int64_t ggml_blck_size(enum ggml_type type) {
    switch (type) {
        case GGML_TYPE_F32:  return 1;
        case GGML_TYPE_F16:  return 1;
        case GGML_TYPE_Q4_0: return QK4_0;
        case GGML_TYPE_Q4_K: return QK4_K;
        case GGML_TYPE_I32:  return 1;
        default: return 1;
    }
}

static inline size_t ggml_type_size(enum ggml_type type) {
    switch (type) {
        case GGML_TYPE_F32:  return 4;
        case GGML_TYPE_F16:  return 2;
        case GGML_TYPE_Q4_0: return 18;   // 2 + 16
        case GGML_TYPE_Q4_K: return 144;  // K-quant block
        case GGML_TYPE_I32:  return 4;
        default: return 0;
    }
}

static inline size_t ggml_row_size(enum ggml_type type, int64_t ne) {
    return ggml_type_size(type) * (ne / ggml_blck_size(type));
}

static inline bool ggml_is_quantized(enum ggml_type type) {
    return type == GGML_TYPE_Q4_0 || type == GGML_TYPE_Q4_K;
}

// =============================================================================
// FP16 Conversion
// =============================================================================

// Simple FP16 conversion (use hardware intrinsics on ARM64)
#if defined(__ARM_NEON) || defined(__aarch64__)
#include <arm_neon.h>

static inline float ggml_fp16_to_fp32(ggml_fp16_t h) {
    __fp16 f16;
    memcpy(&f16, &h, sizeof(h));
    return (float)f16;
}

static inline ggml_fp16_t ggml_fp32_to_fp16(float f) {
    __fp16 f16 = (__fp16)f;
    ggml_fp16_t h;
    memcpy(&h, &f16, sizeof(h));
    return h;
}

#else
// Software fallback
float ggml_fp16_to_fp32(ggml_fp16_t h);
ggml_fp16_t ggml_fp32_to_fp16(float f);
#endif

// =============================================================================
// Tensor Structure
// =============================================================================

struct ggml_tensor {
    enum ggml_type type;
    
    int64_t ne[GGML_MAX_DIMS];  // number of elements
    size_t  nb[GGML_MAX_DIMS];  // stride in bytes
    
    void* data;
    
    char name[GGML_MAX_NAME];
};

// =============================================================================
// Tensor Helpers
// =============================================================================

static inline int64_t ggml_nelements(const struct ggml_tensor* t) {
    return t->ne[0] * t->ne[1] * t->ne[2] * t->ne[3];
}

static inline size_t ggml_nbytes(const struct ggml_tensor* t) {
    return ggml_row_size(t->type, t->ne[0]) * t->ne[1] * t->ne[2] * t->ne[3];
}

static inline bool ggml_is_contiguous(const struct ggml_tensor* t) {
    return t->nb[0] == ggml_type_size(t->type) &&
           t->nb[1] == t->nb[0] * t->ne[0] &&
           t->nb[2] == t->nb[1] * t->ne[1] &&
           t->nb[3] == t->nb[2] * t->ne[2];
}

static inline void* ggml_get_data(const struct ggml_tensor* t) {
    return t->data;
}

// Element access (for F32 tensors)
static inline float* ggml_get_f32_ptr(const struct ggml_tensor* t, 
                                       int64_t i0, int64_t i1, int64_t i2, int64_t i3) {
    return (float*)((char*)t->data + i3*t->nb[3] + i2*t->nb[2] + i1*t->nb[1] + i0*t->nb[0]);
}

// =============================================================================
// Memory Alignment
// =============================================================================

#define GGML_PAD(x, n) (((x) + (n) - 1) & ~((n) - 1))

static inline void* ggml_aligned_alloc(size_t size) {
    void* ptr = NULL;
    #if defined(_WIN32)
    ptr = _aligned_malloc(size, GGML_MEM_ALIGN);
    #else
    posix_memalign(&ptr, GGML_MEM_ALIGN, size);
    #endif
    return ptr;
}

static inline void ggml_aligned_free(void* ptr) {
    #if defined(_WIN32)
    _aligned_free(ptr);
    #else
    free(ptr);
    #endif
}

#ifdef __cplusplus
}
#endif

#endif // GGML_MINIMAL_H
