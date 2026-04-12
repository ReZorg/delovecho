#!/usr/bin/env python3
"""
extract_deps.py — Extract the dependency graph from o9nn/org-oc.

Scans CMakeLists.txt files across the monorepo to build a precise
component dependency DAG. Outputs JSON with nodes, edges, layers,
and topological sort.

Usage:
    python3 extract_deps.py <repo_root> [--output deps.json]
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── Known layer assignments (from top-level CMakeLists.txt) ──────────────
LAYER_MAP = {
    # Foundation (0)
    "cogutil": 0, "moses": 0, "blender_api_msgs": 0,
    "external-tools": 0, "ocpkg": 0,
    # Core (1)
    "atomspace": 1, "atomspace-rocks": 1, "atomspace-pgres": 1,
    "atomspace-ipfs": 1, "atomspace-websockets": 1,
    "atomspace-restful": 1, "atomspace-bridge": 1,
    "atomspace-metta": 1, "atomspace-rpc": 1, "atomspace-cog": 1,
    "atomspace-agents": 1, "atomspace-dht": 1, "atomspace-storage": 1,
    # Logic (2)
    "unify": 2, "ure": 2,
    # Cognitive (3)
    "cogserver": 3, "attention": 3, "spacetime": 3,
    "pattern-index": 3, "dimensional-embedding": 3, "profile": 3,
    # Advanced (4)
    "pln": 4, "miner": 4, "asmoses": 4, "benchmark": 4,
    # Learning (5)
    "learn": 5, "generate": 5, "language-learning": 5,
    # Language (6)
    "lg-atomese": 6, "relex": 6, "link-grammar": 6,
    # Robotics (7)
    "vision": 7, "perception": 7, "sensory": 7,
    "ros-behavior-scripting": 7, "robots_config": 7,
    "pau2motors": 7, "motor": 7,
    # Integration (8)
    "opencog": 8, "TinyCog": 8,
    # Specialized (9)
    "visualization": 9, "cheminformatics": 9, "agi-bio": 9,
    "ghost_bridge": 9, "matrix": 9, "python-attic": 9,
    "atomese-simd": 9,
}

LAYER_NAMES = [
    "Foundation", "Core", "Logic", "Cognitive", "Advanced",
    "Learning", "Language", "Robotics", "Integration", "Specialized",
]

# ── System/external packages (not org-oc components) ─────────────────────
SYSTEM_PKGS = {
    "boost", "doxygen", "valgrind", "cxxtest", "pgsql", "unixodbc",
    "rocksdb", "folly", "ocaml", "stack", "ghc", "openssl", "jsoncpp",
    "zmq", "pkgconfig", "tbb", "catkin", "opencv", "catch2", "gtk3",
    "festival", "openmp", "est", "wiringpi", "raspicam", "alsa",
    "guile", "pocketsphinx", "dlib", "protobuf", "octomap", "mpi",
    "linkgrammar", "uuid", "bfd", "iberty", "parallelstl", "pthreads",
    "stlport", "gnubacktrace", "attentionbank", "lgatomese",
}

# ── Known inter-component dependencies (from Mermaid + CMake analysis) ───
KNOWN_DEPS = {
    "atomspace":            ["cogutil"],
    "atomspace-storage":    ["cogutil", "atomspace"],
    "atomspace-rocks":      ["cogutil", "atomspace"],
    "atomspace-pgres":      ["cogutil", "atomspace"],
    "atomspace-ipfs":       ["cogutil", "atomspace"],
    "atomspace-websockets": ["cogutil", "atomspace"],
    "atomspace-restful":    ["cogutil", "atomspace", "cogserver"],
    "atomspace-bridge":     ["cogutil", "atomspace"],
    "atomspace-metta":      ["cogutil", "atomspace"],
    "atomspace-rpc":        ["cogutil", "atomspace"],
    "atomspace-cog":        ["cogutil", "atomspace", "cogserver"],
    "atomspace-agents":     ["cogutil", "atomspace"],
    "atomspace-dht":        ["cogutil", "atomspace"],
    "unify":                ["cogutil", "atomspace"],
    "ure":                  ["cogutil", "atomspace", "unify"],
    "cogserver":            ["cogutil", "atomspace"],
    "attention":            ["cogutil", "atomspace", "cogserver"],
    "spacetime":            ["cogutil", "atomspace"],
    "pattern-index":        ["cogutil", "atomspace"],
    "dimensional-embedding":["cogutil", "atomspace"],
    "pln":                  ["cogutil", "atomspace", "ure", "spacetime"],
    "miner":                ["cogutil", "atomspace", "ure", "unify"],
    "asmoses":              ["cogutil", "atomspace", "ure"],
    "benchmark":            ["cogutil", "atomspace", "ure"],
    "learn":                ["cogutil", "atomspace", "cogserver"],
    "generate":             ["cogutil", "atomspace"],
    "lg-atomese":           ["cogutil", "atomspace"],
    "vision":               ["cogutil", "atomspace"],
    "sensory":              ["cogutil", "atomspace"],
    "opencog":              ["cogutil", "atomspace", "cogserver", "attention", "ure", "pln"],
    "cheminformatics":      ["cogutil", "atomspace"],
    "agi-bio":              ["cogutil", "atomspace"],
    "visualization":        ["cogutil", "atomspace"],
    "python-attic":         ["cogutil", "atomspace", "cogserver", "ure", "pln"],
}


def scan_cmake_find_packages(repo_root: str, component: str) -> list[str]:
    """Parse CMakeLists.txt for find_package / FIND_PACKAGE calls."""
    cmake_path = Path(repo_root) / component / "CMakeLists.txt"
    if not cmake_path.exists():
        return []
    text = cmake_path.read_text(errors="replace")
    # Match find_package(CogUtil ...) etc.
    found = set()
    for m in re.finditer(r"(?i)find_package\s*\(\s*(\w+)", text):
        pkg = m.group(1).lower()
        found.add(pkg)
    return list(found)


def normalize(name: str) -> str:
    """Normalize component name to directory name."""
    return name.lower().replace("_", "-")


def build_graph(repo_root: str) -> dict:
    """Build the full dependency graph."""
    components = {}
    edges = []

    # Discover all component directories with CMakeLists.txt
    for d in sorted(Path(repo_root).iterdir()):
        if not d.is_dir():
            continue
        name = d.name
        cmake = d / "CMakeLists.txt"
        if not cmake.exists():
            continue
        layer = LAYER_MAP.get(name, -1)
        components[name] = {
            "name": name,
            "layer": layer,
            "layer_name": LAYER_NAMES[layer] if 0 <= layer < len(LAYER_NAMES) else "Unknown",
            "has_cmake": True,
            "deps": [],
        }

    # Merge known deps
    for comp, deps in KNOWN_DEPS.items():
        if comp in components:
            for dep in deps:
                if dep in components:
                    if dep not in components[comp]["deps"]:
                        components[comp]["deps"].append(dep)
                    edges.append({"from": dep, "to": comp})

    # Augment with CMake find_package scanning
    cmake_pkg_to_component = {
        "cogutil": "cogutil", "atomspace": "atomspace",
        "cogserver": "cogserver", "unify": "unify", "ure": "ure",
        "attention": "attention", "spacetime": "spacetime",
        "pln": "pln", "miner": "miner", "moses": "moses",
    }
    for comp in components:
        cmake_deps = scan_cmake_find_packages(repo_root, comp)
        for cpkg in cmake_deps:
            mapped = cmake_pkg_to_component.get(cpkg)
            if mapped and mapped in components and mapped != comp:
                if mapped not in components[comp]["deps"]:
                    components[comp]["deps"].append(mapped)
                    edges.append({"from": mapped, "to": comp})

    # Deduplicate edges
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["from"], e["to"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    return {
        "components": components,
        "edges": unique_edges,
        "layer_names": LAYER_NAMES,
    }


def topological_sort(components: dict) -> list[list[str]]:
    """Kahn's algorithm returning parallel tiers (concurrence groups)."""
    in_degree = defaultdict(int)
    adj = defaultdict(list)
    all_nodes = set(components.keys())

    for comp, info in components.items():
        for dep in info["deps"]:
            if dep in all_nodes:
                adj[dep].append(comp)
                in_degree[comp] += 1

    # Nodes with no in-edges
    queue = sorted([n for n in all_nodes if in_degree[n] == 0])
    tiers = []
    visited = set()

    while queue:
        tier = sorted(queue)
        tiers.append(tier)
        next_queue = []
        for node in tier:
            visited.add(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0 and neighbor not in visited:
                    next_queue.append(neighbor)
        queue = sorted(set(next_queue))

    # Detect cycles
    if len(visited) < len(all_nodes):
        remaining = all_nodes - visited
        tiers.append(sorted(list(remaining)))

    return tiers


def compute_critical_path(components: dict, tiers: list[list[str]]) -> list[str]:
    """Identify the longest dependency chain (critical path)."""
    # BFS/DFS longest path
    dist = {c: 0 for c in components}
    pred = {c: None for c in components}
    topo_order = [c for tier in tiers for c in tier]

    for node in topo_order:
        for dep in components[node]["deps"]:
            if dep in dist and dist[dep] + 1 > dist[node]:
                dist[node] = dist[dep] + 1
                pred[node] = dep

    # Find the node with max distance
    end_node = max(dist, key=dist.get)
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = pred[current]
    path.reverse()
    return path


def main():
    parser = argparse.ArgumentParser(description="Extract org-oc dependency graph")
    parser.add_argument("repo_root", help="Path to org-oc repository root")
    parser.add_argument("--output", "-o", default="deps.json", help="Output JSON file")
    args = parser.parse_args()

    graph = build_graph(args.repo_root)
    tiers = topological_sort(graph["components"])
    critical_path = compute_critical_path(graph["components"], tiers)

    result = {
        "repo": "o9nn/org-oc",
        "total_components": len(graph["components"]),
        "total_edges": len(graph["edges"]),
        "layers": graph["layer_names"],
        "components": graph["components"],
        "edges": graph["edges"],
        "build_tiers": tiers,
        "critical_path": critical_path,
        "tier_count": len(tiers),
    }

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Extracted {result['total_components']} components, "
          f"{result['total_edges']} edges, "
          f"{result['tier_count']} build tiers")
    print(f"Critical path ({len(critical_path)} steps): {' → '.join(critical_path)}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
