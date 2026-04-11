---
name: cogsim-pml
description: Build process-centric discrete event simulations using CogSim's Process Modeling Library (PML). Use for queueing systems, manufacturing lines, service operations, supply chains, or any workflow with entities flowing through processing stages with resources and routing decisions.
---

# CogSim Process Modeling Library

Build discrete event simulations using process-centric modeling patterns.

## Setup

Run setup script before first use:
```bash
python /home/ubuntu/skills/cogsim-pml/scripts/setup_cogsim.py
```

## Workflow

### 1. Define the Process

Identify:
- **Entities**: What flows through the system (customers, orders, batches, patients)
- **Stages**: Processing steps (reception, service, QC, packaging)
- **Resources**: Shared capacity (workers, machines, rooms)
- **Routing**: Decision points (pass/fail, priority routing)

### 2. Create Simulation

```python
import sys
sys.path.insert(0, '/home/ubuntu/cogsim')

from cogsim import (
    SimulationEngine, Source, Sink, Queue, Delay, Service,
    ResourcePool, ResourceTask, Seize, Release,
    SelectOutput, SelectionMode, Combine,
    ArrivalMode, RandomVariate
)

engine = SimulationEngine(seed=42)
rv = RandomVariate(seed=42)
```

### 3. Build Process Flow

**Basic flow:**
```python
source = Source("arrivals", arrival_mode=ArrivalMode.RATE, rate=1.0, engine=engine)
service = Service("server", service_time=lambda: rv.exponential(0.8), capacity=2, engine=engine)
sink = Sink("exit", engine=engine)

source >> service >> sink
```

**With resources:**
```python
workers = ResourcePool("workers", capacity=5, engine=engine)

task = ResourceTask("processing", resource_pool=workers,
                    task_time=lambda: rv.triangular(2, 5, 3),
                    quantity=2, engine=engine)

source >> task >> sink
```

**With routing:**
```python
qc = SelectOutput("qc", mode=SelectionMode.PROBABILITY, probability=0.9, engine=engine)
source >> process >> qc
qc.get_output_port("out_true").connect(good_sink.get_input_port("in"))
qc.get_output_port("out_false").connect(rework.get_input_port("in"))
```

### 4. Run and Analyze

```python
engine.run(until=480)  # 8-hour shift

# Collect statistics
print(f"Throughput: {sink.count()}")
print(f"Avg time: {sink.get_statistics()['average_time_in_system']:.2f}")
print(f"Utilization: {workers.get_statistics()['average_utilization']:.1%}")
```

## Block Selection Guide

| Need | Block | Example |
|------|-------|---------|
| Generate entities | `Source` | Customer arrivals |
| Remove entities | `Sink` | Order completion |
| Wait for capacity | `Queue` | Waiting room |
| Time-based delay | `Delay` | Processing time |
| Queue + processing | `Service` | Bank teller |
| Shared capacity | `ResourcePool` | Workers, machines |
| Acquire resource | `Seize` | Get worker |
| Release resource | `Release` | Free worker |
| Seize-delay-release | `ResourceTask` | Machine operation |
| Binary routing | `SelectOutput` | Pass/fail QC |
| Multi-way routing | `SelectOutput5` | Priority lanes |
| Merge streams | `Combine` | Rework loop |
| Group entities | `Batch` | Box packing |
| Ungroup entities | `Unbatch` | Unpack |

## Common Patterns

### Service with Resources
```python
queue = Queue("wait", engine=engine)
seize = Seize("get_worker", resource_pool=workers, engine=engine)
process = Delay("work", delay_time=lambda: rv.triangular(5, 15, 8), engine=engine)
release = Release("free_worker", resource_pool=workers, engine=engine)

source >> queue >> seize >> process >> release >> sink
```

### Rework Loop
```python
combine = Combine("merge", num_inputs=2, engine=engine)
qc = SelectOutput("qc", mode=SelectionMode.PROBABILITY, probability=0.9, engine=engine)

source >> combine >> process >> qc
qc.get_output_port("out_true").connect(sink.get_input_port("in"))
qc.get_output_port("out_false").connect(rework.get_input_port("in"))
rework.get_output_port("out").connect(combine.get_input_port("in_1"))
```

### Entity Customization
```python
def customize(entity):
    entity.attributes["type"] = rv.weighted_choice(["A", "B"], [0.7, 0.3])
    entity.attributes["value"] = rv.uniform(100, 500)

source.set_entity_customizer(customize)
```

### Conditional Routing
```python
def route_by_type(entity):
    return entity.attributes.get("type") == "premium"

router = SelectOutput("route", mode=SelectionMode.CONDITION, condition=route_by_type, engine=engine)
```

## Distributions

| Distribution | Use Case | Syntax |
|--------------|----------|--------|
| Exponential | Arrivals, service | `rv.exponential(mean)` |
| Uniform | Bounded uncertainty | `rv.uniform(low, high)` |
| Triangular | Task estimates | `rv.triangular(low, high, mode)` |
| Normal | Natural variation | `rv.normal(mean, std)` |

## References

- Block details: `references/pml_blocks.md`
- Analytics: `references/analytics.md`
- Template: `templates/simulation_template.py`

## Examples

Existing models in `/home/ubuntu/cogsim/examples/`:
- `bank_teller.py` - M/M/c queue with analytics
- `manufacturing_line.py` - Multi-stage with resources
- `skincare_salon.py` - Service operations with retail
- `skincare_production_plant.py` - Manufacturing with packaging line
