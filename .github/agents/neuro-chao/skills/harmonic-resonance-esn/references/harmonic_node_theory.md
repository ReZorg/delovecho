# Theory of Harmonic Nodes

## Introduction

Harmonic nodes are a class of ReservoirPy nodes that use a set of coupled harmonic oscillators as their internal state. They are designed to be particularly sensitive to the frequency content of input signals, making them well-suited for tasks involving time-series analysis, signal processing, and modeling of dynamic systems.

## Mathematical Formulation

The state of a harmonic node is defined by the amplitudes and phases of `N` oscillators. The update equations for each oscillator `i` are:

- **Phase update**: `θᵢ(t+1) = θᵢ(t) + 2πωᵢ + f(x(t))`
- **Amplitude update**: `Aᵢ(t+1) = g(Aᵢ(t), x(t))`

Where:
- `θᵢ` is the phase of oscillator `i`
- `Aᵢ` is the amplitude of oscillator `i`
- `ωᵢ` is the natural frequency of oscillator `i`
- `x(t)` is the input signal at time `t`
- `f` is the input coupling function
- `g` is the amplitude dynamics function

## Echo-State Resonance

A key property of harmonic nodes is **echo-state resonance**. This means that the response of the reservoir is maximized when the input signal frequency matches one of the natural frequencies of the oscillators. This allows the reservoir to act as a bank of band-pass filters, effectively performing a spectral analysis of the input signal.

## Readout Layer

The readout layer of a harmonic ESN learns to map the harmonic state of the reservoir to the desired output. This is typically done using a linear regression model, such as `Ridge`, which learns a set of weights to combine the oscillator states.
