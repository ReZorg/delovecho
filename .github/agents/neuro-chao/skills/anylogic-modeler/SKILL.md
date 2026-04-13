---
name: anylogic-modeler
description: Build and analyze simulation models using AnyLogic. Use for tasks involving discrete-event, agent-based, and system dynamics modeling, or any combination of these paradigms. Triggers on mentions of AnyLogic, simulation modeling, DES, ABM, or SD.
---

# AnyLogic Modeler Skill

This skill provides the knowledge and workflows required to build, analyze, and understand AnyLogic simulation models. It is based on an analysis of over 400 official AnyLogic example models.

## Core Workflow

When tasked with an AnyLogic modeling problem, follow these sequential steps:

1.  **Identify the Modeling Paradigm**: Determine the appropriate simulation paradigm(s) for the problem. This is the most critical step.
2.  **Structure the Model**: Outline the main components of the model, including agent types, logic, and experiments.
3.  **Implement the Model Logic**: Build the model using the appropriate libraries and custom Java code where necessary.
4.  **Analyze and Present Results**: Run experiments and present the findings to the user.

## Step 1: Identify the Modeling Paradigm

Before writing any code, you MUST determine which paradigm(s) to use. Consult the paradigms reference guide for detailed descriptions.

-   **Read First**: `/home/ubuntu/skills/anylogic-modeler/references/paradigms.md`

Use the following table to guide your decision based on the user's request:

| If the user wants to model...                                 | Primary Paradigm | Key Indicators                                    |
| ------------------------------------------------------------- | ---------------- | ------------------------------------------------- |
| A process with queues, resources, and entities flowing through | **Discrete-Event** | "Queues", "process flow", "service time", "throughput" |
| Aggregate system behavior with feedback loops                 | **System Dynamics**| "Feedback loops", "stocks and flows", "accumulations"  |
| Interacting, autonomous individuals with emergent behavior    | **Agent-Based**    | "Individual behavior", "interactions", "emergent patterns" |
| A combination of the above (e.g., agents in a process)        | **Multimethod**    | Features from multiple paradigms are present.     |

If the user's request is ambiguous, ask clarifying questions to determine the correct paradigm.

## Step 2: Structure the Model

Once the paradigm is identified, outline the model's structure:

1.  **Main Agent**: Every model has a `Main` agent that typically contains the core logic and other agents.
2.  **Agent Types**: Define the different types of agents in the model (e.g., `Customer`, `Vehicle`, `Patient`).
3.  **Environment**: Define the space where agents live, which can be continuous, discrete, or GIS-based.
4.  **Experiments**: Determine the type of experiment needed. The most common is the `SimulationExperiment`. For optimization tasks, use the `OptimizationExperiment`.

## Step 3: Implement the Model Logic

With the structure defined, implement the model's logic using the appropriate AnyLogic libraries. These reference guides provide details on the most commonly used blocks.

-   **For DES models**: Read `/home/ubuntu/skills/anylogic-modeler/references/process_modeling_library.md`
-   **For warehouse/factory models**: Read `/home/ubuntu/skills/anylogic-modeler/references/material_handling_library.md`
-   **For pedestrian, traffic, or rail models**: Read `/home/ubuntu/skills/anylogic-modeler/references/other_libraries.md`

### Implementation Patterns

-   **Process Flow (DES)**: Use blocks from the Process Modeling Library to create a flowchart that defines the agent's journey.
-   **Behavior (ABM)**: Use **Statecharts** to model the different states an agent can be in and the transitions between them.
-   **System-Level Dynamics (SD)**: Use **Stocks** and **Flows** to model accumulations and rates of change.
-   **Custom Logic**: For complex logic that cannot be expressed with library blocks, use Java code within the properties of AnyLogic elements (e.g., in the "On exit" action of a block).

## Step 4: Analyze and Present Results

After building the model, run the simulation experiment and collect data. Present the results to the user in a clear and understandable format, using charts, plots, and statistics. The `analysis` and `file` tools are well-suited for this.
