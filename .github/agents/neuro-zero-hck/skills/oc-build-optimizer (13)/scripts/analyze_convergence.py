#!/usr/bin/env python3
"""
analyze_convergence.py — Analyze optimizer convergence and generate reports.

Reads the plan.json from optimize_sequence.py and produces:
- Convergence plot data (iterations vs makespan)
- Tier utilization analysis
- Critical path identification
- Recommendations for further optimization

Usage:
    python3 analyze_convergence.py plan.json [--report report.md]
"""

import argparse
import json
import sys
from collections import defaultdict


def analyze(plan_data: dict) -> dict:
    """Analyze the optimized build plan."""
    tiers = plan_data["tiers"]
    schedule = plan_data["schedule"]
    times = plan_data.get("component_times", {})
    history = plan_data.get("history", [])

    # Tier utilization
    tier_stats = []
    for ti, tier in enumerate(tiers):
        tier_time = sum(times.get(c, 5) for c in tier)
        max_comp_time = max(times.get(c, 5) for c in tier) if tier else 0
        tier_stats.append({
            "tier": ti,
            "components": tier,
            "width": len(tier),
            "total_time": tier_time,
            "max_component_time": max_comp_time,
            "utilization": tier_time / (max_comp_time * len(tier)) if tier else 0,
        })

    # Convergence analysis
    convergence = {
        "iterations": len(history),
        "initial_makespan": history[0]["makespan"] if history else 0,
        "final_makespan": history[-1]["makespan"] if history else 0,
        "improvement_pct": (
            (history[0]["makespan"] - history[-1]["makespan"]) / history[0]["makespan"] * 100
            if history and history[0]["makespan"] > 0 else 0
        ),
        "converged": plan_data.get("converged", False),
    }

    # Bottleneck identification
    bottlenecks = []
    for ts in tier_stats:
        if ts["width"] == 1 and ts["max_component_time"] > 8:
            bottlenecks.append({
                "tier": ts["tier"],
                "component": ts["components"][0],
                "time": ts["max_component_time"],
                "reason": "single-component tier with long build time",
            })
        if ts["utilization"] < 0.5 and ts["width"] > 1:
            bottlenecks.append({
                "tier": ts["tier"],
                "components": ts["components"],
                "utilization": ts["utilization"],
                "reason": "low tier utilization — unbalanced component times",
            })

    # Recommendations
    recommendations = []
    if plan_data["speedup"] < 2.0:
        recommendations.append(
            "Low speedup — consider increasing max parallel jobs or "
            "breaking large components into sub-targets."
        )
    if len(bottlenecks) > 0:
        recommendations.append(
            f"Found {len(bottlenecks)} bottleneck(s). Consider caching or "
            "pre-building bottleneck components."
        )
    if not convergence["converged"]:
        recommendations.append(
            "Optimizer did not converge — increase --max-iter or review "
            "dependency graph for cycles."
        )
    if plan_data["efficiency"] < 0.3:
        recommendations.append(
            "Parallelism efficiency below 30%. The dependency chain is "
            "too serial — consider restructuring component boundaries."
        )

    return {
        "tier_stats": tier_stats,
        "convergence": convergence,
        "bottlenecks": bottlenecks,
        "recommendations": recommendations,
    }


def generate_report(plan_data: dict, analysis: dict) -> str:
    """Generate a Markdown report."""
    lines = [
        "# OC Build Optimizer — Convergence Report",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Components | {len(plan_data['tiers'])} tiers, "
        f"{sum(len(t) for t in plan_data['tiers'])} components |",
        f"| Makespan | {plan_data['makespan_minutes']:.0f} min |",
        f"| Sequential time | {plan_data['sequential_minutes']:.0f} min |",
        f"| Speedup | {plan_data['speedup']:.2f}x |",
        f"| Efficiency | {plan_data['efficiency']:.1%} |",
        f"| Parallel jobs | {plan_data['max_parallel_jobs']} |",
        f"| Iterations | {analysis['convergence']['iterations']} |",
        f"| Converged | {'Yes' if analysis['convergence']['converged'] else 'No'} |",
        "",
        "## Optimized Build Tiers",
        "",
    ]

    for ts in analysis["tier_stats"]:
        comps = ", ".join(ts["components"])
        lines.append(
            f"**Tier {ts['tier']}** ({ts['width']} components, "
            f"~{ts['max_component_time']} min): {comps}"
        )
    lines.append("")

    if analysis["bottlenecks"]:
        lines.append("## Bottlenecks")
        lines.append("")
        for b in analysis["bottlenecks"]:
            lines.append(f"- **Tier {b['tier']}**: {b['reason']}")
        lines.append("")

    if analysis["recommendations"]:
        lines.append("## Recommendations")
        lines.append("")
        for r in analysis["recommendations"]:
            lines.append(f"- {r}")
        lines.append("")

    if analysis["convergence"]["iterations"] > 1:
        lines.append("## Convergence History")
        lines.append("")
        lines.append("| Iteration | Makespan (min) | Tiers | Efficiency |")
        lines.append("|-----------|---------------|-------|------------|")
        for h in plan_data.get("history", []):
            lines.append(
                f"| {h['iteration']} | {h['makespan']:.0f} | "
                f"{h['tier_count']} | {h['efficiency']:.1%} |"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze build optimizer convergence")
    parser.add_argument("plan_json", help="Optimized plan JSON")
    parser.add_argument("--report", "-r", default="report.md", help="Output report")
    args = parser.parse_args()

    with open(args.plan_json) as f:
        plan_data = json.load(f)

    analysis = analyze(plan_data)
    report = generate_report(plan_data, analysis)

    with open(args.report, "w") as f:
        f.write(report)

    print(f"Report saved to {args.report}")
    print(f"\nKey findings:")
    print(f"  Speedup: {plan_data['speedup']:.2f}x")
    print(f"  Bottlenecks: {len(analysis['bottlenecks'])}")
    print(f"  Recommendations: {len(analysis['recommendations'])}")

    for r in analysis["recommendations"]:
        print(f"  → {r}")


if __name__ == "__main__":
    main()
