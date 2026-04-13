# Theory of Harmonic LLMs

## Introduction

Harmonic LLMs are a new class of language models that operate directly in the frequency domain. This approach offers several advantages over traditional time-domain models, including computational efficiency, improved handling of long-range dependencies, and a more natural representation of the periodic structures found in language.

## Frequency-Domain Inference

The core idea of harmonic LLMs is to perform the entire inference process in the frequency domain. This is achieved by applying the Fourier transform to the input embeddings and then performing all subsequent operations (attention, feed-forward layers) on the complex-valued spectral representation.

## Phase-Based Attention

Instead of the standard dot-product attention, harmonic LLMs use a **phase-based attention** mechanism. This operates on the phases of the harmonic components, allowing the model to attend to tokens based on their spectral relationships rather than their absolute positions.

## Harmonic Vocabulary

The vocabulary of a harmonic LLM is represented as a set of harmonic modes. Each token is associated with a specific frequency or a combination of frequencies. This allows the model to learn a more continuous and compositional representation of language.
