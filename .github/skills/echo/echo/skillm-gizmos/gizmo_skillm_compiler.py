#!/usr/bin/env python3
"""
GizmoSkillm Compiler: F(nn.Network) → skillm.AST
Applies the function-creator functor to compile the ReZorg/gizmos repository
into a procedural language model AST.

The Core Equation:
  ( ( ( * ) , ** ) , *** )
  *   = nn.Module (action verbs)
  **  = F (this compiler)
  *** = GizmoSkillm AST
"""
import json, os, glob
from collections import Counter

# ── Phase 1: DISCOVER — Scan the repository ──
def discover_gizmos(repo_path):
    """nn.Linear(DISCOVER, scan) → gizmo file list"""
    bootstrap_path = os.path.join(repo_path, 'bootstrap-gizmos.json')
    with open(bootstrap_path) as f:
        data = json.load(f)
    gizmos_list = data.get('gizmos', [])
    
    individual_files = sorted(glob.glob(os.path.join(repo_path, 'gizmos', '*.json')))
    
    return {
        'bootstrap_count': len(gizmos_list),
        'individual_count': len(individual_files),
        'bootstrap_data': gizmos_list,
        'individual_files': individual_files
    }

# ── Phase 2: INSPECT — Parse each gizmo ──
def inspect_gizmos(discovery):
    """nn.Linear(INSPECT, parse) → structured records"""
    records = []
    for item in discovery['bootstrap_data']:
        resource = item.get('resource', {})
        gizmo = resource.get('gizmo', {})
        tools = item.get('tools', [])
        files = item.get('files', [])
        
        instructions = gizmo.get('instructions', '') or ''
        display = gizmo.get('display', {})
        
        records.append({
            'id': gizmo.get('id', ''),
            'name': display.get('name', gizmo.get('name', 'unknown')),
            'description': (display.get('description', '') or '')[:300],
            'instructions_len': len(instructions),
            'instructions_preview': instructions[:200],
            'tools': [t.get('type', '') for t in tools],
            'num_files': len(files),
            'short_url': gizmo.get('short_url', ''),
        })
    return records

# ── Phase 3: CLASSIFY — Domain taxonomy ──
def classify_gizmos(records):
    """nn.Linear(CLASSIFY, categorize) → domain taxonomy"""
    domain_rules = {
        'Skincare/RegimA': ['skincare', 'regima', 'skin twin', 'formulation', 'zone concept', 'medic reactor'],
        'Cognitive/AGI': ['cogprime', 'opencog', 'agi', 'cognitive', 'hypergraph', 'atomspace', 'llml', 'hypercog'],
        'Creative/Wizard': ['wizard', 'unicorn', 'grimoire', 'alchemy', 'garganthaclops', 'cosmic order'],
        'ML/Architecture': ['machine learning', 'neural', 'model builder', 'architect', 'dynamic architect', 'incremental'],
        'Math/Science': ['math', 'numerical', 'gromacs', 'molecular', 'docking', 'wolfram', 'symbolic', 'prolog'],
        'Dev Tools': ['api', 'postman', 'json', 'converter', 'extractor', 'cursor', 'data integration', 'config'],
        'Task Management': ['taskmaster', 'task', 'fixgpt'],
        'Self-Image/Meta': ['autognosis', 'self-image', 'auto-gnosis', 'agsi', 'meaning crisis', 'autoexpert'],
        'Governance/Org': ['holacracy', 'holaspirit', 'governance', 'constitution', 'co-operative', 'enlightened manager'],
        'Hyper/Meta-Prompting': ['hyper', 'hyperdan', 'hyperweeeeeee', 'hyper-expert', 'hyper-titsopolis'],
    }
    
    taxonomy = {d: [] for d in domain_rules}
    unclassified = []
    
    for r in records:
        text = (r['name'] + ' ' + r['description']).lower()
        classified = False
        for domain, keywords in domain_rules.items():
            for kw in keywords:
                if kw in text:
                    taxonomy[domain].append(r['name'])
                    classified = True
                    break
            if classified:
                break
        if not classified:
            unclassified.append(r['name'])
    
    # Remove empty domains
    taxonomy = {d: g for d, g in taxonomy.items() if g}
    if unclassified:
        taxonomy['Uncategorized'] = unclassified
    
    return taxonomy

# ── Phase 4: COMPOSE — Build the instruction corpus ──
def compose_instruction_corpus(records):
    """nn.Linear(COMPOSE, extract) → instruction patterns"""
    verb_patterns = Counter()
    instruction_keywords = Counter()
    
    for r in records:
        text = r['instructions_preview'].lower()
        # Count action-verb-like patterns in instructions
        for verb in ['discover', 'inspect', 'create', 'mutate', 'destroy', 
                     'navigate', 'compose', 'observe', 'orchestrate', 'classify',
                     'analyze', 'generate', 'build', 'map', 'transform', 'simulate']:
            if verb in text:
                verb_patterns[verb.upper()] += 1
        
        # Extract key instruction patterns
        for kw in ['step', 'first', 'then', 'next', 'finally', 'always', 'never',
                    'must', 'should', 'use', 'apply', 'follow', 'ensure']:
            if kw in text:
                instruction_keywords[kw] += 1
    
    return {
        'verb_patterns': dict(verb_patterns.most_common()),
        'instruction_keywords': dict(instruction_keywords.most_common()),
        'total_instruction_chars': sum(r['instructions_len'] for r in records),
        'gizmos_with_instructions': sum(1 for r in records if r['instructions_len'] > 0),
        'gizmos_without_instructions': sum(1 for r in records if r['instructions_len'] == 0),
    }

# ── Phase 5: NAVIGATE — Traverse taxonomy hierarchy ──
def navigate_taxonomy(taxonomy, records):
    """nn.Linear(NAVIGATE, traverse) → hierarchy graph"""
    graph = {
        'root': 'GizmoSkillm',
        'domains': {},
        'edges': []
    }
    
    for domain, gizmo_names in taxonomy.items():
        domain_node = {
            'name': domain,
            'count': len(gizmo_names),
            'gizmos': gizmo_names,
        }
        graph['domains'][domain] = domain_node
        graph['edges'].append(('GizmoSkillm', domain))
        for g in gizmo_names:
            graph['edges'].append((domain, g))
    
    return graph

# ── Phase 6: OBSERVE — Cross-domain patterns ──
def observe_patterns(records, taxonomy):
    """nn.BatchNorm(OBSERVE) → pattern matrix"""
    # Tool usage across all gizmos
    tool_usage = Counter()
    for r in records:
        for t in r['tools']:
            if t:
                tool_usage[t] += 1
    
    # Instruction length distribution by domain
    domain_stats = {}
    name_to_record = {r['name']: r for r in records}
    for domain, names in taxonomy.items():
        lengths = [name_to_record[n]['instructions_len'] for n in names if n in name_to_record]
        if lengths:
            domain_stats[domain] = {
                'count': len(lengths),
                'avg_instructions': sum(lengths) // max(len(lengths), 1),
                'max_instructions': max(lengths),
                'total_instructions': sum(lengths),
            }
    
    return {
        'tool_usage': dict(tool_usage.most_common()),
        'domain_stats': domain_stats,
        'total_gizmos': len(records),
        'total_domains': len(taxonomy),
    }

# ── Phase 7: ORCHESTRATE — Full lifecycle plan ──
def orchestrate_lifecycle(discovery, records, taxonomy, corpus, graph, patterns):
    """nn.Linear(ORCHESTRATE, plan) → orchestration plan"""
    return {
        'lifecycle_stages': [
            {'stage': 'Bootstrap', 'verb': 'DISCOVER', 'description': 'Load bootstrap-gizmos.json, scan gizmos/ directory'},
            {'stage': 'Extract', 'verb': 'INSPECT', 'description': 'Parse resource.gizmo structure from each entry'},
            {'stage': 'Classify', 'verb': 'CLASSIFY', 'description': 'Apply domain taxonomy rules to categorize 87 gizmos into domains'},
            {'stage': 'Compose', 'verb': 'COMPOSE', 'description': 'Extract instruction patterns, verb distributions, knowledge file mappings'},
            {'stage': 'Navigate', 'verb': 'NAVIGATE', 'description': 'Build and traverse the domain → gizmo → instruction hierarchy'},
            {'stage': 'Observe', 'verb': 'OBSERVE', 'description': 'Detect cross-domain patterns, shared files, tool overlap'},
            {'stage': 'Orchestrate', 'verb': 'ORCHESTRATE', 'description': 'Generate deployment plan, evolution strategy, CI/CD pipeline'},
        ],
        'semiring_composition': {
            'pipeline': 'DISCOVER ⊗ INSPECT ⊗ CLASSIFY ⊗ COMPOSE ⊗ NAVIGATE ⊗ OBSERVE ⊗ ORCHESTRATE',
            'choices': [
                'CLASSIFY ⊕ (manual tagging)',
                'COMPOSE ⊕ (template extraction)',
                'ORCHESTRATE ⊕ (manual deployment)',
            ]
        }
    }

# ══════════════════════════════════════════════════════════════
# MAIN: Execute the full pipeline
# ══════════════════════════════════════════════════════════════
def main():
    repo_path = '/home/ubuntu/gizmos'
    
    print("=" * 72)
    print("GizmoSkillm Compiler: F(nn.Network) → skillm.AST")
    print("( ( ( * ) , ** ) , *** ) <=> ( /function-creator [ /nn → skillm ] )")
    print("=" * 72)
    
    # Execute pipeline
    print("\n[1/7] DISCOVER — Scanning repository...")
    discovery = discover_gizmos(repo_path)
    print(f"  Found {discovery['bootstrap_count']} gizmos in bootstrap, {discovery['individual_count']} individual files")
    
    print("\n[2/7] INSPECT — Parsing gizmo structures...")
    records = inspect_gizmos(discovery)
    print(f"  Parsed {len(records)} gizmo records")
    
    print("\n[3/7] CLASSIFY — Building domain taxonomy...")
    taxonomy = classify_gizmos(records)
    for domain, gizmos in sorted(taxonomy.items(), key=lambda x: -len(x[1])):
        print(f"  {domain:25s}: {len(gizmos):3d} gizmos")
    
    print("\n[4/7] COMPOSE — Extracting instruction corpus...")
    corpus = compose_instruction_corpus(records)
    print(f"  Total instruction chars: {corpus['total_instruction_chars']}")
    print(f"  Gizmos with instructions: {corpus['gizmos_with_instructions']}")
    print(f"  Verb patterns found: {corpus['verb_patterns']}")
    
    print("\n[5/7] NAVIGATE — Building taxonomy graph...")
    graph = navigate_taxonomy(taxonomy, records)
    print(f"  Root: {graph['root']}")
    print(f"  Domains: {len(graph['domains'])}")
    print(f"  Edges: {len(graph['edges'])}")
    
    print("\n[6/7] OBSERVE — Detecting cross-domain patterns...")
    patterns = observe_patterns(records, taxonomy)
    print(f"  Tool usage: {patterns['tool_usage']}")
    for domain, stats in sorted(patterns['domain_stats'].items(), key=lambda x: -x[1]['total_instructions']):
        print(f"  {domain:25s}: avg={stats['avg_instructions']:5d} max={stats['max_instructions']:5d} total={stats['total_instructions']:6d}")
    
    print("\n[7/7] ORCHESTRATE — Generating lifecycle plan...")
    lifecycle = orchestrate_lifecycle(discovery, records, taxonomy, corpus, graph, patterns)
    print(f"  Pipeline: {lifecycle['semiring_composition']['pipeline']}")
    for stage in lifecycle['lifecycle_stages']:
        print(f"  [{stage['verb']:12s}] {stage['stage']:15s} — {stage['description']}")
    
    # ── Build the final AST ──
    ast = {
        "version": "2.0.0",
        "goal": "GizmoSkillm: Procedural Language Model for ReZorg/gizmos (87 AI agent architectures)",
        "context": {
            "repository": "github.com/ReZorg/gizmos",
            "connectors": ["github", "notion", "neon"],
            "variables": {
                "repo_path": "/home/ubuntu/gizmos",
                "total_gizmos": 87,
                "total_domains": len(taxonomy),
                "total_instruction_chars": corpus['total_instruction_chars'],
            },
            "nn_architecture": {
                "type": "Sequential",
                "module_count": 7,
                "criterion": "ClassNLLCriterion",
                "outcome_type": "domain_classification"
            }
        },
        "root": {
            "type": "pipeline",
            "steps": [
                {
                    "type": "action",
                    "verb": "DISCOVER",
                    "tool": "github:clone_and_scan",
                    "params": {"repo": "ReZorg/gizmos", "pattern": "**/*.json"},
                    "description": f"Scan repository: {discovery['bootstrap_count']} gizmos in bootstrap, {discovery['individual_count']} individual files",
                    "nn_origin": "nn.Linear(DISCOVER, scan)"
                },
                {
                    "type": "action",
                    "verb": "INSPECT",
                    "tool": "json:parse_gizmo_structure",
                    "params": {"encoding": "utf-8-sig", "schema": "resource.gizmo"},
                    "description": f"Parse {len(records)} gizmo records: id, display.name, instructions, tools, files",
                    "nn_origin": "nn.Linear(INSPECT, parse)"
                },
                {
                    "type": "action",
                    "verb": "CLASSIFY",
                    "tool": "skillm:domain_taxonomy",
                    "params": {"domains": list(taxonomy.keys()), "method": "keyword_analysis"},
                    "description": f"Classify into {len(taxonomy)} domains via keyword analysis",
                    "nn_origin": "nn.Linear(CLASSIFY, categorize)",
                    "output": {domain: len(gizmos) for domain, gizmos in taxonomy.items()}
                },
                {
                    "type": "action",
                    "verb": "COMPOSE",
                    "tool": "skillm:instruction_corpus",
                    "params": {"extract": ["verb_patterns", "instruction_keywords", "knowledge_files"]},
                    "description": f"Extract instruction corpus: {corpus['total_instruction_chars']} chars, {corpus['gizmos_with_instructions']} active gizmos",
                    "nn_origin": "nn.Linear(COMPOSE, extract)"
                },
                {
                    "type": "action",
                    "verb": "NAVIGATE",
                    "tool": "skillm:taxonomy_graph",
                    "params": {"root": "GizmoSkillm", "depth": 3},
                    "description": f"Traverse hierarchy: {len(graph['edges'])} edges across {len(graph['domains'])} domains",
                    "nn_origin": "nn.Linear(NAVIGATE, traverse)"
                },
                {
                    "type": "action",
                    "verb": "OBSERVE",
                    "tool": "skillm:pattern_detector",
                    "params": {"metrics": ["tool_usage", "domain_stats", "cross_references"]},
                    "description": f"Detect cross-domain patterns across {patterns['total_gizmos']} gizmos",
                    "nn_origin": "nn.BatchNorm(OBSERVE)"
                },
                {
                    "type": "action",
                    "verb": "ORCHESTRATE",
                    "tool": "skillm:lifecycle_orchestrator",
                    "params": {"stages": 7, "composition": "pipeline"},
                    "description": "Orchestrate full gizmo lifecycle: bootstrap → extract → classify → compose → navigate → observe → deploy",
                    "nn_origin": "nn.Linear(ORCHESTRATE, plan)"
                }
            ],
            "nn_origin": "nn.Sequential(7 modules → 7 actions)"
        },
        "tuple_construction": {
            "equation": "( ( ( * ) , ** ) , *** )",
            "star": "nn.Module — 10 action verbs (DISCOVER, INSPECT, CLASSIFY, COMPOSE, NAVIGATE, OBSERVE, ORCHESTRATE, CREATE, MUTATE, DESTROY)",
            "star_star": "gizmo_skillm_compiler.py — the function-creator functor F: nn → GizmoSkillm",
            "star_star_star": "This AST — the compiled GizmoSkillm procedural language model for 87 AI agent architectures"
        },
        "semiring_composition": {
            "pipeline_⊗": "DISCOVER ⊗ INSPECT ⊗ CLASSIFY ⊗ COMPOSE ⊗ NAVIGATE ⊗ OBSERVE ⊗ ORCHESTRATE",
            "choices_⊕": [
                "CLASSIFY ⊕ manual_tagging",
                "COMPOSE ⊕ template_extraction",
                "ORCHESTRATE ⊕ manual_deployment"
            ],
            "zero_0": "∅ — failed parse / missing gizmo",
            "identity_1": "ε — no-op / passthrough"
        },
        "domain_taxonomy": taxonomy,
        "corpus_statistics": corpus,
        "pattern_matrix": patterns,
        "lifecycle": lifecycle
    }
    
    # Write the AST
    ast_path = '/home/ubuntu/gizmo_skillm_ast.json'
    with open(ast_path, 'w') as f:
        json.dump(ast, f, indent=2, default=str)
    print(f"\n{'=' * 72}")
    print(f"AST written to: {ast_path}")
    print(f"{'=' * 72}")
    
    return ast

if __name__ == '__main__':
    main()
