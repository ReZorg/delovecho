#!/usr/bin/env python3
"""
Circled-Operators Algebraic Topology Analysis for opencog/* ⊕ openclaw/*

Applies the semiring (R, ⊕, ⊗, 0, 1) to the repository dependency graph:
  ⊕ = Disjoint union (independent repos coexist)
  ⊗ = Dependency integration (repo A depends on repo B)
  0 = Empty repo (no code, no deps)
  1 = Scaffold (cogutil — the identity element everything depends on)

Produces:
  1. Dependency adjacency matrix D[N×N]
  2. Tier assignments (topological sort)
  3. ⊕-components (independent subgraphs)
  4. ⊗-chains (dependency pipelines)
  5. Cross-org bridge analysis (opencog ⊗ openclaw)
  6. Neural network initialization weights
"""

import json
import numpy as np
from collections import defaultdict, deque

# Load scan data
with open('/home/ubuntu/repo_metadata_scan.json') as f:
    data = json.load(f)

# Build component registry
components = {}
for r in data['results']:
    o = r['output']
    repo = o['repo']
    short = repo.split('/')[-1]
    components[short] = {
        'full': repo,
        'org': o['org'],
        'lang': o['primary_language'],
        'build': o['build_system'],
        'archived': o['archived'],
        'size': o['size_kb'],
        'deps_raw': o['internal_deps'],
        'topics': o['topics'],
    }

# Parse dependencies into graph
dep_graph = defaultdict(set)  # component -> set of deps
reverse_graph = defaultdict(set)  # component -> set of dependents

for name, info in components.items():
    deps_str = info['deps_raw']
    if deps_str and deps_str != 'none':
        for dep in deps_str.split(','):
            dep = dep.strip()
            # Normalize: find the actual component name
            if dep in components:
                dep_graph[name].add(dep)
                reverse_graph[dep].add(name)
            else:
                # Try to find partial match
                matches = [c for c in components if dep.lower() in c.lower()]
                if matches:
                    best = matches[0]
                    dep_graph[name].add(best)
                    reverse_graph[best].add(name)

# ============================================
# TOPOLOGICAL SORT → TIER ASSIGNMENT
# ============================================
def topological_tiers(graph, all_nodes):
    """Kahn's algorithm with tier tracking"""
    in_degree = defaultdict(int)
    for node in all_nodes:
        in_degree[node] = 0
    for node, deps in graph.items():
        for dep in deps:
            in_degree[node] += 1  # node depends on dep
    
    tiers = {}
    queue = deque()
    for node in all_nodes:
        if in_degree[node] == 0:
            queue.append(node)
            tiers[node] = 0
    
    while queue:
        node = queue.popleft()
        for dependent in reverse_graph.get(node, []):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                tiers[dependent] = tiers[node] + 1
                queue.append(dependent)
    
    # Assign unresolved nodes to max tier + 1
    max_tier = max(tiers.values()) if tiers else 0
    for node in all_nodes:
        if node not in tiers:
            tiers[node] = max_tier + 1
    
    return tiers

all_nodes = set(components.keys())
tiers = topological_tiers(dep_graph, all_nodes)
max_tier = max(tiers.values())

# ============================================
# ⊕-COMPONENTS (Independent Subgraphs)
# ============================================
def find_connected_components(nodes, graph, reverse):
    """Find ⊕-components (disjoint union of independent subgraphs)"""
    visited = set()
    components_list = []
    
    for node in nodes:
        if node not in visited:
            component = set()
            stack = [node]
            while stack:
                n = stack.pop()
                if n in visited:
                    continue
                visited.add(n)
                component.add(n)
                for dep in graph.get(n, []):
                    stack.append(dep)
                for dependent in reverse.get(n, []):
                    stack.append(dependent)
            components_list.append(component)
    
    return components_list

oplus_components = find_connected_components(all_nodes, dep_graph, reverse_graph)
oplus_components.sort(key=len, reverse=True)

# ============================================
# ⊗-CHAINS (Longest Dependency Pipelines)
# ============================================
def find_longest_chains(graph, tiers):
    """Find ⊗-chains (multiplicative dependency pipelines)"""
    chains = []
    
    def dfs_chain(node, current_chain):
        dependents = reverse_graph.get(node, set())
        if not dependents:
            chains.append(list(current_chain))
            return
        for dep in dependents:
            current_chain.append(dep)
            dfs_chain(dep, current_chain)
            current_chain.pop()
    
    # Start from tier-0 nodes
    for node in sorted(all_nodes):
        if tiers.get(node, 0) == 0 and reverse_graph.get(node):
            dfs_chain(node, [node])
    
    chains.sort(key=len, reverse=True)
    return chains[:20]  # Top 20

otimes_chains = find_longest_chains(dep_graph, tiers)

# ============================================
# CROSS-ORG BRIDGE ANALYSIS
# ============================================
cross_org_bridges = []
for name, deps in dep_graph.items():
    for dep in deps:
        if components[name]['org'] != components.get(dep, {}).get('org', components[name]['org']):
            cross_org_bridges.append((name, dep))

# ============================================
# ADJACENCY MATRIX FOR NEURAL NETWORK
# ============================================
sorted_nodes = sorted(all_nodes)
node_idx = {n: i for i, n in enumerate(sorted_nodes)}
N = len(sorted_nodes)

# Dependency matrix D[i,j] = 1 if i depends on j
D = np.zeros((N, N))
for name, deps in dep_graph.items():
    for dep in deps:
        if name in node_idx and dep in node_idx:
            D[node_idx[name], node_idx[dep]] = 1.0

# Position embedding P[i,s] seeded from tiers
S = max_tier + 2  # number of steps
P = np.zeros((N, S))
for name, tier in tiers.items():
    if name in node_idx:
        P[node_idx[name], min(tier, S-1)] = 2.0  # warm-start

# ============================================
# STATISTICS
# ============================================
stats = {
    'total_repos': len(components),
    'opencog_repos': sum(1 for c in components.values() if c['org'] == 'opencog'),
    'openclaw_repos': sum(1 for c in components.values() if c['org'] == 'openclaw'),
    'repos_with_deps': sum(1 for d in dep_graph.values() if d),
    'total_dep_edges': sum(len(d) for d in dep_graph.values()),
    'max_tier': max_tier,
    'num_tiers': max_tier + 1,
    'oplus_components': len(oplus_components),
    'largest_component_size': len(oplus_components[0]) if oplus_components else 0,
    'longest_chain_length': len(otimes_chains[0]) if otimes_chains else 0,
    'cross_org_bridges': len(cross_org_bridges),
    'archived_repos': sum(1 for c in components.values() if c['archived']),
    'cmake_repos': sum(1 for c in components.values() if c['build'] == 'cmake'),
    'parameters_N': N,
    'parameters_S': S,
    'parameters_total': N * S + N * N,
}

# ============================================
# OUTPUT
# ============================================
print("=" * 70)
print("CIRCLED-OPERATORS TOPOLOGY ANALYSIS")
print(f"opencog/* ⊕ openclaw/* = {stats['total_repos']} repositories")
print("=" * 70)

print(f"\n📊 SEMIRING STATISTICS")
print(f"  Total repos (|R|):           {stats['total_repos']}")
print(f"  opencog repos:               {stats['opencog_repos']}")
print(f"  openclaw repos:              {stats['openclaw_repos']}")
print(f"  Dependency edges (|⊗|):      {stats['total_dep_edges']}")
print(f"  Independent components (|⊕|): {stats['oplus_components']}")
print(f"  Build tiers:                 {stats['num_tiers']}")
print(f"  Longest ⊗-chain:            {stats['longest_chain_length']}")
print(f"  Cross-org bridges:           {stats['cross_org_bridges']}")
print(f"  Archived repos:              {stats['archived_repos']}")

print(f"\n🧮 NEURAL NETWORK DIMENSIONS")
print(f"  Components (N):              {stats['parameters_N']}")
print(f"  Build steps (S):             {stats['parameters_S']}")
print(f"  Position params (N×S):       {N * S}")
print(f"  Dependency params (N×N):     {N * N}")
print(f"  Total parameters:            {stats['parameters_total']}")

print(f"\n🏗️ TIER ASSIGNMENTS (Topological Sort)")
for tier in range(max_tier + 2):
    tier_nodes = [n for n, t in tiers.items() if t == tier]
    if tier_nodes:
        tier_nodes.sort()
        org_breakdown = defaultdict(list)
        for n in tier_nodes:
            org_breakdown[components[n]['org']].append(n)
        parts = []
        for org in ['opencog', 'openclaw']:
            if org in org_breakdown:
                parts.append(f"{org}: {', '.join(org_breakdown[org])}")
        print(f"  Tier {tier} ({len(tier_nodes)} repos): {' | '.join(parts)}")

print(f"\n⊕ INDEPENDENT COMPONENTS (Disjoint Union)")
for i, comp in enumerate(oplus_components[:10]):
    orgs = defaultdict(int)
    for n in comp:
        orgs[components[n]['org']] += 1
    org_str = ', '.join(f"{o}:{c}" for o, c in sorted(orgs.items()))
    print(f"  Component {i+1} ({len(comp)} repos, {org_str}): {', '.join(sorted(comp)[:8])}{'...' if len(comp) > 8 else ''}")

print(f"\n⊗ LONGEST DEPENDENCY CHAINS (Multiplicative Pipelines)")
for i, chain in enumerate(otimes_chains[:10]):
    print(f"  Chain {i+1} (len={len(chain)}): {' → '.join(chain)}")

print(f"\n🌉 CROSS-ORG BRIDGES (opencog ⊗ openclaw)")
if cross_org_bridges:
    for src, dst in cross_org_bridges:
        print(f"  {components[src]['org']}/{src} → {components[dst]['org']}/{dst}")
else:
    print("  No direct cross-org dependencies detected")
    print("  The two orgs form a pure ⊕ (disjoint union)")

# ============================================
# IDENTITY ELEMENT ANALYSIS
# ============================================
print(f"\n🔑 IDENTITY ELEMENT (1 = most depended-upon)")
dep_counts = [(name, len(deps)) for name, deps in reverse_graph.items()]
dep_counts.sort(key=lambda x: -x[1])
for name, count in dep_counts[:10]:
    print(f"  {name}: {count} dependents ({components[name]['org']})")

print(f"\n🕳️ ZERO ELEMENTS (0 = no code, no deps, no dependents)")
zeros = [n for n in all_nodes if not dep_graph.get(n) and not reverse_graph.get(n)]
zeros.sort()
for n in zeros[:20]:
    print(f"  {n} ({components[n]['org']}, {components[n]['lang']}, {components[n]['size']}KB)")

# Save neural state
neural_state = {
    'components': sorted_nodes,
    'n_components': N,
    'n_steps': S,
    'tiers': {n: int(t) for n, t in tiers.items()},
    'dep_graph': {n: sorted(list(d)) for n, d in dep_graph.items() if d},
    'reverse_graph': {n: sorted(list(d)) for n, d in reverse_graph.items() if d},
    'oplus_components': [sorted(list(c)) for c in oplus_components],
    'otimes_chains': otimes_chains[:20],
    'cross_org_bridges': cross_org_bridges,
    'stats': stats,
    'position_weight_seed': P.tolist(),
    'dependency_matrix': D.tolist(),
}

with open('/home/ubuntu/topology_analysis.json', 'w') as f:
    json.dump(neural_state, f, indent=2)

print(f"\n✅ Topology analysis saved to /home/ubuntu/topology_analysis.json")
print(f"   Neural state: {N} components × {S} steps = {N*S + N*N} parameters")
