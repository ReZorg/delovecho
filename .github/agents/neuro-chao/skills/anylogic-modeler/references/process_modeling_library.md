# Process Modeling Library Reference

This library is the foundation for Discrete-Event Simulation (DES) in AnyLogic. It is used to model systems as processes or flowcharts. The following are the most frequently used blocks based on the analysis of the example models.

| Block Name         | Usage Count | Description                                                                                                                               |
| ------------------ | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **`Source`**       | 198         | Generates agents (entities) and starts their flow through the process. Can be configured for various arrival patterns (rate, interarrival time, schedule). |
| **`Queue`**        | 135         | A waiting area for agents when the next block in the process is busy. Key properties include capacity and queuing discipline (FIFO, LIFO, priority).      |
| **`Delay`**        | 263         | Represents a time delay or a process step where an agent waits for a specified amount of time (e.g., a machine processing cycle).             |
| **`Service`**      | 59          | A combination of a `Queue` and a `Delay` with resources. Models a service where agents may have to wait for a resource to become available.        |
| **`Seize`**        | 103         | An agent takes control of one or more resource units from a `ResourcePool`. If no resources are available, the agent waits in a queue.        |
| **`Release`**      | 100         | An agent releases previously seized resource units, making them available for other agents.                                               |
| **`ResourcePool`** | 149         | Defines a set of interchangeable resources that can be seized and released by agents (e.g., operators, machines, vehicles).                 |
| **`MoveTo`**       | 134         | Moves an agent to a new location within the agent's environment (e.g., to a specific node in a network).                                  |
| **`Enter`**        | 74          | An entry point for agents into a flowchart on a different agent or level.                                                                 |
| **`Exit`**         | 62          | An exit point for agents from a flowchart, often to another flowchart on a different agent.                                               |
| **`Split`**        | 15          | Creates a specified number of copies of the original agent to flow through different process branches.                                    |
| **`Combine`**      | 14          | Waits for a specified number of agents to arrive from different branches and then combines them into a single new agent.                    |
| **`SelectOutput`** | 154         | Routes agents to one of two or more output branches based on a condition (e.g., probability, if/else). `SelectOutput5` is a variant with 5 outputs. |
| **`Sink`**         | 189         | Destroys agents, removing them from the model. The end of a process flow.                                                                 |
