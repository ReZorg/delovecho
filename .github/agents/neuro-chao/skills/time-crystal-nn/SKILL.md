---
name: time-crystal-nn
description: Build time crystal neural networks with Torch7 nn modules. Use for implementing hierarchical oscillatory architectures based on Nanobrain time crystal models - nn4c for single neuron (9 temporal scales, 8ms-1s) and nn9c for whole brain (12 hierarchy levels, microtubule to vascular). Supports phase-coupled dynamics, feedback loops, and biologically-inspired junction types.
---

# Time Crystal Neural Networks (nn4c & nn9c)

Torch7 nn implementations of time crystal neural architectures from Nanobrain, providing hierarchical oscillatory processing at neuron and brain scales.

## Modules

| Module | Description | Levels | Period Range |
|--------|-------------|--------|--------------|
| **nn4c** | Single neuron time crystal | 9 temporal scales | 8ms → 1s |
| **nn9c** | Whole brain time crystal | 12 hierarchy levels | 1ms → 1.5s |

## Quick Start

### nn4c: Time Crystal Neuron

```lua
require 'nn'
local nn4c = require 'nn4c'

-- Create neuron with [3,4,3,3] configuration
local neuron = nn.TimeCrystalNeuron({3, 4, 3, 3})

-- Forward pass
local input = torch.randn(batch, 64)
local output = neuron:forward(input)

-- Advance time for oscillatory dynamics
neuron:step(0.001)  -- 1ms timestep
```

### nn9c: Time Crystal Brain

```lua
require 'nn'
local nn9c = require 'nn9c'

-- Create brain model
local brain = nn.TimeCrystalBrain({
   inputSize = 256,
   hiddenSize = 512,
   outputSize = 256,
})

-- Forward pass
local input = torch.randn(batch, 256)
local output = brain:forward(input)

-- Advance time
brain:step(0.01)  -- 10ms timestep
```

## nn4c Architecture

Nine temporal processing levels based on Nanobrain Fig 6.14:

| Level | Period | Components | Function |
|-------|--------|------------|----------|
| 0 | 8ms | Ax, Pr-Ch | Protein dynamics |
| 1 | 26ms | Io-Ch, Li | Ion channel gating |
| 2 | 52ms | Me, Ac | Membrane dynamics |
| 3 | 0.11s | AIS, An-n | Axon initial segment |
| 4 | 0.16s | Ch-Co, PNN | Dendritic integration |
| 5 | 0.25s | Ca, Fi-lo | Synaptic plasticity |
| 6 | 0.33s | Rh, Soma | Soma processing |
| 7 | 0.5s | Gl-S, El | Network sync |
| 8 | 1s | Me-Rh, Sy-c | Global rhythm |

### Key nn4c Modules

```lua
-- Oscillatory activation with phase modulation
nn.OscillatoryActivation(size, period, level)

-- Feedback loop (Fi-lo mechanism)
nn.FeedbackLoop(mainModule, feedbackModule, alpha)

-- Junction types (Ax-d, El, GlS)
nn.JunctionModule(junctionType, inputSize, outputSize)

-- Rhythm modulation
nn.RhythmModule(size, baseFrequency)
```

## nn9c Architecture

Twelve hierarchy levels based on Nanobrain Fig 7.15:

| Level | Name | Scale | Key Modules |
|-------|------|-------|-------------|
| 1 | Microtubule | Molecular | `MicrotubuleModule` |
| 2 | Neuron | Cellular | `TimeCrystalNeuron` |
| 3 | CorticalBranch | Columnar | `CorticalLayerModule` |
| 4 | CortexDomain | Regional | `LobeModule` |
| 5 | Cerebellum | Organ | `CerebellarLobeModule` |
| 6 | Hypothalamus | Nuclear | `HypothalamicModule` |
| 7 | Hippocampus | Nuclear | `HippocampalRegionModule` |
| 8 | ThalamicBody | Relay | `ThalamicModule` |
| 9 | SkinNerveNet | Peripheral | `PeripheralNerveModule` |
| 10 | CranialNerve | Peripheral | `CranialNerveModule` |
| 11 | ThoracicNerve | Spinal | `SpinalNerveModule` |
| 12 | BloodVessel | Vascular | `VascularModule` |

### Brain Regions

```lua
-- Hippocampus with memory trace
nn.HippocampalRegionModule(size, 'CA1')

-- Thalamus with reticular gating
nn.ThalamicModule(size)

-- Hypothalamus with homeostatic feedback
nn.HypothalamicModule(size)

-- Cerebellum with inhibitory gating
nn.CerebellarLobeModule(size, 'Mid')
```

## Training

```lua
-- Create criterion with temporal coherence
local criterion = nn.TimeCrystalCriterion(temporalWeight)

-- Training loop
for epoch = 1, nEpochs do
   for i, sample in ipairs(dataset) do
      local output = model:forward(sample.input)
      local loss = criterion:forward(output, sample.target)
      
      model:zeroGradParameters()
      local gradOutput = criterion:backward(output, sample.target)
      model:backward(sample.input, gradOutput)
      model:updateParameters(learningRate)
      
      model:step(dt)  -- Advance time
   end
end
```

## Configuration

### nn4c [a,b,c,d] Notation

- **a**: Spatial domains (dendrite, soma, axon)
- **b**: Functional layers per domain
- **c**: Temporal scales per layer
- **d**: Component types per scale

Default: `[3,4,3,3]`

### nn9c Configuration

```lua
nn.TimeCrystalBrain({
   inputSize = 256,    -- Input dimension
   hiddenSize = 512,   -- Hidden dimension
   outputSize = 256,   -- Output dimension
   regionSize = 128,   -- Per-region dimension
})
```

## Reference Materials

- `references/architecture.md` — Detailed architecture documentation
- `templates/example_usage.lua` — Complete usage examples

## Scripts

| File | Description |
|------|-------------|
| `scripts/nn4c.lua` | Single neuron time crystal implementation |
| `scripts/nn9c.lua` | Whole brain time crystal implementation |
