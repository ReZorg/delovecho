---
name: harmonic-llm
description: Build minimal LLM inference engines for the frequency domain. Use when creating harmonic oscillator chatbots, implementing the General Relevance architecture, or building models that operate directly on frequency-domain representations.
---

# Harmonic LLM Skill

This skill provides tools to build minimal, efficient LLM inference engines that operate in the frequency domain, based on the principles of the General Relevance architecture.

## Core Concepts

- **Frequency-Domain Inference**: The entire inference process is performed in the frequency domain, avoiding the need for inverse Fourier transforms until the final output stage.
- **Harmonic Vocabulary**: The vocabulary is represented as a set of harmonic modes, with each token corresponding to a specific frequency or combination of frequencies.
- **Phase-Based Attention**: The attention mechanism operates on the phases of the harmonic components, allowing for a more nuanced and efficient form of attention.

## Quick Start

### 1. Generate a Harmonic LLM Scaffold

```bash
python /home/ubuntu/skills/harmonic-llm/scripts/generate_harmonic_llm.py <ModelName>
```

### 2. Implement the Harmonic Layers

Implement the frequency-domain versions of the attention and feed-forward layers, using the harmonic operators from the `harmonic-ggml` skill.

### 3. Train or Fine-Tune in the Frequency Domain

Train the model directly on the spectral representation of the training data.

## Reference Materials

| Task | Reference |
|------|-----------|
| Understanding the theoretical foundation | `/home/ubuntu/general-relevance-spec.md` |
| Mathematical formalism for harmonic metrics | `/home/ubuntu/harmonic-metrics-formalism.md` |
| API for custom harmonic LLM layers | `references/api_reference.md` |
| Theory of frequency-domain LLMs | `references/harmonic_llm_theory.md` |

## Bundled Resources

- **`scripts/generate_harmonic_llm.py`**: Generates a template for a custom harmonic LLM.
- **`scripts/fourier_utils.py`**: Provides utility functions for Fourier transforms and spectral operations.
- **`templates/harmonic_llm.py.tpl`**: The template used by the generator script.
