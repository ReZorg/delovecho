#!/usr/bin/env python3
"""Analyze the ReZorg/gizmos repository structure for skillm synthesis."""
import json, os, glob

# 1. Analyze bootstrap-gizmos.json
with open('/home/ubuntu/gizmos/bootstrap-gizmos.json') as f:
    bootstrap = json.load(f)

print("=== BOOTSTRAP GIZMOS ===")
if isinstance(bootstrap, list):
    print(f"Type: list, Count: {len(bootstrap)}")
    if bootstrap:
        print(f"First item keys: {list(bootstrap[0].keys())[:20]}")
        # Sample first item
        item = bootstrap[0]
        for k, v in item.items():
            if isinstance(v, str):
                print(f"  {k}: {v[:100]}...")
            elif isinstance(v, dict):
                print(f"  {k}: dict with keys {list(v.keys())[:10]}")
            elif isinstance(v, list):
                print(f"  {k}: list with {len(v)} items")
            else:
                print(f"  {k}: {v}")
elif isinstance(bootstrap, dict):
    print(f"Type: dict, Keys: {list(bootstrap.keys())[:20]}")

# 2. Analyze individual gizmo JSON files
gizmo_files = sorted(glob.glob('/home/ubuntu/gizmos/gizmos/*.json'))
print(f"\n=== INDIVIDUAL GIZMO FILES: {len(gizmo_files)} ===")

# Sample one gizmo file
if gizmo_files:
    with open(gizmo_files[0], encoding='utf-8-sig') as f:
        sample = json.load(f)
    print(f"\nSample file: {os.path.basename(gizmo_files[0])}")
    if isinstance(sample, dict):
        for k, v in sample.items():
            if isinstance(v, str):
                print(f"  {k}: {v[:120]}...")
            elif isinstance(v, dict):
                print(f"  {k}: dict with keys {list(v.keys())[:10]}")
            elif isinstance(v, list):
                print(f"  {k}: list with {len(v)} items")
            else:
                print(f"  {k}: {v}")

# 3. Collect all gizmo names and domains
print("\n=== ALL GIZMO NAMES ===")
names = []
for gf in gizmo_files:
    with open(gf, encoding='utf-8-sig') as f:
        g = json.load(f)
    name = g.get('title', g.get('name', os.path.basename(gf)))
    names.append(name)
    print(f"  {os.path.basename(gf)[:50]:50s} -> {name[:60]}")

# 4. Analyze extract scripts
print("\n=== EXTRACT SCRIPTS ===")
for script in ['extract_gizmos.py', 'extract_gizmos.ps1', 'fixmeplz.ps1']:
    path = f'/home/ubuntu/gizmos/{script}'
    if os.path.exists(path):
        with open(path) as f:
            content = f.read()
        print(f"\n{script} ({len(content)} chars):")
        print(content[:500])

# 5. Analyze gizmo_files_mapping.md
mapping_path = '/home/ubuntu/gizmos/gizmo_files_mapping.md'
if os.path.exists(mapping_path):
    with open(mapping_path) as f:
        mapping = f.read()
    print(f"\n=== GIZMO FILES MAPPING ({len(mapping)} chars) ===")
    print(mapping[:1000])
