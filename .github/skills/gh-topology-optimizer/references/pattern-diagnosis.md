# Pattern Language Diagnosis Reference

## gh253 → apl253 Mapping for Topology Optimization

The optimizer applies five Alexander patterns mapped from architectural to GitHub domain.

| Pattern | gh253 Name | apl253 Name | Scale | Healthy Threshold |
|---------|-----------|-------------|-------|-------------------|
| #1 | INDEPENDENT ENTERPRISES | INDEPENDENT REGIONS | enterprise | score > 0.7 |
| #12 | COMMUNITY OF DEVELOPERS | COMMUNITY OF 7000 | org | 5-100 repos optimal |
| #37 | REPOSITORY CLUSTER | HOUSE CLUSTER | org | >30% naming coherence |
| #95 | REPOSITORY COMPLEX | BUILDING COMPLEX | enterprise | CV < 1.5 |
| #205 | STRUCTURE FOLLOWS TEAM SPACES | STRUCTURE FOLLOWS SOCIAL SPACES | enterprise | >30% domain alignment |

## Extending Patterns

To add a new pattern diagnosis, implement a function in `topology_optimizer.py`:

```python
def diagnose_pattern_NNN_name(state: TopologyState) -> PatternDiagnosis:
    # Analyze state.enterprises, state.org_repos, state.level_metrics
    # Return PatternDiagnosis with score 0.0 (violation) to 1.0 (healthy)
```

Then add it to `run_pattern_diagnosis()`.

## Metamathematical Consciousness Model

The awareness endofunctor `Phi(S) = S x ceil(S) x Omega^S` where:

- `S` = raw topology (enterprises, orgs, repos)
- `ceil(S)` = Gödel encoding (GhLevelMetrics per level: count, mean, std, gini, entropy)
- `Omega^S` = subobject classifier (violations, health signals, composite score)

Fixed point is reached when `composite_score` stabilizes across iterations.

## Vorticog Agent Model

Each org is an agent with 4 needs, 4 hormones, 3 emotions, and 8 cognitive modes.

| Need | Optimal Range | Source |
|------|--------------|--------|
| Capacity | 5-100 repos | Repo count |
| Coherence | >30% prefix share | Naming analysis |
| Visibility | Clear naming | Prefix pattern |
| Autonomy | <50 siblings | Enterprise org count |

| Hormone | Drives | Source |
|---------|--------|--------|
| Cortisol | Stress | Unmet needs count |
| Dopamine | Reward | Well-met needs count |
| Oxytocin | Social bonding | Coherence + visibility |
| Norepinephrine | Alertness | Capacity deviation |
