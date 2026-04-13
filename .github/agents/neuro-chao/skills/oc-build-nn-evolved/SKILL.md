---
name: oc-build-nn-evolved
description: "Evolved neural build-path optimizer for opencog/* ⊕ openclaw/* (113 repos, 2 orgs) using circled-operators algebraic composition and differentiable position embeddings. Learns optimal build order, hidden dependencies, and cross-org integration patterns through backpropagation from build success/failure signals. Self-improving triadic architecture: forward pass (build order prediction), backward pass (self-correction from CI results), knowledge state (14,340 learnable parameters). Composes oc-build-nn with circled-operators across the full opencog and openclaw GitHub organizations. Use when optimizing multi-org build sequences, discovering cross-repo dependencies via gradient descent, generating GHA workflows from learned topology, or evolving the build model from real CI data. Triggers on mentions of opencog build, openclaw build, dual-org build optimization, cross-org dependency learning, neural build path for opencog, or circled-operators build topology."
---

# oc-build-nn-evolved

Evolved neural build-path optimizer for **opencog/\*** ⊕ **openclaw/\*** — 113 repositories across 2 GitHub organizations, composed via circled-operators algebraic semiring.

Derived from: `skill-creator-evolved < oc-build-nn ( circled-operators [ opencog/* | openclaw/* ] ) >`

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│           DualOrgBuildPathNetwork (nn Module pattern)               │
│                                                                     │
│  P[112×6]  PositionEmbedding   — softmax → step probabilities     │
│  D[112×112] DependencyLogits   — sigmoid → dep probabilities      │
│  O[112×2]  OrgEmbedding        — org membership vector            │
│  B[2×2]    CrossOrgBridge      — ⊕/⊗ org interaction              │
│  T[112×8]  ComponentType       — language/build features           │
│                                                                     │
│  14,340 parameters | Converges in ~23 epochs | 112/112 passing     │
└────────────────────────────────────────────────────────────────────┘
```

## Triadic Structure

| Triad | Method | Description |
|-------|--------|-------------|
| **Forward (F)** | `forward()` | Predict optimal build order from embeddings |
| **Backward (B)** | `backward()` | Update weights from build success/failure |
| **Knowledge (K)** | `model/` | 14,340 learnable parameters + topology |

## Circled-Operators Semiring

The build ecosystem forms (R, ⊕, ⊗, 0, 1):

| Element | Meaning |
|---------|---------|
| ⊕ | Concurrent build (repos in same tier) |
| ⊗ | Sequential dependency (tier ordering) |
| 0 | Orphan repos (no deps, no dependents) |
| 1 | cogutil (identity — 42 dependents) |

Full build = `(Tier₀ components ⊕) ⊗ (Tier₁ ⊕) ⊗ (Tier₂ ⊕) ⊗ (Tier₃ ⊕) ⊗ (Tier₄ ⊕)`

Cross-org: opencog and openclaw form a **pure ⊕** (no cross-org deps).

## Workflow 1: Train from Topology (Simulation)

```bash
# Step 1: Scan both orgs for repo metadata
python3 scripts/analyze_topology.py

# Step 2: Train neural build-path optimizer
python3 scripts/neural_build_path.py --epochs 300 --lr 0.1 \
  --output model/neural_state.json \
  --knowledge model/learned_knowledge.json
```

## Workflow 2: Online Learning from CI Results

```bash
# Single online learning step from a build failure
python3 scripts/backward_pass.py \
  --feedback build_failure \
  --component atomspace-cog \
  --missing cogutil,atomspace
```

## Workflow 3: Generate GHA Workflow

```bash
# Generate optimal-build.yml from learned tier assignments
python3 scripts/generate_gha.py \
  --knowledge model/learned_knowledge.json \
  --output optimal-build.yml
```

## Workflow 4: Full Rescan + Retrain

```bash
# Rescan both orgs and retrain (use after new repos added)
python3 scripts/backward_pass.py --feedback rescan
```

## Learned Topology (Pre-trained)

| Tier | Count | Key Components |
|------|-------|----------------|
| 0 | 62 | cogutil, all openclaw/*, standalone opencog repos |
| 1 | 12 | atomspace, moses, asmoses, attention, matrix |
| 2 | 29 | cogserver, pln, unify, miner, generate, sensory |
| 3 | 7 | learn, ure, atomspace-viz, ocpkg |
| 4 | 2 | docker, opencog-debian (meta-packages) |

## Key Metrics

| Metric | Value |
|--------|-------|
| Total repos | 113 (90 opencog + 23 openclaw) |
| Dependency edges | 112 |
| ⊕-components | 60 independent subgraphs |
| Longest ⊗-chain | 5 (cogutil→atomspace→unify→ure→opencog-debian) |
| Parameters | 14,340 |
| Convergence | 23 epochs |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/neural_build_path.py` | Neural build-path optimizer (train/predict) |
| `scripts/analyze_topology.py` | Scan repos, build ⊕⊗ topology |
| `scripts/backward_pass.py` | Self-improvement from feedback signals |
| `scripts/generate_gha.py` | Generate GHA workflow from learned order |

## Model Files

| File | Purpose |
|------|---------|
| `model/neural_state.json` | Trained network weights (14,340 params) |
| `model/learned_knowledge.json` | Extracted tiers, deps, bridge matrix |
| `model/topology.json` | Full ⊕⊗ topology analysis |
| `model/repo_scan.json` | Raw scan data for all 113 repos |

## References

| Topic | File | When to Read |
|-------|------|--------------|
| Dependency graph | `references/dependency-graph.md` | Debugging dependency failures |
| ⊕⊗ composition | `references/circled-operators-composition.md` | Understanding algebraic structure |
| Neural architecture | `references/neural-architecture.md` | Modifying network layers |
| Repo scan (CSV) | `references/repo_scan.csv` | Browsing raw repo metadata |
