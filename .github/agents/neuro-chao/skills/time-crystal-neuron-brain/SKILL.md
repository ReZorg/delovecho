---
name: time-crystal-neuron
description: Constructs hierarchical time crystal models for single neurons or the entire brain, mapping domain concepts to the temporal structures from Nanobrain (Figs 6.14 & 7.15). Use for creating complex, multi-scale neural architectures based on time crystal principles.
---

# Time Crystal Neuron & Brain Model Generator

This skill constructs hierarchical time crystal models at two scales: the **Generalized Neuron** (Fig 6.14) and the **Whole Brain** (Fig 7.15). It translates the nested temporal patterns from the Nanobrain project into formal architecture specifications.

Use this skill to design complex, multi-scale neural models that incorporate principles of nested periodicity, phase coupling, and fractal organization. It is ideal for modeling systems with inherent temporal hierarchies, from cellular dynamics to whole-brain systems.

## Core Concepts

The model is based on three pillars:

1.  **Time Crystal Architecture (from Nanobrain)**: A biological model where components oscillate at different, harmonically related frequencies. This skill supports both the single neuron and whole brain models.
2.  **sys-n Framework**: A deterministic state transition model. Slow oscillators map to Universal Sets (global state), and fast oscillators map to Particular Sets (local processing).
3.  **nn (Torch) Framework**: A modular neural network library. The hierarchical structure is mapped to nested `nn.Sequential` and `nn.Concat` containers.

For detailed explanations, see `references/theory.md`, `references/components.md`, and `references/brain_regions.md`.

## Workflow

1.  **Generate Model**: Use the appropriate script (`generate_tcn_model.py` for a single neuron or `generate_brain_model.py` for the whole brain) to create a model specification for your context.
2.  **Visualize Architecture**: Use the visualization scripts (`visualize_tcn.py` or `visualize_brain.py`) to generate diagrams of the model's structure, hierarchy, and dynamics.
3.  **Implement and Train**: Use the generated `.lua` file as a scaffold for a Torch7 implementation.

## Scripts

### Single Neuron Modeling (Fig 6.14)

#### 1. `generate_tcn_model.py`

Creates a model of a single generalized neuron.

**Usage**:
```bash
python /home/ubuntu/skills/time-crystal-neuron/scripts/generate_tcn_model.py \
    --context "your domain context" \
    --structure <a,b,c,d> \
    --output model.json --nn --sysn
```

#### 2. `visualize_tcn.py`

Visualizes a single neuron model.

**Usage**:
```bash
# Hierarchy diagram
python /home/ubuntu/skills/time-crystal-neuron/scripts/visualize_tcn.py model.json -o diagram.png

# State transition timeline
python /home/ubuntu/skills/time-crystal-neuron/scripts/visualize_tcn.py model.json --timeline
```

### Whole Brain Modeling (Fig 7.15)

#### 3. `generate_brain_model.py`

Creates a model of the entire brain, a specific region, or a functional subsystem.

**Usage**:
```bash
# Generate the full brain model
python /home/ubuntu/skills/time-crystal-neuron/scripts/generate_brain_model.py --output brain.json --summary

# Generate a model for a specific region
python /home/ubuntu/skills/time-crystal-neuron/scripts/generate_brain_model.py --region cerebellum --output cerebellum.json

# List available regions or subsystems
python /home/ubuntu/skills/time-crystal-neuron/scripts/generate_brain_model.py --list-regions
```

#### 4. `visualize_brain.py`

Visualizes the whole brain model.

**Usage**:
```bash
# Visualize the 12 hierarchy levels
python /home/ubuntu/skills/time-crystal-neuron/scripts/visualize_brain.py --levels -o levels.png

# Visualize all brain regions
python /home/ubuntu/skills/time-crystal-neuron/scripts/visualize_brain.py brain.json --regions -o regions.png

# Visualize functional subsystems
python /home/ubuntu/skills/time-crystal-neuron/scripts/visualize_brain.py brain.json --subsystems -o subsystems.png
```

## Reference Materials

- **`references/components.md`**: Component list for the single neuron model.
- **`references/brain_regions.md`**: Component list for the whole brain model, organized by region and subsystem.
- **`references/theory.md`**: Theoretical foundations and mapping to `sys-n` and `nn`.
- **`templates/`**: Contains the original reference diagrams from Nanobrain (neuron and brain).
