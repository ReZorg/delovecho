# PML Block Reference

## Flow Blocks

### Source
Generates entities at specified rate or intervals.

```python
Source(
    name: str,
    arrival_mode: ArrivalMode,  # RATE, INTERARRIVAL, SCHEDULE
    rate: float = None,          # entities per time unit (RATE mode)
    interarrival_time: Callable = None,  # function returning time (INTERARRIVAL)
    max_arrivals: int = None,    # limit total arrivals
    entity_type: str = "entity",
    engine: SimulationEngine
)
```

**Entity Customization:**
```python
def customize(entity):
    entity.attributes["type"] = "premium"
    entity.attributes["value"] = rv.uniform(100, 500)

source.set_entity_customizer(customize)
```

### Sink
Disposes entities and collects statistics.

```python
Sink(name: str, engine: SimulationEngine)

# Statistics
sink.count()  # entities disposed
sink.get_statistics()  # detailed metrics
```

### Queue
Holds entities waiting for downstream processing.

```python
Queue(
    name: str,
    capacity: int = float('inf'),
    timeout: float = None,  # max wait time
    engine: SimulationEngine
)
```

### Delay
Time-based processing without resources.

```python
Delay(
    name: str,
    delay_time: Union[float, Callable],  # fixed or stochastic
    capacity: int = 1,  # concurrent entities
    engine: SimulationEngine
)
```

### Service
Combined queue + delay (most common block).

```python
Service(
    name: str,
    service_time: Union[float, Callable],
    capacity: int = 1,           # servers
    queue_capacity: int = inf,   # waiting space
    engine: SimulationEngine
)
```

## Resource Blocks

### ResourcePool
Shared resource pool (machines, workers, rooms).

```python
ResourcePool(
    name: str,
    capacity: int,
    engine: SimulationEngine
)

# Statistics
pool.get_statistics()['average_utilization']
```

### Seize
Acquire resources from pool.

```python
Seize(
    name: str,
    resource_pool: ResourcePool,
    quantity: int = 1,
    priority: int = 0,  # lower = higher priority
    engine: SimulationEngine
)
```

### Release
Return resources to pool.

```python
Release(
    name: str,
    resource_pool: ResourcePool,
    engine: SimulationEngine
)
```

### ResourceTask
Seize-delay-release in one block.

```python
ResourceTask(
    name: str,
    resource_pool: ResourcePool,
    task_time: Union[float, Callable],
    quantity: int = 1,
    engine: SimulationEngine
)
```

## Routing Blocks

### SelectOutput
Binary conditional routing.

```python
SelectOutput(
    name: str,
    mode: SelectionMode,  # CONDITION, PROBABILITY
    condition: Callable = None,   # returns bool
    probability: float = None,    # for PROBABILITY mode
    engine: SimulationEngine
)

# Outputs: out_true, out_false
select.get_output_port("out_true").connect(...)
select.get_output_port("out_false").connect(...)
```

### SelectOutput5
Multi-way routing (up to 5 outputs).

```python
SelectOutput5(
    name: str,
    num_outputs: int,
    mode: SelectionMode,  # INDEX, PROBABILITY
    selector: Callable = None,      # returns 0..n-1
    probabilities: List[float] = None,
    engine: SimulationEngine
)

# Outputs: out_0, out_1, out_2, ...
```

### Split
Create copies of entity.

```python
Split(
    name: str,
    num_copies: int = 2,
    copy_attributes: bool = True,
    engine: SimulationEngine
)
```

### Combine
Merge multiple input streams.

```python
Combine(
    name: str,
    num_inputs: int,
    engine: SimulationEngine
)

# Inputs: in_0, in_1, in_2, ...
combine.get_input_port("in_0")
```

### Hold
Conditional blocking.

```python
Hold(
    name: str,
    initially_blocked: bool = True,
    capacity: int = inf,
    engine: SimulationEngine
)

hold.unblock()  # release entities
hold.block()    # stop flow
```

### Batch
Group entities into batches.

```python
Batch(
    name: str,
    batch_size: int,
    timeout: float = None,  # release partial batch
    engine: SimulationEngine
)
```

### Unbatch
Separate batched entities.

```python
Unbatch(name: str, engine: SimulationEngine)
```

## Connection Patterns

### Fluent API
```python
source >> queue >> service >> sink
```

### Manual Connection
```python
source.get_output_port("out").connect(queue.get_input_port("in"))
```

### Branching
```python
# QC routing
qc = SelectOutput("qc", mode=SelectionMode.PROBABILITY, probability=0.9, engine=engine)
source >> process >> qc
qc.get_output_port("out_true").connect(good_sink.get_input_port("in"))
qc.get_output_port("out_false").connect(rework.get_input_port("in"))
```

### Merging
```python
combine = Combine("merge", num_inputs=2, engine=engine)
stream_a >> combine.get_input_port("in_0")
stream_b >> combine.get_input_port("in_1")
combine >> downstream
```
