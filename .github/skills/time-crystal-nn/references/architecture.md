# Time Crystal Neural Network Architecture Reference

This document describes the architectural foundations of the Time Crystal Neural Network modules (nn4c and nn9c), mapping biological time crystal concepts from Nanobrain to Torch7 nn implementations.

## Theoretical Foundation

### Time Crystal Concept

A **time crystal** is a phase of matter exhibiting periodic structure in time, analogous to spatial periodicity in ordinary crystals. In neural modeling, time crystals represent systems where:

1. **Nested Oscillations**: Components oscillate at characteristic frequencies that nest hierarchically
2. **Phase Coupling**: Different temporal scales maintain stable phase relationships
3. **Fractal Structure**: Self-similar patterns repeat across scales
4. **Deterministic Dynamics**: State transitions follow predictable cyclic patterns

### Mapping to Neural Networks

| Time Crystal Concept | nn Implementation |
|---------------------|-------------------|
| Temporal Hierarchy | `nn.Sequential` with levels |
| Parallel Oscillators | `nn.Concat` branches |
| Phase Coupling | Shared phase state |
| Feedback Loops (Fi-lo) | `nn.FeedbackLoop` module |
| Junction Types | `nn.JunctionModule` variants |
| Rhythm (Rh) | `nn.RhythmModule` |

## nn4c: Single Neuron Architecture

### Temporal Scales (9 Levels)

| Level | Period | Components | nn Module |
|-------|--------|------------|-----------|
| 0 | 8ms | Ax, Pr-Ch | `OscillatoryActivation` |
| 1 | 26ms | Io-Ch, Li, Ax | `OscillatoryActivation` |
| 2 | 52ms | Me, Ac, Li | `OscillatoryActivation` |
| 3 | 0.11s | AIS, An-n, En-re-Mi | `OscillatoryActivation` |
| 4 | 0.16s | Ch-Co, Ac, Se-n, PNN | `OscillatoryActivation` |
| 5 | 0.25s | Ca, Mu-p, Fi-lo, Ax-d | `OscillatoryActivation` |
| 6 | 0.33s | Rh, Ep, Io, Soma | `OscillatoryActivation` |
| 7 | 0.5s | Bu, Au, Gl-S, Nt, El | `OscillatoryActivation` |
| 8 | 1s | Me-Rh, Fi-lo, Bi, Sy-c | `OscillatoryActivation` |

### [a,b,c,d] Notation

The bracket notation encodes hierarchical structure:

- **a**: Number of major spatial domains (dendrite, soma, axon)
- **b**: Number of functional layers per domain
- **c**: Number of temporal scales per layer
- **d**: Number of component types per scale

Default: `[3,4,3,3]`

### Key Modules

#### TimeCrystalNeuron

Main container implementing the 9-level temporal hierarchy.

```lua
local neuron = nn.TimeCrystalNeuron({3, 4, 3, 3})
neuron.inputSize = 64
neuron.hiddenSize = 128
neuron.outputSize = 64
```

#### OscillatoryActivation

Phase-modulated activation function with learnable phase offset and amplitude.

```lua
local osc = nn.OscillatoryActivation(size, period, level)
```

#### FeedbackLoop

Implements Fi-lo (feedback loop) mechanism with configurable feedback strength.

```lua
local fb = nn.FeedbackLoop(mainModule, feedbackModule, alpha)
```

#### JunctionModule

Implements different junction types (Ax-d, El, GlS, etc.) with junction-specific modulation.

```lua
local junc = nn.JunctionModule('Ax-d', inputSize, outputSize)
```

## nn9c: Whole Brain Architecture

### Hierarchy Levels (12 Levels)

| Level | Name | Scale | Period | Key Components |
|-------|------|-------|--------|----------------|
| 1 | Microtubule | Molecular | 1ms | Tubulin, H₂O channels |
| 2 | Neuron | Cellular | 8ms | TimeCrystalNeuron (nn4c) |
| 3 | CorticalBranch | Columnar | 26ms | 6-layer cortex |
| 4 | CortexDomain | Regional | 52ms | Lobes (A-D) |
| 5 | Cerebellum | Organ | 110ms | Mid, Left, Right lobes |
| 6 | Hypothalamus | Nuclear | 160ms | Homeostatic nuclei |
| 7 | Hippocampus | Nuclear | 250ms | CA1-4, DG |
| 8 | ThalamicBody | Relay | 330ms | Sensory relay nuclei |
| 9 | SkinNerveNet | Peripheral | 500ms | Nerve branches |
| 10 | CranialNerve | Peripheral | 750ms | 12 cranial nerves |
| 11 | ThoracicNerve | Spinal | 1s | Motor/sensory rootlets |
| 12 | BloodVessel | Vascular | 1.5s | Cerebral arteries |

### Brain Regions

#### Cortex (Level 4)

Four major lobes processed in parallel:

- **Occipital**: Visual processing
- **Frontal**: Executive function
- **Temporal**: Auditory, memory
- **Parietal**: Sensory integration

#### Cerebellum (Level 5)

Three lobes with inhibitory gating:

- **Mid**: Central vermis
- **Left**: Left hemisphere
- **Right**: Right hemisphere

#### Hypothalamus (Level 6)

Homeostatic control with setpoint-based feedback:

- Arcuate, Supraoptic, Paraventricular, Preoptic nuclei
- Functions: HR, BP, Temperature, Feeding, Sleep

#### Hippocampus (Level 7)

Memory processing with trace decay:

- CA1, CA2, CA3, CA4, Dentate Gyrus
- Functions: Spatial memory, Temporal encoding, Consolidation

#### Thalamus (Level 8)

Sensory relay with reticular gating:

- VM, SC, Anterior, Posterior, Medial, Lateral nuclei
- Functions: Sensory relay, Motor relay, Arousal

### Functional Subsystems

| Subsystem | Components | Function |
|-----------|------------|----------|
| Proprioception | SpinalCord, Thalamus, Cerebellum | Body position sense |
| Homeostatic | Feedback, BrainStem, Thyroid | Internal regulation |
| Emotion/Personality | Insula, Cingulate, Striatum, ACC | Affective processing |
| Entorhinal | MEC, LEC, Perirhinal | Spatial/memory interface |

### Cranial Nerves (Level 10)

| # | Abbrev | Name | Function |
|---|--------|------|----------|
| I | Olf | Olfactory | Smell |
| II | Opt | Optic | Vision |
| III | Ocm | Oculomotor | Eye movement |
| IV | Tro | Trochlear | Eye movement |
| V | Tri | Trigeminal | Face sensation |
| VI | Abd | Abducens | Eye movement |
| VII | Fac | Facial | Face movement |
| VIII | Ves | Vestibulocochlear | Hearing, balance |
| IX | Glo | Glossopharyngeal | Taste, swallow |
| X | Vag | Vagus | Autonomic |
| XI | Acc | Accessory | Neck movement |
| XII | Hyp | Hypoglossal | Tongue movement |

## sys-n Framework Mapping

The time crystal models map to the sys-n state transition framework:

| sys-n Concept | Time Crystal Equivalent |
|---------------|------------------------|
| Universal Sets (U) | Slow oscillators (0.5s-1s) |
| Particular Sets (P) | Fast oscillators (8ms-0.33s) |
| Cycle Length | LCM of component periods |
| State Labels | Component abbreviations |

## Training Considerations

### Temporal Coherence

The `TimeCrystalCriterion` and `TimeCrystalBrainCriterion` include optional temporal coherence penalties to encourage smooth dynamics across time steps.

### Phase Synchronization

Call `model:step(dt)` to advance simulation time and update phase states before each forward pass for proper oscillatory dynamics.

### Memory Management

For long sequences, periodically call `model:reset()` to clear memory traces and phase states.
