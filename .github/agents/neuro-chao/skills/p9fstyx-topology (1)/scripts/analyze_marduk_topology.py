#!/usr/bin/env python3
"""
Marduk ML SDK — P9Fstyx Topological Assembly Analyzer

Models the Marduk cognitive architecture (mad9ml + p9fstyx) as an RTSA
assembly, computes topological invariants, validates structural constraints,
and generates a visual dashboard.

Usage:
    python3 analyze_marduk_topology.py [--config PATH] [--output DIR]

Dependencies: numpy, scipy, networkx, matplotlib
"""

import sys, os, json, argparse

# Add RTSA framework to path
sys.path.insert(0, '/home/ubuntu/skills/runtime-topological-self-assembly/scripts')

from rtsa import Assembly, Component, Port, PortKind, TopoConstraint, AssemblyEngine
from rtsa_viz import plot_assembly_dashboard


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG = os.path.join(SKILL_DIR, 'templates', 'marduk_p9fstyx_assembly.json')


def load_assembly(config_path: str) -> Assembly:
    """Load a Marduk P9Fstyx assembly from a JSON config file."""
    with open(config_path) as f:
        data = json.load(f)
    return Assembly.from_dict(data)


def analyze(assembly: Assembly) -> dict:
    """Run full topological analysis on the assembly."""
    betti = assembly.betti_numbers()
    euler = assembly.euler_characteristic()
    violated = assembly.violated_constraints()
    pairs = assembly.persistence_pairs()

    # Classify components by layer
    layers = {}
    for cid, comp in assembly.components.items():
        layer = comp.metadata.get("layer", "unknown")
        layers.setdefault(layer, []).append(cid)

    # Classify components by subsystem
    subsystems = {}
    for cid, comp in assembly.components.items():
        sub = comp.metadata.get("subsystem", "unknown")
        subsystems.setdefault(sub, []).append(cid)

    return {
        "name": assembly.name,
        "num_components": len(assembly.components),
        "simplices_by_dim": {d: len(assembly.simplices(d)) for d in range(assembly.max_dim() + 1)},
        "betti_numbers": betti,
        "euler_characteristic": euler,
        "constraints_satisfied": len(violated) == 0,
        "violated_constraints": [c.name for c in violated],
        "persistence_pairs": pairs,
        "layers": layers,
        "subsystems": subsystems,
    }


def print_report(result: dict):
    """Print a human-readable topological analysis report."""
    print(f"\n{'='*60}")
    print(f"  Marduk P9Fstyx Topological Analysis: {result['name']}")
    print(f"{'='*60}\n")

    print(f"Components: {result['num_components']}")
    for dim, count in sorted(result['simplices_by_dim'].items()):
        labels = {0: "vertices", 1: "edges", 2: "triangles", 3: "tetrahedra"}
        print(f"  {labels.get(dim, f'{dim}-simplices')}: {count}")

    print(f"\nBetti numbers: {dict(sorted(result['betti_numbers'].items()))}")
    print(f"  β₀ = {result['betti_numbers'].get(0, 0)} (connected components)")
    print(f"  β₁ = {result['betti_numbers'].get(1, 0)} (independent cycles / redundant paths)")
    if 2 in result['betti_numbers']:
        print(f"  β₂ = {result['betti_numbers'][2]} (enclosed voids / higher-order structure)")

    print(f"\nEuler characteristic: χ = {result['euler_characteristic']}")

    if result['constraints_satisfied']:
        print(f"\n✅ All topological constraints satisfied")
    else:
        print(f"\n❌ Violated constraints: {result['violated_constraints']}")

    print(f"\nArchitectural Layers:")
    for layer, cids in sorted(result['layers'].items()):
        print(f"  {layer}: {', '.join(cids)}")

    print(f"\nCognitive Subsystems:")
    for sub, cids in sorted(result['subsystems'].items()):
        print(f"  {sub}: {', '.join(cids)}")

    print(f"\nPersistence Diagram:")
    print(f"  {'Dim':<5} {'Birth':<10} {'Death':<10} {'Persist':<10}")
    for p in result['persistence_pairs']:
        pers = "∞" if p["death"] == float("inf") else f"{p['death'] - p['birth']:.2f}"
        death = "∞" if p["death"] == float("inf") else f"{p['death']:.2f}"
        print(f"  {p['dim']:<5} {p['birth']:<10.2f} {death:<10} {pers:<10}")


def main():
    parser = argparse.ArgumentParser(description="Analyze Marduk P9Fstyx topology")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Assembly config JSON path")
    parser.add_argument("--output", default="/home/ubuntu", help="Output directory for dashboard PNG")
    args = parser.parse_args()

    print(f"Loading assembly from: {args.config}")
    assembly = load_assembly(args.config)

    result = analyze(assembly)
    print_report(result)

    # Generate dashboard
    dashboard_path = os.path.join(args.output, "marduk_p9fstyx_topology.png")
    try:
        plot_assembly_dashboard(assembly, show=False, save_path=dashboard_path)
        print(f"\n📊 Dashboard saved to: {dashboard_path}")
    except Exception as e:
        print(f"\n⚠ Dashboard generation failed: {e}")

    # Save analysis JSON
    json_path = os.path.join(args.output, "marduk_p9fstyx_analysis.json")
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"📄 Analysis JSON saved to: {json_path}")


if __name__ == "__main__":
    main()
