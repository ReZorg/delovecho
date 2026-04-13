# AnyLogic Modeling Paradigms

AnyLogic supports three main simulation modeling paradigms: Discrete-Event Simulation (DES), System Dynamics (SD), and Agent-Based Modeling (ABM). Many models also combine these paradigms (multimethod modeling).

## 1. Discrete-Event Simulation (DES)

DES is used to model systems as a sequence of discrete events over time. It is well-suited for process-centric models, such as queuing systems, manufacturing processes, and logistics.

- **Identification**: Look for the use of the **Process Modeling Library**. The presence of blocks like `Source`, `Queue`, `Delay`, `Service`, and `Sink` is a strong indicator of a DES model.
- **Key Elements**: The core components are entities (agents), resources, and flowchart blocks that define the process flow.
- **Example Models**: Call Center, Emergency Department, Bank Office.

## 2. System Dynamics (SD)

SD is used to model the behavior of complex systems over time. It focuses on feedback loops and the aggregate behavior of system components.

- **Identification**: Look for **stocks** (accumulations) and **flows** (rates of change). The presence of `StockVariable` and `Flow` elements in the `.alp` file is a clear sign of an SD model.
- **Key Elements**: Stocks, flows, auxiliary variables, and feedback loops.
- **Example Models**: SIR Model, Bass Diffusion, Urban Dynamics.

## 3. Agent-Based Modeling (ABM)

ABM is used to model systems as a collection of autonomous, interacting agents. It is ideal for modeling systems where individual behavior and interactions lead to emergent, system-level patterns.

- **Identification**: Look for the use of **statecharts** to define agent behavior. The presence of `StatechartElement` tags like `State` and `Transition` is a strong indicator. Also, look for populations of agents.
- **Key Elements**: Agents with states, rules of behavior, and interactions with other agents and the environment.
- **Example Models**: SIR Agent Based, Schelling Segregation, Flocks of Boids.

## Multimethod Modeling

AnyLogic's strength lies in its ability to combine these paradigms within a single model.

- **Identification**: Look for the presence of elements from multiple paradigms. For example, a model with both `StockVariable` (SD) and `Queue` (DES) blocks is a multimethod model.
- **Common Combinations**:
    - **ABM + DES**: Agents move through a process defined by a DES flowchart.
    - **SD + ABM**: System-level dynamics (SD) influence the behavior of individual agents (ABM).
    - **SD + DES**: The output of a system dynamics model can be used as an input for a discrete-event model, for example, to set arrival rates.
- **Example Models**: Supply Chain and Market, Autoclaved Aerated Concrete Factory, Product Delivery Service Center with Spare Parts Supply Chain Reaction to Handle Customer Calls.
