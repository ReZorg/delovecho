#!/usr/bin/env python3
"""Deep analysis of gizmos for skillm domain classification."""
import json, os, glob, re
from collections import Counter

with open('/home/ubuntu/gizmos/bootstrap-gizmos.json') as f:
    data = json.load(f)

gizmos_list = data.get('gizmos', [])
print(f"Total gizmos in bootstrap: {len(gizmos_list)}")

# Extract structured info from each gizmo
gizmo_records = []
for item in gizmos_list:
    resource = item.get('resource', {})
    gizmo = resource.get('gizmo', {})
    tools = item.get('tools', [])
    files = item.get('files', [])
    
    record = {
        'id': gizmo.get('id', ''),
        'short_url': gizmo.get('short_url', ''),
        'display_name': gizmo.get('display', {}).get('name', gizmo.get('name', 'unknown')),
        'description': gizmo.get('display', {}).get('description', '')[:200],
        'instructions_len': len(gizmo.get('instructions', '') or ''),
        'tools': [t.get('type', '') for t in tools],
        'num_files': len(files),
        'categories': gizmo.get('tags', []),
    }
    gizmo_records.append(record)

# Print summary table
print(f"\n{'#':>3} {'Name':40s} {'Instr':>6} {'Tools':20s} {'Files':>5}")
print("-" * 80)
for i, r in enumerate(gizmo_records):
    tools_str = ','.join(r['tools'])[:20]
    print(f"{i+1:>3} {r['display_name'][:40]:40s} {r['instructions_len']:>6} {tools_str:20s} {r['num_files']:>5}")

# Domain classification by keyword analysis
print("\n=== DOMAIN CLASSIFICATION ===")
domain_keywords = {
    'Skincare/RegimA': ['skincare', 'regima', 'skin twin', 'formulation', 'zone concept'],
    'Cognitive/AGI': ['cogprime', 'opencog', 'agi', 'cognitive', 'hypergraph', 'atomspace', 'llml'],
    'Governance/Org': ['holacracy', 'holaspirit', 'governance', 'constitution', 'co-operative'],
    'Dev Tools': ['api', 'postman', 'json', 'converter', 'extractor', 'cursor', 'data integration'],
    'Math/Science': ['math', 'numerical', 'gromacs', 'molecular', 'docking', 'wolfram', 'symbolic'],
    'Task Management': ['taskmaster', 'task', 'project'],
    'Creative/Wizard': ['wizard', 'unicorn', 'hyper', 'grimoire', 'alchemy'],
    'ML/Architecture': ['machine learning', 'neural', 'model', 'architect', 'dynamic'],
    'Self-Image/Meta': ['autognosis', 'self-image', 'auto-gnosis', 'agsi', 'meaning crisis'],
}

domain_counts = Counter()
for r in gizmo_records:
    text = (r['display_name'] + ' ' + r['description']).lower()
    for domain, keywords in domain_keywords.items():
        for kw in keywords:
            if kw in text:
                domain_counts[domain] += 1
                break

for domain, count in domain_counts.most_common():
    print(f"  {domain:25s}: {count} gizmos")

# Tool usage stats
print("\n=== TOOL USAGE ===")
tool_counter = Counter()
for r in gizmo_records:
    for t in r['tools']:
        tool_counter[t] += 1
for tool, count in tool_counter.most_common():
    print(f"  {tool:20s}: {count}")

# Instruction length stats
lengths = [r['instructions_len'] for r in gizmo_records]
print(f"\n=== INSTRUCTION STATS ===")
print(f"  Total gizmos: {len(lengths)}")
print(f"  Min instructions: {min(lengths)} chars")
print(f"  Max instructions: {max(lengths)} chars")
print(f"  Avg instructions: {sum(lengths)//len(lengths)} chars")
print(f"  Total instruction chars: {sum(lengths)}")

# File reference stats
file_counts = [r['num_files'] for r in gizmo_records]
print(f"\n=== FILE REFERENCE STATS ===")
print(f"  Gizmos with files: {sum(1 for f in file_counts if f > 0)}")
print(f"  Total file refs: {sum(file_counts)}")
print(f"  Max files per gizmo: {max(file_counts)}")
