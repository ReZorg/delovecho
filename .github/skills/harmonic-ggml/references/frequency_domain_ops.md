# Theory of Frequency-Domain Operators

## Introduction

In the Harmonic GGML framework, tensor operations are redefined to operate on signals in the frequency domain. This document outlines the theoretical basis for these operations.

## Convolution Theorem

The most important principle is the **Convolution Theorem**, which states that element-wise multiplication in the frequency domain is equivalent to convolution in the time domain:

> `F{f * g} = F{f} ⋅ F{g}`

This means that the `mul_mat` operation in a traditional GGML graph can be replaced by an element-wise product in the frequency domain, which is computationally much more efficient.

## Harmonic Operations

- **`mul_mat`**: Becomes element-wise product of complex-valued tensors.
- **`add`**: Remains element-wise addition.
- **`rope`**: Becomes a phase shift operation.
- **`softmax`**: Becomes a spectral normalization operation.

## Continued-Fraction Quantization

Instead of quantizing to a fixed number of bits, we represent numbers as **continued fractions**. This provides an exact, rational representation that can be truncated to any desired precision. This avoids the loss of information associated with floating-point arithmetic and fixed-point quantization.
