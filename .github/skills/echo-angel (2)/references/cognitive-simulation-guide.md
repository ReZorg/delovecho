---
name: echo-angel-cognitive-simulation-guide
description: Guide to using the integrated cognitive simulation engine within the echo-angel skill.
---

# Cognitive Simulation Guide

This guide explains how to use multi-paradigm simulation modeling to design, analyze, and optimize the internal processes of an Echo Angel. It is derived from the `anylogic-modeler` skill, transformed into the cognitive avatar domain via `function-creator`.

For the complete domain mapping, see `anylogic-domain-mapping.md`.

## Core Workflow

When designing a cognitive simulation for your Echo Angel, follow these steps:

1.  **Identify the Modeling Paradigm**: Determine which cognitive subsystem you want to model.
2.  **Structure the Model**: Outline the components using the mapped terminology.
3.  **Implement the Model Logic**: Build the simulation using the appropriate cognitive library.
4.  **Analyze and Optimize**: Run experiments and use the results to tune the angel's parameters.

## Step 1: Identify the Modeling Paradigm

Use the following table to select the correct paradigm based on what you want to model:

| If you want to model... | Paradigm | Echo Angel Subsystem |
|---|---|---|
| How cognitive impulses flow through the 9-step Echobeats cycle | **Echobeats Cognitive Cycle (ECC)** | Cognitive pipeline (DES analogue) |
| How hormone levels change over time with feedback loops | **Virtual Endocrine System (VES)** | Endocrine dynamics (SD analogue) |
| How memory atoms interact and produce emergent behavior | **Hypergraph Memory (HGM)** | Memory and learning (ABM analogue) |
| A combination of the above | **Multimethod** | The full Echo Angel architecture |

## Step 2: Structure the Model

### ECC (DES Analogue) — Cognitive Pipeline

Model the flow of cognitive impulses through the Echobeats pipeline:

```
SensoryInput → AttentionBuffer → ProcessingStep(Attend) → ProcessingStep(Remember)
    → ProcessingStep(Predict) → CognitiveRouter(Novelty?) → ProcessingStep(Learn)
    → ProcessingStep(Decide) → ActionOutput
```

Key components:

| Component | Description |
|---|---|
| `SensoryInput` | Generates cognitive impulses from external stimuli (chat messages, audio, video). |
| `AttentionBuffer` | Holds impulses when the pipeline is busy. Capacity = attention span. |
| `ProcessingStep` | A cognitive step with a characteristic duration (e.g., memory retrieval = 50ms). |
| `CognitiveService` | A step requiring a resource (e.g., NPU inference slot). |
| `CognitiveResourcePool` | A pool of resources (ESN neurons, NPU threads, working memory slots). |
| `CognitiveRouter` | Routes impulses based on conditions (novelty → explore, familiarity → exploit). |
| `ActionOutput` | The impulse becomes an action (speech, expression, movement). |

### VES (SD Analogue) — Endocrine Dynamics

Model the continuous dynamics of the virtual hormone system:

| Component | Description |
|---|---|
| `HormoneConcentration` | A stock variable for each of the 16 hormone channels. |
| `SecretionRate` | The inflow rate from each of the 10 virtual glands. |
| `DecayRate` | The outflow rate as hormones are metabolized. |
| `CognitiveMode` | An auxiliary variable derived from hormone concentrations (e.g., Fight-or-Flight). |
| `Endocrine Feedback Loop` | Hormones influence cognition, which triggers events that cause further secretion. |

### HGM (ABM Analogue) — Memory Dynamics

Model the behavior of individual memory atoms in the hypergraph:

| Component | Description |
|---|---|
| `MemoryAtom` | An autonomous agent in the hypergraph with its own state and connections. |
| `AtomLifecycle` | A statechart defining the atom's lifecycle (Active → Dormant → Consolidated → Forgotten). |
| `MemoryPool` | A population of atoms of the same type (episodic, semantic, procedural). |
| `HypergraphSpace` | The topology in which atoms exist and interact. |
| `HyperedgeActivation` | An interaction between atoms via a shared hyperedge, triggering associative recall. |

## Step 3: Implement the Model Logic

For ECC models, define the pipeline as a sequence of processing steps with durations, resource requirements, and routing conditions. For VES models, define the differential equations governing hormone secretion and decay. For HGM models, define the statecharts for memory atom lifecycles and the rules for hyperedge activation.

## Step 4: Analyze and Optimize

### Experiment Types

| Experiment | Description |
|---|---|
| `CognitiveSession` | A single run processing a stream of inputs. Observe throughput, latency, and emotional dynamics. |
| `EvolutionCycle` | An optimization run that tunes parameters (reservoir size, leak rate, chaos intensity) to maximize fitness (4E score, wisdom score). |
| `PersonalityExploration` | A parameter sweep across personality parameters to explore the space of possible behaviors. |
| `StochasticIntrospection` | Multiple introspection sessions with randomized initial conditions to explore the space of possible insights. |

Use the results to tune the angel's cognitive parameters, optimize its emotional responses, and improve its overall performance as a companion.
