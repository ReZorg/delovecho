#!/usr/bin/env python3
"""
Generate procedural programs (action sequences) for the GizmoSkillm domain.
Each program is a concrete executable workflow composed from the 10-verb vocabulary.
"""
import json

programs = []

# ── Program 1: Gizmo Inventory & Audit ──
programs.append({
    "id": "P1",
    "name": "gizmo_inventory_audit",
    "goal": "Perform a complete inventory and audit of all gizmos in the repository",
    "semiring": "⊗ Pipeline (Sequential)",
    "nn_architecture": "nn.Sequential(DISCOVER, INSPECT, CLASSIFY, OBSERVE)",
    "steps": [
        {"verb": "DISCOVER", "action": "Scan bootstrap-gizmos.json for all gizmo entries", "tool": "json:load", "input": "bootstrap-gizmos.json", "output": "gizmo_list[87]"},
        {"verb": "INSPECT", "action": "Parse resource.gizmo.display.name, instructions, tools for each entry", "tool": "json:parse", "input": "gizmo_list[87]", "output": "gizmo_records[87]"},
        {"verb": "CLASSIFY", "action": "Apply keyword-based domain taxonomy (11 domains)", "tool": "skillm:classify", "input": "gizmo_records[87]", "output": "domain_taxonomy"},
        {"verb": "OBSERVE", "action": "Compute statistics: instruction lengths, tool usage, file references", "tool": "skillm:stats", "input": "domain_taxonomy", "output": "audit_report"},
    ]
})

# ── Program 2: Domain-Specific Gizmo Extraction ──
programs.append({
    "id": "P2",
    "name": "domain_gizmo_extraction",
    "goal": "Extract all gizmos belonging to a specific domain (e.g., Cognitive/AGI)",
    "semiring": "⊗ Pipeline with ⊕ Choice",
    "nn_architecture": "nn.Sequential(DISCOVER, CLASSIFY, nn.Concat(INSPECT ⊕ NAVIGATE))",
    "steps": [
        {"verb": "DISCOVER", "action": "Load bootstrap and identify all gizmo entries", "tool": "json:load", "input": "bootstrap-gizmos.json", "output": "all_gizmos"},
        {"verb": "CLASSIFY", "action": "Filter gizmos matching target domain keywords", "tool": "skillm:filter", "input": "all_gizmos + domain_query", "output": "domain_gizmos"},
        {"verb": "INSPECT", "action": "Deep-parse instructions and tool configs for filtered set", "tool": "json:deep_parse", "input": "domain_gizmos", "output": "detailed_records"},
        {"verb": "NAVIGATE", "action": "Traverse knowledge file references for domain gizmos", "tool": "fs:traverse", "input": "detailed_records.files", "output": "knowledge_graph"},
    ]
})

# ── Program 3: Gizmo Evolution (CRUD Lifecycle) ──
programs.append({
    "id": "P3",
    "name": "gizmo_crud_lifecycle",
    "goal": "Create, update, and manage gizmo definitions in the repository",
    "semiring": "⊗ Pipeline (Full CRUD)",
    "nn_architecture": "nn.Sequential(DISCOVER, CREATE, MUTATE, INSPECT, DESTROY)",
    "steps": [
        {"verb": "DISCOVER", "action": "Check existing gizmos to avoid duplicates", "tool": "json:search", "input": "gizmo_name", "output": "existing_check"},
        {"verb": "CREATE", "action": "Generate new gizmo JSON with id, display, instructions, tools", "tool": "json:create", "input": "gizmo_spec", "output": "new_gizmo.json"},
        {"verb": "MUTATE", "action": "Update bootstrap-gizmos.json with new entry", "tool": "json:append", "input": "new_gizmo.json", "output": "updated_bootstrap"},
        {"verb": "INSPECT", "action": "Validate the new gizmo structure against schema", "tool": "json:validate", "input": "updated_bootstrap", "output": "validation_result"},
        {"verb": "COMPOSE", "action": "Run extract_gizmos.py to regenerate individual files", "tool": "python:exec", "input": "extract_gizmos.py", "output": "gizmos/*.json"},
    ]
})

# ── Program 4: Cross-Domain Pattern Mining ──
programs.append({
    "id": "P4",
    "name": "cross_domain_pattern_mining",
    "goal": "Discover shared patterns across gizmo domains (knowledge files, instruction templates, tool configs)",
    "semiring": "⊗ Pipeline with nested ⊗",
    "nn_architecture": "nn.Sequential(DISCOVER, INSPECT, OBSERVE, COMPOSE, CLASSIFY)",
    "steps": [
        {"verb": "DISCOVER", "action": "Load all 87 gizmos and 352 unique knowledge file references", "tool": "json:load_all", "input": "bootstrap + gizmo_files_mapping.md", "output": "full_corpus"},
        {"verb": "INSPECT", "action": "Extract instruction text and knowledge file IDs per gizmo", "tool": "text:extract", "input": "full_corpus", "output": "instruction_matrix"},
        {"verb": "OBSERVE", "action": "Compute co-occurrence matrix: which gizmos share knowledge files", "tool": "matrix:cooccurrence", "input": "instruction_matrix", "output": "sharing_matrix"},
        {"verb": "COMPOSE", "action": "Identify instruction template patterns (e.g., SME panels, iterative refinement)", "tool": "text:pattern_match", "input": "instruction_matrix", "output": "template_patterns"},
        {"verb": "CLASSIFY", "action": "Cluster gizmos by shared patterns into meta-domains", "tool": "cluster:kmeans", "input": "sharing_matrix + template_patterns", "output": "meta_taxonomy"},
    ]
})

# ── Program 5: Gizmo Deployment Orchestration ──
programs.append({
    "id": "P5",
    "name": "gizmo_deployment_orchestration",
    "goal": "Orchestrate the deployment of gizmos to target environments (ChatGPT, API, Notion)",
    "semiring": "⊗ Pipeline with ⊕ Choice at deployment",
    "nn_architecture": "nn.Sequential(DISCOVER, INSPECT, COMPOSE, ORCHESTRATE, nn.Concat(CREATE_chatgpt ⊕ CREATE_api ⊕ CREATE_notion))",
    "steps": [
        {"verb": "DISCOVER", "action": "Select gizmos for deployment batch", "tool": "json:filter", "input": "deployment_manifest", "output": "deploy_batch"},
        {"verb": "INSPECT", "action": "Validate each gizmo has required fields for target platform", "tool": "json:validate", "input": "deploy_batch", "output": "validated_batch"},
        {"verb": "COMPOSE", "action": "Transform gizmo JSON to platform-specific format", "tool": "transform:platform", "input": "validated_batch + target_platform", "output": "platform_configs"},
        {"verb": "ORCHESTRATE", "action": "Execute deployment pipeline with rollback capability", "tool": "deploy:orchestrate", "input": "platform_configs", "output": "deployment_status"},
        {"verb": "OBSERVE", "action": "Monitor deployment health and collect metrics", "tool": "monitor:health", "input": "deployment_status", "output": "health_report"},
    ]
})

# ── Program 6: Gizmo Knowledge Graph Builder ──
programs.append({
    "id": "P6",
    "name": "gizmo_knowledge_graph",
    "goal": "Build a knowledge graph connecting gizmos, domains, knowledge files, tools, and instruction patterns",
    "semiring": "⊗ Pipeline (Graph Construction)",
    "nn_architecture": "nn.Sequential(DISCOVER, INSPECT, NAVIGATE, COMPOSE, CREATE)",
    "steps": [
        {"verb": "DISCOVER", "action": "Enumerate all entities: 87 gizmos, 11 domains, 352 knowledge files", "tool": "json:enumerate", "input": "bootstrap + mapping", "output": "entity_list"},
        {"verb": "INSPECT", "action": "Extract relationships: gizmo→domain, gizmo→files, gizmo→tools", "tool": "json:extract_relations", "input": "entity_list", "output": "relation_triples"},
        {"verb": "NAVIGATE", "action": "Traverse and resolve cross-references between gizmos", "tool": "graph:traverse", "input": "relation_triples", "output": "resolved_graph"},
        {"verb": "COMPOSE", "action": "Merge into unified knowledge graph with typed edges", "tool": "graph:compose", "input": "resolved_graph", "output": "knowledge_graph"},
        {"verb": "CREATE", "action": "Persist knowledge graph to Neon database", "tool": "neon:create_tables", "input": "knowledge_graph", "output": "db_schema"},
    ]
})

# ── Build the complete procedural program catalog ──
catalog = {
    "version": "1.0.0",
    "name": "GizmoSkillm Procedural Programs",
    "description": "6 executable action sequence programs for the ReZorg/gizmos domain",
    "core_equation": "( ( ( * ) , ** ) , *** ) <=> ( /function-creator [ /nn → skillm ] )",
    "vocabulary": ["DISCOVER", "INSPECT", "CREATE", "MUTATE", "DESTROY", "NAVIGATE", "COMPOSE", "OBSERVE", "ORCHESTRATE", "CLASSIFY"],
    "programs": programs,
    "composition_summary": {
        "total_programs": len(programs),
        "total_steps": sum(len(p['steps']) for p in programs),
        "verb_distribution": {},
        "pipeline_compositions": len(programs),
        "choice_compositions": sum(1 for p in programs if '⊕' in p['semiring']),
    }
}

# Count verb usage across all programs
from collections import Counter
verb_counts = Counter()
for p in programs:
    for s in p['steps']:
        verb_counts[s['verb']] += 1
catalog['composition_summary']['verb_distribution'] = dict(verb_counts.most_common())

# Write catalog
with open('/home/ubuntu/gizmo_procedural_programs.json', 'w') as f:
    json.dump(catalog, f, indent=2)

# Print summary
print("=" * 72)
print("GizmoSkillm Procedural Program Catalog")
print("=" * 72)
for p in programs:
    print(f"\n[{p['id']}] {p['name']}")
    print(f"  Goal: {p['goal']}")
    print(f"  Semiring: {p['semiring']}")
    print(f"  nn: {p['nn_architecture']}")
    for i, s in enumerate(p['steps']):
        print(f"  {i+1}. [{s['verb']:12s}] {s['action']}")

print(f"\n{'=' * 72}")
print(f"Total: {catalog['composition_summary']['total_programs']} programs, {catalog['composition_summary']['total_steps']} steps")
print(f"Verb distribution: {catalog['composition_summary']['verb_distribution']}")
print(f"Pipeline (⊗): {catalog['composition_summary']['pipeline_compositions']}")
print(f"Choice (⊕): {catalog['composition_summary']['choice_compositions']}")
print(f"Catalog written to: /home/ubuntu/gizmo_procedural_programs.json")
