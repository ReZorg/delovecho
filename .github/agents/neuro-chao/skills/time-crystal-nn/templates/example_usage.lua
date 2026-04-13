--[[
   Example Usage: Time Crystal Neural Networks
   
   This file demonstrates how to use nn4c (single neuron) and nn9c (whole brain)
   time crystal neural network modules.
]]--

require 'nn'

-- Load time crystal modules
local nn4c = require 'nn4c'
local nn9c = require 'nn9c'

------------------------------------------------------------------------
-- Example 1: Single Neuron Time Crystal (nn4c)
------------------------------------------------------------------------

print('=== Example 1: Time Crystal Neuron (nn4c) ===\n')

-- Create a time crystal neuron with default [3,4,3,3] configuration
local neuron = nn.TimeCrystalNeuron({3, 4, 3, 3})
print(neuron)

-- Create input tensor (batch_size=4, input_size=64)
local input = torch.randn(4, 64)

-- Forward pass
local output = neuron:forward(input)
print('\nInput shape:', input:size())
print('Output shape:', output:size())

-- Simulate temporal dynamics
print('\nSimulating temporal dynamics...')
for t = 1, 10 do
   neuron:step(0.01)  -- 10ms timestep
   output = neuron:forward(input)
   print(string.format('  t=%.3fs, output mean=%.4f', neuron.time, output:mean()))
end

-- Reset for next simulation
neuron:reset()

------------------------------------------------------------------------
-- Example 2: Custom Neuron Configuration
------------------------------------------------------------------------

print('\n=== Example 2: Custom Neuron Configuration ===\n')

-- Create neuron with custom dimensions
local customNeuron = nn.TimeCrystalNeuron.create({
   nDomains = 3,
   nLayers = 4,
   nScales = 3,
   nComponents = 3,
   inputSize = 128,
   hiddenSize = 256,
   outputSize = 128,
})
print(customNeuron)

------------------------------------------------------------------------
-- Example 3: Whole Brain Time Crystal (nn9c)
------------------------------------------------------------------------

print('\n=== Example 3: Time Crystal Brain (nn9c) ===\n')

-- Create a time crystal brain model
local brain = nn.TimeCrystalBrain({
   inputSize = 256,
   hiddenSize = 512,
   outputSize = 256,
   regionSize = 128,
})
print(brain)

-- Create input tensor
local brainInput = torch.randn(2, 256)

-- Forward pass
local brainOutput = brain:forward(brainInput)
print('\nInput shape:', brainInput:size())
print('Output shape:', brainOutput:size())

-- Simulate brain dynamics
print('\nSimulating brain dynamics...')
for t = 1, 5 do
   brain:step(0.1)  -- 100ms timestep
   brainOutput = brain:forward(brainInput)
   print(string.format('  t=%.3fs, output mean=%.4f', brain.time, brainOutput:mean()))
end

------------------------------------------------------------------------
-- Example 4: Training a Time Crystal Neuron
------------------------------------------------------------------------

print('\n=== Example 4: Training Time Crystal Neuron ===\n')

-- Create model and criterion
local model = nn.TimeCrystalNeuron({3, 4, 3, 3})
local criterion = nn.TimeCrystalCriterion(0.1)  -- temporal weight = 0.1

-- Create simple dataset
local dataset = {}
function dataset:size() return 100 end
for i = 1, 100 do
   local x = torch.randn(64)
   local y = torch.tanh(x)  -- Simple target function
   dataset[i] = {x:view(1, -1), y:view(1, -1)}
end

-- Training loop
local learningRate = 0.01
local nEpochs = 10

print('Training for ' .. nEpochs .. ' epochs...')
for epoch = 1, nEpochs do
   local totalLoss = 0
   
   for i = 1, dataset:size() do
      local input, target = dataset[i][1], dataset[i][2]
      
      -- Forward pass
      local output = model:forward(input)
      local loss = criterion:forward(output, target)
      totalLoss = totalLoss + loss
      
      -- Backward pass
      model:zeroGradParameters()
      local gradOutput = criterion:backward(output, target)
      model:backward(input, gradOutput)
      model:updateParameters(learningRate)
      
      -- Advance time for temporal dynamics
      model:step(0.001)
   end
   
   print(string.format('  Epoch %d: avg loss = %.6f', epoch, totalLoss / dataset:size()))
end

------------------------------------------------------------------------
-- Example 5: Using Individual Brain Region Modules
------------------------------------------------------------------------

print('\n=== Example 5: Individual Brain Region Modules ===\n')

-- Hippocampal region with memory trace
local hippocampus = nn.HippocampalRegionModule(64, 'CA1')
local hippoInput = torch.randn(4, 64)

print('Hippocampal CA1 region:')
for t = 1, 5 do
   local hippoOutput = hippocampus:forward(hippoInput)
   print(string.format('  t=%d: memory trace mean=%.4f', t, hippocampus.memoryTrace:mean()))
end

-- Thalamic relay with gating
local thalamus = nn.ThalamicModule(64)
local thalamusInput = torch.randn(4, 64)
local thalamusOutput = thalamus:forward(thalamusInput)
print('\nThalamic relay output shape:', thalamusOutput:size())

-- Hypothalamic homeostatic control
local hypothalamus = nn.HypothalamicModule(64)
local hypoInput = torch.randn(4, 64)
local hypoOutput = hypothalamus:forward(hypoInput)
print('Hypothalamic output shape:', hypoOutput:size())

------------------------------------------------------------------------
-- Example 6: Junction Types
------------------------------------------------------------------------

print('\n=== Example 6: Junction Types ===\n')

local junctionTypes = {'Ax-d', 'El', 'GlS'}
for _, jType in ipairs(junctionTypes) do
   local junction = nn.JunctionModule(jType, 32, 32)
   local jInput = torch.randn(4, 32)
   local jOutput = junction:forward(jInput)
   print(string.format('Junction %s: input→output = %dx%d → %dx%d',
      jType, jInput:size(1), jInput:size(2), jOutput:size(1), jOutput:size(2)))
end

------------------------------------------------------------------------
-- Example 7: Oscillatory Activation Dynamics
------------------------------------------------------------------------

print('\n=== Example 7: Oscillatory Activation Dynamics ===\n')

local oscAct = nn.OscillatoryActivation(32, 0.1, 0)  -- 100ms period
local oscInput = torch.randn(4, 32)

print('Oscillatory activation over time:')
for t = 0, 10 do
   oscAct:setTime(t * 0.01)  -- 10ms steps
   local oscOutput = oscAct:forward(oscInput)
   print(string.format('  t=%.3fs: output range [%.3f, %.3f]',
      t * 0.01, oscOutput:min(), oscOutput:max()))
end

------------------------------------------------------------------------
-- Example 8: Rhythm Module
------------------------------------------------------------------------

print('\n=== Example 8: Rhythm Module ===\n')

local rhythm = nn.RhythmModule(32, 2.0)  -- 2 Hz base frequency
local rhythmInput = torch.randn(4, 32)

print('Rhythm modulation over one cycle:')
for t = 0, 10 do
   rhythm:setTime(t * 0.05)  -- 50ms steps
   local rhythmOutput = rhythm:forward(rhythmInput)
   print(string.format('  t=%.3fs: modulation factor range [%.3f, %.3f]',
      t * 0.05, rhythmOutput:min() / rhythmInput:min(), rhythmOutput:max() / rhythmInput:max()))
end

print('\n=== All examples completed ===')
