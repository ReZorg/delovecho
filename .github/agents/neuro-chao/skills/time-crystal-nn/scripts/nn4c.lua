--[[
   nn4c.lua - Time Crystal Neuron Net
   
   A Torch7 nn implementation of the Generalized Neuron Time Crystal model
   from Nanobrain Figure 6.14. This module implements a hierarchical neural
   architecture with 9 temporal scales (8ms to 1s) organized as nested
   oscillatory processing stages.
   
   The [a,b,c,d] notation encodes:
   - a: Number of major spatial domains (dendrite, soma, axon)
   - b: Number of functional layers per domain
   - c: Number of temporal scales per layer
   - d: Number of component types per scale
   
   Default configuration: Neuron [3,4,3,3]
   
   Copyright (c) 2026 Time Crystal Neural Networks
   License: MIT
]]--

require 'nn'

------------------------------------------------------------------------
-- TimeCrystalNeuron: Main container for single neuron time crystal model
------------------------------------------------------------------------

local TimeCrystalNeuron, parent = torch.class('nn.TimeCrystalNeuron', 'nn.Container')

-- Temporal scale periods in seconds (from Nanobrain Fig 6.14)
TimeCrystalNeuron.TEMPORAL_SCALES = {
   [0] = 0.008,   -- Ultra-fast: Protein dynamics (Pr-Ch)
   [1] = 0.026,   -- Fast: Ion channel gating (Io-Ch)
   [2] = 0.052,   -- Medium-fast: Membrane dynamics (Me)
   [3] = 0.110,   -- Medium: Axon initial segment (AIS)
   [4] = 0.160,   -- Medium-slow: Dendritic integration (PNN)
   [5] = 0.250,   -- Slow: Synaptic plasticity (Ca)
   [6] = 0.330,   -- Very-slow: Soma processing (Soma)
   [7] = 0.500,   -- Ultra-slow: Network synchronization (Gl)
   [8] = 1.000,   -- Slowest: Global rhythm (Me-Rh)
}

-- Component abbreviations per temporal scale
TimeCrystalNeuron.SCALE_COMPONENTS = {
   [0] = {'Ax', 'Pr-Ch'},                           -- 8ms
   [1] = {'Io-Ch', 'Li', 'Ax'},                     -- 26ms
   [2] = {'Me', 'Ac', 'Li'},                        -- 52ms
   [3] = {'AIS', 'An-n', 'En-re-Mi', 'P-As', 'An'}, -- 0.11s
   [4] = {'Ch-Co', 'Ac', 'Se-n', 'Br', 'PNN'},      -- 0.16s
   [5] = {'Ca', 'Mu-p', 'Fi-lo', 'Ax-d', 'Ax-s'},   -- 0.25s
   [6] = {'Rh', 'Ep', 'Io', 'Mi-fm', 'Soma'},       -- 0.33s
   [7] = {'Bu', 'Au', 'Gl-S', 'Nt', 'El', 'Gl'},    -- 0.5s
   [8] = {'Me-Rh', 'Fi-lo', 'Bi', 'Bu', 'Sy-c'},    -- 1s
}

function TimeCrystalNeuron:__init(config)
   parent.__init(self)
   
   -- Parse configuration [a,b,c,d]
   config = config or {3, 4, 3, 3}
   self.nDomains = config[1] or 3        -- Spatial domains
   self.nLayers = config[2] or 4         -- Layers per domain
   self.nScales = config[3] or 3         -- Temporal scales per layer
   self.nComponents = config[4] or 3     -- Components per scale
   
   -- Dimension configuration
   self.inputSize = 64                   -- Default input dimension
   self.hiddenSize = 128                 -- Hidden layer dimension
   self.outputSize = 64                  -- Output dimension
   
   -- Phase state for oscillatory dynamics
   self.phase = torch.zeros(9)           -- Phase for each temporal scale
   self.time = 0                         -- Current simulation time
   
   -- Build the hierarchical architecture
   self:_buildArchitecture()
end

function TimeCrystalNeuron:_buildArchitecture()
   -- Main sequential container for temporal hierarchy
   self.temporalHierarchy = nn.Sequential()
   
   -- Level 0: Ultra-fast processing (8ms) - Protein channels
   self.temporalHierarchy:add(self:_createTemporalLevel(0, self.inputSize, self.hiddenSize))
   
   -- Level 1: Fast processing (26ms) - Ion channels
   self.temporalHierarchy:add(self:_createTemporalLevel(1, self.hiddenSize, self.hiddenSize))
   
   -- Level 2: Medium-fast (52ms) - Membrane dynamics
   self.temporalHierarchy:add(self:_createTemporalLevel(2, self.hiddenSize, self.hiddenSize))
   
   -- Level 3: Medium (0.11s) - Axon initial segment
   self.temporalHierarchy:add(self:_createTemporalLevel(3, self.hiddenSize, self.hiddenSize))
   
   -- Level 4: Medium-slow (0.16s) - Dendritic integration
   self.temporalHierarchy:add(self:_createTemporalLevel(4, self.hiddenSize, self.hiddenSize))
   
   -- Level 5: Slow (0.25s) - Synaptic plasticity
   self.temporalHierarchy:add(self:_createTemporalLevel(5, self.hiddenSize, self.hiddenSize))
   
   -- Level 6: Very-slow (0.33s) - Soma processing
   self.temporalHierarchy:add(self:_createTemporalLevel(6, self.hiddenSize, self.hiddenSize))
   
   -- Level 7: Ultra-slow (0.5s) - Network synchronization
   self.temporalHierarchy:add(self:_createTemporalLevel(7, self.hiddenSize, self.hiddenSize))
   
   -- Level 8: Slowest (1s) - Global rhythm
   self.temporalHierarchy:add(self:_createTemporalLevel(8, self.hiddenSize, self.outputSize))
   
   -- Add to modules
   self.modules = {self.temporalHierarchy}
end

-- Create a temporal processing level with oscillatory modulation
function TimeCrystalNeuron:_createTemporalLevel(level, inputDim, outputDim)
   local period = self.TEMPORAL_SCALES[level]
   local components = self.SCALE_COMPONENTS[level]
   
   local levelModule = nn.Sequential()
   
   -- Linear transformation
   levelModule:add(nn.Linear(inputDim, outputDim))
   
   -- Batch normalization for stability
   levelModule:add(nn.BatchNormalization(outputDim))
   
   -- Oscillatory activation (phase-modulated tanh)
   levelModule:add(nn.OscillatoryActivation(outputDim, period, level))
   
   -- Residual connection for feedback (Fi-lo)
   if level > 0 then
      levelModule:add(nn.Dropout(0.1))
   end
   
   return levelModule
end

function TimeCrystalNeuron:updateOutput(input)
   -- Update phase state based on time
   self:_updatePhases()
   
   -- Forward through temporal hierarchy
   self.output = self.temporalHierarchy:forward(input)
   
   return self.output
end

function TimeCrystalNeuron:updateGradInput(input, gradOutput)
   self.gradInput = self.temporalHierarchy:updateGradInput(input, gradOutput)
   return self.gradInput
end

function TimeCrystalNeuron:accGradParameters(input, gradOutput, scale)
   self.temporalHierarchy:accGradParameters(input, gradOutput, scale)
end

function TimeCrystalNeuron:_updatePhases()
   -- Update phases for each temporal scale
   for level = 0, 8 do
      local period = self.TEMPORAL_SCALES[level]
      self.phase[level + 1] = (2 * math.pi * self.time / period) % (2 * math.pi)
   end
end

function TimeCrystalNeuron:step(dt)
   -- Advance simulation time
   dt = dt or 0.001  -- Default 1ms timestep
   self.time = self.time + dt
end

function TimeCrystalNeuron:reset()
   self.time = 0
   self.phase:zero()
   self.temporalHierarchy:reset()
end

function TimeCrystalNeuron:__tostring__()
   local str = 'nn.TimeCrystalNeuron [' .. self.nDomains .. ',' .. 
               self.nLayers .. ',' .. self.nScales .. ',' .. self.nComponents .. ']'
   str = str .. '\n  Temporal Levels: 9 (8ms → 1s)'
   str = str .. '\n  Input: ' .. self.inputSize
   str = str .. '\n  Hidden: ' .. self.hiddenSize
   str = str .. '\n  Output: ' .. self.outputSize
   return str
end

------------------------------------------------------------------------
-- OscillatoryActivation: Phase-modulated activation function
------------------------------------------------------------------------

local OscillatoryActivation, OscParent = torch.class('nn.OscillatoryActivation', 'nn.Module')

function OscillatoryActivation:__init(size, period, level)
   OscParent.__init(self)
   self.size = size
   self.period = period
   self.level = level
   self.phase = 0
   self.time = 0
   
   -- Learnable phase offset
   self.phaseOffset = torch.zeros(size)
   self.gradPhaseOffset = torch.zeros(size)
   
   -- Learnable amplitude
   self.amplitude = torch.ones(size)
   self.gradAmplitude = torch.zeros(size)
end

function OscillatoryActivation:updateOutput(input)
   -- Compute oscillatory modulation
   local phase = (2 * math.pi * self.time / self.period) + self.phaseOffset:view(1, -1):expandAs(input)
   local modulation = self.amplitude:view(1, -1):expandAs(input):cmul(torch.sin(phase))
   
   -- Apply modulated tanh activation
   self.output = torch.tanh(input):cmul(1 + 0.1 * modulation)
   
   return self.output
end

function OscillatoryActivation:updateGradInput(input, gradOutput)
   -- Gradient through tanh
   local tanhOut = torch.tanh(input)
   local dtanh = 1 - torch.pow(tanhOut, 2)
   
   -- Gradient through modulation
   local phase = (2 * math.pi * self.time / self.period) + self.phaseOffset:view(1, -1):expandAs(input)
   local modulation = 1 + 0.1 * self.amplitude:view(1, -1):expandAs(input):cmul(torch.sin(phase))
   
   self.gradInput = gradOutput:cmul(dtanh):cmul(modulation)
   
   return self.gradInput
end

function OscillatoryActivation:parameters()
   return {self.phaseOffset, self.amplitude}, {self.gradPhaseOffset, self.gradAmplitude}
end

function OscillatoryActivation:setTime(t)
   self.time = t
end

------------------------------------------------------------------------
-- TemporalDomain: Spatial domain with multiple functional layers
------------------------------------------------------------------------

local TemporalDomain, TDParent = torch.class('nn.TemporalDomain', 'nn.Container')

function TemporalDomain:__init(name, inputSize, outputSize, nLayers)
   TDParent.__init(self)
   self.name = name
   self.inputSize = inputSize
   self.outputSize = outputSize
   self.nLayers = nLayers or 4
   
   self:_buildLayers()
end

function TemporalDomain:_buildLayers()
   local currentSize = self.inputSize
   local layerSize = math.floor((self.inputSize + self.outputSize) / 2)
   
   for i = 1, self.nLayers do
      local nextSize = (i == self.nLayers) and self.outputSize or layerSize
      
      local layer = nn.Sequential()
      layer:add(nn.Linear(currentSize, nextSize))
      layer:add(nn.BatchNormalization(nextSize))
      layer:add(nn.ReLU())
      
      self:add(layer)
      currentSize = nextSize
   end
end

function TemporalDomain:updateOutput(input)
   local currentOutput = input
   for i = 1, #self.modules do
      currentOutput = self.modules[i]:forward(currentOutput)
   end
   self.output = currentOutput
   return self.output
end

function TemporalDomain:updateGradInput(input, gradOutput)
   local currentGradOutput = gradOutput
   for i = #self.modules, 1, -1 do
      local prevInput = (i == 1) and input or self.modules[i-1].output
      currentGradOutput = self.modules[i]:updateGradInput(prevInput, currentGradOutput)
   end
   self.gradInput = currentGradOutput
   return self.gradInput
end

------------------------------------------------------------------------
-- FeedbackLoop: Implements Fi-lo (feedback loop) mechanism
------------------------------------------------------------------------

local FeedbackLoop, FLParent = torch.class('nn.FeedbackLoop', 'nn.Container')

function FeedbackLoop:__init(mainModule, feedbackModule, alpha)
   FLParent.__init(self)
   self.mainModule = mainModule
   self.feedbackModule = feedbackModule or nn.Identity()
   self.alpha = alpha or 0.1  -- Feedback strength
   
   self.prevOutput = nil
   
   self:add(mainModule)
   self:add(feedbackModule)
end

function FeedbackLoop:updateOutput(input)
   -- Combine input with feedback from previous output
   local combinedInput = input
   if self.prevOutput then
      local feedback = self.feedbackModule:forward(self.prevOutput)
      combinedInput = input + self.alpha * feedback
   end
   
   -- Forward through main module
   self.output = self.mainModule:forward(combinedInput)
   
   -- Store for next iteration
   self.prevOutput = self.output:clone()
   
   return self.output
end

function FeedbackLoop:reset()
   self.prevOutput = nil
   self.mainModule:reset()
   self.feedbackModule:reset()
end

------------------------------------------------------------------------
-- JunctionModule: Implements different junction types (Ax-d, El, GlS)
------------------------------------------------------------------------

local JunctionModule, JMParent = torch.class('nn.JunctionModule', 'nn.Module')

-- Junction types from Nanobrain
JunctionModule.JUNCTION_TYPES = {
   ['Ax-d']    = 'axo_dendrite',      -- Feed-forward
   ['Ax-s']    = 'axo_spino',         -- Skip connection
   ['Ax-Ax-d'] = 'axo_axo_dendrite',  -- Residual pathway
   ['El']      = 'electrical',         -- Gap junction (lateral)
   ['GlS']     = 'glial_synapse',     -- Tripartite synapse (attention)
   ['Sy-c']    = 'synaptic_cleft',    -- Chemical synapse
}

function JunctionModule:__init(junctionType, inputSize, outputSize)
   JMParent.__init(self)
   self.junctionType = junctionType or 'Ax-d'
   self.inputSize = inputSize
   self.outputSize = outputSize
   
   -- Junction-specific parameters
   self.weight = torch.Tensor(outputSize, inputSize)
   self.bias = torch.Tensor(outputSize)
   self.gradWeight = torch.Tensor(outputSize, inputSize)
   self.gradBias = torch.Tensor(outputSize)
   
   -- Synaptic strength (learnable)
   self.synapticStrength = torch.ones(outputSize)
   self.gradSynapticStrength = torch.zeros(outputSize)
   
   self:reset()
end

function JunctionModule:reset(stdv)
   stdv = stdv or 1.0 / math.sqrt(self.inputSize)
   self.weight:uniform(-stdv, stdv)
   self.bias:zero()
   self.synapticStrength:fill(1)
end

function JunctionModule:updateOutput(input)
   -- Linear transformation
   self.output = input * self.weight:t()
   self.output:add(self.bias:view(1, -1):expandAs(self.output))
   
   -- Apply junction-specific modulation
   if self.junctionType == 'El' then
      -- Electrical junction: direct coupling
      self.output = self.output:cmul(self.synapticStrength:view(1, -1):expandAs(self.output))
   elseif self.junctionType == 'GlS' then
      -- Glial synapse: attention-like gating
      local gate = torch.sigmoid(self.output)
      self.output = self.output:cmul(gate)
   end
   
   return self.output
end

function JunctionModule:updateGradInput(input, gradOutput)
   self.gradInput = gradOutput * self.weight
   return self.gradInput
end

function JunctionModule:accGradParameters(input, gradOutput, scale)
   scale = scale or 1
   self.gradWeight:addmm(scale, gradOutput:t(), input)
   self.gradBias:add(scale, gradOutput:sum(1):squeeze())
end

function JunctionModule:parameters()
   return {self.weight, self.bias, self.synapticStrength}, 
          {self.gradWeight, self.gradBias, self.gradSynapticStrength}
end

------------------------------------------------------------------------
-- RhythmModule: Implements Rh (rhythm) oscillatory component
------------------------------------------------------------------------

local RhythmModule, RhParent = torch.class('nn.RhythmModule', 'nn.Module')

function RhythmModule:__init(size, baseFrequency)
   RhParent.__init(self)
   self.size = size
   self.baseFrequency = baseFrequency or 1.0  -- Hz
   self.time = 0
   
   -- Learnable frequency modulation
   self.freqMod = torch.ones(size)
   self.gradFreqMod = torch.zeros(size)
   
   -- Learnable phase
   self.phaseShift = torch.zeros(size)
   self.gradPhaseShift = torch.zeros(size)
end

function RhythmModule:updateOutput(input)
   -- Compute rhythm modulation
   local freq = self.baseFrequency * self.freqMod:view(1, -1):expandAs(input)
   local phase = 2 * math.pi * freq * self.time + self.phaseShift:view(1, -1):expandAs(input)
   local rhythm = torch.sin(phase)
   
   -- Modulate input with rhythm
   self.output = input:cmul(1 + 0.2 * rhythm)
   
   return self.output
end

function RhythmModule:updateGradInput(input, gradOutput)
   local freq = self.baseFrequency * self.freqMod:view(1, -1):expandAs(input)
   local phase = 2 * math.pi * freq * self.time + self.phaseShift:view(1, -1):expandAs(input)
   local rhythm = torch.sin(phase)
   
   self.gradInput = gradOutput:cmul(1 + 0.2 * rhythm)
   return self.gradInput
end

function RhythmModule:setTime(t)
   self.time = t
end

function RhythmModule:parameters()
   return {self.freqMod, self.phaseShift}, {self.gradFreqMod, self.gradPhaseShift}
end

------------------------------------------------------------------------
-- Factory function to create configured TimeCrystalNeuron
------------------------------------------------------------------------

function nn.TimeCrystalNeuron.create(config)
   config = config or {}
   
   local neuron = nn.TimeCrystalNeuron({
      config.nDomains or 3,
      config.nLayers or 4,
      config.nScales or 3,
      config.nComponents or 3
   })
   
   if config.inputSize then neuron.inputSize = config.inputSize end
   if config.hiddenSize then neuron.hiddenSize = config.hiddenSize end
   if config.outputSize then neuron.outputSize = config.outputSize end
   
   -- Rebuild architecture with new dimensions
   neuron:_buildArchitecture()
   
   return neuron
end

------------------------------------------------------------------------
-- Utility: Create criterion for time crystal neuron training
------------------------------------------------------------------------

local TimeCrystalCriterion, TCCParent = torch.class('nn.TimeCrystalCriterion', 'nn.Criterion')

function TimeCrystalCriterion:__init(temporalWeight)
   TCCParent.__init(self)
   self.temporalWeight = temporalWeight or 0.1
   self.mseCriterion = nn.MSECriterion()
   self.temporalCoherence = 0
end

function TimeCrystalCriterion:updateOutput(input, target)
   -- Standard MSE loss
   local mseLoss = self.mseCriterion:forward(input, target)
   
   -- Temporal coherence penalty (encourages smooth temporal dynamics)
   -- This would be computed across time steps in practice
   self.temporalCoherence = 0
   
   self.output = mseLoss + self.temporalWeight * self.temporalCoherence
   return self.output
end

function TimeCrystalCriterion:updateGradInput(input, target)
   self.gradInput = self.mseCriterion:backward(input, target)
   return self.gradInput
end

------------------------------------------------------------------------
-- Return module table for require
------------------------------------------------------------------------

return {
   TimeCrystalNeuron = nn.TimeCrystalNeuron,
   OscillatoryActivation = nn.OscillatoryActivation,
   TemporalDomain = nn.TemporalDomain,
   FeedbackLoop = nn.FeedbackLoop,
   JunctionModule = nn.JunctionModule,
   RhythmModule = nn.RhythmModule,
   TimeCrystalCriterion = nn.TimeCrystalCriterion,
}
