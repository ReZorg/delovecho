---
name: resonance
description: "Provides algebraic analysis (⊕/⊗) and development expertise for the Resonance PHP Framework. Use when building applications with Resonance, architecting its composable features (HTTP, AI, WebSockets, GraphQL), or analyzing existing Resonance codebases through the lens of circled-operators."
---

# Resonance: The Composable PHP Framework

This skill provides expertise in the **Resonance PHP Framework**, an async-first platform for building IO-intensive applications with integrated AI/ML capabilities. It analyzes Resonance through the algebraic lens of `circled-operators` (⊕/⊗), treating the framework as a **semiring of composable features**.

Use this skill when developing with Resonance, architecting new applications, or analyzing existing Resonance codebases. It helps in understanding and applying the framework's core composition patterns.

## 1. The Resonance Semiring: An Algebraic View

Resonance's architecture is a **tensor of polynomials**: a core runtime (Swoole ⊗ DI) that multiplicatively binds to a sum of optional features (HTTP ⊕ WebSocket ⊕ AI ⊕ ...).

| Element | Resonance Interpretation |
|---|---|
| **⊕ (Additive)** | **Feature Gating & Singleton Collections**: Independent modules coexist. `#[WantsFeature]` adds a feature to the sum. `SingletonCollection` gathers alternative implementations. |
| **⊗ (Multiplicative)** | **Attribute-Driven Wiring & DI**: Components interact via PHP Attributes (`#[RespondsToHttp]`, `#[ListensTo]`) and constructor injection. |
| **0 (Zero)** | **Empty Project**: No features enabled, no singletons registered. |
| **1 (Unit)** | **DependencyInjectionContainer**: The identity element for composition. |

For a detailed breakdown, read `references/semiring.md`.

## 2. Workflow: Building with Resonance

Building a Resonance application is an exercise in composition. Follow this workflow:

### Step 1: Decompose the Problem (⊕-analysis)

Identify the top-level, independent capabilities your application needs. These are the features you will additively compose.

*   Needs to serve a website? → **HTTP**
*   Needs real-time updates? → **WebSocket**
*   Needs to understand user commands? → **AI/LLM**
*   Needs to store data? → **Database**
*   Needs user accounts? → **Auth/Security**

### Step 2: Select Features (⊕-composition)

For each required capability, enable the corresponding `Feature` by having a class use the `#[WantsFeature(Feature::...)]` attribute. This performs the ⊕ operation, adding the feature's modules to the DI container.

### Step 3: Wire Components (⊗-composition)

Within each feature, wire components together using attributes and constructor injection. This performs the ⊗ operation, creating interactive pipelines.

*   `#[RespondsToHttp]` → Wires a controller to a route.
*   `#[ListensTo]` → Wires a listener to an event.
*   `#[RespondsToPromptSubject]` → Wires a handler to an LLM intent.
*   `__construct(MyDependency $dep)` → Wires a class to its dependency.

For a full list of attributes and their ⊗-effects, see `references/attributes.md`.

### Step 4: Implement Business Logic

With the scaffolding composed, fill in the business logic within your controllers, responders, listeners, and other components.

### Step 5: Analyze the Composition

Use the `analyze_composition.py` script to visualize the ⊕ and ⊗ compositions in your project. This helps in understanding the architecture and debugging dependency issues.

```bash
python /home/ubuntu/skills/resonance/scripts/analyze_composition.py /path/to/your/resonance/project
```

## 3. Core Composition Patterns

Resonance's power comes from its clear separation of additive and multiplicative patterns.

*   **Additive (⊕) Patterns**: Use when you need alternatives, choices, or independent features. (e.g., `SingletonCollection` for multiple loggers, `Feature` for optional subsystems).
*   **Multiplicative (⊗) Patterns**: Use when you need interacting components in a pipeline. (e.g., HTTP request lifecycle, LLM prompt processing).

For a guide to recognizing and applying these patterns, read `references/patterns.md`.

## 4. Subsystem Decompositions

Each of Resonance's major subsystems has a clear ⊕/⊗ algebraic structure. Understanding this structure is key to mastering the framework.

*   **HTTP**: `Controller ⊗ Middleware ⊗ Interceptor ⊗ Responder ⊗ Router`
*   **AI/LLM**: `LlamaCppClient ⊗ LlmPrompt ⊗ LlmPersona ⊗ (BNFGrammar ⊕ Extractor)`
*   **Dialogue**: `DialogueNode ⊗ (ResponseA ⊕ ResponseB ⊕ ...)`

For a detailed algebraic breakdown of all 10 subsystems, read `references/subsystems.md`.
