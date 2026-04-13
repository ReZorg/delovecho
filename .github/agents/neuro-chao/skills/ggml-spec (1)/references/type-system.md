# GGML Type System

This document provides complete specifications for all GGML data types, with particular focus on quantization formats and their implementation contracts.

## Type Enumeration

```c
enum ggml_type {
    // Floating point
    GGML_TYPE_F32     = 0,   // 32-bit float
    GGML_TYPE_F16     = 1,   // 16-bit float (IEEE 754)
    GGML_TYPE_BF16    = 30,  // Brain float 16
    GGML_TYPE_F64     = 28,  // 64-bit double
    
    // Basic quantization
    GGML_TYPE_Q4_0    = 2,   // 4-bit, symmetric
    GGML_TYPE_Q4_1    = 3,   // 4-bit, asymmetric
    GGML_TYPE_Q5_0    = 6,   // 5-bit, symmetric
    GGML_TYPE_Q5_1    = 7,   // 5-bit, asymmetric
    GGML_TYPE_Q8_0    = 8,   // 8-bit, symmetric
    GGML_TYPE_Q8_1    = 9,   // 8-bit, asymmetric
    
    // K-quants (super-block)
    GGML_TYPE_Q2_K    = 10,  // 2-bit K-quant
    GGML_TYPE_Q3_K    = 11,  // 3-bit K-quant
    GGML_TYPE_Q4_K    = 12,  // 4-bit K-quant
    GGML_TYPE_Q5_K    = 13,  // 5-bit K-quant
    GGML_TYPE_Q6_K    = 14,  // 6-bit K-quant
    GGML_TYPE_Q8_K    = 15,  // 8-bit K-quant
    
    // IQ (importance-based quantization)
    GGML_TYPE_IQ2_XXS = 16,
    GGML_TYPE_IQ2_XS  = 17,
    GGML_TYPE_IQ3_XXS = 18,
    GGML_TYPE_IQ1_S   = 19,
    GGML_TYPE_IQ4_NL  = 20,
    GGML_TYPE_IQ3_S   = 21,
    GGML_TYPE_IQ2_S   = 22,
    GGML_TYPE_IQ4_XS  = 23,
    GGML_TYPE_IQ1_M   = 29,
    
    // Integer types
    GGML_TYPE_I8      = 24,
    GGML_TYPE_I16     = 25,
    GGML_TYPE_I32     = 26,
    GGML_TYPE_I64     = 27,
    
    // Ternary quantization
    GGML_TYPE_TQ1_0   = 34,
    GGML_TYPE_TQ2_0   = 35,
};
```

---

## Floating Point Types

### F32 (32-bit Float)

```
Layout: IEEE 754 single precision
Size: 4 bytes
Block size: 1
Range: ±3.4e38
Precision: ~7 decimal digits
```

### F16 (16-bit Float)

```
Layout: IEEE 754 half precision
  Sign: 1 bit
  Exponent: 5 bits (bias 15)
  Mantissa: 10 bits
Size: 2 bytes
Block size: 1
Range: ±65504
Precision: ~3 decimal digits
```

**Conversion:**
```c
float ggml_fp16_to_fp32(ggml_fp16_t h) {
    // Use hardware intrinsics when available
    // Fallback: bit manipulation
}

ggml_fp16_t ggml_fp32_to_fp16(float f) {
    // Round to nearest, ties to even
}
```

### BF16 (Brain Float 16)

```
Layout: Truncated F32
  Sign: 1 bit
  Exponent: 8 bits (same as F32)
  Mantissa: 7 bits
Size: 2 bytes
Block size: 1
Range: Same as F32 (±3.4e38)
Precision: ~2 decimal digits
```

**Conversion:**
```c
float ggml_bf16_to_fp32(ggml_bf16_t bf) {
    // Simply shift left by 16 bits
    uint32_t u = ((uint32_t)bf.bits) << 16;
    return *(float*)&u;
}

ggml_bf16_t ggml_fp32_to_bf16(float f) {
    // Truncate lower 16 bits (with rounding)
}
```

---

## Basic Quantization Types

### Q4_0 (4-bit Symmetric)

```
Block size: 32 elements
Structure:
  ggml_fp16_t scale;     // 2 bytes
  uint8_t quants[16];    // 16 bytes (32 × 4 bits)
Total: 18 bytes per block
Bits per weight: 4.5
```

**Dequantization:**
```c
void dequantize_row_q4_0(const void* src, float* dst, int64_t n) {
    const block_q4_0* blocks = (const block_q4_0*)src;
    int nb = n / 32;  // number of blocks
    
    for (int i = 0; i < nb; i++) {
        float scale = ggml_fp16_to_fp32(blocks[i].scale);
        
        for (int j = 0; j < 16; j++) {
            uint8_t q = blocks[i].quants[j];
            // Each byte contains 2 4-bit values
            int q0 = (q & 0x0F) - 8;  // Symmetric: subtract 8
            int q1 = (q >> 4) - 8;
            
            dst[i*32 + j]      = scale * q0;
            dst[i*32 + j + 16] = scale * q1;
        }
    }
}
```

### Q4_1 (4-bit Asymmetric)

```
Block size: 32 elements
Structure:
  ggml_fp16_t scale;     // 2 bytes
  ggml_fp16_t min;       // 2 bytes (minimum value)
  uint8_t quants[16];    // 16 bytes
Total: 20 bytes per block
Bits per weight: 5.0
```

**Dequantization:**
```c
// value = scale * quant + min
dst[j] = scale * (q & 0x0F) + min;
```

### Q5_0 (5-bit Symmetric)

```
Block size: 32 elements
Structure:
  ggml_fp16_t scale;     // 2 bytes
  uint8_t qh[4];         // 4 bytes (high bits)
  uint8_t quants[16];    // 16 bytes (low 4 bits)
Total: 22 bytes per block
Bits per weight: 5.5
```

**Dequantization:**
```c
// Combine 4 low bits from quants + 1 high bit from qh
int q = (quants[j] & 0x0F) | ((qh[j/8] >> (j%8)) & 1) << 4;
q -= 16;  // Symmetric: subtract 16
dst[j] = scale * q;
```

### Q8_0 (8-bit Symmetric)

```
Block size: 32 elements
Structure:
  ggml_fp16_t scale;     // 2 bytes
  int8_t quants[32];     // 32 bytes
Total: 34 bytes per block
Bits per weight: 8.5
```

**Dequantization:**
```c
dst[j] = scale * quants[j];  // Direct multiply, no offset
```

---

## K-Quant Types (Super-Block)

K-quants use a two-level quantization scheme with super-blocks containing multiple sub-blocks.

### Q4_K

```
Super-block size: 256 elements (8 sub-blocks of 32)
Structure:
  ggml_fp16_t d;           // 2 bytes - super-block scale
  ggml_fp16_t dmin;        // 2 bytes - super-block min
  uint8_t scales[12];      // 12 bytes - 8 × 6-bit scale/min pairs
  uint8_t quants[128];     // 128 bytes - 256 × 4-bit values
Total: 144 bytes per super-block
Bits per weight: 4.5
```

**Dequantization (simplified):**
```c
for each sub-block b in 0..7:
    // Extract 6-bit scale and min for this sub-block
    scale_b = extract_scale(scales, b) * d;
    min_b = extract_min(scales, b) * dmin;
    
    for j in 0..31:
        q = extract_4bit(quants, b*32 + j);
        dst[b*32 + j] = scale_b * q - min_b;
```

### Q6_K

```
Super-block size: 256 elements
Structure:
  uint8_t ql[128];         // 128 bytes - low 4 bits
  uint8_t qh[64];          // 64 bytes - high 2 bits
  int8_t scales[16];       // 16 bytes - 8-bit scales
  ggml_fp16_t d;           // 2 bytes - super-block scale
Total: 210 bytes per super-block
Bits per weight: 6.5625
```

### K-Quant Summary

| Type | Block | Bits/Weight | Quality | Speed |
|------|-------|-------------|---------|-------|
| Q2_K | 256 | 2.56 | Low | Fastest |
| Q3_K | 256 | 3.44 | Medium-Low | Fast |
| Q4_K | 256 | 4.50 | Medium | Balanced |
| Q5_K | 256 | 5.50 | Medium-High | Slower |
| Q6_K | 256 | 6.56 | High | Slowest |

---

## Type Metadata Functions

Every type must provide these metadata functions:

```c
// Elements per quantization block
int64_t ggml_blck_size(enum ggml_type type) {
    switch (type) {
        case GGML_TYPE_F32:  return 1;
        case GGML_TYPE_F16:  return 1;
        case GGML_TYPE_Q4_0: return 32;
        case GGML_TYPE_Q4_K: return 256;
        // ...
    }
}

// Bytes per block
size_t ggml_type_size(enum ggml_type type) {
    switch (type) {
        case GGML_TYPE_F32:  return 4;
        case GGML_TYPE_F16:  return 2;
        case GGML_TYPE_Q4_0: return 18;  // 2 + 16
        case GGML_TYPE_Q4_K: return 144;
        // ...
    }
}

// Bytes for n elements
size_t ggml_row_size(enum ggml_type type, int64_t ne) {
    return ggml_type_size(type) * (ne / ggml_blck_size(type));
}

// Is this a quantized type?
bool ggml_is_quantized(enum ggml_type type) {
    return type >= GGML_TYPE_Q4_0 && type <= GGML_TYPE_Q6_K;
}
```

---

## Quantization Implementation Contract

For each quantized type, implement:

### 1. Quantize Row

```c
void quantize_row_TYPE(const float* src, void* dst, int64_t n);
```

Quantize `n` float values from `src` to `dst`.

### 2. Dequantize Row

```c
void dequantize_row_TYPE(const void* src, float* dst, int64_t n);
```

Dequantize `n` elements from `src` to `dst`.

### 3. Vector Dot Product

```c
void ggml_vec_dot_TYPE(int n, float* s, size_t bs, 
                       const void* vx, size_t bx,
                       const void* vy, size_t by,
                       int nrc);
```

Compute dot product of quantized vector `vx` with float vector `vy`.

This is the **critical hot path** for matrix multiplication with quantized weights.

### 4. Type Traits Structure

```c
struct ggml_type_traits {
    const char* type_name;
    int64_t     blck_size;
    size_t      type_size;
    bool        is_quantized;
    
    // Function pointers
    ggml_to_float_t    to_float;      // dequantize
    ggml_from_float_t  from_float;    // quantize
    ggml_vec_dot_t     vec_dot;       // dot product
    enum ggml_type     vec_dot_type;  // type for vec_dot second arg
};
```

---

## SIMD Optimization Patterns

### ARM NEON (ARM64)

```c
void dequantize_row_q4_0_neon(const void* src, float* dst, int64_t n) {
    const block_q4_0* blocks = src;
    
    for (int i = 0; i < n/32; i++) {
        float32x4_t scale = vdupq_n_f32(ggml_fp16_to_fp32(blocks[i].scale));
        
        // Load 16 bytes = 32 4-bit values
        uint8x16_t quants = vld1q_u8(blocks[i].quants);
        
        // Split into low and high nibbles
        uint8x16_t lo = vandq_u8(quants, vdupq_n_u8(0x0F));
        uint8x16_t hi = vshrq_n_u8(quants, 4);
        
        // Convert to float and apply scale
        // ... (expand to float32x4_t, subtract 8, multiply by scale)
    }
}
```

### x86 AVX2

```c
void dequantize_row_q4_0_avx2(const void* src, float* dst, int64_t n) {
    const block_q4_0* blocks = src;
    
    for (int i = 0; i < n/32; i++) {
        __m256 scale = _mm256_set1_ps(ggml_fp16_to_fp32(blocks[i].scale));
        
        // Load and unpack 4-bit values
        __m128i quants = _mm_loadu_si128((__m128i*)blocks[i].quants);
        
        // Expand to 8-bit, then to 32-bit float
        // Apply scale and offset
        // ...
    }
}
```

---

## Type Selection Guide

| Use Case | Recommended Type | Notes |
|----------|------------------|-------|
| Maximum quality | F16, BF16 | 2x memory vs F32 |
| Balanced (7B models) | Q4_K_M | Good quality/size |
| Balanced (13B+ models) | Q5_K_M | Better quality |
| Minimum size | Q2_K | Significant quality loss |
| Fast inference | Q4_0 | Simple dequant |
| High quality | Q6_K, Q8_0 | Near-F16 quality |

---

## Implementation Checklist

For a minimal quantized implementation:

### Required
- [ ] F32 (baseline)
- [ ] F16 (model weights often in F16)
- [ ] Q4_0 or Q4_K (most common quantization)

### Recommended
- [ ] Q8_0 (high quality, simple)
- [ ] Q5_K (good balance)
- [ ] Q6_K (high quality)

### Optional
- [ ] Q2_K, Q3_K (extreme compression)
- [ ] IQ types (importance quantization)
- [ ] BF16 (for specific hardware)
