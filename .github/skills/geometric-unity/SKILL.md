---
name: geometric-unity
description: Provides tools and a framework for exploring and implementing Eric Weinstein's Geometric Unity (GU) theory. Use this skill for tasks involving GU concepts, such as constructing the observerse, applying gauge transformations, computing swervature, or simulating GU field equations.
---

# Geometric Unity

## Overview

This skill provides a comprehensive framework for working with the mathematical and computational aspects of Eric Weinstein's Geometric Unity (GU) theory. It includes Python scripts for constructing core GU objects, reference documentation detailing the mathematical framework, and templates for building custom GU computations. Use this skill to explore GU's core concepts, implement its operators, and simulate its field equations.

## Core Capabilities

This skill is structured around the core components of Geometric Unity, providing both theoretical references and practical implementations.

### 1. Observerse Construction

The foundational arena of GU is the **observerse**, the 14-dimensional space of all metrics on a 4-dimensional manifold. This skill provides tools to construct and interact with the observerse.

**When to use:**
- When you need to define the base manifold and metric space for a GU simulation.
- When you need to work with points in the observerse, projecting them to the base manifold or extracting the metric at a point.
- When you need to compute the DeWitt supermetric on the fiber of metrics.

**Resources:**
- **Script:** `scripts/observerse.py` - A Python script to construct the observerse, create points, and compute metrics.
- **Reference:** `references/gu_framework.md` - Detailed explanation of the observerse and its properties.

**Example:**
```bash
# Run the observerse demo to see it in action
python /home/ubuntu/skills/geometric-unity/scripts/observerse.py demo
```

### 2. Gauge Transformations

GU extends standard gauge theory to unify gravity with other forces. This skill provides tools to apply both standard and GU-specific gauge transformations.

**When to use:**
- When you need to apply gauge transformations to connections or curvature tensors.
- When you need to work with inhomogeneous or tilted gauge groups.
- When you need to implement the **Shiab (Ship in a Bottle) operator** to ensure gauge covariance.

**Resources:**
- **Script:** `scripts/gauge_transformer.py` - A Python script for applying gauge transformations and the Shiab operator.
- **Reference:** `references/glossary.md` - Definitions of gauge-related terms in GU.

**Example:**
```bash
# Run the gauge transformer demo
python /home/ubuntu/skills/geometric-unity/scripts/gauge_transformer.py demo
```

### 3. Swervature and Field Equations

The central object in the GU field equations is **swervature**, which combines curvature and torsion. This skill provides tools to compute swervature and explore the unified field equations.

**When to use:**
- When you need to compute the Riemann curvature tensor, Ricci tensor, or Ricci scalar from a given connection.
- When you need to compute torsion and augmented torsion.
- When you need to apply the Hodge star operator to differential forms.
- When you need to compute the full swervature equation: `Swervature = Shiab(F_∇) + ★(T_aug)`.

**Resources:**
- **Script:** `scripts/swervature.py` - A Python script for computing curvature, torsion, and swervature.
- **Reference:** `references/gu_framework.md` - Detailed breakdown of the swervature equation.

**Example:**
```bash
# Run the swervature computation demo
python /home/ubuntu/skills/geometric-unity/scripts/swervature.py demo
```

### 4. Custom GU Computations

To facilitate custom explorations of Geometric Unity, this skill includes a template for building your own GU computations.

**When to use:**
- When you want to set up a new GU simulation with a custom metric, connection, or gauge group.
- When you want to experiment with different aspects of the GU framework.

**Resources:**
- **Template:** `templates/gu_computation.py.template` - A Python template with a pre-defined structure for GU computations.

**How to use:**
1.  Copy the template to a new file: `cp /home/ubuntu/skills/geometric-unity/templates/gu_computation.py.template my_gu_sim.py`
2.  Edit `my_gu_sim.py` to define your custom metric, connection, and other parameters in the designated `TODO` sections.
3.  Run your custom simulation: `python my_gu_sim.py`

## Resources

This skill includes the following resources to support your work with Geometric Unity:

### scripts/

- `observerse.py`: Constructs the observerse `U^14 = met(X^4)`, creates points, and computes metrics.
- `gauge_transformer.py`: Implements standard and inhomogeneous gauge transformations, including the Shiab operator.
- `swervature.py`: Computes curvature, torsion, and the full swervature equation.

### references/

- `gu_framework.md`: A detailed mathematical reference for the core concepts of Geometric Unity, including the observerse, chimeric bundle, Shiab operator, and swervature.
- `glossary.md`: A glossary of key terms and concepts in Geometric Unity.

### templates/

- `gu_computation.py.template`: A Python template for building custom Geometric Unity computations.
