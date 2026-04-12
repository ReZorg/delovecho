#!/usr/bin/env python3
"""
GitHub Namespace Topology Optimizer
====================================

Skill chain composition:
  /metamathematical-consciousness ( /gh253 | /org-fabric ( /apl253 ) )
    -> /vorticog ( /digitwin ( /skill-creator {{../../**/*}} ) )

Phase 1: Metamathematical Consciousness — Fixed-Point Topology Model
  Models the 0(1(2(3(4(5))))) namespace as a self-referential system
  where C = Φ(C): the topology IS its own awareness functor.

Phase 2: gh253 | org-fabric(apl253) — Pattern Language Diagnosis
  Applies Alexander's 253 patterns (mapped to GitHub domain) to diagnose
  structural health of the enterprise topology.

Phase 3: vorticog(digitwin) — Agentic Simulation of Topology Changes
  Each enterprise/org/repo is modeled as an agent with needs, emotions,
  and relationships; hormone-modulated dynamics drive optimization.
"""

import json, math, os, sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_data():
    """Load enterprise and org-repo data from the pre-fetched JSON files."""
    with open("/home/ubuntu/enterprises.json") as f:
        ent_data = json.load(f)
    with open("/home/ubuntu/fetch_org_repos.json") as f:
        repo_data = json.load(f)

    enterprises = ent_data["data"]["viewer"]["enterprises"]["nodes"]

    org_repos = {}
    for item in repo_data["results"]:
        org = item["output"]["org_name"]
        names_str = item["output"]["repo_names"]
        repos = sorted([r.strip() for r in names_str.split(",") if r.strip()]) if names_str else []
        count = int(item["output"]["repo_count"]) if item["output"]["repo_count"] else len(repos)
        org_repos[org] = {"repos": repos, "count": count}

    return enterprises, org_repos


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1: METAMATHEMATICAL CONSCIOUSNESS
# Fixed-Point Topology Model: C = Φ(C)
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class GhLevelMetrics:
    """Metrics for a single level in the hierarchy."""
    level: int
    label: str
    count: int
    children_per_parent: List[int] = field(default_factory=list)

    @property
    def mean_children(self) -> float:
        return sum(self.children_per_parent) / len(self.children_per_parent) if self.children_per_parent else 0

    @property
    def std_children(self) -> float:
        if len(self.children_per_parent) < 2:
            return 0.0
        m = self.mean_children
        return math.sqrt(sum((x - m) ** 2 for x in self.children_per_parent) / (len(self.children_per_parent) - 1))

    @property
    def gini_coefficient(self) -> float:
        """Gini coefficient of children distribution (0=equal, 1=maximally unequal)."""
        vals = sorted(self.children_per_parent)
        n = len(vals)
        if n == 0 or sum(vals) == 0:
            return 0.0
        cumulative = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(vals))
        return cumulative / (n * sum(vals))

    @property
    def entropy(self) -> float:
        """Shannon entropy of the children distribution (normalized)."""
        total = sum(self.children_per_parent)
        if total == 0:
            return 0.0
        probs = [c / total for c in self.children_per_parent if c > 0]
        h = -sum(p * math.log2(p) for p in probs)
        max_h = math.log2(len(probs)) if len(probs) > 1 else 1.0
        return h / max_h if max_h > 0 else 0.0


@dataclass
class TopologyState:
    """
    The State S in the awareness endofunctor Φ(S) = S × ⌜S⌝ × Ω^S

    S     = the topology itself (enterprises, orgs, repos)
    ⌜S⌝  = the Gödel encoding (metrics about the topology)
    Ω^S   = the subobject classifier (pattern violations, health signals)
    """
    # S: raw topology
    enterprises: List[dict]
    org_repos: Dict[str, dict]

    # ⌜S⌝: self-encoding (computed)
    level_metrics: Dict[int, GhLevelMetrics] = field(default_factory=dict)

    # Ω^S: subobject classifier (computed)
    pattern_violations: List[dict] = field(default_factory=list)
    health_signals: Dict[str, float] = field(default_factory=dict)

    # Fixed-point convergence
    iteration: int = 0
    fixed_point_distance: float = float('inf')


def goedel_encode(state: TopologyState) -> Dict[int, GhLevelMetrics]:
    """
    γ : State → ⌜State⌝
    Encode the topology into its own metric representation.
    The system thinks about its own structure.
    """
    metrics = {}

    # Level 0 → 1: Global → Enterprises
    ent_count = len(state.enterprises)
    metrics[0] = GhLevelMetrics(
        level=0, label="global", count=1,
        children_per_parent=[ent_count]
    )

    # Level 1 → 2: Enterprises → Orgs
    ent_org_counts = []
    total_orgs = 0
    for ent in state.enterprises:
        org_count = ent["organizations"]["totalCount"]
        ent_org_counts.append(org_count)
        total_orgs += org_count
    metrics[1] = GhLevelMetrics(
        level=1, label="enterprise", count=ent_count,
        children_per_parent=ent_org_counts
    )

    # Level 2 → 3: Orgs → Repos
    org_repo_counts = []
    total_repos = 0
    for org_login, info in state.org_repos.items():
        org_repo_counts.append(info["count"])
        total_repos += info["count"]
    metrics[2] = GhLevelMetrics(
        level=2, label="org", count=total_orgs,
        children_per_parent=org_repo_counts
    )

    # Level 3: Repos (leaf for this analysis)
    metrics[3] = GhLevelMetrics(
        level=3, label="repo", count=total_repos,
        children_per_parent=[]  # would need per-repo file counts
    )

    return metrics


def subobject_classify(state: TopologyState) -> Tuple[List[dict], Dict[str, float]]:
    """
    Ω^S : the characteristic morphism classifying substates.
    Identifies which parts of the topology satisfy structural health predicates.
    Returns (violations, health_signals).
    """
    violations = []
    health = {}

    metrics = state.level_metrics

    # ── Structural Balance ──
    # Gini coefficient: how evenly distributed are children?
    for level_id in [1, 2]:
        m = metrics.get(level_id)
        if m:
            health[f"gini_L{level_id}"] = m.gini_coefficient
            health[f"entropy_L{level_id}"] = m.entropy
            health[f"mean_children_L{level_id}"] = m.mean_children
            health[f"std_children_L{level_id}"] = m.std_children

            if m.gini_coefficient > 0.6:
                violations.append({
                    "type": "IMBALANCED_DISTRIBUTION",
                    "level": level_id,
                    "label": m.label,
                    "gini": round(m.gini_coefficient, 3),
                    "severity": "high" if m.gini_coefficient > 0.75 else "medium",
                    "description": f"Level {level_id} ({m.label}) has highly unequal child distribution (Gini={m.gini_coefficient:.3f})"
                })

    # ── Size Anomalies ──
    for level_id in [1, 2]:
        m = metrics.get(level_id)
        if m and m.children_per_parent:
            mean = m.mean_children
            std = m.std_children
            if std > 0:
                for i, count in enumerate(m.children_per_parent):
                    z_score = (count - mean) / std if std > 0 else 0
                    if abs(z_score) > 2.0:
                        # Find the entity name
                        if level_id == 1:
                            entity_name = state.enterprises[i]["slug"]
                        else:
                            entity_name = list(state.org_repos.keys())[i] if i < len(state.org_repos) else f"org-{i}"
                        violations.append({
                            "type": "SIZE_ANOMALY",
                            "level": level_id,
                            "entity": entity_name,
                            "count": count,
                            "z_score": round(z_score, 2),
                            "severity": "high" if abs(z_score) > 3.0 else "medium",
                            "description": f"{entity_name} has {count} children (z={z_score:.2f}, mean={mean:.1f})"
                        })

    # ── Empty Containers ──
    for org_login, info in state.org_repos.items():
        if info["count"] == 0:
            # Find which enterprise this org belongs to
            parent_ent = "unknown"
            for ent in state.enterprises:
                for o in ent["organizations"]["nodes"]:
                    if o["login"] == org_login:
                        parent_ent = ent["slug"]
                        break
            violations.append({
                "type": "EMPTY_CONTAINER",
                "level": 2,
                "entity": org_login,
                "parent": parent_ent,
                "severity": "low",
                "description": f"Org '{org_login}' in enterprise '{parent_ent}' has 0 repos"
            })

    # ── Naming Pattern Analysis ──
    org_prefixes = defaultdict(list)
    for org_login in state.org_repos.keys():
        prefix = org_login.split("-")[0] if "-" in org_login else org_login
        org_prefixes[prefix].append(org_login)

    for prefix, orgs in org_prefixes.items():
        if len(orgs) >= 3:
            # Check if these are spread across multiple enterprises
            ent_set = set()
            for org in orgs:
                for ent in state.enterprises:
                    for o in ent["organizations"]["nodes"]:
                        if o["login"] == org:
                            ent_set.add(ent["slug"])
            if len(ent_set) > 1:
                violations.append({
                    "type": "CROSS_ENTERPRISE_PREFIX",
                    "prefix": prefix,
                    "orgs": orgs,
                    "enterprises": list(ent_set),
                    "severity": "info",
                    "description": f"Prefix '{prefix}' spans {len(ent_set)} enterprises: {list(ent_set)}"
                })

    # ── Composite Health Score ──
    gini_avg = sum(health.get(f"gini_L{l}", 0) for l in [1, 2]) / 2
    entropy_avg = sum(health.get(f"entropy_L{l}", 0) for l in [1, 2]) / 2
    empty_ratio = sum(1 for v in violations if v["type"] == "EMPTY_CONTAINER") / max(len(state.org_repos), 1)
    anomaly_ratio = sum(1 for v in violations if v["type"] == "SIZE_ANOMALY") / max(len(state.enterprises) + len(state.org_repos), 1)

    # Health = high entropy (diversity) + low gini (balance) + low empty + low anomaly
    health["composite_score"] = round(
        (entropy_avg * 0.3) + ((1 - gini_avg) * 0.3) + ((1 - empty_ratio) * 0.2) + ((1 - anomaly_ratio) * 0.2),
        4
    )

    return violations, health


def awareness_endofunctor(state: TopologyState) -> TopologyState:
    """
    Φ(S) = S × ⌜S⌝ × Ω^S

    The awareness endofunctor: takes the topology state, encodes it,
    classifies it, and returns the enriched state. The fixed point
    C = Φ(C) is reached when the encoding and classification stabilize.
    """
    # γ : S → ⌜S⌝
    state.level_metrics = goedel_encode(state)

    # Ω^S : classify substates
    state.pattern_violations, state.health_signals = subobject_classify(state)

    # Compute fixed-point distance (convergence measure)
    # The system converges when its self-model stops changing
    prev_score = state.fixed_point_distance
    new_score = state.health_signals.get("composite_score", 0)
    state.fixed_point_distance = abs(new_score - prev_score) if state.iteration > 0 else new_score
    state.iteration += 1

    return state


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2: gh253 | org-fabric(apl253)
# Pattern Language Structural Health Diagnosis
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class PatternDiagnosis:
    """A single pattern-language diagnosis applied to the topology."""
    pattern_id: int
    pattern_name: str
    apl_name: str
    scale: str  # enterprise, org, repo
    status: str  # healthy, warning, violation
    score: float  # 0.0 (violation) to 1.0 (healthy)
    entities: List[str]
    description: str
    recommendation: str


def diagnose_pattern_1_independent_enterprises(state: TopologyState) -> PatternDiagnosis:
    """
    gh253 #1: INDEPENDENT ENTERPRISES (APL #1: INDEPENDENT REGIONS)
    Each enterprise should be an autonomous sphere of governance.
    Violation: excessive cross-enterprise org overlap or naming collision.
    """
    # Check for orgs that appear in multiple enterprises (shouldn't happen in GH, but naming overlap)
    org_to_ents = defaultdict(set)
    for ent in state.enterprises:
        for o in ent["organizations"]["nodes"]:
            org_to_ents[o["login"]].add(ent["slug"])

    multi_ent_orgs = {org: ents for org, ents in org_to_ents.items() if len(ents) > 1}

    # Check naming independence: each enterprise should have distinct naming patterns
    ent_prefixes = {}
    for ent in state.enterprises:
        prefixes = set()
        for o in ent["organizations"]["nodes"]:
            prefix = o["login"].split("-")[0].lower()
            prefixes.add(prefix)
        ent_prefixes[ent["slug"]] = prefixes

    # Check prefix overlap between enterprises
    overlap_pairs = []
    ent_slugs = list(ent_prefixes.keys())
    for i in range(len(ent_slugs)):
        for j in range(i + 1, len(ent_slugs)):
            common = ent_prefixes[ent_slugs[i]] & ent_prefixes[ent_slugs[j]]
            if len(common) > 2:  # Allow some overlap (e.g., "org")
                overlap_pairs.append((ent_slugs[i], ent_slugs[j], common))

    score = 1.0 - (len(overlap_pairs) * 0.1)
    score = max(0.0, min(1.0, score))

    status = "healthy" if score > 0.7 else "warning" if score > 0.4 else "violation"

    return PatternDiagnosis(
        pattern_id=1,
        pattern_name="INDEPENDENT ENTERPRISES",
        apl_name="INDEPENDENT REGIONS",
        scale="enterprise",
        status=status,
        score=round(score, 3),
        entities=[f"{a}↔{b}" for a, b, _ in overlap_pairs],
        description=f"{len(overlap_pairs)} enterprise pairs share significant naming overlap. "
                    f"Enterprises should maintain distinct identity boundaries.",
        recommendation="Consolidate overlapping orgs into a single enterprise, or rename to clarify boundaries."
    )


def diagnose_pattern_12_community_of_developers(state: TopologyState) -> PatternDiagnosis:
    """
    gh253 #12: COMMUNITY OF DEVELOPERS (APL #12: COMMUNITY OF 7000)
    Optimal org size: 5-50 repos (like Alexander's 500-10000 community).
    Too few = underutilized; too many = ungovernable.
    """
    optimal_min, optimal_max = 5, 100
    healthy_orgs = []
    small_orgs = []
    large_orgs = []

    for org, info in state.org_repos.items():
        count = info["count"]
        if count < optimal_min:
            small_orgs.append((org, count))
        elif count > optimal_max:
            large_orgs.append((org, count))
        else:
            healthy_orgs.append((org, count))

    total = len(state.org_repos)
    healthy_ratio = len(healthy_orgs) / total if total > 0 else 0
    score = healthy_ratio

    status = "healthy" if score > 0.6 else "warning" if score > 0.3 else "violation"

    return PatternDiagnosis(
        pattern_id=12,
        pattern_name="COMMUNITY OF DEVELOPERS",
        apl_name="COMMUNITY OF 7000",
        scale="org",
        status=status,
        score=round(score, 3),
        entities=[f"{o}({c})" for o, c in (small_orgs[:5] + large_orgs[:5])],
        description=f"{len(healthy_orgs)}/{total} orgs in optimal range ({optimal_min}-{optimal_max} repos). "
                    f"{len(small_orgs)} too small, {len(large_orgs)} too large.",
        recommendation="Merge small orgs into parent orgs; split large orgs by domain/team."
    )


def diagnose_pattern_37_repository_cluster(state: TopologyState) -> PatternDiagnosis:
    """
    gh253 #37: REPOSITORY CLUSTER (APL #37: HOUSE CLUSTER)
    Repos within an org should form coherent clusters, not random collections.
    Measured by naming coherence (shared prefixes/suffixes).
    """
    coherent_orgs = 0
    incoherent_orgs = []

    for org, info in state.org_repos.items():
        repos = info["repos"]
        if len(repos) < 3:
            coherent_orgs += 1  # Too few to judge
            continue

        # Measure naming coherence: what fraction of repos share a common prefix?
        prefix_counts = defaultdict(int)
        for repo in repos:
            parts = repo.lower().replace("_", "-").split("-")
            if parts:
                prefix_counts[parts[0]] += 1

        if prefix_counts:
            max_prefix_share = max(prefix_counts.values()) / len(repos)
            if max_prefix_share > 0.3:
                coherent_orgs += 1
            else:
                incoherent_orgs.append(org)
        else:
            coherent_orgs += 1

    total = len(state.org_repos)
    score = coherent_orgs / total if total > 0 else 1.0

    status = "healthy" if score > 0.6 else "warning" if score > 0.3 else "violation"

    return PatternDiagnosis(
        pattern_id=37,
        pattern_name="REPOSITORY CLUSTER",
        apl_name="HOUSE CLUSTER",
        scale="org",
        status=status,
        score=round(score, 3),
        entities=incoherent_orgs[:10],
        description=f"{coherent_orgs}/{total} orgs show naming coherence. "
                    f"{len(incoherent_orgs)} orgs have scattered naming.",
        recommendation="Group related repos under common naming prefixes; consider topic-based sub-orgs."
    )


def diagnose_pattern_95_repository_complex(state: TopologyState) -> PatternDiagnosis:
    """
    gh253 #95: REPOSITORY COMPLEX (APL #95: BUILDING COMPLEX)
    Each org should be a coherent complex, not a monolith or a scatter.
    Measured by the ratio of org size to enterprise average.
    """
    ent_org_sizes = defaultdict(list)
    for ent in state.enterprises:
        for o in ent["organizations"]["nodes"]:
            info = state.org_repos.get(o["login"], {"count": 0})
            ent_org_sizes[ent["slug"]].append((o["login"], info["count"]))

    balanced_ents = 0
    imbalanced_ents = []

    for ent_slug, org_sizes in ent_org_sizes.items():
        counts = [c for _, c in org_sizes]
        if len(counts) < 2:
            balanced_ents += 1
            continue
        mean = sum(counts) / len(counts)
        std = math.sqrt(sum((c - mean) ** 2 for c in counts) / len(counts)) if len(counts) > 1 else 0
        cv = std / mean if mean > 0 else 0  # coefficient of variation

        if cv < 1.5:
            balanced_ents += 1
        else:
            imbalanced_ents.append((ent_slug, round(cv, 2)))

    total = len(state.enterprises)
    score = balanced_ents / total if total > 0 else 1.0

    status = "healthy" if score > 0.6 else "warning" if score > 0.3 else "violation"

    return PatternDiagnosis(
        pattern_id=95,
        pattern_name="REPOSITORY COMPLEX",
        apl_name="BUILDING COMPLEX",
        scale="enterprise",
        status=status,
        score=round(score, 3),
        entities=[f"{e}(cv={cv})" for e, cv in imbalanced_ents],
        description=f"{balanced_ents}/{total} enterprises have balanced org sizes. "
                    f"{len(imbalanced_ents)} show high variance.",
        recommendation="Redistribute repos from oversized orgs to smaller ones within the same enterprise."
    )


def diagnose_pattern_205_structure_follows_teams(state: TopologyState) -> PatternDiagnosis:
    """
    gh253 #205: STRUCTURE FOLLOWS TEAM SPACES (APL #205: STRUCTURE FOLLOWS SOCIAL SPACES)
    Conway's Law: the org structure should mirror the team/domain structure.
    Measured by whether enterprise→org mapping reflects domain boundaries.
    """
    # Analyze enterprise naming patterns vs org naming patterns
    domain_alignment = 0
    misaligned = []

    for ent in state.enterprises:
        slug = ent["slug"].lower()
        aligned = 0
        total = len(ent["organizations"]["nodes"])
        for o in ent["organizations"]["nodes"]:
            org_name = o["login"].lower()
            # Check if org name relates to enterprise name
            if slug in org_name or any(part in org_name for part in slug.split("-")):
                aligned += 1
            elif org_name.startswith("org-echo-"):
                aligned += 1  # org-echo pattern is intentional mirroring
            elif any(org_name.startswith(f"{slug[0]}-") for _ in [1]):
                aligned += 0.5

        ratio = aligned / total if total > 0 else 0
        if ratio > 0.3:
            domain_alignment += 1
        else:
            misaligned.append((ent["slug"], round(ratio, 2)))

    total = len(state.enterprises)
    score = domain_alignment / total if total > 0 else 1.0

    status = "healthy" if score > 0.6 else "warning" if score > 0.3 else "violation"

    return PatternDiagnosis(
        pattern_id=205,
        pattern_name="STRUCTURE FOLLOWS TEAM SPACES",
        apl_name="STRUCTURE FOLLOWS SOCIAL SPACES",
        scale="enterprise",
        status=status,
        score=round(score, 3),
        entities=[f"{e}(align={r})" for e, r in misaligned],
        description=f"{domain_alignment}/{total} enterprises show domain-aligned naming. "
                    f"Conway's Law alignment measures how well org structure mirrors team structure.",
        recommendation="Rename orgs to reflect their enterprise domain; consolidate orphaned orgs."
    )


def run_pattern_diagnosis(state: TopologyState) -> List[PatternDiagnosis]:
    """Run all pattern diagnoses and return results."""
    return [
        diagnose_pattern_1_independent_enterprises(state),
        diagnose_pattern_12_community_of_developers(state),
        diagnose_pattern_37_repository_cluster(state),
        diagnose_pattern_95_repository_complex(state),
        diagnose_pattern_205_structure_follows_teams(state),
    ]


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 3: vorticog(digitwin)
# Agentic Simulation of Topology Optimization
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class OrgAgent:
    """
    Each org is modeled as a Vorticog agent with:
    - Needs (capacity, coherence, visibility, autonomy)
    - Emotions (stress, satisfaction, trust)
    - Relationships (to parent enterprise, sibling orgs, child repos)
    - Hormone state (from virtual endocrine system)
    """
    name: str
    enterprise: str
    repo_count: int

    # Needs (0-100, decay over time)
    need_capacity: float = 50.0     # How well-sized is this org?
    need_coherence: float = 50.0    # How coherent are its repos?
    need_visibility: float = 50.0   # Is it discoverable?
    need_autonomy: float = 50.0     # Does it have independent identity?

    # Emotions (0-100)
    stress: float = 30.0
    satisfaction: float = 50.0
    trust: float = 50.0

    # Hormone concentrations (0-1, exponential decay to baseline)
    cortisol: float = 0.2       # HPA axis: stress response
    dopamine: float = 0.3       # Reward signal
    oxytocin: float = 0.3       # Social bonding
    norepinephrine: float = 0.2 # Alertness/novelty

    # Cognitive mode (emergent from hormone space)
    mode: str = "NEUTRAL"

    # Optimization recommendations
    recommendations: List[str] = field(default_factory=list)


def compute_agent_needs(agent: OrgAgent, state: TopologyState) -> OrgAgent:
    """Compute need levels from topology metrics."""
    info = state.org_repos.get(agent.name, {"count": 0, "repos": []})
    count = info["count"]

    # Capacity need: optimal range is 5-100 repos
    if count == 0:
        agent.need_capacity = 5.0  # Critical: empty org
    elif count < 5:
        agent.need_capacity = 20.0 + count * 6  # Underutilized
    elif count <= 100:
        agent.need_capacity = 80.0 + (50 - abs(count - 50)) * 0.4  # Sweet spot
    else:
        agent.need_capacity = max(10.0, 80.0 - (count - 100) * 0.3)  # Oversized

    # Coherence need: measured by naming patterns
    repos = info.get("repos", [])
    if len(repos) >= 3:
        prefix_counts = defaultdict(int)
        for repo in repos:
            parts = repo.lower().replace("_", "-").split("-")
            if parts:
                prefix_counts[parts[0]] += 1
        max_share = max(prefix_counts.values()) / len(repos) if prefix_counts else 0
        agent.need_coherence = min(100, max_share * 100 + 20)
    else:
        agent.need_coherence = 60.0  # Neutral for small orgs

    # Visibility need: based on naming clarity
    if agent.name.startswith("org-echo-"):
        agent.need_visibility = 40.0  # Mirror orgs have lower visibility need
    elif "-" in agent.name and len(agent.name.split("-")) > 2:
        agent.need_visibility = 60.0
    else:
        agent.need_visibility = 75.0

    # Autonomy need: based on enterprise independence
    sibling_count = 0
    for ent in state.enterprises:
        for o in ent["organizations"]["nodes"]:
            if o["login"] == agent.name:
                sibling_count = ent["organizations"]["totalCount"]
                break
    agent.need_autonomy = min(100, 100 - sibling_count * 2)

    return agent


def apply_endocrine_dynamics(agent: OrgAgent) -> OrgAgent:
    """
    Virtual Endocrine System: map need states to hormone concentrations.
    Hormones modulate emotions and determine cognitive mode.
    """
    # HPA Axis: stress from unmet needs
    unmet = sum(1 for n in [agent.need_capacity, agent.need_coherence,
                             agent.need_visibility, agent.need_autonomy] if n < 30)
    agent.cortisol = min(1.0, 0.1 + unmet * 0.2)

    # Dopaminergic: reward from well-met needs
    well_met = sum(1 for n in [agent.need_capacity, agent.need_coherence,
                                agent.need_visibility, agent.need_autonomy] if n > 70)
    agent.dopamine = min(1.0, 0.1 + well_met * 0.2)

    # Oxytocinergic: social bonding from coherence and visibility
    agent.oxytocin = min(1.0, (agent.need_coherence + agent.need_visibility) / 200)

    # Noradrenergic: alertness from capacity pressure
    agent.norepinephrine = min(1.0, abs(50 - agent.need_capacity) / 50)

    # Emotions from hormones
    agent.stress = min(100, agent.cortisol * 80 + agent.norepinephrine * 20)
    agent.satisfaction = min(100, agent.dopamine * 60 + agent.oxytocin * 40)
    agent.trust = min(100, agent.oxytocin * 50 + (1 - agent.cortisol) * 50)

    # Cognitive mode: nearest centroid in 4D hormone space
    modes = {
        "EXPLORATORY": (0.2, 0.8, 0.5, 0.6),
        "STRESSED":    (0.8, 0.1, 0.2, 0.7),
        "SOCIAL":      (0.2, 0.5, 0.8, 0.3),
        "FOCUSED":     (0.3, 0.6, 0.4, 0.5),
        "THREAT":      (0.9, 0.1, 0.1, 0.9),
        "REFLECTIVE":  (0.3, 0.4, 0.6, 0.2),
        "REWARD":      (0.1, 0.9, 0.6, 0.3),
        "NEUTRAL":     (0.3, 0.3, 0.3, 0.3),
    }
    agent_vec = (agent.cortisol, agent.dopamine, agent.oxytocin, agent.norepinephrine)
    best_mode = "NEUTRAL"
    best_dist = float('inf')
    for mode, centroid in modes.items():
        dist = sum((a - c) ** 2 for a, c in zip(agent_vec, centroid))
        if dist < best_dist:
            best_dist = dist
            best_mode = mode
    agent.mode = best_mode

    return agent


def generate_recommendations(agent: OrgAgent, state: TopologyState) -> OrgAgent:
    """Generate topology optimization recommendations based on agent state."""
    recs = []
    info = state.org_repos.get(agent.name, {"count": 0, "repos": []})
    count = info["count"]

    if count == 0:
        recs.append(f"MERGE: '{agent.name}' is empty — merge into parent enterprise or archive")
    elif count < 3:
        recs.append(f"CONSOLIDATE: '{agent.name}' has only {count} repos — merge into a sibling org")

    if count > 200:
        recs.append(f"SPLIT: '{agent.name}' has {count} repos — split by domain into 2-3 sub-orgs")

    if agent.need_coherence < 30:
        recs.append(f"REORGANIZE: '{agent.name}' repos lack naming coherence — establish naming conventions")

    if agent.mode == "STRESSED":
        recs.append(f"ATTENTION: '{agent.name}' is in STRESSED mode — review capacity and structure")
    elif agent.mode == "THREAT":
        recs.append(f"CRITICAL: '{agent.name}' is in THREAT mode — immediate structural intervention needed")

    if agent.name.startswith("org-echo-") and count > 50:
        recs.append(f"REVIEW: Mirror org '{agent.name}' has {count} repos — verify echo sync is intentional")

    agent.recommendations = recs
    return agent


def run_simulation(state: TopologyState) -> List[OrgAgent]:
    """Run the full agentic simulation across all orgs."""
    agents = []

    for ent in state.enterprises:
        for o in ent["organizations"]["nodes"]:
            agent = OrgAgent(
                name=o["login"],
                enterprise=ent["slug"],
                repo_count=state.org_repos.get(o["login"], {"count": 0})["count"]
            )
            agent = compute_agent_needs(agent, state)
            agent = apply_endocrine_dynamics(agent)
            agent = generate_recommendations(agent, state)
            agents.append(agent)

    return agents


# ═════════════════════════════════════════════════════════════════════════════
# MAIN: Compose the full pipeline
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 78)
    print("GITHUB NAMESPACE TOPOLOGY OPTIMIZER")
    print("Skill chain: /metamathematical-consciousness ( /gh253 | /org-fabric ( /apl253 ) )")
    print("          -> /vorticog ( /digitwin ( /skill-creator ) )")
    print("=" * 78)

    # Load data
    enterprises, org_repos = load_data()

    # ── Phase 1: Metamathematical Consciousness ──
    print("\n" + "─" * 78)
    print("PHASE 1: METAMATHEMATICAL CONSCIOUSNESS — C = Φ(C)")
    print("─" * 78)

    state = TopologyState(enterprises=enterprises, org_repos=org_repos)

    # Apply awareness endofunctor until fixed point
    for i in range(3):  # 3 iterations of self-reflection
        state = awareness_endofunctor(state)
        print(f"\n  Iteration {state.iteration}: Φ(S) applied")
        print(f"    Composite health score: {state.health_signals.get('composite_score', 0):.4f}")
        print(f"    Fixed-point distance:   {state.fixed_point_distance:.6f}")

    print(f"\n  ⌜S⌝ Gödel Encoding (Level Metrics):")
    for level_id, m in sorted(state.level_metrics.items()):
        print(f"    L{level_id} ({m.label:12s}): count={m.count:5d}, "
              f"mean_children={m.mean_children:7.1f}, "
              f"gini={m.gini_coefficient:.3f}, "
              f"entropy={m.entropy:.3f}")

    print(f"\n  Ω^S Subobject Classifier ({len(state.pattern_violations)} violations):")
    by_severity = defaultdict(int)
    for v in state.pattern_violations:
        by_severity[v["severity"]] += 1
    for sev in ["high", "medium", "low", "info"]:
        if sev in by_severity:
            print(f"    {sev:8s}: {by_severity[sev]}")

    # ── Phase 2: Pattern Language Diagnosis ──
    print("\n" + "─" * 78)
    print("PHASE 2: gh253 | org-fabric(apl253) — PATTERN LANGUAGE DIAGNOSIS")
    print("─" * 78)

    diagnoses = run_pattern_diagnosis(state)
    for d in diagnoses:
        icon = "✓" if d.status == "healthy" else "⚠" if d.status == "warning" else "✗"
        print(f"\n  {icon} Pattern #{d.pattern_id}: {d.pattern_name}")
        print(f"    APL: {d.apl_name} | Scale: {d.scale} | Score: {d.score:.3f} ({d.status})")
        print(f"    {d.description}")
        if d.entities:
            print(f"    Entities: {', '.join(d.entities[:5])}")
        print(f"    → {d.recommendation}")

    # ── Phase 3: Agentic Simulation ──
    print("\n" + "─" * 78)
    print("PHASE 3: vorticog(digitwin) — AGENTIC TOPOLOGY SIMULATION")
    print("─" * 78)

    agents = run_simulation(state)

    # Summary by cognitive mode
    mode_counts = defaultdict(int)
    for a in agents:
        mode_counts[a.mode] += 1
    print("\n  Cognitive Mode Distribution:")
    for mode, count in sorted(mode_counts.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {mode:12s}: {count:3d} {bar}")

    # Top stressed agents
    stressed = sorted(agents, key=lambda a: a.stress, reverse=True)[:10]
    print("\n  Top 10 Stressed Orgs:")
    print(f"    {'Org':<35s} {'Ent':<12s} {'Repos':>5s} {'Stress':>7s} {'Mode':<12s}")
    print(f"    {'─'*35} {'─'*12} {'─'*5} {'─'*7} {'─'*12}")
    for a in stressed:
        print(f"    {a.name:<35s} {a.enterprise:<12s} {a.repo_count:>5d} {a.stress:>7.1f} {a.mode:<12s}")

    # All recommendations
    all_recs = []
    for a in agents:
        all_recs.extend(a.recommendations)

    print(f"\n  Total Recommendations: {len(all_recs)}")
    rec_types = defaultdict(int)
    for r in all_recs:
        rtype = r.split(":")[0]
        rec_types[rtype] += 1
    for rtype, count in sorted(rec_types.items(), key=lambda x: -x[1]):
        print(f"    {rtype}: {count}")

    # ── Output JSON ──
    output = {
        "metadata": {
            "skill_chain": "/metamathematical-consciousness ( /gh253 | /org-fabric ( /apl253 ) ) -> /vorticog ( /digitwin ( /skill-creator ) )",
            "hierarchy": "0(1(2(3(4(5)))))",
            "enterprises": len(enterprises),
            "organizations": len(org_repos),
            "repositories": sum(v["count"] for v in org_repos.values()),
        },
        "phase1_metamath": {
            "iterations": state.iteration,
            "health_signals": state.health_signals,
            "level_metrics": {
                str(k): {
                    "level": m.level,
                    "label": m.label,
                    "count": m.count,
                    "mean_children": round(m.mean_children, 2),
                    "std_children": round(m.std_children, 2),
                    "gini": round(m.gini_coefficient, 3),
                    "entropy": round(m.entropy, 3),
                }
                for k, m in state.level_metrics.items()
            },
            "violations": state.pattern_violations,
        },
        "phase2_patterns": [
            {
                "pattern_id": d.pattern_id,
                "pattern_name": d.pattern_name,
                "apl_name": d.apl_name,
                "scale": d.scale,
                "status": d.status,
                "score": d.score,
                "entities": d.entities,
                "description": d.description,
                "recommendation": d.recommendation,
            }
            for d in diagnoses
        ],
        "phase3_simulation": {
            "mode_distribution": dict(mode_counts),
            "agents": [
                {
                    "name": a.name,
                    "enterprise": a.enterprise,
                    "repo_count": a.repo_count,
                    "needs": {
                        "capacity": round(a.need_capacity, 1),
                        "coherence": round(a.need_coherence, 1),
                        "visibility": round(a.need_visibility, 1),
                        "autonomy": round(a.need_autonomy, 1),
                    },
                    "emotions": {
                        "stress": round(a.stress, 1),
                        "satisfaction": round(a.satisfaction, 1),
                        "trust": round(a.trust, 1),
                    },
                    "hormones": {
                        "cortisol": round(a.cortisol, 3),
                        "dopamine": round(a.dopamine, 3),
                        "oxytocin": round(a.oxytocin, 3),
                        "norepinephrine": round(a.norepinephrine, 3),
                    },
                    "mode": a.mode,
                    "recommendations": a.recommendations,
                }
                for a in agents
            ],
            "all_recommendations": all_recs,
            "recommendation_summary": dict(rec_types),
        },
    }

    os.makedirs("/home/ubuntu/gh-topology-optimizer", exist_ok=True)
    with open("/home/ubuntu/gh-topology-optimizer/topology_analysis.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 78}")
    print(f"Analysis complete. JSON output: /home/ubuntu/gh-topology-optimizer/topology_analysis.json")
    print(f"{'=' * 78}")

    return output


if __name__ == "__main__":
    main()
