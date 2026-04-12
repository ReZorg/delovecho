---
name: oc-build-optimizer
description: Iteratively refine the build sequence for o9nn/org-oc (OpenCog monorepo) until it converges on the optimal sequence-vs-concurrence configuration to build all components with optimal efficiency and exact dependencies. Self-correcting diagnosis engine identifies errors, missing steps, and missing dependencies from build logs, applies fixes to a persistent model, and regenerates the optimal-build.yml GitHub Actions workflow. Use when optimizing CI build order, generating GitHub Actions workflows, analyzing build dependencies, reducing build times, or debugging dependency failures in the org-oc repository. Triggers on mentions of org-oc build, OpenCog build order, build sequence optimization, CI pipeline for opencog, or build dependency analysis.
---

# OC Build Optimizer

Self-correcting, self-updating build-sequence optimizer for **o9nn/org-oc** (42+ buildable components, 10 dependency layers). Uses deterministic error diagnosis and topological optimization to converge on the exact dependency chain and optimal build order through iterative refinement.

**Complementary skill**: Compose with **oc-build-nn** (neural build-path optimizer) for combined deterministic + neural optimization. This skill provides the diagnosis engine, GHA workflow generation, and self-update mechanism; oc-build-nn provides the differentiable learning layer.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              Deterministic Diagnosis Engine                    │
│                                                                │
│  Parses build logs → pattern match → structured fix proposals │
│  Missing CMake packages → component dep                       │
│  Missing headers → internal component or apt package          │
│  Linker errors → ldconfig / missing install                   │
│  Cython errors → python package or build step                 │
│  Applies fixes directly to persistent model                   │
└──────────────────────────────────────────────────────────────┘
         ↕ fixes applied to model
┌──────────────────────────────────────────────────────────────┐
│              Topological Build Optimizer                       │
│                                                                │
│  Kahn's algorithm → parallel concurrence tiers                │
│  Critical-path priority → within-tier ordering                │
│  Wide-tier splitting + thin-tier merging                      │
│  Timing EMA from observed build durations                     │
│  Generates optimal-build.yml with all fixes incorporated      │
└──────────────────────────────────────────────────────────────┘
         ↕ optional neural training (via oc-build-nn)
┌──────────────────────────────────────────────────────────────┐
│              Neural Build-Path (oc-build-nn)                  │
│                                                                │
│  Learnable position embeddings + dependency logits            │
│  Backpropagation from build success/failure                   │
│  Automatically invoked at step 6/8 if available               │
└──────────────────────────────────────────────────────────────┘
```

### Persistent State

All state lives in `model/build_model.json`:

- Component catalog (deps, sys_deps, status, errors, fixes, timings)
- Build sequence (tiers, critical path, makespan estimate)
- Iteration log (fixes applied, diagnoses found per iteration)
- Neural state (if oc-build-nn has been used)

Every script reads from and writes back to this model. The model evolves with each iteration.

## Workflow

### Quick Start: Dry Run

```bash
python3 scripts/run_iteration.py --repo /path/to/org-oc --dry-run
```

Computes optimal tiers, generates `optimal-build.yml`. If oc-build-nn is available, also runs neural simulation training.

### Full Iteration: Local Build

```bash
python3 scripts/run_iteration.py --repo /path/to/org-oc --local
```

Builds all components tier-by-tier, captures errors, diagnoses failures, applies fixes, regenerates YAML. Run repeatedly until convergence.

### Diagnose from Existing Logs

```bash
python3 scripts/run_iteration.py --logs /path/to/logs/ --diagnose-only
```

### Diagnose from GitHub Actions Run

```bash
python3 scripts/run_iteration.py --gha-run 12345678 --repo o9nn/org-oc
```

### Self-Update Skill Files

Regenerate references from the model after any iteration:

```bash
python3 scripts/self_update.py --report --push-yml o9nn/org-oc
```

## What Each Iteration Does (8 Steps)

1. **Load** persistent model from `model/build_model.json`
2. **Compute** optimal tiers via topological sort + critical-path priority
3. **Build** components tier-by-tier (local, GHA, or from logs)
4. **Diagnose** failures via pattern matching (10+ error signatures)
5. **Apply fixes** to model (new deps, sys packages, build steps)
6. **Neural training** (optional, via oc-build-nn) — forward/backward/update on build results
7. **Regenerate** `model/optimal-build.yml` with all fixes
8. **Save** updated model (self-update)

### Error Diagnosis Patterns

| Pattern | Detection | Fix |
|---------|-----------|-----|
| Missing CMake package | `Could not find a package configuration file` | Add component dep |
| Missing internal header | `fatal error: opencog/X/Y.h: No such file` | Map header to source component, add dep |
| Missing system header | `fatal error: X.h: No such file` | Map to apt package, add sys_dep |
| Linker error | `undefined reference to` | Add missing dep or ldconfig step |
| Shared library error | `cannot open shared object file` | Add ldconfig post-install step |
| Cython error | `cython: command not found` | Add cython3 sys_dep |
| Permission error | `Permission denied` | Add sudo step |
| CMake version | `CMake .* or higher is required` | Add cmake upgrade step |
| Boost missing | `Could not find.*Boost` | Add libboost-dev sys_dep |
| Guile missing | `Could not find.*Guile` | Add guile-3.0-dev sys_dep |

### Convergence Criteria

- **Deterministic**: No new fixes discovered AND all tested components pass
- **Combined** (with oc-build-nn): Both systems agree → `converged`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_iteration.py` | Main entry — one full build-diagnose-fix iteration |
| `scripts/diagnose_errors.py` | Error pattern matching and fix proposal engine |
| `scripts/self_update.py` | Regenerate skill reference files from model |
| `scripts/extract_deps.py` | Scan repo CMakeLists.txt to build dependency DAG |
| `scripts/optimize_sequence.py` | Simulate parallel schedules (standalone) |
| `scripts/analyze_convergence.py` | Generate convergence reports (standalone) |
| `scripts/integrate_feedback.py` | Integrate real build timings (standalone) |
| `scripts/neural_build_path.py` | Neural optimizer (also available standalone via oc-build-nn) |

## Model Files

| File | Purpose |
|------|---------|
| `model/build_model.json` | Persistent model — single source of truth |
| `model/optimal-build.yml` | Generated GitHub Actions workflow |
| `model/reports/` | Per-iteration reports |

## Reference Files

- **`references/dependency-graph.md`**: Auto-regenerated component catalog, layer architecture, deps, system packages, accumulated fixes. Read when debugging dependency failures.
- **`references/gha-patterns.md`**: Auto-regenerated workflow patterns with accumulated build fixes. Read when generating or debugging CI workflows.

## Critical Path

```
cogutil (5m) → atomspace (15m) → unify (6m) → ure (8m) → pln (10m) → opencog (15m)
Total: 59 min minimum
```
