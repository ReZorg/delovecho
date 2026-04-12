#!/usr/bin/env python3
"""
run_iteration.py — One full iteration of the build-optimize-diagnose-fix loop.

This is the main entry point for the self-correcting build optimizer.
Each invocation:

1. Loads the persistent build model from model/build_model.json
2. Computes the optimal build sequence from current model state
3. Attempts to build each component (locally or via GHA)
4. Captures errors, diagnoses them, proposes fixes
5. Applies fixes to the model (new deps, new sys packages, new steps)
6. Regenerates optimal-build.yml with the updated model
7. Writes the updated model back to model/build_model.json (self-update)
8. Reports convergence status

Usage:
    # Local build iteration (builds in sandbox)
    python3 run_iteration.py --repo /path/to/org-oc --local

    # GHA-based iteration (triggers workflow, waits, diagnoses)
    python3 run_iteration.py --repo o9nn/org-oc --gha

    # Diagnose-only from existing logs (no build)
    python3 run_iteration.py --logs /path/to/logs/ --diagnose-only

    # Dry-run: compute sequence + generate YAML without building
    python3 run_iteration.py --repo /path/to/org-oc --dry-run
"""

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = SKILL_DIR / "model" / "build_model.json"
OPTIMAL_YML = SKILL_DIR / "model" / "optimal-build.yml"
DEFAULT_BUILD_TIME = 5


# ═══════════════════════════════════════════════════════════════════════════
# Model I/O
# ═══════════════════════════════════════════════════════════════════════════

def load_model() -> dict:
    with open(MODEL_PATH) as f:
        return json.load(f)


def save_model(model: dict):
    model["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(MODEL_PATH, "w") as f:
        json.dump(model, f, indent=2)
    print(f"  ✓ Model saved to {MODEL_PATH}")


# ═══════════════════════════════════════════════════════════════════════════
# Topological Sort → Build Tiers
# ═══════════════════════════════════════════════════════════════════════════

def compute_tiers(model: dict) -> list[list[str]]:
    """Kahn's algorithm producing parallel concurrence tiers."""
    components = model["components"]
    in_degree = defaultdict(int)
    adj = defaultdict(list)
    all_nodes = set(components.keys())

    for comp, info in components.items():
        for dep in info.get("deps", []):
            if dep in all_nodes:
                adj[dep].append(comp)
                in_degree[comp] += 1

    queue = sorted([n for n in all_nodes if in_degree[n] == 0])
    tiers = []
    visited = set()

    while queue:
        tier = sorted(queue)
        tiers.append(tier)
        next_q = []
        for node in tier:
            visited.add(node)
            for nb in adj[node]:
                in_degree[nb] -= 1
                if in_degree[nb] == 0 and nb not in visited:
                    next_q.append(nb)
        queue = sorted(set(next_q))

    if len(visited) < len(all_nodes):
        remaining = sorted(all_nodes - visited)
        tiers.append(remaining)

    return tiers


def compute_critical_path(model: dict, tiers: list[list[str]]) -> list[str]:
    """Longest dependency chain."""
    components = model["components"]
    dist = {c: 0 for c in components}
    pred = {c: None for c in components}
    topo = [c for tier in tiers for c in tier]

    for node in topo:
        for dep in components[node].get("deps", []):
            if dep in dist and dist[dep] + 1 > dist[node]:
                dist[node] = dist[dep] + 1
                pred[node] = dep

    end = max(dist, key=dist.get)
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = pred[cur]
    path.reverse()
    return path


def reorder_tiers_by_priority(tiers: list[list[str]], model: dict) -> list[list[str]]:
    """Sort within each tier: longest downstream chain first."""
    components = model["components"]

    def chain_len(comp, visited=None):
        if visited is None:
            visited = set()
        if comp in visited:
            return 0
        visited.add(comp)
        deps = components.get(comp, {}).get("deps", [])
        t = components.get(comp, {}).get("build_time_est", DEFAULT_BUILD_TIME)
        downstream = [d for d in deps if d in components]
        if not downstream:
            return t
        return t + max(chain_len(d, visited.copy()) for d in downstream)

    return [sorted(tier, key=lambda c: -chain_len(c)) for tier in tiers]


# ═══════════════════════════════════════════════════════════════════════════
# Local Build Execution
# ═══════════════════════════════════════════════════════════════════════════

def build_component_locally(repo_root: str, comp: str, model: dict,
                            log_dir: str) -> dict:
    """Attempt to build a single component locally, capture output."""
    comp_dir = Path(repo_root) / comp
    cmake_file = comp_dir / "CMakeLists.txt"
    log_file = Path(log_dir) / f"{comp}.log"

    result = {
        "component": comp,
        "status": "skipped",
        "duration_seconds": 0,
        "log_file": str(log_file),
        "errors": [],
    }

    if not cmake_file.exists():
        result["status"] = "no_cmake"
        log_file.write_text(f"SKIP: {comp} has no CMakeLists.txt\n")
        return result

    # Install system deps first
    sys_deps = model["components"].get(comp, {}).get("sys_deps", [])
    if sys_deps:
        apt_cmd = f"sudo apt-get install -y {' '.join(sys_deps)} 2>&1"
        subprocess.run(apt_cmd, shell=True, capture_output=True, text=True)

    build_dir = comp_dir / "build"
    build_dir.mkdir(exist_ok=True)

    start = time.time()
    try:
        # CMake configure
        cmake_proc = subprocess.run(
            ["cmake", "..", "-DCMAKE_BUILD_TYPE=Release"],
            cwd=str(build_dir), capture_output=True, text=True, timeout=300
        )
        log_output = f"=== CMAKE CONFIGURE ===\n{cmake_proc.stdout}\n{cmake_proc.stderr}\n"

        if cmake_proc.returncode != 0:
            result["status"] = "cmake_error"
            result["errors"].append("cmake_configure_failed")
            log_file.write_text(log_output)
            result["duration_seconds"] = time.time() - start
            return result

        # Make
        nproc = os.cpu_count() or 2
        make_proc = subprocess.run(
            ["make", f"-j{nproc}"],
            cwd=str(build_dir), capture_output=True, text=True, timeout=600
        )
        log_output += f"\n=== MAKE BUILD ===\n{make_proc.stdout}\n{make_proc.stderr}\n"

        if make_proc.returncode != 0:
            result["status"] = "build_error"
            result["errors"].append("make_failed")
        else:
            # Install
            install_proc = subprocess.run(
                ["sudo", "make", "install"],
                cwd=str(build_dir), capture_output=True, text=True, timeout=120
            )
            log_output += f"\n=== MAKE INSTALL ===\n{install_proc.stdout}\n{install_proc.stderr}\n"

            subprocess.run(["sudo", "ldconfig"], capture_output=True)

            if install_proc.returncode != 0:
                result["status"] = "install_error"
                result["errors"].append("install_failed")
            else:
                result["status"] = "success"

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["errors"].append("build_timeout")
        log_output = f"TIMEOUT: Build exceeded time limit\n"
    except Exception as e:
        result["status"] = "exception"
        result["errors"].append(str(e))
        log_output = f"EXCEPTION: {e}\n"

    result["duration_seconds"] = time.time() - start
    log_file.write_text(log_output)
    return result


def run_local_build(repo_root: str, model: dict, tiers: list[list[str]],
                    log_dir: str) -> list[dict]:
    """Build all components tier-by-tier locally."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    results = []
    completed = set()

    for ti, tier in enumerate(tiers):
        print(f"\n  Tier {ti}: {', '.join(tier)}")
        for comp in tier:
            # Check deps are satisfied
            deps = model["components"].get(comp, {}).get("deps", [])
            unmet = [d for d in deps if d not in completed]
            if unmet:
                print(f"    ⚠ {comp}: skipping — unmet deps: {unmet}")
                results.append({
                    "component": comp, "status": "dep_unmet",
                    "duration_seconds": 0, "errors": [f"unmet_deps:{','.join(unmet)}"],
                })
                continue

            print(f"    → Building {comp}...", end=" ", flush=True)
            r = build_component_locally(repo_root, comp, model, log_dir)
            print(f"[{r['status']}] ({r['duration_seconds']:.0f}s)")
            results.append(r)

            if r["status"] == "success":
                completed.add(comp)

    return results


# ═══════════════════════════════════════════════════════════════════════════
# Diagnose + Apply Fixes
# ═══════════════════════════════════════════════════════════════════════════

def diagnose_results(results: list[dict], model: dict, log_dir: str) -> list[dict]:
    """Run diagnosis on all failed components."""
    # Import diagnosis engine
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    from diagnose_errors import diagnose_log_text

    all_diagnoses = []
    for r in results:
        if r["status"] in ("success", "skipped", "no_cmake"):
            continue
        log_file = Path(log_dir) / f"{r['component']}.log"
        if log_file.exists():
            log_text = log_file.read_text()
            diags = diagnose_log_text(log_text, r["component"], model)
            all_diagnoses.extend(diags)

    return all_diagnoses


def apply_fixes(model: dict, diagnoses: list[dict]) -> tuple[dict, list[str]]:
    """Apply diagnosed fixes to the model. Returns (updated_model, changes_made)."""
    changes = []

    for d in diagnoses:
        fix = d.get("fix")
        if not fix:
            continue

        comp = fix.get("component", d.get("component"))
        if comp not in model["components"]:
            continue

        comp_info = model["components"][comp]
        action = fix["action"]

        if action == "add_dep":
            new_dep = fix["new_dep"]
            if new_dep not in comp_info["deps"]:
                comp_info["deps"].append(new_dep)
                change = f"[{comp}] +dep {new_dep}"
                changes.append(change)
                comp_info["fixes_applied"].append(change)

        elif action == "add_sys_dep":
            pkg = fix.get("package", "")
            # Validate: only add known-good apt package names
            KNOWN_APT_PACKAGES = {
                "autoconf", "automake", "binutils-dev", "cmake", "cxxtest",
                "cython3", "guile-3.0-dev", "libboost-all-dev", "libiberty-dev",
                "libdlib-dev", "liboctomap-dev", "libopencv-dev", "libopenmpi-dev",
                "libpqxx-dev", "libprotobuf-dev", "librocksdb-dev", "libssl-dev",
                "libtool", "libzmq3-dev", "swig", "unixodbc-dev", "uuid-dev",
                "build-essential", "pkg-config", "python3-dev",
            }
            if pkg and pkg not in comp_info["sys_deps"]:
                if pkg.startswith("lib") or pkg in KNOWN_APT_PACKAGES:
                    comp_info["sys_deps"].append(pkg)
                    change = f"[{comp}] +sys_dep {pkg}"
                    changes.append(change)
                    comp_info["fixes_applied"].append(change)
                else:
                    change = f"[{comp}] SKIPPED sys_dep '{pkg}' (not a known apt package)"
                    changes.append(change)

        elif action == "add_build_step":
            step = fix.get("step", "")
            when = fix.get("when", "before_build")
            if "extra_steps" not in comp_info:
                comp_info["extra_steps"] = []
            step_entry = {"step": step, "when": when}
            if step_entry not in comp_info["extra_steps"]:
                comp_info["extra_steps"].append(step_entry)
                change = f"[{comp}] +step '{step}' ({when})"
                changes.append(change)
                comp_info["fixes_applied"].append(change)

    # Update statuses based on results
    return model, changes


def update_timings(model: dict, results: list[dict], alpha: float = 0.3) -> dict:
    """Update build time estimates from observed durations."""
    for r in results:
        comp = r["component"]
        if comp in model["components"] and r["duration_seconds"] > 0:
            observed_min = r["duration_seconds"] / 60.0
            old = model["components"][comp]["build_time_est"]
            new = alpha * observed_min + (1 - alpha) * old
            model["components"][comp]["build_time_est"] = round(new, 1)

        if comp in model["components"]:
            model["components"][comp]["status"] = r["status"]
            if r["errors"]:
                model["components"][comp]["errors"] = r["errors"]
            elif r["status"] == "success":
                model["components"][comp]["errors"] = []

    return model


# ═══════════════════════════════════════════════════════════════════════════
# Generate optimal-build.yml
# ═══════════════════════════════════════════════════════════════════════════

def generate_optimal_yml(model: dict, tiers: list[list[str]],
                         output_path: str) -> str:
    """Generate the optimal-build.yml from current model state.

    Architecture: Each job does its own `actions/checkout@v4` (fast, ~10s)
    instead of downloading a 2GB workspace artifact. Only *install artifacts*
    (small — /usr/local/{include,lib,share}/opencog) are shared between jobs.
    This avoids the GitHub Artifacts limitation on special characters in paths
    (colons in language-learning/data/) and is much faster.
    """
    components = model["components"]
    crit_path = model["build_sequence"].get("critical_path", [])
    makespan = model["build_sequence"].get("makespan_est", "?")
    iteration = model["_meta"]["iterations_completed"]

    lines = [
        f"# optimal-build.yml — Auto-generated by oc-build-optimizer",
        f"# Iteration: {iteration} | Generated: {datetime.now(timezone.utc).isoformat()}",
        f"# Critical path: {' → '.join(crit_path)}",
        f"# Estimated makespan: {makespan} min | Tiers: {len(tiers)}",
        f"#",
        f"# Architecture: per-job checkout + install-artifact sharing.",
        f"# Each job checks out the repo independently and only downloads",
        f"# install artifacts from upstream dependencies.",
        "",
        "name: OC Optimal Build",
        "",
        "on:",
        "  push:",
        "    branches: [main]",
        "  pull_request:",
        "    branches: [main]",
        "  workflow_dispatch:",
        "    inputs:",
        "      components:",
        "        description: 'Comma-separated list of components to build (empty=all)'",
        "        required: false",
        "        default: ''",
        "",
        "env:",
        "  CMAKE_BUILD_TYPE: Release",
        '  MAKEFLAGS: "-j$(nproc)"',
        "  INSTALL_PREFIX: /usr/local",
        "",
        "jobs:",
    ]

    # Collect all system deps for the shared setup job
    all_sys_deps = set()
    for comp_info in components.values():
        if comp_info.get("disabled"):
            continue
        all_sys_deps.update(comp_info.get("sys_deps", []))

    # System setup job — validates packages, no artifact upload
    lines.extend([
        "  system_setup:",
        '    name: "System Dependencies"',
        "    runs-on: ubuntu-latest",
        "    steps:",
        "      - name: Install system packages",
        "        run: |",
        "          sudo apt-get update",
    ])
    if all_sys_deps:
        lines.append(f"          sudo apt-get install -y {' '.join(sorted(all_sys_deps))}")
    lines.extend([
        '          echo "/usr/local/lib/opencog" | sudo tee /etc/ld.so.conf.d/opencog.conf',
        "          sudo ldconfig",
        "          echo '✓ All system packages installed successfully'",
        "",
    ])

    # Component jobs — each does its own checkout
    for ti, tier in enumerate(tiers):
        for comp in tier:
            comp_info = components.get(comp, {})

            # Skip disabled components (e.g., ROS-only)
            if comp_info.get("status") == "disabled" or comp_info.get("disabled_reason"):
                continue

            job_name = comp.replace("-", "_").replace(".", "_")
            deps = comp_info.get("deps", [])
            sys_deps = comp_info.get("sys_deps", [])
            extra_steps = comp_info.get("extra_steps", [])
            build_system = comp_info.get("build_system", "cmake")

            # Compute needs
            needs = ["system_setup"]
            active_deps = []  # deps that are not disabled
            for dep in deps:
                dep_info = components.get(dep, {})
                if dep_info.get("status") == "disabled" or dep_info.get("disabled_reason"):
                    continue  # Skip disabled deps
                dep_job = dep.replace("-", "_").replace(".", "_")
                active_deps.append(dep)
                # Only add if dep is in an earlier tier
                for prev_ti in range(ti):
                    if dep in tiers[prev_ti]:
                        needs.append(dep_job)
                        break

            lines.append(f"  {job_name}:")
            lines.append(f'    name: "T{ti}: {comp}"')
            lines.append(f"    runs-on: ubuntu-latest")
            lines.append(f"    needs: [{', '.join(needs)}]")
            lines.append(f"    continue-on-error: true")
            lines.append(f"    steps:")

            # Each job checks out the repo independently
            lines.append(f"      - uses: actions/checkout@v4")

            # Install system packages (each runner is fresh)
            if sys_deps:
                lines.append(f"      - name: Install system deps")
                lines.append(f"        run: |")
                lines.append(f"          sudo apt-get update")
                lines.append(f"          sudo apt-get install -y {' '.join(sys_deps)}")
                lines.append(f'          echo "/usr/local/lib/opencog" | sudo tee /etc/ld.so.conf.d/opencog.conf')
                lines.append(f"          sudo ldconfig")
            else:
                lines.append(f"      - name: Setup environment")
                lines.append(f"        run: |")
                lines.append(f"          sudo apt-get update")
                lines.append(f"          sudo apt-get install -y cmake build-essential")
                lines.append(f'          echo "/usr/local/lib/opencog" | sudo tee /etc/ld.so.conf.d/opencog.conf')
                lines.append(f"          sudo ldconfig")

            # Download and restore dep install artifacts
            for dep in active_deps:
                dep_job = dep.replace("-", "_").replace(".", "_")
                lines.append(f"      - name: Download {dep} install")
                lines.append(f"        uses: actions/download-artifact@v4")
                lines.append(f"        with:")
                lines.append(f"          name: {dep_job}-install")
                lines.append(f"          path: /tmp/{dep}-install")
                lines.append(f"      - name: Restore {dep}")
                lines.append(f"        run: |")
                lines.append(f"          if [ -d /tmp/{dep}-install ]; then")
                lines.append(f"            sudo cp -r /tmp/{dep}-install/* /usr/local/ 2>/dev/null || true")
                lines.append(f"            sudo ldconfig")
                lines.append(f"          fi")

            # Extra pre-build steps
            before_steps = [s for s in extra_steps if s.get("when") == "before_build"]
            if before_steps:
                lines.append(f"      - name: Pre-build fixes for {comp}")
                lines.append(f"        run: |")
                for s in before_steps:
                    lines.append(f"          {s['step']}")

            # Build
            lines.append(f"      - name: Build {comp}")
            lines.append(f"        run: |")
            lines.append(f"          set -eo pipefail")
            if build_system == "autotools":
                lines.append(f"          if [ -d \"{comp}\" ] && [ -f \"{comp}/autogen.sh\" ]; then")
                lines.append(f"            cd {comp}")
                lines.append(f"            ./autogen.sh 2>&1 | tee autogen.log")
                lines.append(f"            ./configure --prefix=/usr/local 2>&1 | tee configure.log")
                lines.append(f"            make ${{{{env.MAKEFLAGS}}}} 2>&1 | tee make.log")
                lines.append(f"            sudo make install 2>&1 | tee install.log")
                lines.append(f"            sudo ldconfig")
                lines.append(f"          elif [ -d \"{comp}\" ] && [ -f \"{comp}/CMakeLists.txt\" ]; then")
                lines.append(f"            cd {comp}")
                lines.append(f"            mkdir -p build && cd build")
                lines.append(f"            cmake .. -DCMAKE_BUILD_TYPE=${{{{env.CMAKE_BUILD_TYPE}}}} 2>&1 | tee cmake.log")
                lines.append(f"            make ${{{{env.MAKEFLAGS}}}} 2>&1 | tee make.log")
                lines.append(f"            sudo make install 2>&1 | tee install.log")
                lines.append(f"            sudo ldconfig")
                lines.append(f"          else")
                lines.append(f'            echo "SKIP: {comp} — no autogen.sh or CMakeLists.txt"')
                lines.append(f"          fi")
            else:
                lines.append(f"          if [ -d \"{comp}\" ] && [ -f \"{comp}/CMakeLists.txt\" ]; then")
                lines.append(f"            cd {comp}")
                lines.append(f"            mkdir -p build && cd build")
                lines.append(f"            cmake .. -DCMAKE_BUILD_TYPE=${{{{env.CMAKE_BUILD_TYPE}}}} 2>&1 | tee cmake.log")
                lines.append(f"            make ${{{{env.MAKEFLAGS}}}} 2>&1 | tee make.log")
                lines.append(f"            sudo make install 2>&1 | tee install.log")
                lines.append(f"            sudo ldconfig")
                lines.append(f"          else")
                lines.append(f'            echo "SKIP: {comp} — no CMakeLists.txt"')
                lines.append(f"          fi")

            # Extra post-install steps
            after_steps = [s for s in extra_steps if s.get("when") == "after_install"]
            if after_steps:
                lines.append(f"      - name: Post-install fixes for {comp}")
                lines.append(f"        run: |")
                for s in after_steps:
                    lines.append(f"          {s['step']}")

            # Upload install artifacts for downstream deps
            lines.append(f"      - name: Upload {comp} install")
            lines.append(f"        if: success()")
            lines.append(f"        uses: actions/upload-artifact@v4")
            lines.append(f"        with:")
            lines.append(f"          name: {job_name}-install")
            lines.append(f"          path: |")
            lines.append(f"            /usr/local/include/opencog")
            lines.append(f"            /usr/local/lib/opencog")
            lines.append(f"            /usr/local/lib/cmake")
            lines.append(f"            /usr/local/share/opencog")
            # Also include link-grammar specific install paths
            if comp == "link-grammar":
                lines.append(f"            /usr/local/include/link-grammar")
                lines.append(f"            /usr/local/lib/liblink-grammar*")
                lines.append(f"            /usr/local/lib/pkgconfig/link-grammar*")

            # Upload build logs for diagnosis
            lines.append(f"      - name: Upload {comp} logs")
            lines.append(f"        if: always()")
            lines.append(f"        uses: actions/upload-artifact@v4")
            lines.append(f"        with:")
            lines.append(f"          name: {job_name}-logs")
            lines.append(f"          path: |")
            if build_system == "autotools":
                lines.append(f"            {comp}/autogen.log")
                lines.append(f"            {comp}/configure.log")
                lines.append(f"            {comp}/make.log")
                lines.append(f"            {comp}/install.log")
            else:
                lines.append(f"            {comp}/build/cmake.log")
                lines.append(f"            {comp}/build/make.log")
                lines.append(f"            {comp}/build/install.log")
            lines.append("")

    yaml_text = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(yaml_text)
    return yaml_text


# ═══════════════════════════════════════════════════════════════════════════
# Main Iteration Loop
# ═══════════════════════════════════════════════════════════════════════════

def run_iteration(args):
    print("=" * 70)
    print("  OC Build Optimizer — Iteration")
    print("=" * 70)

    # 1. Load model
    print("\n[1/7] Loading build model...")
    model = load_model()
    iteration = model["_meta"]["iterations_completed"]
    print(f"  Model version: {model['_meta']['version']}, iteration: {iteration}")
    print(f"  Components: {len(model['components'])}")

    # 2. Compute optimal sequence
    print("\n[2/7] Computing optimal build sequence...")
    tiers = compute_tiers(model)
    tiers = reorder_tiers_by_priority(tiers, model)
    crit_path = compute_critical_path(model, tiers)

    # Estimate makespan
    total_seq = sum(c.get("build_time_est", DEFAULT_BUILD_TIME)
                    for c in model["components"].values())
    tier_times = [max(model["components"].get(c, {}).get("build_time_est", DEFAULT_BUILD_TIME)
                      for c in tier) for tier in tiers]
    makespan_est = sum(tier_times)

    model["build_sequence"]["tiers"] = tiers
    model["build_sequence"]["critical_path"] = crit_path
    model["build_sequence"]["makespan_est"] = makespan_est
    model["build_sequence"]["speedup"] = round(total_seq / makespan_est, 2) if makespan_est > 0 else 0

    print(f"  Tiers: {len(tiers)}")
    print(f"  Critical path: {' → '.join(crit_path)}")
    print(f"  Estimated makespan: {makespan_est} min (seq: {total_seq} min, "
          f"speedup: {model['build_sequence']['speedup']}x)")

    for ti, tier in enumerate(tiers):
        print(f"    T{ti}: {', '.join(tier)}")

    # 3. Build (or skip if dry-run/diagnose-only)
    results = []
    log_dir = args.log_dir or f"/tmp/oc-build-logs-iter{iteration}"

    if args.dry_run:
        print("\n[3/7] DRY RUN — skipping build")
    elif args.diagnose_only and args.logs:
        print(f"\n[3/7] DIAGNOSE ONLY — using logs from {args.logs}")
        log_dir = args.logs
    elif args.local and args.repo:
        print(f"\n[3/7] Building locally in {args.repo}...")
        results = run_local_build(args.repo, model, tiers, log_dir)
        successes = sum(1 for r in results if r["status"] == "success")
        failures = sum(1 for r in results if r["status"] not in ("success", "skipped", "no_cmake"))
        print(f"  Results: {successes} success, {failures} failed")
    elif args.gha_run:
        print(f"\n[3/7] Using GHA run {args.gha_run} for diagnosis...")
    else:
        print("\n[3/7] No build mode specified — generating YAML only")

    # 4. Diagnose errors
    print("\n[4/7] Diagnosing errors...")
    diagnoses = []
    if results:
        diagnoses = diagnose_results(results, model, log_dir)
    elif args.logs or args.diagnose_only:
        actual_log_dir = args.logs or log_dir
        if Path(actual_log_dir).is_dir():
            sys.path.insert(0, str(SKILL_DIR / "scripts"))
            from diagnose_errors import diagnose_log_directory
            diagnoses = diagnose_log_directory(actual_log_dir, model)
    elif args.gha_run:
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        from diagnose_errors import diagnose_gha_run
        diagnoses = diagnose_gha_run(args.gha_run, args.repo or "o9nn/org-oc", model)

    if diagnoses:
        print(f"  Found {len(diagnoses)} diagnostic(s)")
        for d in diagnoses[:10]:
            print(f"    [{d['component']}] {d['pattern']}: {d['diagnosis']}")
    else:
        print("  No errors diagnosed")

    # 5. Apply fixes to model
    print("\n[5/7] Applying fixes to model...")
    if diagnoses:
        model, changes = apply_fixes(model, diagnoses)
        if changes:
            print(f"  Applied {len(changes)} fix(es):")
            for c in changes:
                print(f"    {c}")
        else:
            print("  No actionable fixes to apply")
    else:
        changes = []
        print("  No fixes needed")

    # 6. Update timings from real build data
    if results:
        print("\n[5b/8] Updating timing estimates from observed data...")
        model = update_timings(model, results)

    # 6b. Neural build-path training
    print("\n[6/8] Neural build-path training...")
    try:
        from neural_build_path import train_from_real_results, train, apply_to_model

        if results:
            # Convert results to neural format: {comp: {status, missing_dep}}
            neural_results = {}
            for r in results:
                comp = r["component"]
                if r["status"] == "success":
                    neural_results[comp] = {"status": "success", "missing_dep": None}
                elif r["status"] in ("dep_unmet", "cmake_error", "build_error"):
                    # Find missing dep from diagnosis
                    missing = None
                    for d in diagnoses:
                        if d.get("component") == comp and d.get("fix", {}).get("action") == "add_dep":
                            missing = d["fix"]["new_dep"]
                            break
                    neural_results[comp] = {"status": "failure", "missing_dep": missing}

            if neural_results:
                # Save model first so neural module can read it
                save_model(model)
                nn_result = train_from_real_results(neural_results, str(MODEL_PATH), lr=0.05)
                print(f"  Neural step: loss={nn_result['loss']:.4f}, entropy={nn_result['entropy']:.3f}")
                # Reload model (neural module updated it)
                model = load_model()
        else:
            # Simulation-based training (dry-run or diagnose-only)
            save_model(model)
            nn_result = train(
                model_path=str(MODEL_PATH),
                epochs=50,
                lr=0.1,
                warm_start=True,
                verbose=True,
            )
            apply_to_model(nn_result, str(MODEL_PATH))
            model = load_model()
            print(f"  Neural training: {nn_result['epochs_run']} epochs, "
                  f"loss={nn_result['best_loss']:.4f}, "
                  f"converged={nn_result['converged']}")
    except Exception as e:
        print(f"  ⚠ Neural training skipped: {e}")

    # Recompute tiers after fixes (deps may have changed)
    tiers = compute_tiers(model)
    tiers = reorder_tiers_by_priority(tiers, model)
    crit_path = compute_critical_path(model, tiers)
    tier_times = [max(model["components"].get(c, {}).get("build_time_est", DEFAULT_BUILD_TIME)
                      for c in tier) for tier in tiers]
    makespan_est = sum(tier_times)

    model["build_sequence"]["tiers"] = tiers
    model["build_sequence"]["critical_path"] = crit_path
    model["build_sequence"]["makespan_est"] = makespan_est

    # 7. Generate optimal-build.yml
    print("\n[7/8] Generating optimal-build.yml...")
    yml_path = str(args.yaml_output or OPTIMAL_YML)
    generate_optimal_yml(model, tiers, yml_path)
    print(f"  Written to {yml_path}")

    # Also copy to repo if specified
    if args.repo and Path(args.repo).is_dir():
        repo_yml = Path(args.repo) / ".github" / "workflows" / "optimal-build.yml"
        repo_yml.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(yml_path, str(repo_yml))
        print(f"  Also copied to {repo_yml}")

    # 8. Save updated model (self-update)
    print("\n[8/8] Saving updated model (self-update)...")
    model["_meta"]["iterations_completed"] = iteration + 1

    # Determine convergence
    log_entry = {
        "iteration": iteration,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tier_count": len(tiers),
        "makespan_est": makespan_est,
        "critical_path": crit_path,
        "fixes_applied": len(changes),
        "diagnoses_found": len(diagnoses),
        "components_success": sum(1 for r in results if r["status"] == "success"),
        "components_failed": sum(1 for r in results if r["status"] not in ("success", "skipped", "no_cmake")),
    }
    model["iteration_log"].append(log_entry)

    # Check convergence: no new fixes + all tested components pass
    if not changes and all(
        model["components"][c]["status"] in ("success", "no_cmake", "untested")
        for c in model["components"]
    ):
        model["_meta"]["convergence_status"] = "converged"
    elif not changes:
        model["_meta"]["convergence_status"] = "stable_with_failures"
    else:
        model["_meta"]["convergence_status"] = "iterating"

    save_model(model)

    # Summary
    print("\n" + "=" * 70)
    print("  Iteration Summary")
    print("=" * 70)
    print(f"  Iteration:        {iteration} → {iteration + 1}")
    print(f"  Convergence:      {model['_meta']['convergence_status']}")
    print(f"  Tiers:            {len(tiers)}")
    print(f"  Makespan (est):   {makespan_est} min")
    print(f"  Fixes applied:    {len(changes)}")
    print(f"  Diagnoses:        {len(diagnoses)}")
    print(f"  Model:            {MODEL_PATH}")
    print(f"  Workflow:         {yml_path}")

    if model["_meta"]["convergence_status"] == "converged":
        print("\n  ✅ BUILD MODEL HAS CONVERGED")
    elif model["_meta"]["convergence_status"] == "stable_with_failures":
        print("\n  ⚠  Stable but some components still failing — may need manual investigation")
    else:
        print(f"\n  → Run another iteration to continue refining")

    # Save diagnoses
    if diagnoses:
        diag_path = Path(log_dir) / "diagnoses.json"
        diag_path.parent.mkdir(parents=True, exist_ok=True)
        with open(diag_path, "w") as f:
            json.dump(diagnoses, f, indent=2)
        print(f"  Diagnoses:        {diag_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run one iteration of the build-optimize-diagnose-fix loop"
    )
    parser.add_argument("--repo", help="Path to org-oc repo (local) or GitHub slug (GHA)")
    parser.add_argument("--local", action="store_true", help="Build locally in sandbox")
    parser.add_argument("--gha-run", help="GitHub Actions run ID to diagnose")
    parser.add_argument("--logs", help="Directory of existing build logs to diagnose")
    parser.add_argument("--diagnose-only", action="store_true", help="Only diagnose, don't build")
    parser.add_argument("--dry-run", action="store_true", help="Compute sequence + YAML only")
    parser.add_argument("--log-dir", help="Directory to store build logs")
    parser.add_argument("--yaml-output", help="Path for optimal-build.yml output")
    args = parser.parse_args()

    run_iteration(args)


if __name__ == "__main__":
    main()
