#!/usr/bin/env python3
"""
diagnose_errors.py — Parse build logs and diagnose errors against the build model.

Scans build output for known error patterns, identifies missing dependencies
(both system packages and inter-component), missing build steps, and wrong
ordering. Returns structured diagnoses with proposed fixes.

Usage:
    python3 diagnose_errors.py <build_log> --model model/build_model.json
    python3 diagnose_errors.py --gha-run <run_id> --repo o9nn/org-oc --model model/build_model.json
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


# ── Error pattern → fix mapping ──────────────────────────────────────────

def load_model(model_path: str) -> dict:
    with open(model_path) as f:
        return json.load(f)


def diagnose_log_text(log_text: str, component: str, model: dict) -> list[dict]:
    """Diagnose errors in a single component's build log."""
    diagnoses = []
    error_patterns = model.get("error_patterns", {})
    cmake_map = model.get("cmake_pkg_to_component", {})
    sys_map = model.get("sys_pkg_to_apt", {})
    comp_info = model.get("components", {}).get(component, {})

    for pattern_name, pattern_info in error_patterns.items():
        regex = pattern_info["regex"]
        for m in re.finditer(regex, log_text, re.IGNORECASE):
            captured = m.group(1) if m.lastindex else m.group(0)
            fix_type = pattern_info["fix_type"]
            diagnosis = {
                "component": component,
                "pattern": pattern_name,
                "match": m.group(0)[:200],
                "captured": captured,
                "diagnosis": pattern_info["diagnosis"],
                "fix_type": fix_type,
                "fix": None,
            }

            # Resolve fix
            if fix_type == "add_component_dep":
                # Map CMake package name to component
                norm = captured.lower().replace("-", "").replace("_", "")
                mapped = cmake_map.get(norm) or cmake_map.get(captured.lower())
                if mapped:
                    diagnosis["fix"] = {
                        "action": "add_dep",
                        "component": component,
                        "new_dep": mapped,
                        "reason": f"CMake could not find {captured} — add {mapped} as build dependency",
                    }
                else:
                    diagnosis["fix"] = {
                        "action": "add_sys_dep",
                        "component": component,
                        "package": captured.lower(),
                        "reason": f"Unknown package {captured} — may need system package or new component mapping",
                    }

            elif fix_type == "add_sys_dep":
                # First check if header maps to an internal component
                header = captured
                internal_comp = _header_to_component(header)
                if internal_comp and internal_comp in model.get("components", {}):
                    diagnosis["fix_type"] = "add_component_dep"
                    diagnosis["fix"] = {
                        "action": "add_dep",
                        "component": component,
                        "new_dep": internal_comp,
                        "reason": f"Missing header {header} — maps to internal component {internal_comp}",
                    }
                else:
                    # Try to map header to apt package
                    pkg = _header_to_apt(header, sys_map)
                    if pkg:
                        diagnosis["fix"] = {
                            "action": "add_sys_dep",
                            "component": component,
                            "package": pkg,
                            "reason": f"Missing header {header} — install {pkg}",
                        }
                    else:
                        diagnosis["fix"] = {
                            "action": "investigate",
                            "component": component,
                            "header": header,
                            "reason": f"Missing header {header} — unknown package, needs manual investigation",
                        }

            elif fix_type == "add_ldconfig_fix":
                diagnosis["fix"] = {
                    "action": "add_build_step",
                    "component": component,
                    "step": "sudo ldconfig",
                    "when": "after_install",
                    "reason": f"Shared library {captured} not found — ldconfig needed after install",
                }

            elif fix_type == "add_cython_fix":
                diagnosis["fix"] = {
                    "action": "add_build_step",
                    "component": component,
                    "step": "pip install --upgrade cython",
                    "when": "before_build",
                    "reason": "Cython not found or version mismatch",
                }

            elif fix_type == "add_sudo_fix":
                diagnosis["fix"] = {
                    "action": "add_build_step",
                    "component": component,
                    "step": "use sudo for make install",
                    "when": "install",
                    "reason": "Permission denied during install — need sudo",
                }

            elif fix_type == "upgrade_cmake":
                diagnosis["fix"] = {
                    "action": "upgrade_tool",
                    "tool": "cmake",
                    "min_version": captured,
                    "reason": f"CMake {captured} required — upgrade needed",
                }

            diagnoses.append(diagnosis)

    # Also check for generic failure indicators
    if re.search(r"make\[\d+\]: \*\*\* .+ Error \d+", log_text):
        if not diagnoses:
            diagnoses.append({
                "component": component,
                "pattern": "generic_make_error",
                "match": "make error detected but no specific pattern matched",
                "captured": "",
                "diagnosis": "Build failed with make error — needs manual investigation",
                "fix_type": "investigate",
                "fix": {
                    "action": "investigate",
                    "component": component,
                    "reason": "Generic make error — review full build log",
                },
            })

    if "CMake Error" in log_text and not any(d["pattern"].startswith("missing_cmake") for d in diagnoses):
        for line in log_text.split("\n"):
            if "CMake Error" in line:
                diagnoses.append({
                    "component": component,
                    "pattern": "cmake_error",
                    "match": line[:200],
                    "captured": "",
                    "diagnosis": "CMake configuration error",
                    "fix_type": "investigate",
                    "fix": {
                        "action": "investigate",
                        "component": component,
                        "reason": line[:200],
                    },
                })
                break

    return diagnoses


# ── Internal header → component mapping ───────────────────────────────
INTERNAL_HEADER_TO_COMPONENT = {
    "opencog/cogutil": "cogutil",
    "opencog/util": "cogutil",
    "opencog/atoms": "atomspace",
    "opencog/atomspace": "atomspace",
    "opencog/truthvalue": "atomspace",
    "opencog/persist": "atomspace",
    "opencog/cogserver": "cogserver",
    "opencog/network": "cogserver",
    "opencog/unify": "unify",
    "opencog/ure": "ure",
    "opencog/rule-engine": "ure",
    "opencog/attention": "attention",
    "opencog/spacetime": "spacetime",
    "opencog/pln": "pln",
    "opencog/miner": "miner",
    "opencog/moses": "moses",
    "opencog/asmoses": "asmoses",
    "opencog/generate": "generate",
    "opencog/learn": "learn",
    "opencog/nlp": "opencog",
    "opencog/ghost": "opencog",
}


def _header_to_apt(header: str, sys_map: dict) -> str | None:
    """Map a missing header file to an apt package."""
    header_map = {
        "boost/": "libboost-all-dev",
        "guile/": "guile-3.0-dev",
        "rocksdb/": "librocksdb-dev",
        "pqxx/": "libpqxx-dev",
        "opencv": "libopencv-dev",
        "openssl/": "libssl-dev",
        "octomap/": "liboctomap-dev",
        "mpi.h": "libmpi-dev",
        "uuid/uuid.h": "uuid-dev",
        "bfd.h": "binutils-dev",
        "cxxtest/": "cxxtest",
        "dlib/": "libdlib-dev",
        "zmq.h": "libzmq3-dev",
        "protobuf/": "libprotobuf-dev",
    }
    for prefix, pkg in header_map.items():
        if prefix in header:
            return pkg
    return None


def _header_to_component(header: str) -> str | None:
    """Map an internal OpenCog header to its source component."""
    for prefix, comp in INTERNAL_HEADER_TO_COMPONENT.items():
        if prefix in header:
            return comp
    return None


def diagnose_gha_run(run_id: str, repo: str, model: dict) -> list[dict]:
    """Fetch and diagnose a GitHub Actions run."""
    try:
        result = subprocess.run(
            ["gh", "run", "view", run_id, "--repo", repo, "--json", "jobs",
             "--jq", ".jobs"],
            capture_output=True, text=True, check=True
        )
        jobs = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error fetching GHA run: {e}", file=sys.stderr)
        return []

    all_diagnoses = []
    for job in jobs:
        name = job.get("name", "")
        conclusion = job.get("conclusion", "")
        if conclusion != "failure":
            continue

        # Extract component name from job name
        comp = name.split(":")[-1].strip() if ":" in name else name.strip()

        # Fetch job log
        try:
            log_result = subprocess.run(
                ["gh", "run", "view", run_id, "--repo", repo, "--log-failed"],
                capture_output=True, text=True, check=True
            )
            log_text = log_result.stdout
        except subprocess.CalledProcessError:
            log_text = ""

        if log_text:
            diags = diagnose_log_text(log_text, comp, model)
            all_diagnoses.extend(diags)

    return all_diagnoses


def diagnose_local_log(log_path: str, component: str, model: dict) -> list[dict]:
    """Diagnose a local build log file."""
    with open(log_path) as f:
        log_text = f.read()
    return diagnose_log_text(log_text, component, model)


def diagnose_log_directory(log_dir: str, model: dict) -> list[dict]:
    """Diagnose all .log files in a directory (component name from filename)."""
    all_diagnoses = []
    log_path = Path(log_dir)
    for log_file in sorted(log_path.glob("*.log")):
        comp = log_file.stem
        with open(log_file) as f:
            log_text = f.read()
        diags = diagnose_log_text(log_text, comp, model)
        all_diagnoses.extend(diags)
    return all_diagnoses


def main():
    parser = argparse.ArgumentParser(description="Diagnose org-oc build errors")
    parser.add_argument("log", nargs="?", help="Build log file or directory of .log files")
    parser.add_argument("--component", "-c", help="Component name (if single log file)")
    parser.add_argument("--gha-run", help="GitHub Actions run ID")
    parser.add_argument("--repo", default="o9nn/org-oc", help="GitHub repo")
    parser.add_argument("--model", "-m", required=True, help="Path to build_model.json")
    parser.add_argument("--output", "-o", default="diagnoses.json", help="Output file")
    args = parser.parse_args()

    model = load_model(args.model)

    if args.gha_run:
        diagnoses = diagnose_gha_run(args.gha_run, args.repo, model)
    elif args.log:
        p = Path(args.log)
        if p.is_dir():
            diagnoses = diagnose_log_directory(args.log, model)
        else:
            comp = args.component or p.stem
            diagnoses = diagnose_local_log(args.log, comp, model)
    else:
        print("Error: provide a log file/directory or --gha-run", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w") as f:
        json.dump(diagnoses, f, indent=2)

    # Summary
    by_type = {}
    for d in diagnoses:
        ft = d.get("fix_type", "unknown")
        by_type[ft] = by_type.get(ft, 0) + 1

    print(f"Diagnosed {len(diagnoses)} error(s) across components:")
    for ft, count in sorted(by_type.items()):
        print(f"  {ft}: {count}")

    # Print actionable fixes
    fixes = [d for d in diagnoses if d.get("fix") and d["fix"]["action"] != "investigate"]
    if fixes:
        print(f"\nActionable fixes ({len(fixes)}):")
        for d in fixes:
            fix = d["fix"]
            print(f"  [{d['component']}] {fix['action']}: {fix.get('reason', '')}")

    investigate = [d for d in diagnoses if d.get("fix") and d["fix"]["action"] == "investigate"]
    if investigate:
        print(f"\nNeeds investigation ({len(investigate)}):")
        for d in investigate:
            print(f"  [{d['component']}] {d['diagnosis']}")

    print(f"\nDiagnoses saved to {args.output}")


if __name__ == "__main__":
    main()
