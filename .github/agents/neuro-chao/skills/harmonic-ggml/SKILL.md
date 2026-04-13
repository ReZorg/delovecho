---
name: harmonic-ggml
description: Build minimal GGML tensor libraries for the frequency domain. Use when implementing harmonic tensor operations, continuous-fraction quantization, or building inference engines for the General Relevance architecture.
---

# Harmonic GGML Skill

This skill provides tools to build minimal, efficient GGML implementations that operate in the frequency domain, aligning with the principles of the General Relevance architecture.

## Core Concepts

- **Frequency-Domain Tensors**: Tensors represent signals in the frequency domain, storing complex values (amplitudes and phases) of harmonic components.
- **Harmonic Operations**: Standard tensor operations (e.g., `mul_mat`) are redefined as harmonic operations (e.g., convolution, cross-correlation).
- **Continuous-Fraction Quantization**: Numbers are represented as continued fractions, providing an exact, rational representation that avoids floating-point errors.

## Quick Start

### 1. Generate a Harmonic Operator Scaffold

```bash
python /home/ubuntu/skills/harmonic-ggml/scripts/generate_harmonic_ops.py <OperatorName>
```

### 2. Implement the Harmonic Operation

Implement the frequency-domain logic for the operator. Use the utilities in `scripts/fourier_utils.py`.

### 3. Integrate into a GGML Graph

Use the custom harmonic operators to build a GGML computation graph for frequency-domain inference.

## Reference Materials

| Task | Reference |
|------|-----------|
| Understanding the theoretical foundation | `/home/ubuntu/general-relevance-spec.md` |
| Mathematical formalism for harmonic metrics | `/home/ubuntu/harmonic-metrics-formalism.md` |
| API for custom harmonic operators | `references/api_reference.md` |
| Theory of frequency-domain operators | `references/frequency_domain_ops.md` |

## Bundled Resources

- **`scripts/generate_harmonic_ops.py`**: Generates a template for a custom harmonic tensor operator.
- **`scripts/fourier_utils.py`**: Provides utility functions for Fourier transforms and spectral operations.
- **`scripts/continued_fractions.py`**: Provides utilities for encoding and decoding continued fractions.
- **`templates/harmonic_operator.c.tpl`**: The template used by the generator script.
