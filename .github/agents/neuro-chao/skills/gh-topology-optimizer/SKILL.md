---
name: gh-topology-optimizer
description: Analyze and optimize GitHub enterprise/org/repo topology using a 3-phase pipeline composing metamathematical consciousness (self-referential fixed-point topology model), gh253/apl253 pattern language structural health diagnosis, and Vorticog digital twin agentic simulation with virtual endocrine dynamics. Use for diagnosing organizational structure health, identifying imbalanced enterprises/orgs, generating merge/split/consolidate recommendations, and running what-if topology simulations. Triggers on mentions of GitHub topology optimization, enterprise org structure analysis, namespace hierarchy health, pattern language diagnosis, or agentic org simulation.
---

# GitHub Namespace Topology Optimizer

Skill chain: `/metamathematical-consciousness ( /gh253 | /org-fabric ( /apl253 ) ) -> /vorticog ( /digitwin ( /skill-creator ) )`

Hierarchy model: `0(1(2(3(4(5)))))` where level-0=global, 1=enterprise, 2=org, 3=repo, 4=folder, 5=file.

## Prerequisites

- `beast` PAT env var with `read:enterprise`, `read:org`, `repo` scopes
- Python 3.11+ with matplotlib, numpy
- Pre-fetched data files (or run the fetch step below)

## Workflow

### Step 1: Fetch Enterprise and Org Data

Use the `beast` PAT to query GitHub GraphQL for enterprises and their orgs:

```bash
curl -s -H "Authorization: bearer $beast" \
  -H "Content-Type: application/json" \
  https://api.github.com/graphql \
  -d '{"query":"{ viewer { enterprises(first:100) { nodes { slug organizations(first:100) { totalCount nodes { login } } } } } }"}' \
  > /home/ubuntu/enterprises.json
```

Then fetch repos for each org using parallel subtasks (see `scripts/topology_optimizer.py` for the `load_data()` function signature). Save results to `/home/ubuntu/fetch_org_repos.json`.

### Step 2: Run the 3-Phase Analysis

```bash
python3 /home/ubuntu/skills/gh-topology-optimizer/scripts/topology_optimizer.py
```

This executes:

1. **Phase 1 — Metamathematical Consciousness**: Applies the awareness endofunctor `Phi(S) = S x ceil(S) x Omega^S` iteratively until the composite health score converges (fixed point). Computes Gini coefficient, Shannon entropy, and mean/std children per level. Classifies violations: `IMBALANCED_DISTRIBUTION`, `SIZE_ANOMALY`, `EMPTY_CONTAINER`, `CROSS_ENTERPRISE_PREFIX`.

2. **Phase 2 — gh253 Pattern Language Diagnosis**: Evaluates 5 Alexander patterns mapped to GitHub domain. See `references/pattern-diagnosis.md` for the full mapping table and extension guide.

3. **Phase 3 — Vorticog Digital Twin**: Models each org as an agent with needs (capacity, coherence, visibility, autonomy), virtual endocrine hormones (cortisol, dopamine, oxytocin, norepinephrine), emotions (stress, satisfaction, trust), and cognitive modes (EXPLORATORY, FOCUSED, SOCIAL, REFLECTIVE, NEUTRAL, STRESSED, THREAT, REWARD). Generates typed recommendations: MERGE, CONSOLIDATE, SPLIT, REORGANIZE, REVIEW, ATTENTION, CRITICAL.

Output: `/home/ubuntu/gh-topology-optimizer/topology_analysis.json`

### Step 3: Generate Visualizations

```bash
python3 /home/ubuntu/skills/gh-topology-optimizer/scripts/visualize.py
```

Produces three dark-themed PNG charts:
- `topology_overview.png` — 4-panel: hierarchy bar, level metrics, pattern radar, cognitive mode donut
- `agent_heatmap.png` — 3-panel: needs heatmap, hormone heatmap, emotion bars (top 30 agents)
- `recommendations.png` — 2-panel: recommendation distribution, violation severity

### Step 4: Interpret Results

Key signals to act on:

| Signal | Threshold | Action |
|--------|-----------|--------|
| Gini > 0.6 at any level | High inequality | Redistribute children |
| Pattern score < 0.4 | Violation | Follow pattern recommendation |
| Agent mode = STRESSED/THREAT | Structural crisis | Immediate intervention |
| MERGE recommendation | Empty or near-empty org | Archive or merge into sibling |
| SPLIT recommendation | >200 repos in one org | Split by domain |

### Extending

To add new patterns, see `references/pattern-diagnosis.md`. To add new agent needs or hormones, extend the `OrgAgent` dataclass and corresponding compute functions in `topology_optimizer.py`.

The skill composes with:
- `/gh253` and `/apl253` for pattern definitions
- `/org-fabric` for multi-tenant topology management
- `/vorticog` and `/digitwin` for simulation dynamics
- `/metamathematical-consciousness` for the fixed-point self-model
- `/circled-operators` for additive (choice) vs multiplicative (interaction) composition
