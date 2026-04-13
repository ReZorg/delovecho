#include "ggml-quants.h"
#include <arm_neon.h>
#include <string.h>

// =============================================================================
// Q4_0 Dequantization (NEON)
// =============================================================================

void dequantize_row_q4_0(const block_q4_0* x, float* y, int64_t k) {
    const int nb = k / QK4_0;
    
    for (int i = 0; i < nb; i++) {
        const float d = ggml_fp16_to_fp32(x[i].d);
        const float32x4_t vd = vdupq_n_f32(d);
        
        const uint8x16_t quants = vld1q_u8(x[i].qs);
        
        // Mask for low nibble
        const uint8x16_t m4b = vdupq_n_u8(0x0F);
        const int8x16_t  v8  = vdupq_n_s8(8);
        
        // Extract low and high nibbles
        const uint8x16_t vl = vandq_u8(quants, m4b);
        const uint8x16_t vh = vshrq_n_u8(quants, 4);
        
        // Convert to signed and subtract 8 (symmetric quantization)
        const int8x16_t vl_s = vsubq_s8(vreinterpretq_s8_u8(vl), v8);
        const int8x16_t vh_s = vsubq_s8(vreinterpretq_s8_u8(vh), v8);
        
        // Widen to 16-bit
        const int16x8_t vl_lo = vmovl_s8(vget_low_s8(vl_s));
        const int16x8_t vl_hi = vmovl_s8(vget_high_s8(vl_s));
        const int16x8_t vh_lo = vmovl_s8(vget_low_s8(vh_s));
        const int16x8_t vh_hi = vmovl_s8(vget_high_s8(vh_s));
        
        // Widen to 32-bit and convert to float
        // Low nibble values (first 16 elements)
        vst1q_f32(y + i*32 +  0, vmulq_f32(vd, vcvtq_f32_s32(vmovl_s16(vget_low_s16(vl_lo)))));
        vst1q_f32(y + i*32 +  4, vmulq_f32(vd, vcvtq_f32_s32(vmovl_s16(vget_high_s16(vl_lo)))));
        vst1q_f32(y + i*32 +  8, vmulq_f32(vd, vcvtq_f32_s32(vmovl_s16(vget_low_s16(vl_hi)))));
        vst1q_f32(y + i*32 + 12, vmulq_f32(vd, vcvtq_f32_s32(vmovl_s16(vget_high_s16(vl_hi)))));
        
        // High nibble values (next 16 elements)
        vst1q_f32(y + i*32 + 16, vmulq_f32(vd, vcvtq_f32_s32(vmovl_s16(vget_low_s16(vh_lo)))));
        vst1q_f32(y + i*32 + 20, vmulq_f32(vd, vcvtq_f32_s32(vmovl_s16(vget_high_s16(vh_lo)))));
        vst1q_f32(y + i*32 + 24, vmulq_f32(vd, vcvtq_f32_s32(vmovl_s16(vget_low_s16(vh_hi)))));
        vst1q_f32(y + i*32 + 28, vmulq_f32(vd, vcvtq_f32_s32(vmovl_s16(vget_high_s16(vh_hi)))));
    }
}

// =============================================================================
// Q4_0 × F32 Dot Product (NEON)
// =============================================================================

void ggml_vec_dot_q4_0_f32(int n, float* s, const void* vx, const float* vy) {
    const block_q4_0* x = (const block_q4_0*)vx;
    const int nb = n / QK4_0;
    
    float32x4_t sumv0 = vdupq_n_f32(0.0f);
    float32x4_t sumv1 = vdupq_n_f32(0.0f);
    
    for (int i = 0; i < nb; i++) {
        const float d = ggml_fp16_to_fp32(x[i].d);
        
        const uint8x16_t quants = vld1q_u8(x[i].qs);
        const uint8x16_t m4b = vdupq_n_u8(0x0F);
        const int8x16_t  v8  = vdupq_n_s8(8);
        
        // Extract nibbles and convert to signed
        const int8x16_t vl = vsubq_s8(vreinterpretq_s8_u8(vandq_u8(quants, m4b)), v8);
        const int8x16_t vh = vsubq_s8(vreinterpretq_s8_u8(vshrq_n_u8(quants, 4)), v8);
        
        // Load y values
        const float32x4_t y0 = vld1q_f32(vy + i*32 +  0);
        const float32x4_t y1 = vld1q_f32(vy + i*32 +  4);
        const float32x4_t y2 = vld1q_f32(vy + i*32 +  8);
        const float32x4_t y3 = vld1q_f32(vy + i*32 + 12);
        const float32x4_t y4 = vld1q_f32(vy + i*32 + 16);
        const float32x4_t y5 = vld1q_f32(vy + i*32 + 20);
        const float32x4_t y6 = vld1q_f32(vy + i*32 + 24);
        const float32x4_t y7 = vld1q_f32(vy + i*32 + 28);
        
        // Convert x to float and multiply
        const int16x8_t vl_lo = vmovl_s8(vget_low_s8(vl));
        const int16x8_t vl_hi = vmovl_s8(vget_high_s8(vl));
        const int16x8_t vh_lo = vmovl_s8(vget_low_s8(vh));
        const int16x8_t vh_hi = vmovl_s8(vget_high_s8(vh));
        
        const float32x4_t x0 = vcvtq_f32_s32(vmovl_s16(vget_low_s16(vl_lo)));
        const float32x4_t x1 = vcvtq_f32_s32(vmovl_s16(vget_high_s16(vl_lo)));
        const float32x4_t x2 = vcvtq_f32_s32(vmovl_s16(vget_low_s16(vl_hi)));
        const float32x4_t x3 = vcvtq_f32_s32(vmovl_s16(vget_high_s16(vl_hi)));
        const float32x4_t x4 = vcvtq_f32_s32(vmovl_s16(vget_low_s16(vh_lo)));
        const float32x4_t x5 = vcvtq_f32_s32(vmovl_s16(vget_high_s16(vh_lo)));
        const float32x4_t x6 = vcvtq_f32_s32(vmovl_s16(vget_low_s16(vh_hi)));
        const float32x4_t x7 = vcvtq_f32_s32(vmovl_s16(vget_high_s16(vh_hi)));
        
        // Accumulate x * y
        sumv0 = vfmaq_f32(sumv0, x0, y0);
        sumv1 = vfmaq_f32(sumv1, x1, y1);
        sumv0 = vfmaq_f32(sumv0, x2, y2);
        sumv1 = vfmaq_f32(sumv1, x3, y3);
        sumv0 = vfmaq_f32(sumv0, x4, y4);
        sumv1 = vfmaq_f32(sumv1, x5, y5);
        sumv0 = vfmaq_f32(sumv0, x6, y6);
        sumv1 = vfmaq_f32(sumv1, x7, y7);
        
        // Scale by d
        sumv0 = vmulq_n_f32(sumv0, d);
        sumv1 = vmulq_n_f32(sumv1, d);
    }
    
    // Horizontal sum
    sumv0 = vaddq_f32(sumv0, sumv1);
    *s = vaddvq_f32(sumv0);
}

// =============================================================================
// Q4_K Dequantization (NEON) - Simplified
// =============================================================================

// Helper to extract 6-bit scale from packed scales array
static inline uint8_t get_scale_q4k(const uint8_t* scales, int i) {
    // Scales are packed as 6-bit values
    // This is a simplified extraction
    if (i < 4) {
        return scales[i] & 0x3F;
    } else {
        return ((scales[i-4] >> 6) | ((scales[i] & 0x0F) << 2));
    }
}

void dequantize_row_q4_k(const block_q4_k* x, float* y, int64_t k) {
    const int nb = k / QK4_K;
    
    for (int i = 0; i < nb; i++) {
        const float d = ggml_fp16_to_fp32(x[i].d);
        const float dmin = ggml_fp16_to_fp32(x[i].dmin);
        
        // Process 8 sub-blocks of 32 elements each
        for (int j = 0; j < 8; j++) {
            const uint8_t sc = get_scale_q4k(x[i].scales, j);
            const uint8_t m  = get_scale_q4k(x[i].scales, j + 8);
            
            const float scale = d * sc;
            const float min   = dmin * m;
            
            // Dequantize 32 elements
            for (int l = 0; l < 16; l++) {
                const uint8_t q = x[i].qs[j*16 + l];
                y[i*256 + j*32 + l]      = scale * (q & 0x0F) - min;
                y[i*256 + j*32 + l + 16] = scale * (q >> 4) - min;
            }
        }
    }
}

// =============================================================================
// Q4_K × F32 Dot Product (NEON) - Simplified
// =============================================================================

void ggml_vec_dot_q4_k_f32(int n, float* s, const void* vx, const float* vy) {
    const block_q4_k* x = (const block_q4_k*)vx;
    const int nb = n / QK4_K;
    
    float sum = 0.0f;
    
    for (int i = 0; i < nb; i++) {
        const float d = ggml_fp16_to_fp32(x[i].d);
        const float dmin = ggml_fp16_to_fp32(x[i].dmin);
        
        float32x4_t sumv = vdupq_n_f32(0.0f);
        float smin = 0.0f;
        
        for (int j = 0; j < 8; j++) {
            const uint8_t sc = get_scale_q4k(x[i].scales, j);
            const uint8_t m  = get_scale_q4k(x[i].scales, j + 8);
            
            const float scale = d * sc;
            const float min   = dmin * m;
            
            // Sum y values for min contribution
            float32x4_t ysum = vdupq_n_f32(0.0f);
            for (int l = 0; l < 32; l += 4) {
                ysum = vaddq_f32(ysum, vld1q_f32(vy + i*256 + j*32 + l));
            }
            smin += min * vaddvq_f32(ysum);
            
            // Compute scale * q * y
            for (int l = 0; l < 16; l++) {
                const uint8_t q = x[i].qs[j*16 + l];
                sum += scale * (q & 0x0F) * vy[i*256 + j*32 + l];
                sum += scale * (q >> 4)   * vy[i*256 + j*32 + l + 16];
            }
        }
        
        sum -= smin;
    }
    
    *s = sum;
}

// =============================================================================
// Quantization (for completeness)
// =============================================================================

void quantize_row_q4_0(const float* x, block_q4_0* y, int64_t k) {
    const int nb = k / QK4_0;
    
    for (int i = 0; i < nb; i++) {
        // Find max absolute value
        float amax = 0.0f;
        for (int j = 0; j < QK4_0; j++) {
            float v = fabsf(x[i*QK4_0 + j]);
            if (v > amax) amax = v;
        }
        
        const float d = amax / 7.0f;  // 4-bit range: -8 to 7
        const float id = d ? 1.0f/d : 0.0f;
        
        y[i].d = ggml_fp32_to_fp16(d);
        
        for (int j = 0; j < 16; j++) {
            int q0 = (int)(x[i*QK4_0 + j]      * id + 8.5f);
            int q1 = (int)(x[i*QK4_0 + j + 16] * id + 8.5f);
            
            q0 = q0 < 0 ? 0 : (q0 > 15 ? 15 : q0);
            q1 = q1 < 0 ? 0 : (q1 > 15 ? 15 : q1);
            
            y[i].qs[j] = q0 | (q1 << 4);
        }
    }
}

void quantize_row_q4_k(const float* x, block_q4_k* y, int64_t k) {
    // Simplified Q4_K quantization
    // Full implementation would compute optimal scales per sub-block
    const int nb = k / QK4_K;
    
    for (int i = 0; i < nb; i++) {
        // Find global max for super-block
        float amax = 0.0f;
        float amin = 0.0f;
        for (int j = 0; j < QK4_K; j++) {
            float v = x[i*QK4_K + j];
            if (v > amax) amax = v;
            if (v < amin) amin = v;
        }
        
        const float d = (amax - amin) / 15.0f;
        const float dmin = amin;
        
        y[i].d = ggml_fp32_to_fp16(d);
        y[i].dmin = ggml_fp32_to_fp16(-dmin);
        
        // Set all scales to 1 (simplified)
        memset(y[i].scales, 0x11, 12);
        
        // Quantize
        const float id = d ? 1.0f/d : 0.0f;
        for (int j = 0; j < QK4_K/2; j++) {
            int q0 = (int)((x[i*QK4_K + j*2]     - dmin) * id + 0.5f);
            int q1 = (int)((x[i*QK4_K + j*2 + 1] - dmin) * id + 0.5f);
            
            q0 = q0 < 0 ? 0 : (q0 > 15 ? 15 : q0);
            q1 = q1 < 0 ? 0 : (q1 > 15 ? 15 : q1);
            
            y[i].qs[j] = q0 | (q1 << 4);
        }
    }
}
