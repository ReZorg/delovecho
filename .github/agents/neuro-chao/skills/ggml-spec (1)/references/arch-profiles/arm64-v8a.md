# ARM64-v8a Architecture Profile

Target: ARMv8-A 64-bit processors (Apple Silicon, Snapdragon, AWS Graviton, etc.)

## Hardware Characteristics

| Feature | Specification |
|---------|--------------|
| Register width | 64-bit general, 128-bit SIMD |
| SIMD extension | NEON (mandatory in ARMv8) |
| Vector registers | 32 × 128-bit (v0-v31) |
| FP16 support | Optional (FEAT_FP16) |
| BF16 support | Optional (ARMv8.6+) |
| SVE/SVE2 | Optional (scalable vectors) |
| Memory alignment | 16-byte recommended |

## NEON Intrinsics Reference

### Data Types

```c
// 64-bit vectors (D registers)
int8x8_t, int16x4_t, int32x2_t, int64x1_t
uint8x8_t, uint16x4_t, uint32x2_t, uint64x1_t
float32x2_t, float64x1_t

// 128-bit vectors (Q registers)
int8x16_t, int16x8_t, int32x4_t, int64x2_t
uint8x16_t, uint16x8_t, uint32x4_t, uint64x2_t
float32x4_t, float64x2_t, float16x8_t
```

### Essential Operations

```c
// Load/Store
float32x4_t vld1q_f32(const float* ptr);
void vst1q_f32(float* ptr, float32x4_t val);

// Arithmetic
float32x4_t vaddq_f32(float32x4_t a, float32x4_t b);
float32x4_t vmulq_f32(float32x4_t a, float32x4_t b);
float32x4_t vfmaq_f32(float32x4_t a, float32x4_t b, float32x4_t c); // a + b*c

// Broadcast
float32x4_t vdupq_n_f32(float val);

// Horizontal operations
float32x2_t vpadd_f32(float32x2_t a, float32x2_t b);  // pairwise add
float vaddvq_f32(float32x4_t a);  // sum all lanes (ARMv8.1+)

// Type conversion
float32x4_t vcvtq_f32_s32(int32x4_t a);
int32x4_t vcvtq_s32_f32(float32x4_t a);

// Comparison
uint32x4_t vcgtq_f32(float32x4_t a, float32x4_t b);  // a > b

// Bitwise
uint8x16_t vandq_u8(uint8x16_t a, uint8x16_t b);
uint8x16_t vshrq_n_u8(uint8x16_t a, int n);  // shift right
```

## Optimized Patterns

### Vector Dot Product (F32)

```c
float vec_dot_f32_neon(int n, const float* x, const float* y) {
    float32x4_t sum0 = vdupq_n_f32(0.0f);
    float32x4_t sum1 = vdupq_n_f32(0.0f);
    
    for (int i = 0; i < n; i += 8) {
        float32x4_t x0 = vld1q_f32(x + i);
        float32x4_t x1 = vld1q_f32(x + i + 4);
        float32x4_t y0 = vld1q_f32(y + i);
        float32x4_t y1 = vld1q_f32(y + i + 4);
        
        sum0 = vfmaq_f32(sum0, x0, y0);
        sum1 = vfmaq_f32(sum1, x1, y1);
    }
    
    sum0 = vaddq_f32(sum0, sum1);
    return vaddvq_f32(sum0);  // horizontal sum
}
```

### Q4_0 Dequantization

```c
void dequantize_row_q4_0_neon(const block_q4_0* x, float* y, int64_t k) {
    const int nb = k / QK4_0;
    
    for (int i = 0; i < nb; i++) {
        const float d = ggml_fp16_to_fp32(x[i].d);
        const float32x4_t vd = vdupq_n_f32(d);
        
        const uint8x16_t quants = vld1q_u8(x[i].qs);
        
        // Extract low and high nibbles
        const uint8x16_t m4b = vdupq_n_u8(0x0F);
        const int8x16_t v8  = vdupq_n_s8(8);
        
        const uint8x16_t vl = vandq_u8(quants, m4b);
        const uint8x16_t vh = vshrq_n_u8(quants, 4);
        
        // Convert to signed and subtract 8
        const int8x16_t vl_s = vsubq_s8(vreinterpretq_s8_u8(vl), v8);
        const int8x16_t vh_s = vsubq_s8(vreinterpretq_s8_u8(vh), v8);
        
        // Widen to 16-bit, then 32-bit, convert to float
        // ... (expand and multiply by scale)
        
        vst1q_f32(y + i*32 +  0, ...);
        vst1q_f32(y + i*32 +  4, ...);
        // ... store all 32 values
    }
}
```

### Q4_0 × F32 Dot Product

```c
void ggml_vec_dot_q4_0_q8_0_neon(int n, float* s, 
                                  const void* vx, const void* vy) {
    const block_q4_0* x = vx;
    const block_q8_0* y = vy;
    
    float32x4_t sumv0 = vdupq_n_f32(0.0f);
    float32x4_t sumv1 = vdupq_n_f32(0.0f);
    
    for (int i = 0; i < n/QK4_0; i += 2) {
        const block_q4_0* x0 = &x[i];
        const block_q4_0* x1 = &x[i+1];
        const block_q8_0* y0 = &y[i];
        const block_q8_0* y1 = &y[i+1];
        
        // Load scales
        const float d0 = ggml_fp16_to_fp32(x0->d) * ggml_fp16_to_fp32(y0->d);
        const float d1 = ggml_fp16_to_fp32(x1->d) * ggml_fp16_to_fp32(y1->d);
        
        // Load quantized values
        const uint8x16_t qx0 = vld1q_u8(x0->qs);
        const uint8x16_t qx1 = vld1q_u8(x1->qs);
        const int8x16_t qy0_0 = vld1q_s8(y0->qs);
        const int8x16_t qy0_1 = vld1q_s8(y0->qs + 16);
        const int8x16_t qy1_0 = vld1q_s8(y1->qs);
        const int8x16_t qy1_1 = vld1q_s8(y1->qs + 16);
        
        // Unpack 4-bit to 8-bit and compute dot products
        // Use vdotq_s32 if available (ARMv8.2+), otherwise manual
        // ...
        
        sumv0 = vfmaq_n_f32(sumv0, vcvtq_f32_s32(p0), d0);
        sumv1 = vfmaq_n_f32(sumv1, vcvtq_f32_s32(p1), d1);
    }
    
    *s = vaddvq_f32(vaddq_f32(sumv0, sumv1));
}
```

## Apple Silicon Specifics

### AMX (Apple Matrix Extensions)

Apple Silicon (M1/M2/M3) has undocumented AMX instructions for matrix operations. GGML uses these via the Accelerate framework:

```c
#ifdef GGML_USE_ACCELERATE
#include <Accelerate/Accelerate.h>

// Use vDSP for vector operations
vDSP_dotpr(x, 1, y, 1, &result, n);

// Use BLAS for matrix multiply
cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasTrans,
            m, n, k, 1.0f, A, k, B, k, 0.0f, C, n);
#endif
```

### Metal Backend

For GPU acceleration on Apple Silicon:

```c
// Metal compute kernel for matrix multiply
kernel void matmul_f32(
    device const float* A [[buffer(0)]],
    device const float* B [[buffer(1)]],
    device float* C [[buffer(2)]],
    constant int& M [[buffer(3)]],
    constant int& N [[buffer(4)]],
    constant int& K [[buffer(5)]],
    uint2 gid [[thread_position_in_grid]]
) {
    // Tiled matrix multiplication
    // ...
}
```

## Build Configuration

### CMake Flags

```cmake
# Basic ARM64 build
cmake -DCMAKE_SYSTEM_PROCESSOR=aarch64 ..

# With NEON (default on ARM64)
# NEON is mandatory in ARMv8, no flag needed

# With FP16 (if supported)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=armv8.2-a+fp16")

# With Apple Accelerate
cmake -DGGML_ACCELERATE=ON ..

# With Metal
cmake -DGGML_METAL=ON ..
```

### Compiler Flags

```bash
# Generic ARM64
-march=armv8-a

# Apple Silicon (M1+)
-march=armv8.4-a+crypto+fp16+simd

# AWS Graviton 2
-march=armv8.2-a+crypto+fp16+simd

# AWS Graviton 3
-march=armv8.4-a+crypto+fp16+simd+sve
```

## Android NDK Cross-Compilation

```cmake
cmake .. \
    -DCMAKE_SYSTEM_NAME=Android \
    -DCMAKE_SYSTEM_VERSION=28 \
    -DCMAKE_ANDROID_ARCH_ABI=arm64-v8a \
    -DCMAKE_ANDROID_NDK=$NDK_PATH \
    -DCMAKE_ANDROID_STL_TYPE=c++_shared
```

## Performance Considerations

| Operation | Optimization Strategy |
|-----------|----------------------|
| Matrix multiply | Use NEON FMA, tile for cache |
| Quantized matmul | Use vdotq_s32 (ARMv8.2+) |
| Softmax | Vectorize exp(), use vaddvq |
| RMS norm | Vectorize square/sum |
| Memory access | Align to 16 bytes, prefetch |

## Minimal Implementation Files

For ARM64-only GGML:

```
src/
├── ggml.c              # Core tensor operations
├── ggml-quants.c       # Quantization (NEON optimized)
├── ggml-backend.c      # Backend abstraction
└── ggml-cpu/
    ├── ggml-cpu.c      # CPU backend
    └── ggml-cpu-aarch64.c  # ARM64 SIMD kernels
```
