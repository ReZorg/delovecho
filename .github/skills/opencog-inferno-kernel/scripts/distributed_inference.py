#!/usr/bin/env python3
"""
Distributed Inference Acceleration Script
Demonstrates pattern matching and inference distribution across multiple nodes
"""

import sys
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class InferenceNode:
    """Represents a computational node in the distributed system"""
    node_id: str
    host: str
    port: int
    capacity: int  # Max concurrent inferences
    current_load: int = 0


@dataclass
class InferenceTask:
    """Represents an inference task to be distributed"""
    task_id: str
    pattern: str
    premises: List[str]
    priority: int = 0
    estimated_cost: int = 1


class DistributedInferenceScheduler:
    """Schedules inference tasks across distributed nodes"""
    
    def __init__(self):
        self.nodes: List[InferenceNode] = []
        self.tasks: List[InferenceTask] = []
    
    def add_node(self, node: InferenceNode):
        """Register a new computational node"""
        self.nodes.append(node)
    
    def add_task(self, task: InferenceTask):
        """Add an inference task to the queue"""
        self.tasks.append(task)
    
    def schedule(self) -> Dict[str, List[str]]:
        """
        Schedule tasks across nodes using a simple load-balancing algorithm
        Returns: Dict mapping node_id to list of task_ids
        """
        # Sort tasks by priority (higher first)
        sorted_tasks = sorted(self.tasks, key=lambda t: t.priority, reverse=True)
        
        # Sort nodes by available capacity
        sorted_nodes = sorted(
            self.nodes,
            key=lambda n: n.capacity - n.current_load,
            reverse=True
        )
        
        schedule = {node.node_id: [] for node in self.nodes}
        
        for task in sorted_tasks:
            # Find node with most available capacity
            best_node = None
            for node in sorted_nodes:
                available = node.capacity - node.current_load
                if available >= task.estimated_cost:
                    best_node = node
                    break
            
            if best_node:
                schedule[best_node.node_id].append(task.task_id)
                best_node.current_load += task.estimated_cost
                # Re-sort nodes after assignment
                sorted_nodes = sorted(
                    self.nodes,
                    key=lambda n: n.capacity - n.current_load,
                    reverse=True
                )
        
        return schedule
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduling statistics"""
        total_capacity = sum(n.capacity for n in self.nodes)
        total_load = sum(n.current_load for n in self.nodes)
        
        return {
            "total_nodes": len(self.nodes),
            "total_capacity": total_capacity,
            "total_load": total_load,
            "utilization": total_load / total_capacity if total_capacity > 0 else 0,
            "tasks_scheduled": len(self.tasks),
            "node_details": [
                {
                    "node_id": n.node_id,
                    "capacity": n.capacity,
                    "load": n.current_load,
                    "utilization": n.current_load / n.capacity if n.capacity > 0 else 0
                }
                for n in self.nodes
            ]
        }


def main():
    """Example usage of distributed inference scheduler"""
    
    # Create scheduler
    scheduler = DistributedInferenceScheduler()
    
    # Add computational nodes
    scheduler.add_node(InferenceNode("node-1", "192.168.1.10", 5000, capacity=10))
    scheduler.add_node(InferenceNode("node-2", "192.168.1.11", 5000, capacity=15))
    scheduler.add_node(InferenceNode("node-3", "192.168.1.12", 5000, capacity=20))
    
    # Add inference tasks
    scheduler.add_task(InferenceTask("task-1", "InheritanceLink", ["Cat", "Animal"], priority=5, estimated_cost=2))
    scheduler.add_task(InferenceTask("task-2", "SimilarityLink", ["Dog", "Wolf"], priority=3, estimated_cost=3))
    scheduler.add_task(InferenceTask("task-3", "EvaluationLink", ["Predicate", "Arg"], priority=8, estimated_cost=1))
    scheduler.add_task(InferenceTask("task-4", "ImplicationLink", ["P", "Q"], priority=6, estimated_cost=4))
    scheduler.add_task(InferenceTask("task-5", "AndLink", ["A", "B", "C"], priority=2, estimated_cost=2))
    
    # Schedule tasks
    schedule = scheduler.schedule()
    
    # Get statistics
    stats = scheduler.get_statistics()
    
    # Output results
    print("=== Distributed Inference Schedule ===\n")
    print("Schedule:")
    print(json.dumps(schedule, indent=2))
    print("\nStatistics:")
    print(json.dumps(stats, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
