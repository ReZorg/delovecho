#!/usr/bin/env python3
"""
integrate_feedback.py — Integrate real build results to refine estimates.

Reads GitHub Actions run logs or local build timing data and updates
the component time estimates used by optimize_sequence.py.

This closes the autognosis loop: plan → build → observe → refine → plan.

Usage:
    python3 integrate_feedback.py plan.json --timings timings.json [--output updated_plan.json]
    python3 integrate_feedback.py plan.json --gha-run <run_id> [--repo o9nn/org-oc]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_timings_from_file(path: str) -> dict:
    """Load component timings from a JSON file.

    Expected format:
    {
        "cogutil": {"duration_minutes": 4.2, "status": "success"},
        "atomspace": {"duration_minutes": 13.8, "status": "success"},
        ...
    }
    """
    with open(path) as f:
        return json.load(f)


def load_timings_from_gha(repo: str, run_id: str) -> dict:
    """Fetch timing data from a GitHub Actions run via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "run", "view", run_id, "--repo", repo, "--json",
             "jobs", "--jq", ".jobs"],
            capture_output=True, text=True, check=True
        )
        jobs = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error fetching GHA run: {e}", file=sys.stderr)
        return {}

    timings = {}
    for job in jobs:
        name = job.get("name", "")
        # Extract component name from job name like "Tier 0: cogutil"
        if ":" in name:
            comp = name.split(":")[-1].strip()
        else:
            comp = name.strip()

        started = job.get("startedAt", "")
        completed = job.get("completedAt", "")
        status = job.get("conclusion", "unknown")

        if started and completed:
            from datetime import datetime
            try:
                start_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(completed.replace("Z", "+00:00"))
                duration = (end_dt - start_dt).total_seconds() / 60.0
                timings[comp] = {
                    "duration_minutes": round(duration, 1),
                    "status": status,
                }
            except ValueError:
                pass

    return timings


def update_plan(plan_data: dict, timings: dict, alpha: float = 0.3) -> dict:
    """Update plan with observed timings using exponential moving average.

    alpha: learning rate (0 = keep old, 1 = use only new observation)
    """
    current_times = plan_data.get("component_times", {})
    updated_times = dict(current_times)

    updates = []
    for comp, obs in timings.items():
        if "duration_minutes" not in obs:
            continue
        observed = obs["duration_minutes"]
        old = current_times.get(comp, 5)
        new = alpha * observed + (1 - alpha) * old
        updated_times[comp] = round(new, 1)
        updates.append({
            "component": comp,
            "old_estimate": old,
            "observed": observed,
            "new_estimate": round(new, 1),
            "status": obs.get("status", "unknown"),
        })

    plan_data["component_times"] = updated_times
    plan_data["feedback_applied"] = True
    plan_data["feedback_updates"] = updates
    plan_data["feedback_alpha"] = alpha

    return plan_data


def main():
    parser = argparse.ArgumentParser(description="Integrate build feedback")
    parser.add_argument("plan_json", help="Current plan JSON")
    parser.add_argument("--timings", help="Timings JSON file")
    parser.add_argument("--gha-run", help="GitHub Actions run ID")
    parser.add_argument("--repo", default="o9nn/org-oc", help="GitHub repo")
    parser.add_argument("--alpha", type=float, default=0.3, help="Learning rate")
    parser.add_argument("--output", "-o", default=None, help="Output updated plan")
    args = parser.parse_args()

    with open(args.plan_json) as f:
        plan_data = json.load(f)

    if args.timings:
        timings = load_timings_from_file(args.timings)
    elif args.gha_run:
        timings = load_timings_from_gha(args.repo, args.gha_run)
    else:
        print("Error: provide --timings or --gha-run", file=sys.stderr)
        sys.exit(1)

    if not timings:
        print("No timing data found.", file=sys.stderr)
        sys.exit(1)

    updated = update_plan(plan_data, timings, args.alpha)

    output_path = args.output or args.plan_json
    with open(output_path, "w") as f:
        json.dump(updated, f, indent=2)

    print(f"Updated {len(updated['feedback_updates'])} component estimates:")
    for u in updated["feedback_updates"]:
        delta = u["new_estimate"] - u["old_estimate"]
        direction = "+" if delta > 0 else ""
        print(f"  {u['component']}: {u['old_estimate']} → {u['new_estimate']} "
              f"({direction}{delta:.1f} min) [{u['status']}]")

    print(f"\nUpdated plan saved to {output_path}")
    print("Run optimize_sequence.py again with updated times to re-converge.")


if __name__ == "__main__":
    main()
