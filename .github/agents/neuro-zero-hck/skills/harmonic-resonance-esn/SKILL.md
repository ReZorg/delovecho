---
name: harmonic-resonance-esn
description: Create custom ReservoirPy nodes for frequency-domain Echo State Networks (ESNs). Use when building harmonic oscillator reservoirs, implementing echo-state resonance sensitivity, or modeling cognitive dynamics with the General Relevance architecture.
---

# Harmonic Resonance ESN Skill

This skill provides tools and patterns for creating custom ReservoirPy nodes that operate in the frequency domain, enabling the construction of Echo State Networks (ESNs) based on the principles of the General Relevance architecture.

## Core Concepts

Instead of traditional reservoirs with random recurrent connections, Harmonic Resonance ESNs use a **superposition of harmonic oscillators** as their reservoir. This aligns with the frequency-domain foundation of the General Relevance architecture.

- **Reservoir State**: The state of the reservoir is a vector of phases and amplitudes of a set of harmonic oscillators.
- **Input Coupling**: Input signals modulate the frequency and amplitude of the oscillators.
- **Echo-State Resonance**: The reservoir exhibits echo-state resonance sensitivity, meaning its response is highly dependent on the frequency content of the input signal.
- **Readout**: The readout layer learns to map the harmonic state of the reservoir to the desired output, performing a form of spectral analysis.

## Quick Start

### 1. Generate a Harmonic Node Scaffold

```bash
python /home/ubuntu/skills/harmonic-resonance-esn/scripts/generate_harmonic_node.py <NodeClassName>
```

This will create a new Python file in the current directory with a template for a harmonic oscillator node.

### 2. Implement the Harmonic Dynamics

Fill in the `_step` method of the generated node with the harmonic oscillator update equations. You can use the utilities in `scripts/fourier_utils.py` for spectral operations.

### 3. Integrate into a ReservoirPy Model

```python
from reservoirpy import Reservoir, Ridge
from my_harmonic_node import MyHarmonicNode

# Create a harmonic reservoir
reservoir = MyHarmonicNode(n_oscillators=100, fundamental_freq=0.05)

# Create a readout layer
readout = Ridge(ridge=1e-6)

# Build the ESN model
esn_model = reservoir >> readout

# Train and run the model
esn_model.fit(X_train, y_train)
predictions = esn_model.run(X_test)
```

## Reference Materials

| Task | Reference |
|------|-----------|
| Understanding the theoretical foundation | `/home/ubuntu/general-relevance-spec.md` |
| Mathematical formalism for harmonic metrics | `/home/ubuntu/harmonic-metrics-formalism.md` |
| API for custom harmonic nodes | `references/api_reference.md` |
| Theory of harmonic nodes | `references/harmonic_node_theory.md` |

## Bundled Resources

- **`scripts/generate_harmonic_node.py`**: Generates a template for a custom harmonic oscillator node.
- **`scripts/fourier_utils.py`**: Provides utility functions for Fourier transforms, phase coherence, and other spectral operations.
- **`templates/harmonic_oscillator_node.py.tpl`**: The template used by the generator script.
