---
name: echo-angel-anylogic-domain-mapping
description: Domain mapping from AnyLogic simulation paradigms to the Echo Angel cognitive avatar architecture.
---

# AnyLogic → Echo Angel Domain Mapping

This document defines the functor `F: anylogic-modeler → echo-angel` that maps simulation modeling concepts into the cognitive avatar domain.

## Paradigm Mapping

| AnyLogic Paradigm | Echo Angel Analogue | Rationale |
|---|---|---|
| **Discrete-Event Simulation (DES)** | **Echobeats Cognitive Cycle** | Both are process-centric: entities flow through discrete steps. In DES, entities are customers/parts; in Echo Angel, the "entity" is a cognitive impulse flowing through the 9-step Echobeats cycle. |
| **System Dynamics (SD)** | **Virtual Endocrine System** | Both model aggregate, continuous behavior with feedback loops. SD uses stocks and flows; the endocrine system uses hormone concentrations (stocks) and gland secretion/decay rates (flows). |
| **Agent-Based Modeling (ABM)** | **Hypergraph Memory + 4E Cognition** | Both model autonomous, interacting agents with emergent behavior. In ABM, agents have statecharts; in Echo Angel, memory atoms are agents in a hypergraph, and 4E metrics emerge from their interactions. |
| **Multimethod Modeling** | **The Full Echo Angel Architecture** | The Echo Angel is inherently multimethod: the DES-like cognitive cycle drives the SD-like endocrine system, which modulates the ABM-like memory agents. |

## Term Mapping: DES → Echobeats Cognitive Cycle

| AnyLogic DES Term | Echo Angel Term | Description |
|---|---|---|
| `Source` | `SensoryInput` | Generates cognitive impulses from external stimuli (chat, audio, video). |
| `Queue` | `AttentionBuffer` | A waiting area for stimuli when the cognitive cycle is busy processing. Capacity is the attention span. |
| `Delay` | `ProcessingStep` | A cognitive processing step (e.g., memory retrieval, prediction generation) with a characteristic duration. |
| `Service` | `CognitiveService` | A processing step that requires a cognitive resource (e.g., ESN reservoir capacity, NPU inference slot). |
| `Seize` | `AllocateResource` | The cognitive cycle seizes a resource (e.g., a slot in the ESN reservoir, an NPU inference thread). |
| `Release` | `FreeResource` | The cognitive cycle releases the resource after processing. |
| `ResourcePool` | `CognitiveResourcePool` | A pool of cognitive resources (ESN neurons, NPU threads, working memory slots). |
| `SelectOutput` | `CognitiveRouter` | Routes the cognitive impulse based on conditions (e.g., novelty → explore path, familiarity → exploit path). |
| `Sink` | `ActionOutput` | The end of the cognitive process: the impulse is transformed into an action (speech, expression, movement). |
| `Entity` | `CognitiveImpulse` | The unit of work flowing through the cognitive cycle. |
| `Flowchart` | `EchobeatsPipeline` | The 9-step cognitive pipeline defined as a process flowchart. |

## Term Mapping: SD → Virtual Endocrine System

| AnyLogic SD Term | Echo Angel Term | Description |
|---|---|---|
| `Stock` | `HormoneConcentration` | An accumulation variable representing the current level of a hormone (e.g., cortisol, dopamine). |
| `Flow` | `SecretionRate` / `DecayRate` | The rate at which a gland secretes a hormone (inflow) or the rate at which it decays (outflow). |
| `Auxiliary Variable` | `CognitiveMode` | A derived variable computed from hormone concentrations (e.g., "Fight-or-Flight" mode from high cortisol + NE). |
| `Feedback Loop` | `Endocrine Feedback Loop` | Hormones influence cognitive processing, which triggers events that cause further hormone secretion. |
| `Causal Loop Diagram` | `Endocrine Causal Map` | A diagram showing the causal relationships between hormones, cognitive modes, and behaviors. |

## Term Mapping: ABM → Hypergraph Memory + 4E Cognition

| AnyLogic ABM Term | Echo Angel Term | Description |
|---|---|---|
| `Agent` | `MemoryAtom` / `HypergraphNode` | An autonomous unit in the memory hypergraph with its own state and connections. |
| `Statechart` | `AtomLifecycle` | The lifecycle of a memory atom (e.g., Active → Dormant → Consolidated → Forgotten). |
| `State` | `AtomState` | A specific state of a memory atom (e.g., `Active`, `Dormant`). |
| `Transition` | `AtomTransition` | A transition between atom states, triggered by attention (ECAN STI), time, or reinforcement. |
| `Population` | `MemoryPool` | A collection of memory atoms of the same type (e.g., episodic memories, semantic concepts). |
| `Environment` | `HypergraphSpace` | The hypergraph topology in which memory atoms exist and interact. |
| `Interaction` | `HyperedgeActivation` | An interaction between memory atoms via a shared hyperedge, leading to associative recall or pattern completion. |
| `Emergent Behavior` | `4E Cognitive Metrics` | The system-level properties (Embodied, Embedded, Enacted, Extended scores) that emerge from the interactions of individual memory atoms. |

## Experiment Mapping

| AnyLogic Experiment | Echo Angel Analogue | Description |
|---|---|---|
| `SimulationExperiment` | `CognitiveSession` | A single run of the cognitive cycle, processing a stream of inputs. |
| `OptimizationExperiment` | `EvolutionCycle` | An optimization run that tunes cognitive parameters (reservoir size, leak rate, chaos intensity) to maximize a fitness function (4E score, wisdom score). |
| `ParameterVariation` | `PersonalityExploration` | A sweep across personality parameters to explore the space of possible angel behaviors. |
| `MonteCarloExperiment` | `StochasticIntrospection` | Running multiple introspection sessions with randomized initial conditions to explore the space of possible insights. |
