# Analogy Patterns Reference

Domain-to-architecture mappings for topology generation. Use these patterns to map concepts from source contexts to neural network components.

## Table of Contents

1. [Quantum Field Theory Analogies](#quantum-field-theory-analogies)
2. [Biological Analogies](#biological-analogies)
3. [Information Theory Analogies](#information-theory-analogies)
4. [Graph Theory Analogies](#graph-theory-analogies)
5. [Custom Mapping Guidelines](#custom-mapping-guidelines)

## Quantum Field Theory Analogies

The default mapping for wave-particle duality frameworks:

| QFT Concept | Neural Component | Tag | Rationale |
|-------------|------------------|-----|-----------|
| Particle | Neuron/Unit | `discrete_feature` | Localized, countable, has definite position |
| Wave | Activation Pattern | `distributed_field` | Spread across space, interference-capable |
| Field | Weight Matrix | `coupling_field` | Mediates interactions between particles |
| Propagator | Linear Layer | `field_evolution` | Describes how fields evolve |
| Vertex | Nonlinearity | `interaction_vertex` | Where particles interact/transform |
| Measurement | Softmax/Argmax | `collapse_operator` | Collapses superposition to definite state |
| Superposition | Hidden State | `superposed_state` | Multiple states simultaneously |
| Entanglement | Attention | `entanglement_link` | Non-local correlations |
| Vacuum | Bias Term | `vacuum_energy` | Background energy/offset |
| Renormalization | LayerNorm | `renormalization` | Scale adjustment |

### Wave-Particle Duality in Transformers

```
Attention (Wave-like):
  - Distributed across sequence
  - Interference patterns in attention weights
  - Superposition of value vectors

MLP (Particle-like):
  - Position-local processing
  - Discrete feature detection
  - Definite activation values
```

## Biological Analogies

For neuroscience-inspired architectures:

| Bio Concept | Neural Component | Tag | Rationale |
|-------------|------------------|-----|-----------|
| Neuron | Unit | `neural_unit` | Basic computational element |
| Synapse | Weight | `synaptic_weight` | Connection strength |
| Dendrite | Input Aggregation | `dendritic_input` | Collects inputs |
| Axon | Output Projection | `axonal_output` | Sends signal forward |
| Spike | Activation | `spike_event` | Binary/threshold event |
| Plasticity | Learning | `plastic_weight` | Modifiable connection |
| Inhibition | Negative Weight | `inhibitory_link` | Suppressive connection |
| Excitation | Positive Weight | `excitatory_link` | Activating connection |

## Information Theory Analogies

For compression/coding frameworks:

| Info Concept | Neural Component | Tag | Rationale |
|--------------|------------------|-----|-----------|
| Encoder | First Projection | `encoding_stage` | Compress/transform input |
| Decoder | Second Projection | `decoding_stage` | Reconstruct/expand |
| Channel | Hidden Layer | `channel_capacity` | Information bottleneck |
| Noise | Dropout | `noise_injection` | Regularization |
| Entropy | Softmax Output | `entropy_measure` | Uncertainty distribution |
| Mutual Info | Attention Score | `mutual_information` | Shared information |

## Graph Theory Analogies

For graph neural network contexts:

| Graph Concept | Neural Component | Tag | Rationale |
|---------------|------------------|-----|-----------|
| Node | Token/Position | `graph_node` | Entity in graph |
| Edge | Attention Weight | `graph_edge` | Connection between nodes |
| Message | Value Vector | `message_content` | Information passed |
| Aggregation | Attention Sum | `message_aggregate` | Combine messages |
| Update | MLP | `node_update` | Transform node state |
| Neighborhood | Attention Window | `local_neighborhood` | Connected nodes |

## Custom Mapping Guidelines

When creating custom mappings from a new domain:

### Step 1: Identify Structural Analogies

Look for concepts that share structural properties:

```
Source Domain          Neural Architecture
─────────────          ───────────────────
Discrete entities  →   Neurons/Units
Continuous fields  →   Activation patterns
Transformations    →   Linear layers
Interactions       →   Nonlinearities
Flow/Propagation   →   Forward pass
Composition        →   Layer stacking
```

### Step 2: Map Dynamics

Match temporal/causal relationships:

```
Source: A causes B     →   Layer A feeds Layer B
Source: A and B merge  →   Concatenation or addition
Source: A modulates B  →   Gating mechanism
Source: A selects B    →   Attention mechanism
```

### Step 3: Preserve Invariants

Ensure mappings preserve key properties:

- **Locality**: Local operations → position-wise layers
- **Globality**: Global operations → attention layers
- **Hierarchy**: Nested structures → layer depth
- **Symmetry**: Symmetric relations → weight sharing

### Step 4: Name Tags Meaningfully

Tag naming conventions:

```
<domain>_<operation>    e.g., particle_creation
<property>_<component>  e.g., discrete_feature
<action>_<target>       e.g., collapse_state
```

### Example: Creating a Custom Mapping

Source domain: Fluid dynamics

```yaml
custom_mappings:
  fluid_particle:
    component: neuron
    tag: fluid_element
    description: Discrete fluid element
    
  pressure_field:
    component: activation_pattern
    tag: pressure_distribution
    description: Distributed pressure field
    
  flow_velocity:
    component: gradient
    tag: velocity_field
    description: Direction of information flow
    
  turbulence:
    component: nonlinearity
    tag: turbulent_mixing
    description: Chaotic mixing of features
    
  viscosity:
    component: regularization
    tag: viscous_damping
    description: Smoothing/regularization effect
```
