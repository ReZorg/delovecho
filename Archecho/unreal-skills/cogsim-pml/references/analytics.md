# Analytics & Distributions Reference

## RandomVariate

Statistical distributions for stochastic modeling.

```python
rv = RandomVariate(seed=42)

# Exponential - Poisson arrivals, service times
rv.exponential(mean=5.0)

# Uniform - bounded uncertainty
rv.uniform(low=1.0, high=5.0)

# Triangular - task time estimates (min, max, mode)
rv.triangular(low=2.0, high=8.0, mode=5.0)

# Normal - natural variation
rv.normal(mean=10.0, std=2.0)

# Choice - random selection
rv.choice(["A", "B", "C"])

# Weighted choice - probabilistic selection
rv.weighted_choice(["small", "medium", "large"], [0.2, 0.5, 0.3])
```

## Queueing Theory Calculators

### M/M/1 Queue
Single server, Poisson arrivals, exponential service.

```python
from cogsim import MM1Calculator

result = MM1Calculator.calculate(
    arrival_rate=0.8,  # λ
    service_rate=1.0   # μ
)

result.traffic_intensity       # ρ = λ/μ
result.avg_entities_in_system  # L
result.avg_entities_in_queue   # Lq
result.avg_time_in_system      # W
result.avg_time_in_queue       # Wq
result.prob_system_empty       # P0
```

### M/M/c Queue
Multiple servers.

```python
from cogsim import MMcCalculator

result = MMcCalculator.calculate(
    arrival_rate=2.0,
    service_rate=1.0,
    num_servers=3
)

result.prob_waiting  # P(wait > 0)
```

## Little's Law Verification

L = λW (entities in system = arrival rate × time in system)

```python
from cogsim import SimulationAnalyzer

analyzer = SimulationAnalyzer(engine)
metrics = analyzer.calculate_metrics()
verification = metrics.verify_littles_law(tolerance=0.1)

verification['L_equals_lambda_W']  # bool
verification['relative_error_L']   # float
```

## Block Statistics

### Source Statistics
```python
source.get_statistics()
# arrivals_generated, arrival_rate
```

### Sink Statistics
```python
sink.get_statistics()
# entities_disposed, average_time_in_system, throughput
```

### Queue Statistics
```python
queue.get_statistics()
# average_queue_length, max_queue_length, average_wait_time
```

### Service Statistics
```python
service.get_statistics()
# entities_served, average_service_time, utilization
# average_queue_length, average_wait_time
```

### ResourcePool Statistics
```python
pool.get_statistics()
# average_utilization, peak_utilization
# average_queue_length, average_wait_time
```

## Common Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Utilization (ρ) | λ/(cμ) | Fraction of capacity used |
| Throughput (X) | entities/time | System output rate |
| Lead Time (W) | Wq + Ws | Total time in system |
| WIP (L) | λW | Work in progress |

## Steady State Conditions

- ρ < 1 required for stability
- ρ ≥ 1 means unbounded queue growth
- Warmup period needed before collecting statistics
