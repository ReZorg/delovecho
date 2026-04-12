---
name: nn
description: Build and train neural networks with Torch7's nn package. Use when creating MLPs, CNNs, RNNs, or custom layers in Lua/Torch. Covers modules, containers, criterions, transfer functions, convolutions, and training workflows.
---

# Neural Network Skill (Torch nn)

Build and train neural networks using Torch7's modular `nn` package. Networks are composed of **Modules** connected via **Containers**, optimized using **Criterions**.

## Core Concepts

| Concept | Purpose | Key Classes |
|---------|---------|-------------|
| **Module** | Base building block | `nn.Module`, `nn.Linear`, `nn.Tanh` |
| **Container** | Compose modules | `nn.Sequential`, `nn.Parallel`, `nn.Concat` |
| **Criterion** | Loss function | `nn.MSECriterion`, `nn.ClassNLLCriterion` |
| **Transfer** | Non-linearity | `nn.ReLU`, `nn.Sigmoid`, `nn.Tanh` |

## Quick Start

### Build a Multi-Layer Perceptron

```lua
require "nn"

mlp = nn.Sequential()
mlp:add(nn.Linear(10, 25))   -- 10 inputs → 25 hidden
mlp:add(nn.Tanh())           -- activation
mlp:add(nn.Linear(25, 1))    -- 25 hidden → 1 output

output = mlp:forward(torch.randn(10))
```

### Train on XOR Problem

```lua
require "nn"

-- Build network
mlp = nn.Sequential()
mlp:add(nn.Linear(2, 20))
mlp:add(nn.Tanh())
mlp:add(nn.Linear(20, 1))

criterion = nn.MSECriterion()

-- Training loop
for i = 1, 2500 do
  local input = torch.randn(2)
  local target = torch.Tensor(1)
  target[1] = (input[1] * input[2] > 0) and -1 or 1
  
  -- Forward pass
  local pred = mlp:forward(input)
  local loss = criterion:forward(pred, target)
  
  -- Backward pass
  mlp:zeroGradParameters()
  local gradCriterion = criterion:backward(pred, target)
  mlp:backward(input, gradCriterion)
  mlp:updateParameters(0.01)
end
```

### Using StochasticGradient

```lua
-- Create dataset
dataset = {}
function dataset:size() return 100 end
for i = 1, 100 do
  local input = torch.randn(2)
  local output = torch.Tensor(1)
  output[1] = (input[1] * input[2] > 0) and -1 or 1
  dataset[i] = {input, output}
end

-- Train
trainer = nn.StochasticGradient(mlp, criterion)
trainer.learningRate = 0.01
trainer:train(dataset)
```

## Module API

Every module implements these core methods:

| Method | Description |
|--------|-------------|
| `forward(input)` | Compute output from input |
| `backward(input, gradOutput)` | Compute gradients |
| `zeroGradParameters()` | Zero accumulated gradients |
| `updateParameters(lr)` | Update weights with learning rate |
| `parameters()` | Return `{weights}, {gradWeights}` |
| `getParameters()` | Return flattened params and grads |

**State variables:**
- `module.output` — result of last `forward()`
- `module.gradInput` — result of last `backward()`

## Containers

### Sequential — Feed-forward chain

```lua
mlp = nn.Sequential()
mlp:add(nn.Linear(10, 25))
mlp:add(nn.ReLU())
mlp:add(nn.Linear(25, 1))
```

### Parallel — Split input by dimension

```lua
mlp = nn.Parallel(2, 1)  -- split on dim 2, concat on dim 1
mlp:add(nn.Linear(10, 3))
mlp:add(nn.Linear(10, 2))
-- Input: 10x2 → Output: 5
```

### Concat — Same input, concat outputs

```lua
mlp = nn.Concat(1)
mlp:add(nn.Linear(5, 3))
mlp:add(nn.Linear(5, 7))
-- Input: 5 → Output: 10
```

## Transfer Functions

| Function | Formula | Use Case |
|----------|---------|----------|
| `nn.ReLU()` | `max(0, x)` | Default hidden layer |
| `nn.Tanh()` | `tanh(x)` | Bounded output [-1, 1] |
| `nn.Sigmoid()` | `1/(1+exp(-x))` | Binary classification |
| `nn.LogSoftMax()` | `log(softmax(x))` | Multi-class with NLL |
| `nn.SoftMax()` | `exp(x)/sum(exp(x))` | Probability output |
| `nn.LeakyReLU(k)` | `max(kx, x)` | Avoid dead neurons |
| `nn.ELU(α)` | `x if x>0 else α(exp(x)-1)` | Smooth ReLU variant |

## Criterions (Loss Functions)

### Classification

```lua
-- Multi-class (use with LogSoftMax)
criterion = nn.ClassNLLCriterion()

-- Binary cross-entropy (use with Sigmoid)
criterion = nn.BCECriterion()

-- Combined LogSoftMax + NLL
criterion = nn.CrossEntropyCriterion()
```

### Regression

```lua
-- Mean Squared Error
criterion = nn.MSECriterion()

-- Mean Absolute Error
criterion = nn.AbsCriterion()

-- Smooth L1 (Huber loss)
criterion = nn.SmoothL1Criterion()
```

## Convolution Layers

### Temporal (1D sequences)

```lua
-- 1D convolution: inputFrameSize → outputFrameSize
conv = nn.TemporalConvolution(inputSize, outputSize, kernelWidth, [stride])
pool = nn.TemporalMaxPooling(kernelWidth, [stride])
```

### Spatial (2D images)

```lua
-- 2D convolution: nInputPlane → nOutputPlane
conv = nn.SpatialConvolution(nIn, nOut, kW, kH, [dW], [dH], [padW], [padH])
pool = nn.SpatialMaxPooling(kW, kH, [dW], [dH], [padW], [padH])
bn = nn.SpatialBatchNormalization(nFeatures)
```

### Volumetric (3D video/volume)

```lua
conv = nn.VolumetricConvolution(nIn, nOut, kT, kW, kH)
pool = nn.VolumetricMaxPooling(kT, kW, kH)
```

## Table Layers

For multi-input/output architectures:

```lua
-- Split tensor into table
split = nn.SplitTable(dim)

-- Join table into tensor
join = nn.JoinTable(dim)

-- Apply same module to each table element
map = nn.MapTable(module)

-- Apply different modules to table elements
parallel = nn.ParallelTable()
parallel:add(module1)
parallel:add(module2)
```

## Common Patterns

### CNN for Image Classification

```lua
cnn = nn.Sequential()
-- Conv block 1
cnn:add(nn.SpatialConvolution(3, 32, 3, 3, 1, 1, 1, 1))
cnn:add(nn.SpatialBatchNormalization(32))
cnn:add(nn.ReLU())
cnn:add(nn.SpatialMaxPooling(2, 2, 2, 2))
-- Conv block 2
cnn:add(nn.SpatialConvolution(32, 64, 3, 3, 1, 1, 1, 1))
cnn:add(nn.SpatialBatchNormalization(64))
cnn:add(nn.ReLU())
cnn:add(nn.SpatialMaxPooling(2, 2, 2, 2))
-- Classifier
cnn:add(nn.View(64 * 7 * 7))
cnn:add(nn.Linear(64 * 7 * 7, 128))
cnn:add(nn.ReLU())
cnn:add(nn.Dropout(0.5))
cnn:add(nn.Linear(128, 10))
cnn:add(nn.LogSoftMax())
```

### Weight Sharing

```lua
-- Share weights between modules
linear = nn.Linear(100, 10)
linear_clone = linear:clone('weight', 'bias')

-- For optim (share gradients too)
linear_clone = linear:clone('weight', 'bias', 'gradWeight', 'gradBias')
```

### GPU Acceleration

```lua
require 'cunn'
model:cuda()
criterion:cuda()
input = input:cuda()
target = target:cuda()
```

## Testing Custom Modules

Use `nn.Jacobian` to verify gradients:

```lua
local precision = 1e-5
local jac = nn.Jacobian

-- Test gradient w.r.t. input
local err = jac.testJacobian(module, input)
assert(err < precision, 'gradient error: ' .. err)

-- Test gradient w.r.t. parameters
local err = jac.testJacobianParameters(module, input, 
  module.weight, module.gradWeight)
assert(err < precision, 'weight gradient error: ' .. err)
```

## Reference Documentation

For detailed API documentation, see:

| Topic | Reference File |
|-------|----------------|
| Module base class | `references/module.md` |
| Container classes | `references/containers.md` |
| Transfer functions | `references/transfer.md` |
| Simple layers | `references/simple.md` |
| Convolution layers | `references/convolution.md` |
| Table layers | `references/table.md` |
| Loss functions | `references/criterion.md` |
| Training guide | `references/training.md` |
| Testing modules | `references/testing.md` |
| Full overview | `references/overview.md` |

## Template Files

Lua module implementations are available in `template/` for reference or as starting points for custom modules. Key files:

- `template/Linear.lua` — Linear transformation
- `template/Sequential.lua` — Sequential container
- `template/SpatialConvolution.lua` — 2D convolution
- `template/ReLU.lua` — ReLU activation
- `template/MSECriterion.lua` — MSE loss
