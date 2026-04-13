# Other Key AnyLogic Libraries

This document covers other important libraries identified in the example models: Pedestrian, Rail, Road Traffic, and Fluid.

## Pedestrian Library

Used for simulating pedestrian flows in environments like airports, shopping malls, and stadiums.

| Block Name      | Usage Count | Description                                                                 |
| --------------- | ----------- | --------------------------------------------------------------------------- |
| **`PedSource`** | 68          | Generates pedestrians.                                                      |
| **`PedGoTo`**   | 108         | Moves pedestrians to a target location.                                     |
| **`PedService`**| 53          | Models a service where pedestrians wait for and receive service.            |
| **`PedWait`**   | 39          | Makes pedestrians wait at a specific location for a given time or condition.|
| **`PedSink`**   | 56          | Removes pedestrians from the model.                                         |

## Road Traffic Library

Used for detailed simulation of vehicle traffic on roads.

| Block Name      | Usage Count | Description                                                                 |
| --------------- | ----------- | --------------------------------------------------------------------------- |
| **`CarSource`** | 63          | Generates cars and places them on the road network.                         |
| **`CarMoveTo`** | 101         | Moves a car to a specified destination (e.g., a parking spot, end of road). |
| **`CarDispose`**| 41          | Removes a car from the model.                                               |

## Rail Library

Used for modeling and simulating rail transportation systems.

| Block Name         | Usage Count | Description                                                                 |
| ------------------ | ----------- | --------------------------------------------------------------------------- |
| **`TrainSource`**  | 31          | Generates trains.                                                           |
| **`TrainMoveTo`**  | 84          | Moves a train along a railway track to a destination.                       |
| **`TrainDispose`** | 28          | Removes a train from the model.                                             |

## Fluid Library

Used for simulating the flow of fluids and bulk materials through pipes and tanks.

| Block Name          | Usage Count | Description                                                                 |
| ------------------- | ----------- | --------------------------------------------------------------------------- |
| **`FluidSource`**   | 34          | A source of fluid.                                                          |
| **`Tank`**          | 45          | A storage tank for fluid.                                                   |
| **`Pipeline`**      | 45          | A pipe that transports fluid.                                               |
| **`Valve`**         | 30          | Controls the flow of fluid.                                                 |
| **`FluidExit`**     | 46          | An exit point for fluid from the system.                                    |
| **`FluidDispose`**  | 38          | Removes fluid from the model.                                               |
