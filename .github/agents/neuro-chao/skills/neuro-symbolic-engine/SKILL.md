---
name: neuro-symbolic-engine
description: "A framework for building and composing neuro-symbolic skills. Use when creating systems that bridge explicit, rule-based symbolic models with sub-symbolic neural network insights. Implements the skill = func(form[flow]) algebra, where re(structure[process]) leads to relato(symbo[neuro]) which results in meta-cogno(hyper-graph[tensor-embed]). Grounded in Nettica (symbolic) and Netron (neural inspection) architectures."
---

# Neuro-Symbolic Engine

This skill provides a comprehensive framework for designing, building, and composing neuro-symbolic capabilities. It integrates a structured, symbolic system with a neural, sub-symbolic model to enable a higher-order, meta-cognitive understanding of the system's state.

The architecture is defined by the following transformation:

> `re(structure[process]) -> relato(symbo[neuro]) => meta-cogno(hyper-graph[tensor-embed])`

This translates to a system where a real-world symbolic structure is observed by a neural model, and the combination of the two creates a meta-cognitive layer capable of advanced reasoning.

## Core Architecture

The framework is grounded in the duality between a symbolic system (`symbo`) and a neural observer (`neuro`).

- **Symbolic Grounding (`symbo`):** The architecture is anchored in the **Nettica** ecosystem, a rule-based system for managing network entities (users, devices, networks). This provides the explicit, verifiable `structure` and `process`.
- **Neural Insight (`neuro`):** A conceptual neural network observes the symbolic graph, generating **tensor embeddings** for its components. **Netron** is the designated tool for inspecting and visualizing the architecture of this neural model.
- **Meta-Cognition (`meta-cogno`):** The fusion of the symbolic graph and the neural embeddings creates a **tensor-attributed hypergraph**. This `meta-cogno` layer enables advanced operations like semantic search, anomaly detection, and predictive modeling.

For a detailed breakdown of this architecture, refer to the synthesis document:

```
/home/ubuntu/skills/neuro-symbolic-engine/references/architecture_synthesis.md
```

## The Skill Algebra: `skill = func(form[flow])`

Skills within this engine are defined by a formal algebra, providing a clear and composable structure.

| Component | Definition | Description |
| :--- | :--- | :--- |
| **`form`** | The data domain | The data structure a skill operates on (e.g., `form_symbo`, `form_neuro`, `form_meta`). |
| **`func`** | The operation | The specific transformation performed (e.g., `func_manage`, `func_embed`, `func_query`). |
| **`flow`** | The composition | The pattern for connecting skills, using `⊕` (additive) and `⊗` (multiplicative) operators. |

A skill is a `(func, form)` tuple. The `flow` describes how skills are composed into more complex workflows.

For a complete definition of the algebra, including composition patterns, refer to the algebra design document:

```
/home/ubuntu/skills/neuro-symbolic-engine/references/skill_algebra.md
```

## Example Workflow: Conceptual Demonstration

This skill includes a demonstration script that simulates the core neuro-symbolic workflow.

**Workflow:**

1.  **Get Symbolic State (`func_manage` on `form_symbo`):** Retrieve the current state of the symbolic network.
2.  **Embed Graph (`func_embed` on `form_symbo`):** Generate tensor embeddings for the symbolic graph, creating the `form_meta` state.
3.  **Query Meta-Graph (`func_query` on `form_meta`):** Perform a meta-cognitive query on the attributed hypergraph.

To run the conceptual demonstration:

```bash
python /home/ubuntu/skills/neuro-symbolic-engine/scripts/demonstrate_workflow.py
```

This script provides a practical example of how to compose skills using the `⊗` (pipeline) flow to achieve a complex, multi-stage task.

## Composition with Other Skills

This engine is designed to compose with other foundational skills:

- **`skill-nn`**: Provides the underlying neural network patterns for defining `func_embed` and composing skill modules.
- **`circled-operators`**: Defines the universal `⊕` and `⊗` operators used for the `flow` composition.
- **`topology-weaver`**: Can be used to design the architecture of the `neuro` model by mapping concepts from the `symbo` domain.
- **`hypergauge-orbifold`**: Provides a framework for analyzing the geometric properties of the `meta-cogno` state space.
