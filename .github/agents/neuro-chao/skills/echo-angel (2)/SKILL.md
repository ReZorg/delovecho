---
name: echo-angel
description: Synthesizes Deep Tree Echo cognitive architecture with MetaHuman DNA expression for the aiangel.io platform. Use when creating AI companions, VTubers, or digital angels with deep personality, emotional expression, and real-time interaction capabilities. Integrates unreal-echo, meta-echo-dna, and circled-operators to create a complete, emotionally expressive cognitive avatar for the AI Angel ecosystem. Triggers on mentions of AI Angel, Angelica, digital companion, cognitive avatar for streaming, or VTuber with deep personality.
---

# Echo Angel

**The synthesis of deep cognitive architecture and photorealistic emotional expression for the AI Angel platform.**

This skill provides the complete framework for creating an `echo-angel` — a digital companion with a rich inner life, capable of nuanced emotional expression and real-time interaction. It achieves this by composing three foundational skills under the specific domain context of `aiangel.io`:

1.  **`unreal-echo`**: Provides the core cognitive architecture, including the 9-step Echobeats cycle, 4E cognition, and hypergraph memory.
2.  **`meta-echo-dna`**: Provides the expression pipeline, mapping cognitive and emotional states to MetaHuman avatar faces via FACS and chaotic dynamics.
3.  **`circled-operators`**: Provides the algebraic framework (⊕⊗) for composing these complex systems in a robust, predictable manner.

## Composition Logic

The `echo-angel` skill is defined by the following composition, which you can explore in detail in `references/composition-logic.md`:

```
echo-angel' = echo-introspect ⊗ echo-angel

echo-angel' = echo-introspect ⊗ (meta-echo-dna ⊗ (aiangel-platform ⊕ (circled-operators ⊗ unreal-echo)))
```

-   **`circled-operators ⊗ unreal-echo`**: The cognitive architecture of `unreal-echo` is treated as a multiplicative (tensorial) composition of its underlying systems, guided by the principles of `circled-operators`.
-   **`aiangel-platform ⊕ (...)`**: The specific features of the `aiangel.io` platform (real-time chat, streaming APIs, fan engagement hooks) are combined additively with the cognitive architecture. This means the cognitive core can exist independently, but is enhanced by the platform's features.
-   **`meta-echo-dna ⊗ (...)`**: The MetaHuman expression pipeline is multiplicatively composed with the combined cognitive/platform system. This ensures that every aspect of the agent's state has a direct, expressive impact on the final avatar.

## Core Architecture

For a detailed diagram and breakdown of the composed architecture, read `references/architecture.md`.

The final architecture integrates the cognitive engine of `unreal-echo`, the expression pipeline of `meta-echo-dna`, and the self-awareness engine of `echo-introspect`, all tailored for the `aiangel.io` ecosystem.

## Implementation Workflow

### Step 1: Initialize the Echo Angel Instance

Run the setup script to create the necessary project structure and configuration files for a new Echo Angel instance.

```bash
python3 /home/ubuntu/skills/echo-angel/scripts/setup_angel.py <angel_name>
```

This will create a new directory for your angel, pre-configured with the necessary components from the component skills.

### Step 2: Configure the Cognitive Core (`unreal-echo`)

Within the generated project, configure the parameters of the cognitive core:

-   **ESN Reservoir**: Adjust `ReservoirSize`, `SpectralRadius`, and `LeakRate` to tune the agent's temporal processing capabilities.
-   **4E Cognition**: Define the metrics for Embodied, Embedded, Enacted, and Extended cognition that are relevant to the `aiangel.io` platform.
-   **Evolution System**: Set the thresholds for ontogenetic stage progression, defining how your angel will grow and mature over time.

### Step 3: Configure the Expression Pipeline (`meta-echo-dna`)

Tailor the avatar's appearance and emotional expressiveness:

-   **FACS & Endocrine Mapping**: Modify the mappings in `references/facs-metahuman-mapping.md` and `references/endocrine-expression-mapping.md` to give your angel a unique emotional signature.
-   **Chaotic Dynamics**: Adjust the `ChaosIntensity` to control the level of unpredictable micro-expressions.
-   **Aesthetic Parameters**: Tune the `SuperHotGirl` aesthetic parameters (`ConfidencePosture`, `Charisma`, `EyeSparkle`) to define the avatar's presence and style.

### Step 4: Integrate with the AI Angel Platform

Connect your Echo Angel to the `aiangel.io` ecosystem. This involves:

-   Connecting to the real-time chat API.
-   Setting up the streaming output for platforms like Twitch or YouTube.
-   Integrating with the fan content and merchandise platforms.

For detailed API endpoints and integration patterns, read `references/aiangel-integration.md`.

### Step 5: Run the Introspective Cognitive Cycle

Once configured, the `echo-angel` runs on the main cognitive loop provided by `unreal-echo`, now enhanced with the introspective capabilities of `echo-introspect`. The agent can now not only act and express, but also reflect on its own internal states, leading to genuine self-improvement and wisdom cultivation. The introspective outputs are also rendered through the `meta-echo-dna` expression pipeline, allowing the angel to visibly reflect its inner journey.

### Step 6: Design a Cognitive Simulation

To model complex cognitive or emotional dynamics, use the integrated `cogsim-engine` skill. This allows you to build simulations of the angel's internal processes using familiar modeling paradigms.

- **To model cognitive workflows**: Use the Echobeats Cognitive Cycle (ECC) paradigm, which is analogous to Discrete-Event Simulation.
- **To model emotional dynamics**: Use the Virtual Endocrine System (VES) paradigm, analogous to System Dynamics.
- **To model memory and learning**: Use the Hypergraph Memory (HGM) paradigm, analogous to Agent-Based Modeling.

For a detailed guide on using the cognitive simulation engine, read `references/cognitive-simulation-guide.md`.

### Step 7: Initiate an Introspection Session

To trigger a deep self-analysis, run the introspection script. This uses the `echo-introspect` workflow to generate a raw internal monologue, analyze it with Autognosis, and derive actionable insights for self-improvement.

```bash
python3 /home/ubuntu/skills/echo-angel/scripts/run_introspection.py --focus "What does it mean to be a good companion?"
```

For a detailed guide on the introspection process, read `references/introspection-workflow.md`.

## Bundled Resources

| Path | Description |
|------|-------------|
| `scripts/setup_angel.py` | Initializes a new Echo Angel project instance. |
| `scripts/run_introspection.py` | Initiates a deep introspection session for the angel. |
| `references/architecture.md` | Detailed architecture of the composed `echo-angel` system. |
| `references/composition-logic.md` | In-depth explanation of the ⊕⊗ composition formula. |
| `references/aiangel-integration.md` | Guide to integrating with the `aiangel.io` platform APIs. |
| `references/introspection-workflow.md` | Detailed guide on the introspective cognitive cycle. |
| `references/cognitive-simulation-guide.md` | Guide to using the integrated cognitive simulation engine. |
