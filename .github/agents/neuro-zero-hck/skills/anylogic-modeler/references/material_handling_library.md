# Material Handling Library Reference

This library is designed for detailed modeling of in-factory and warehouse material handling processes. It is often used in conjunction with the Process Modeling Library.

| Block Name                | Usage Count | Description                                                                                                                                 |
| ------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **`Convey`**              | 129         | The core block for modeling conveyor systems. Agents (items) move along a defined path.                                                     |
| **`MoveByTransporter`**   | 70          | Manages the movement of agents (e.g., AGVs, forklifts) from one location to another. Requires a `TransporterFleet`.                          |
| **`TransporterFleet`**    | 38          | Defines a fleet of mobile resources (transporters) that can be requested by agents to perform transportation tasks.                         |
| **`SeizeTransporter`**    | 17          | An agent seizes a transporter from a `TransporterFleet`.                                                                                    |
| **`ReleaseTransporter`**  | 17          | An agent releases a seized transporter.                                                                                                     |
| **`MoveByCrane`**         | 38          | Models the movement of items by an overhead crane.                                                                                          |
| **`RackSystem`**          | 12          | A dense storage system. Used with `RackStore` and `RackPick`.                                                                               |
| **`RackStore`**           | 21          | An agent (item) is stored in a specific cell within a `RackSystem`.                                                                         |
| **`RackPick`**            | 16          | An agent retrieves an item from a `RackSystem`.                                                                                             |
