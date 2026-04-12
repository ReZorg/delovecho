#!/usr/bin/env python3
"""
self_update.py — Write the refined build model back into the skill itself.

After each iteration, this script:
1. Reads the current build model from model/build_model.json
2. Regenerates references/dependency-graph.md from the model
3. Regenerates references/gha-patterns.md with accumulated fixes
4. Updates model/optimal-build.yml from the model
5. Generates a human-readable iteration report
6. Optionally commits changes to the skill repo

This is the "self-modifying" core — the skill's own reference files
evolve with each iteration, encoding everything learned.

Usage:
    python3 self_update.py                    # Update all skill files from model
    python3 self_update.py --report           # Also generate iteration report
    python3 self_update.py --commit           # Also git commit the changes
    python3 self_update.py --push-yml <repo>  # Push optimal-build.yml to org-oc
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = SKILL_DIR / "model" / "build_model.json"
DEP_GRAPH_PATH = SKILL_DIR / "references" / "dependency-graph.md"
GHA_PATTERNS_PATH = SKILL_DIR / "references" / "gha-patterns.md"
OPTIMAL_YML = SKILL_DIR / "model" / "optimal-build.yml"
REPORT_DIR = SKILL_DIR / "model" / "reports"


def load_model() -> dict:
    with open(MODEL_PATH) as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════════════════
# Regenerate dependency-graph.md
# ═══════════════════════════════════════════════════════════════════════════

def regenerate_dependency_graph(model: dict):
    """Rewrite references/dependency-graph.md from the current model."""
    components = model["components"]
    tiers = model["build_sequence"].get("tiers", [])
    crit_path = model["build_sequence"].get("critical_path", [])
    iteration = model["_meta"]["iterations_completed"]

    # Group by layer
    layers = defaultdict(list)
    for name, info in components.items():
        layers[info.get("layer", -1)].append(name)

    layer_names = [
        "Foundation", "Core", "Logic", "Cognitive", "Advanced",
        "Learning", "Language", "Robotics", "Integration", "Specialized",
    ]

    lines = [
        "# org-oc Dependency Graph Reference",
        "",
        f"> Auto-generated from build model (iteration {iteration}). "
        f"Last updated: {model['_meta']['last_updated']}",
        "",
        "## Table of Contents",
        "",
        "1. [Layer Architecture](#layer-architecture)",
        "2. [Build Tiers (Optimized)](#build-tiers-optimized)",
        "3. [Critical Build Path](#critical-build-path)",
        "4. [Component Catalog](#component-catalog)",
        "5. [Known Inter-Component Dependencies](#known-inter-component-dependencies)",
        "6. [System-Level Dependencies](#system-level-dependencies)",
        "7. [Accumulated Fixes](#accumulated-fixes)",
        "",
        "## Layer Architecture",
        "",
        "| Layer | Name | Components | Status |",
        "|-------|------|-----------|--------|",
    ]

    for li in range(10):
        name = layer_names[li] if li < len(layer_names) else "Unknown"
        comps = sorted(layers.get(li, []))
        statuses = [components[c].get("status", "untested") for c in comps]
        ok = sum(1 for s in statuses if s == "success")
        fail = sum(1 for s in statuses if s not in ("success", "untested", "no_cmake", "skipped"))
        status_str = f"{ok}✓ {fail}✗" if ok + fail > 0 else "untested"
        lines.append(f"| {li} | {name} | {', '.join(comps)} | {status_str} |")

    lines.extend([
        "",
        "## Build Tiers (Optimized)",
        "",
        "Components within each tier build **concurrently**; tiers execute **sequentially**.",
        "",
    ])

    for ti, tier in enumerate(tiers):
        tier_time = max(components.get(c, {}).get("build_time_est", 5) for c in tier) if tier else 0
        lines.append(f"**Tier {ti}** (~{tier_time} min): {', '.join(tier)}")

    lines.extend([
        "",
        "## Critical Build Path",
        "",
        "The longest dependency chain determining minimum build time:",
        "",
        "```",
    ])

    if crit_path:
        parts = []
        total = 0
        for c in crit_path:
            t = components.get(c, {}).get("build_time_est", 5)
            parts.append(f"{c} ({t}m)")
            total += t
        lines.append(" → ".join(parts))
        lines.append(f"Total: {total} min minimum")
    lines.append("```")

    lines.extend([
        "",
        "## Component Catalog",
        "",
        "| Component | Layer | Deps | Sys Deps | Est. Time | Status |",
        "|-----------|-------|------|----------|-----------|--------|",
    ])

    for name in sorted(components.keys()):
        info = components[name]
        deps = ", ".join(info.get("deps", [])) or "—"
        sys_deps = ", ".join(info.get("sys_deps", [])) or "—"
        t = info.get("build_time_est", 5)
        status = info.get("status", "untested")
        lines.append(f"| {name} | {info.get('layer', '?')} | {deps} | {sys_deps} | {t}m | {status} |")

    lines.extend([
        "",
        "## Known Inter-Component Dependencies",
        "",
        "Verified dependencies (auto-updated from build diagnosis):",
        "",
        "```",
    ])

    for name in sorted(components.keys()):
        deps = components[name].get("deps", [])
        if deps:
            lines.append(f"{name:25s} → {', '.join(deps)}")
        else:
            lines.append(f"{name:25s} → (no org-oc deps)")
    lines.append("```")

    lines.extend([
        "",
        "## System-Level Dependencies",
        "",
        "| Package | Required By |",
        "|---------|------------|",
    ])

    pkg_users = defaultdict(list)
    for name, info in components.items():
        for pkg in info.get("sys_deps", []):
            pkg_users[pkg].append(name)
    for pkg in sorted(pkg_users.keys()):
        lines.append(f"| {pkg} | {', '.join(sorted(pkg_users[pkg]))} |")

    lines.extend([
        "",
        "## Accumulated Fixes",
        "",
        "Fixes discovered and applied through iterative diagnosis:",
        "",
    ])

    any_fixes = False
    for name in sorted(components.keys()):
        fixes = components[name].get("fixes_applied", [])
        if fixes:
            any_fixes = True
            lines.append(f"**{name}**:")
            for fix in fixes:
                lines.append(f"- {fix}")
            lines.append("")

    if not any_fixes:
        lines.append("No fixes applied yet.")

    lines.append("")

    DEP_GRAPH_PATH.write_text("\n".join(lines))
    print(f"  ✓ Updated {DEP_GRAPH_PATH}")


# ═══════════════════════════════════════════════════════════════════════════
# Regenerate gha-patterns.md
# ═══════════════════════════════════════════════════════════════════════════

def regenerate_gha_patterns(model: dict):
    """Rewrite references/gha-patterns.md with accumulated knowledge."""
    components = model["components"]
    iteration = model["_meta"]["iterations_completed"]

    # Collect all extra steps
    all_before = []
    all_after = []
    for name, info in components.items():
        for step in info.get("extra_steps", []):
            entry = f"[{name}] {step['step']}"
            if step.get("when") == "before_build":
                all_before.append(entry)
            else:
                all_after.append(entry)

    lines = [
        "# GitHub Actions Workflow Patterns for org-oc",
        "",
        f"> Auto-generated from build model (iteration {iteration}). "
        f"Last updated: {model['_meta']['last_updated']}",
        "",
        "## Container Strategy",
        "",
        "Two proven approaches exist for org-oc CI:",
        "",
        "**Option A: opencog/opencog-deps container** (from config.yml / CircleCI)",
        "- Pre-installed system dependencies, fastest cold start",
        "- Use `image: opencog/opencog-deps` with `--user root`",
        "- Includes Guile, Boost, CxxTest, Python bindings",
        "",
        "**Option B: ubuntu:22.04 bare** (from consolidated-build)",
        "- More control, explicit dependency installation",
        "- Requires `apt-get install` step per job",
        "- Better for debugging dependency issues",
        "",
        "Recommended: Use opencog-deps for the main build, bare ubuntu for validation.",
        "",
        "## System Packages (Consolidated)",
        "",
        "All system packages required across all components:",
        "",
        "```bash",
        "sudo apt-get install -y \\",
    ]

    all_sys = set()
    for info in components.values():
        all_sys.update(info.get("sys_deps", []))
    for pkg in sorted(all_sys):
        lines.append(f"  {pkg} \\")
    lines.append("```")

    lines.extend([
        "",
        "## Artifact Passing Pattern",
        "",
        "Each component uploads its install artifacts for downstream jobs:",
        "",
        "```yaml",
        "- uses: actions/upload-artifact@v4",
        "  with:",
        "    name: <component>-install",
        "    path: |",
        "      /usr/local/include/opencog",
        "      /usr/local/lib/opencog",
        "      /usr/local/lib/cmake",
        "      /usr/local/share/opencog",
        "```",
        "",
        "Downstream jobs download and restore:",
        "",
        "```yaml",
        "- uses: actions/download-artifact@v4",
        "  with:",
        "    name: <dep>-install",
        "    path: /tmp/<dep>-install",
        "- run: sudo cp -r /tmp/<dep>-install/* / && sudo ldconfig",
        "```",
        "",
        "## Known Build Fixes (Auto-Accumulated)",
        "",
        "Fixes discovered through iterative diagnosis:",
        "",
    ])

    fix_num = 1
    # Static known fixes
    static_fixes = [
        "**atomspace missing lib/ directory**: Create `mkdir -p lib && echo '# Build compatibility' > lib/CMakeLists.txt`",
        "**Cython version mismatch**: Always `pip install --upgrade cython` before building Python bindings",
        "**ldconfig after install**: Every `sudo make install` must be followed by `sudo ldconfig`",
        '**opencog/lib path**: Add `echo "/usr/local/lib/opencog" | sudo tee /etc/ld.so.conf.d/opencog.conf`',
        "**Boost discovery**: Set `-DBOOST_ROOT` and `-DCMAKE_PREFIX_PATH` when using conda-based Boost",
        "**atomspace-storage prerequisite**: Many atomspace-* extensions require atomspace-storage installed first",
    ]
    for fix in static_fixes:
        lines.append(f"{fix_num}. {fix}")
        fix_num += 1

    # Dynamic fixes from model
    for name in sorted(components.keys()):
        for fix in components[name].get("fixes_applied", []):
            lines.append(f"{fix_num}. **{name}**: {fix}")
            fix_num += 1

    if all_before:
        lines.extend(["", "### Pre-Build Steps", ""])
        for step in all_before:
            lines.append(f"- {step}")

    if all_after:
        lines.extend(["", "### Post-Install Steps", ""])
        for step in all_after:
            lines.append(f"- {step}")

    lines.append("")

    GHA_PATTERNS_PATH.write_text("\n".join(lines))
    print(f"  ✓ Updated {GHA_PATTERNS_PATH}")


# ═══════════════════════════════════════════════════════════════════════════
# Generate Iteration Report
# ═══════════════════════════════════════════════════════════════════════════

def generate_report(model: dict) -> str:
    """Generate a human-readable iteration report."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    iteration = model["_meta"]["iterations_completed"]
    report_path = REPORT_DIR / f"iteration-{iteration:03d}.md"

    components = model["components"]
    tiers = model["build_sequence"].get("tiers", [])
    crit_path = model["build_sequence"].get("critical_path", [])
    makespan = model["build_sequence"].get("makespan_est", "?")
    speedup = model["build_sequence"].get("speedup", "?")
    log = model.get("iteration_log", [])

    lines = [
        f"# Iteration {iteration} Report",
        "",
        f"**Date**: {model['_meta']['last_updated']}",
        f"**Convergence**: {model['_meta']['convergence_status']}",
        "",
        "## Build Sequence",
        "",
        f"- **Tiers**: {len(tiers)}",
        f"- **Makespan**: {makespan} min",
        f"- **Speedup**: {speedup}x",
        f"- **Critical path**: {' → '.join(crit_path)}",
        "",
        "## Tier Breakdown",
        "",
        "| Tier | Components | Max Time | Width |",
        "|------|-----------|----------|-------|",
    ]

    for ti, tier in enumerate(tiers):
        max_t = max(components.get(c, {}).get("build_time_est", 5) for c in tier) if tier else 0
        lines.append(f"| T{ti} | {', '.join(tier)} | {max_t}m | {len(tier)} |")

    lines.extend([
        "",
        "## Component Status",
        "",
        "| Component | Status | Errors | Fixes |",
        "|-----------|--------|--------|-------|",
    ])

    for name in sorted(components.keys()):
        info = components[name]
        status = info.get("status", "untested")
        errors = len(info.get("errors", []))
        fixes = len(info.get("fixes_applied", []))
        lines.append(f"| {name} | {status} | {errors} | {fixes} |")

    if log:
        lines.extend([
            "",
            "## Iteration History",
            "",
            "| Iter | Tiers | Makespan | Fixes | Diagnoses | OK | Fail |",
            "|------|-------|----------|-------|-----------|-----|------|",
        ])
        for entry in log:
            lines.append(
                f"| {entry.get('iteration', '?')} | {entry.get('tier_count', '-')} | "
                f"{entry.get('makespan_est', '-')}m | {entry.get('fixes_applied', 0)} | "
                f"{entry.get('diagnoses_found', 0)} | {entry.get('components_success', '-')} | "
                f"{entry.get('components_failed', '-')} |"
            )

    lines.append("")
    report_text = "\n".join(lines)
    report_path.write_text(report_text)
    print(f"  ✓ Generated report: {report_path}")
    return str(report_path)


# ═══════════════════════════════════════════════════════════════════════════
# Push to repo
# ═══════════════════════════════════════════════════════════════════════════

def push_yml_to_repo(repo_slug: str):
    """Push optimal-build.yml to the target repository."""
    try:
        # Use gh api to update the file
        import base64
        yml_content = OPTIMAL_YML.read_text()
        encoded = base64.b64encode(yml_content.encode()).decode()

        # Get current SHA if file exists
        result = subprocess.run(
            ["gh", "api", f"/repos/{repo_slug}/contents/.github/workflows/optimal-build.yml",
             "--jq", ".sha"],
            capture_output=True, text=True
        )
        sha = result.stdout.strip() if result.returncode == 0 else None

        payload = {
            "message": f"chore: update optimal-build.yml (iteration {load_model()['_meta']['iterations_completed']})",
            "content": encoded,
        }
        if sha:
            payload["sha"] = sha

        result = subprocess.run(
            ["gh", "api", f"/repos/{repo_slug}/contents/.github/workflows/optimal-build.yml",
             "-X", "PUT", "--input", "-"],
            input=json.dumps(payload), capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  ✓ Pushed optimal-build.yml to {repo_slug}")
        else:
            print(f"  ✗ Failed to push: {result.stderr}")
    except Exception as e:
        print(f"  ✗ Push failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# Git commit skill changes
# ═══════════════════════════════════════════════════════════════════════════

def commit_skill_changes(model: dict):
    """Git commit all changes within the skill directory."""
    iteration = model["_meta"]["iterations_completed"]
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(SKILL_DIR), check=True,
                       capture_output=True)
        subprocess.run(
            ["git", "commit", "-m",
             f"chore: self-update after iteration {iteration} "
             f"({model['_meta']['convergence_status']})"],
            cwd=str(SKILL_DIR), check=True, capture_output=True
        )
        print(f"  ✓ Committed skill changes (iteration {iteration})")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠ Git commit skipped: {e.stderr.decode()[:200] if e.stderr else 'no changes'}")


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Self-update skill files from the refined build model"
    )
    parser.add_argument("--report", action="store_true", help="Generate iteration report")
    parser.add_argument("--commit", action="store_true", help="Git commit changes")
    parser.add_argument("--push-yml", help="Push optimal-build.yml to GitHub repo (e.g. o9nn/org-oc)")
    args = parser.parse_args()

    print("=" * 70)
    print("  OC Build Optimizer — Self-Update")
    print("=" * 70)

    model = load_model()
    iteration = model["_meta"]["iterations_completed"]
    print(f"\n  Model iteration: {iteration}")
    print(f"  Convergence: {model['_meta']['convergence_status']}")

    print("\n[1/4] Regenerating dependency-graph.md...")
    regenerate_dependency_graph(model)

    print("\n[2/4] Regenerating gha-patterns.md...")
    regenerate_gha_patterns(model)

    print("\n[3/4] Verifying optimal-build.yml...")
    if OPTIMAL_YML.exists():
        print(f"  ✓ optimal-build.yml exists ({OPTIMAL_YML.stat().st_size} bytes)")
    else:
        print("  ⚠ optimal-build.yml not found — run run_iteration.py first")

    if args.report:
        print("\n[3b/4] Generating iteration report...")
        generate_report(model)

    if args.push_yml:
        print(f"\n[3c/4] Pushing optimal-build.yml to {args.push_yml}...")
        push_yml_to_repo(args.push_yml)

    if args.commit:
        print("\n[4/4] Committing skill changes...")
        commit_skill_changes(model)
    else:
        print("\n[4/4] Skipping git commit (use --commit to enable)")

    print("\n  ✅ Self-update complete")
    print(f"  Updated files:")
    print(f"    {DEP_GRAPH_PATH}")
    print(f"    {GHA_PATTERNS_PATH}")
    print(f"    {MODEL_PATH}")
    if OPTIMAL_YML.exists():
        print(f"    {OPTIMAL_YML}")


if __name__ == "__main__":
    main()
