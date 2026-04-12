#!/usr/bin/env python3
"""
optimize_sequence.py — Iteratively refine the build sequence for org-oc.

Takes the dependency graph (from extract_deps.py) and iteratively
converges on the optimal sequence-vs-concurrence configuration by:

1. Starting from a naive topological sort
2. Simulating build execution with timing estimates
3. Applying heuristics: critical-path priority, concurrence widening,
   dependency-chain compression, and resource-aware scheduling
4. Iterating until the schedule converges (delta < threshold)

Outputs a build plan as JSON + GitHub Actions YAML.

Usage:
    python3 optimize_sequence.py deps.json [--max-iter 20] [--jobs 4] [--output plan.json]
"""

import argparse
import copy
import json
import math
import sys
from collections import defaultdict

# ── Estimated build times (minutes) based on component complexity ────────
# These are initial estimates; the optimizer refines them per iteration.
DEFAULT_TIMES = {
    "cogutil": 5, "moses": 12, "blender_api_msgs": 2,
    "atomspace": 15, "atomspace-storage": 8, "atomspace-rocks": 6,
    "atomspace-pgres": 6, "atomspace-ipfs": 5, "atomspace-websockets": 4,
    "atomspace-restful": 5, "atomspace-bridge": 5, "atomspace-metta": 5,
    "atomspace-rpc": 4, "atomspace-cog": 5, "atomspace-agents": 5,
    "atomspace-dht": 5, "atomspace-metta": 5,
    "unify": 6, "ure": 8,
    "cogserver": 8, "attention": 7, "spacetime": 5,
    "pattern-index": 5, "dimensional-embedding": 4,
    "pln": 10, "miner": 8, "asmoses": 12, "benchmark": 6,
    "learn": 6, "generate": 5, "language-learning": 4,
    "lg-atomese": 5, "relex": 4, "link-grammar": 8,
    "vision": 6, "perception": 4, "sensory": 3,
    "opencog": 15, "TinyCog": 5,
    "visualization": 4, "cheminformatics": 4, "agi-bio": 4,
    "ghost_bridge": 3, "matrix": 3, "python-attic": 5,
    "atomese-simd": 4,
}

DEFAULT_BUILD_TIME = 5  # minutes for unknown components


class BuildSimulator:
    """Simulate a parallel build schedule and compute makespan."""

    def __init__(self, components: dict, max_jobs: int, times: dict):
        self.components = components
        self.max_jobs = max_jobs
        self.times = times

    def simulate(self, tiers: list[list[str]]) -> dict:
        """Simulate build execution, return schedule with timing."""
        schedule = []
        clock = 0
        completed = set()
        running = {}  # comp -> finish_time

        flat_queue = [c for tier in tiers for c in tier]
        remaining = set(flat_queue)

        while remaining or running:
            # Check for completions
            newly_done = [c for c, ft in running.items() if ft <= clock]
            for c in newly_done:
                completed.add(c)
                del running[c]

            # Find ready components (all deps satisfied)
            ready = []
            for comp in list(remaining):
                deps = self.components.get(comp, {}).get("deps", [])
                if all(d in completed for d in deps):
                    ready.append(comp)

            # Schedule as many as max_jobs allows
            slots = self.max_jobs - len(running)
            for comp in sorted(ready, key=lambda c: -self._priority(c))[:slots]:
                build_time = self.times.get(comp, DEFAULT_BUILD_TIME)
                running[comp] = clock + build_time
                remaining.discard(comp)
                schedule.append({
                    "component": comp,
                    "start": clock,
                    "end": clock + build_time,
                    "duration": build_time,
                    "concurrent_with": list(running.keys()),
                })

            # Advance clock to next event
            if running:
                clock = min(running.values())
            elif remaining:
                clock += 1  # safety: avoid infinite loop

        makespan = max(s["end"] for s in schedule) if schedule else 0
        return {
            "schedule": schedule,
            "makespan": makespan,
            "total_build_time": sum(s["duration"] for s in schedule),
            "parallelism_efficiency": (
                sum(s["duration"] for s in schedule) / (makespan * self.max_jobs)
                if makespan > 0 else 0
            ),
        }

    def _priority(self, comp: str) -> float:
        """Priority score: critical-path components get higher priority."""
        # Longest remaining chain from this component
        return self._chain_length(comp, set())

    def _chain_length(self, comp: str, visited: set) -> int:
        if comp in visited:
            return 0
        visited.add(comp)
        deps = self.components.get(comp, {}).get("deps", [])
        if not deps:
            return self.times.get(comp, DEFAULT_BUILD_TIME)
        return self.times.get(comp, DEFAULT_BUILD_TIME) + max(
            self._chain_length(d, visited) for d in deps if d in self.components
        )


def reorder_tiers(tiers: list[list[str]], components: dict,
                  times: dict) -> list[list[str]]:
    """Reorder within tiers by critical-path priority (longest chain first)."""
    def chain_len(comp, visited=None):
        if visited is None:
            visited = set()
        if comp in visited:
            return 0
        visited.add(comp)
        deps = components.get(comp, {}).get("deps", [])
        downstream = [d for d in deps if d in components]
        t = times.get(comp, DEFAULT_BUILD_TIME)
        if not downstream:
            return t
        return t + max(chain_len(d, visited.copy()) for d in downstream)

    new_tiers = []
    for tier in tiers:
        sorted_tier = sorted(tier, key=lambda c: -chain_len(c))
        new_tiers.append(sorted_tier)
    return new_tiers


def split_wide_tiers(tiers: list[list[str]], max_width: int) -> list[list[str]]:
    """Split tiers wider than max_width into sub-tiers for resource control."""
    result = []
    for tier in tiers:
        for i in range(0, len(tier), max_width):
            result.append(tier[i:i + max_width])
    return result


def merge_thin_tiers(tiers: list[list[str]], components: dict,
                     min_width: int) -> list[list[str]]:
    """Merge adjacent thin tiers if dependencies allow."""
    if len(tiers) <= 1:
        return tiers

    result = [list(tiers[0])]
    for tier in tiers[1:]:
        prev = result[-1]
        # Check if all items in tier have deps only in earlier tiers
        can_merge = len(prev) + len(tier) <= min_width * 2
        if can_merge:
            # Verify no dependency within the merged set
            merged_set = set(prev) | set(tier)
            conflict = False
            for comp in tier:
                deps = components.get(comp, {}).get("deps", [])
                if any(d in set(prev) for d in deps):
                    conflict = True
                    break
            if not conflict:
                result[-1].extend(tier)
                continue
        result.append(list(tier))
    return result


def iterate(deps_data: dict, max_jobs: int, max_iter: int) -> dict:
    """Main iterative refinement loop."""
    components = deps_data["components"]
    tiers = deps_data["build_tiers"]
    times = {c: DEFAULT_TIMES.get(c, DEFAULT_BUILD_TIME) for c in components}

    sim = BuildSimulator(components, max_jobs, times)
    best_plan = None
    best_makespan = float("inf")
    history = []

    for iteration in range(max_iter):
        # Step 1: Reorder within tiers by critical-path priority
        tiers = reorder_tiers(tiers, components, times)

        # Step 2: Resource-aware tier splitting/merging
        if max_jobs < 8:
            tiers = split_wide_tiers(tiers, max_jobs)
        tiers = merge_thin_tiers(tiers, components, max_jobs)

        # Step 3: Simulate
        result = sim.simulate(tiers)
        makespan = result["makespan"]

        history.append({
            "iteration": iteration,
            "makespan": makespan,
            "tier_count": len(tiers),
            "efficiency": result["parallelism_efficiency"],
        })

        if makespan < best_makespan:
            best_makespan = makespan
            best_plan = {
                "tiers": copy.deepcopy(tiers),
                "schedule": result["schedule"],
                "makespan": makespan,
                "total_build_time": result["total_build_time"],
                "efficiency": result["parallelism_efficiency"],
            }

        # Step 4: Check convergence
        if len(history) >= 3:
            recent = [h["makespan"] for h in history[-3:]]
            delta = max(recent) - min(recent)
            if delta < 0.5:
                break

        # Step 5: Perturb — try swapping within tiers
        for ti, tier in enumerate(tiers):
            if len(tier) > 1:
                # Move the slowest component earlier in the tier
                slowest = max(tier, key=lambda c: times.get(c, DEFAULT_BUILD_TIME))
                tier.remove(slowest)
                tier.insert(0, slowest)

    return {
        "best_plan": best_plan,
        "iterations": len(history),
        "converged": len(history) < max_iter,
        "history": history,
        "components": components,
        "times": times,
    }


def generate_gha_yaml(plan: dict, components: dict, max_jobs: int) -> str:
    """Generate a GitHub Actions workflow YAML from the optimized plan."""
    lines = [
        "# Auto-generated by oc-build-optimizer",
        "# Optimized build sequence for o9nn/org-oc",
        f"# Makespan: {plan['makespan']:.0f} min | Efficiency: {plan['efficiency']:.1%}",
        "",
        "name: OC Optimized Build",
        "",
        "on:",
        "  push:",
        "    branches: [main]",
        "  pull_request:",
        "    branches: [main]",
        "  workflow_dispatch:",
        "",
        "env:",
        "  CMAKE_BUILD_TYPE: Release",
        '  MAKEFLAGS: "-j$(nproc)"',
        "",
        "jobs:",
    ]

    tier_job_names = {}  # tier_index -> list of job names

    for ti, tier in enumerate(plan["tiers"]):
        tier_job_names[ti] = []
        for comp in tier:
            job_name = comp.replace("-", "_").replace(".", "_")
            tier_job_names[ti].append(job_name)
            deps = components.get(comp, {}).get("deps", [])

            # Find which tier each dep is in
            needs = []
            for dep in deps:
                dep_job = dep.replace("-", "_").replace(".", "_")
                for prev_ti in range(ti):
                    if dep in plan["tiers"][prev_ti]:
                        needs.append(dep_job)
                        break

            lines.append(f"  {job_name}:")
            lines.append(f'    name: "Tier {ti}: {comp}"')
            lines.append("    runs-on: ubuntu-latest")
            if needs:
                lines.append(f"    needs: [{', '.join(needs)}]")
            lines.append("    continue-on-error: true")
            lines.append("    steps:")
            lines.append("      - uses: actions/checkout@v4")
            lines.append(f"      - name: Build {comp}")
            lines.append("        run: |")
            lines.append(f"          if [ -d \"{comp}\" ] && [ -f \"{comp}/CMakeLists.txt\" ]; then")
            lines.append(f"            cd {comp} && mkdir -p build && cd build")
            lines.append(f"            cmake .. -DCMAKE_BUILD_TYPE=${{{{CMAKE_BUILD_TYPE}}}}")
            lines.append(f"            make ${{{{MAKEFLAGS}}}}")
            lines.append(f"            sudo make install && sudo ldconfig")
            lines.append(f"          else")
            lines.append(f'            echo "Skipping {comp}: no CMakeLists.txt"')
            lines.append(f"          fi")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Optimize org-oc build sequence")
    parser.add_argument("deps_json", help="Dependency graph JSON from extract_deps.py")
    parser.add_argument("--max-iter", type=int, default=20, help="Max iterations")
    parser.add_argument("--jobs", type=int, default=4, help="Max parallel jobs")
    parser.add_argument("--output", "-o", default="plan.json", help="Output plan JSON")
    parser.add_argument("--yaml", default=None, help="Output GHA workflow YAML")
    args = parser.parse_args()

    with open(args.deps_json) as f:
        deps_data = json.load(f)

    print(f"Optimizing build for {deps_data['total_components']} components, "
          f"max {args.jobs} parallel jobs...")

    result = iterate(deps_data, args.jobs, args.max_iter)

    plan = result["best_plan"]
    print(f"\nConverged after {result['iterations']} iterations")
    print(f"Makespan: {plan['makespan']:.0f} min "
          f"(vs {plan['total_build_time']:.0f} min sequential)")
    print(f"Parallelism efficiency: {plan['efficiency']:.1%}")
    print(f"Build tiers: {len(plan['tiers'])}")

    for ti, tier in enumerate(plan["tiers"]):
        print(f"  Tier {ti}: {', '.join(tier)}")

    # Save plan
    output = {
        "iterations": result["iterations"],
        "converged": result["converged"],
        "makespan_minutes": plan["makespan"],
        "sequential_minutes": plan["total_build_time"],
        "speedup": plan["total_build_time"] / plan["makespan"] if plan["makespan"] > 0 else 0,
        "efficiency": plan["efficiency"],
        "max_parallel_jobs": args.jobs,
        "tier_count": len(plan["tiers"]),
        "tiers": plan["tiers"],
        "schedule": plan["schedule"],
        "history": result["history"],
        "component_times": result["times"],
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nPlan saved to {args.output}")

    # Generate YAML if requested
    if args.yaml:
        yaml_content = generate_gha_yaml(plan, result["components"], args.jobs)
        with open(args.yaml, "w") as f:
            f.write(yaml_content)
        print(f"GitHub Actions workflow saved to {args.yaml}")


if __name__ == "__main__":
    main()
