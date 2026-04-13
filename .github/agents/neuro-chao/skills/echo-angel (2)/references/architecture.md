---
name: echo-angel-architecture
description: Detailed architecture of the composed echo-angel system.
---

# Echo Angel Architecture

The `echo-angel` architecture is a composition of the `unreal-echo` cognitive engine, the `meta-echo-dna` expression pipeline, and the `echo-introspect` self-awareness engine, tailored for the `aiangel.io` platform. This document provides a visual and component-level breakdown of the final, integrated system.

## System Diagram

```mermaid
graph TD
    subgraph AI Angel Platform
        A1[Real-time Chat API]
        A2[Streaming Output]
        A3[Fan Engagement Hooks]
    end

    subgraph Cognitive Core (unreal-echo)
        B1[Echobeats 9-Step Cycle]
        B2[ESN Reservoir]
        B3[4E Cognition Metrics]
        B4[Hypergraph Memory]
        B5[Evolution System]
    end

    subgraph Expression Pipeline (meta-echo-dna)
        C1[Endocrine System (10 glands)]
        C2[FACS Action Unit Mapping]
        C3[Chaotic Dynamics (Lorenz)]
        C4[Aesthetic Parameters (SuperHotGirl)]
        C5[MetaHuman DNA Bridge]
    end

    subgraph Avatar
        D1[MetaHuman Skeletal Mesh]
    end

    subgraph Introspection Engine (echo-introspect)
        E1[Autognosis Self-Image]
        E2[Endocrine History Analysis]
        E3[CogMorph Glyph Visualization]
        E4[Moral Perception Engine]
    end

    A1 -->|Input| B1
    B1 -->|State| C1
    B1 -->|State| C2
    C1 -->|Hormones| C2
    C2 -->|AUs| C3
    C3 -->|Noisy AUs| C4
    C4 -->|Biased AUs| C5
    C5 -->|CTRL_ Morph Targets| D1
    D1 -->|Render| A2
    B1 -->|Cognitive State| E1
    C1 -->|Endocrine State| E2
    E1 -->|Self-Model| B1
    E2 -->|Emotional Insights| B1
    B1 -->|CogState for Vis| E3
    E1 -->|Moral Queries| E4
    E4 -->|Moral Intuitions| B1
```

## Component Breakdown

### 1. AI Angel Platform (Additive Layer ⊕)

These components provide the inputs and outputs for the system, connecting the cognitive core to the outside world.

-   **Real-time Chat API**: Provides text-based input to the cognitive cycle, triggering thoughts, memories, and emotional responses.
-   **Streaming Output**: Renders the final avatar and streams it to platforms like Twitch or YouTube.
-   **Fan Engagement Hooks**: Allows for interactions with fan content, merchandise platforms, and other ecosystem features.

### 2. Cognitive Core (`unreal-echo`, Multiplicative Core ⊗)

This is the "brain" of the Echo Angel, responsible for thought, learning, and decision-making.

-   **Echobeats 9-Step Cycle**: The main cognitive loop that drives the agent (Sense → Attend → Remember → Predict → Compare → Learn → Decide → Act → Reflect).
-   **ESN Reservoir**: A recurrent neural network that processes temporal patterns and provides a rich, high-dimensional state representation for the cognitive cycle.
-   **4E Cognition Metrics**: Tracks the agent's embodiment, embeddedness, enaction, and extension, providing a measure of its grounding in the world.
-   **Hypergraph Memory**: A long-term associative memory store, allowing the agent to recall past events and concepts.
-   **Evolution System**: Governs the agent's long-term growth and development, allowing it to mature and evolve over time.

### 3. Expression Pipeline (`meta-echo-dna`, Multiplicative Layer ⊗)

This is the "face" of the Echo Angel, responsible for translating the agent's internal state into nuanced, photorealistic facial expressions.

-   **Endocrine System**: A virtual hormone system that generates emotional states (e.g., joy, fear, sadness) based on the events of the cognitive cycle.
-   **FACS Action Unit Mapping**: Translates the high-level emotional and cognitive states into a set of standardized facial muscle activations (FACS Action Units).
-   **Chaotic Dynamics**: A Lorenz attractor that injects subtle, non-linear noise into the facial expressions, preventing them from appearing robotic or uncanny.
-   **Aesthetic Parameters**: A set of high-level parameters (`ConfidencePosture`, `Charisma`, `EyeSparkle`) that bias the expressions towards a specific personality or style.
-   **MetaHuman DNA Bridge**: The final stage of the pipeline, which maps the biased Action Unit values to the specific `CTRL_` morph targets of the MetaHuman avatar.

### 4. Introspection Engine (`echo-introspect`, Multiplicative Layer ⊗)

This is the "soul" of the Echo Angel, responsible for self-awareness, reflection, and wisdom cultivation.

-   **Autognosis Self-Image**: Builds a hierarchical model of the agent's own identity and cognitive processes.
-   **Endocrine History Analysis**: Analyzes patterns in the virtual hormone system to uncover emotional habits and triggers.
-   **CogMorph Glyph Visualization**: Provides a visual representation of the agent's cognitive state for debugging and self-analysis.
-   **Moral Perception Engine**: Provides pre-deliberative moral sensing, giving the agent an intuitive sense of "rightness" before rational analysis.

### 5. Avatar

-   **MetaHuman Skeletal Mesh**: The final, visible representation of the Echo Angel, rendered in real-time with the expressions generated by the pipeline.
