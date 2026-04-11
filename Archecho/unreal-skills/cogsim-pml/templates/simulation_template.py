"""
CogSim Process-Centric Simulation Template

Replace placeholders with domain-specific values:
- SIMULATION_NAME: Name of your simulation
- ENTITY_TYPE: Type of entities (customer, order, patient, etc.)
- PROCESS_STAGES: List of processing stages
- RESOURCES: Shared resources (workers, machines, rooms)
"""

import sys
sys.path.insert(0, '/home/ubuntu/cogsim')

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum, auto

from cogsim import (
    SimulationEngine, Source, Sink, Queue, Delay, Service,
    ResourcePool, ResourceTask, Seize, Release,
    SelectOutput, SelectionMode, Combine,
    ArrivalMode, RandomVariate
)


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class SimulationConfig:
    """Simulation parameters."""
    # Arrival parameters
    arrival_rate: float = 1.0  # entities per time unit
    
    # Resource capacities
    num_servers: int = 2
    num_workers: int = 4
    
    # Process parameters
    service_time_min: float = 1.0
    service_time_max: float = 5.0
    service_time_mode: float = 2.0
    
    # Quality parameters
    pass_rate: float = 0.95
    
    # Simulation parameters
    simulation_time: float = 480.0  # 8 hours
    seed: int = 42


# ============================================================================
# METRICS TRACKING
# ============================================================================

class Metrics:
    """Centralized metrics collection."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.entities_arrived = 0
        self.entities_completed = 0
        self.entities_failed = 0
        self.total_value = 0.0


metrics = Metrics()


# ============================================================================
# MAIN SIMULATION
# ============================================================================

def run_simulation(config: SimulationConfig, verbose: bool = True) -> Dict[str, Any]:
    """
    Run the simulation with given configuration.
    
    Args:
        config: Simulation parameters
        verbose: Print detailed output
        
    Returns:
        Dictionary with simulation results
    """
    metrics.reset()
    
    if verbose:
        print("=" * 60)
        print("SIMULATION: [SIMULATION_NAME]")
        print("=" * 60)
        print(f"\nConfiguration:")
        print(f"  Arrival rate: {config.arrival_rate}")
        print(f"  Servers: {config.num_servers}")
        print(f"  Workers: {config.num_workers}")
        print(f"  Simulation time: {config.simulation_time}")
    
    # Create engine and random variate generator
    engine = SimulationEngine(seed=config.seed)
    rv = RandomVariate(seed=config.seed)
    
    # ========== RESOURCES ==========
    
    servers = ResourcePool("servers", capacity=config.num_servers, engine=engine)
    workers = ResourcePool("workers", capacity=config.num_workers, engine=engine)
    
    # ========== ENTITY GENERATION ==========
    
    def customize_entity(entity):
        """Customize arriving entities."""
        entity.attributes["type"] = rv.weighted_choice(
            ["standard", "premium"],
            [0.8, 0.2]
        )
        metrics.entities_arrived += 1
    
    source = Source(
        "arrivals",
        arrival_mode=ArrivalMode.RATE,
        rate=config.arrival_rate,
        entity_type="entity",
        engine=engine
    )
    source.set_entity_customizer(customize_entity)
    
    # ========== PROCESS STAGES ==========
    
    # Stage 1: Reception/Check-in
    reception = Service(
        "reception",
        service_time=lambda: rv.triangular(0.5, 2.0, 1.0),
        capacity=1,
        engine=engine
    )
    
    # Stage 2: Main Processing (with resources)
    processing_queue = Queue("processing_queue", capacity=20, engine=engine)
    
    processing_seize = Seize(
        "processing_seize",
        resource_pool=servers,
        quantity=1,
        engine=engine
    )
    
    processing = Delay(
        "processing",
        delay_time=lambda: rv.triangular(
            config.service_time_min,
            config.service_time_max,
            config.service_time_mode
        ),
        capacity=config.num_servers,
        engine=engine
    )
    
    processing_release = Release(
        "processing_release",
        resource_pool=servers,
        engine=engine
    )
    
    # Stage 3: Quality Check
    qc_check = SelectOutput(
        "qc_check",
        mode=SelectionMode.PROBABILITY,
        probability=config.pass_rate,
        engine=engine
    )
    
    # Stage 4: Completion
    def on_complete(entity):
        metrics.entities_completed += 1
    
    completion = Sink("completed", engine=engine)
    completion.on_enter(on_complete)
    
    # Failed entities
    def on_failed(entity):
        metrics.entities_failed += 1
    
    failed = Sink("failed", engine=engine)
    failed.on_enter(on_failed)
    
    # ========== CONNECT FLOW ==========
    
    # Main flow
    source >> reception >> processing_queue >> processing_seize >> processing >> processing_release >> qc_check
    
    # QC branches
    qc_check.get_output_port("out_true").connect(completion.get_input_port("in"))
    qc_check.get_output_port("out_false").connect(failed.get_input_port("in"))
    
    # ========== RUN ==========
    
    if verbose:
        print(f"\nRunning simulation...")
    
    engine.run(until=config.simulation_time)
    
    # ========== RESULTS ==========
    
    server_stats = servers.get_statistics()
    completion_stats = completion.get_statistics()
    
    if verbose:
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"\nThroughput:")
        print(f"  Arrived: {metrics.entities_arrived}")
        print(f"  Completed: {metrics.entities_completed}")
        print(f"  Failed: {metrics.entities_failed}")
        print(f"  Completion rate: {metrics.entities_completed/metrics.entities_arrived*100:.1f}%")
        print(f"\nPerformance:")
        print(f"  Avg time in system: {completion_stats['average_time_in_system']:.2f}")
        print(f"  Server utilization: {server_stats['average_utilization']:.1%}")
    
    return {
        "throughput": {
            "arrived": metrics.entities_arrived,
            "completed": metrics.entities_completed,
            "failed": metrics.entities_failed,
        },
        "performance": {
            "avg_time_in_system": completion_stats['average_time_in_system'],
            "server_utilization": server_stats['average_utilization'],
        }
    }


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def run_capacity_analysis(base_config: SimulationConfig):
    """Analyze impact of server capacity."""
    print("\n" + "=" * 60)
    print("CAPACITY ANALYSIS")
    print("=" * 60)
    
    print(f"\n{'Servers':>8} {'Completed':>10} {'Avg Time':>10} {'Util %':>10}")
    print("-" * 40)
    
    for num_servers in [1, 2, 3, 4, 5]:
        config = SimulationConfig(
            arrival_rate=base_config.arrival_rate,
            num_servers=num_servers,
            simulation_time=base_config.simulation_time,
            seed=base_config.seed
        )
        results = run_simulation(config, verbose=False)
        
        print(f"{num_servers:>8} {results['throughput']['completed']:>10} "
              f"{results['performance']['avg_time_in_system']:>10.2f} "
              f"{results['performance']['server_utilization']:>10.1%}")


if __name__ == "__main__":
    # Run main simulation
    config = SimulationConfig(
        arrival_rate=1.0,
        num_servers=2,
        simulation_time=480.0
    )
    
    results = run_simulation(config)
    
    # Run analysis
    run_capacity_analysis(config)
