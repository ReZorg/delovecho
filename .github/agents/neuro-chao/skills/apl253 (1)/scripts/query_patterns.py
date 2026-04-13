#!/usr/bin/env python3
"""
APL253 Pattern Query Tool
Usage: python query_patterns.py <command> [args]

Commands:
  get <id>              Get pattern by ID (1-253)
  search <term>         Search patterns by name/content
  broader <id>          Get broader (parent) patterns
  narrower <id>         Get narrower (child) patterns
  roots                 List root patterns (no broader)
  hubs                  List high-connectivity hub patterns
  path <from> <to>      Find path between patterns
"""

import sys
import os
import re
from pathlib import Path
from collections import deque

BASE = Path("/home/ubuntu/skills/apl253/patterns/apl0/dim0")

def find_pattern_file(pattern_id: int) -> Path:
    """Find pattern file by ID"""
    for cat in ["cat1", "cat2", "cat3"]:
        cat_path = BASE / cat
        if not cat_path.exists():
            continue
        for seq_dir in cat_path.iterdir():
            if not seq_dir.is_dir():
                continue
            pattern_file = seq_dir / f"apl{pattern_id:03d}.md"
            if pattern_file.exists():
                return pattern_file
    return None

def get_pattern(pattern_id: int) -> dict:
    """Get pattern content"""
    path = find_pattern_file(pattern_id)
    if not path:
        return None
    
    content = path.read_text()
    
    # Extract name from description
    name_match = re.search(r'description:\s*["\']?(\d+\s*-\s*)?(.+?)["\']?\s*$', content, re.MULTILINE)
    name = name_match.group(2).strip() if name_match else f"Pattern {pattern_id}"
    
    return {"id": pattern_id, "name": name, "content": content, "path": str(path)}

def get_refs(pattern_id: int, ref_type: str) -> list:
    """Get broader or narrower references"""
    path = find_pattern_file(pattern_id)
    if not path:
        return []
    
    ref_file = path.parent / f"apl{pattern_id:03d}" / f"{ref_type}.md"
    if not ref_file.exists():
        return []
    
    content = ref_file.read_text()
    matches = re.findall(r'-\s*apl(\d+)', content, re.IGNORECASE)
    return [int(m) for m in matches]

def search_patterns(term: str) -> list:
    """Search patterns by term"""
    results = []
    term_lower = term.lower()
    
    for cat in ["cat1", "cat2", "cat3"]:
        cat_path = BASE / cat
        if not cat_path.exists():
            continue
        for seq_dir in cat_path.iterdir():
            if not seq_dir.is_dir():
                continue
            for pattern_file in seq_dir.glob("apl*.md"):
                if pattern_file.is_dir():
                    continue
                content = pattern_file.read_text()
                if term_lower in content.lower():
                    match = re.search(r'apl(\d+)', pattern_file.name)
                    if match:
                        pid = int(match.group(1))
                        pattern = get_pattern(pid)
                        if pattern:
                            results.append(pattern)
    
    return results

def find_path(start: int, end: int) -> list:
    """Find shortest path between patterns (via narrower)"""
    if start == end:
        return [start]
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current, path = queue.popleft()
        for child in get_refs(current, "narrower"):
            if child == end:
                return path + [child]
            if child not in visited:
                visited.add(child)
                queue.append((child, path + [child]))
    
    return []

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "get" and len(sys.argv) > 2:
        pid = int(sys.argv[2])
        pattern = get_pattern(pid)
        if pattern:
            print(f"[{pattern['id']}] {pattern['name']}")
            print(f"Path: {pattern['path']}")
            print("-" * 50)
            print(pattern['content'][:1000])
        else:
            print(f"Pattern {pid} not found")
    
    elif cmd == "search" and len(sys.argv) > 2:
        term = " ".join(sys.argv[2:])
        results = search_patterns(term)
        print(f"Found {len(results)} patterns matching '{term}':")
        for p in results[:20]:
            print(f"  [{p['id']:3d}] {p['name']}")
    
    elif cmd == "broader" and len(sys.argv) > 2:
        pid = int(sys.argv[2])
        refs = get_refs(pid, "broader")
        print(f"Broader patterns for {pid}:")
        for ref in refs:
            p = get_pattern(ref)
            print(f"  [{ref:3d}] {p['name'] if p else 'Unknown'}")
    
    elif cmd == "narrower" and len(sys.argv) > 2:
        pid = int(sys.argv[2])
        refs = get_refs(pid, "narrower")
        print(f"Narrower patterns for {pid}:")
        for ref in refs:
            p = get_pattern(ref)
            print(f"  [{ref:3d}] {p['name'] if p else 'Unknown'}")
    
    elif cmd == "roots":
        print("Root patterns (no broader context):")
        for pid in [1, 18, 24, 95, 253]:
            p = get_pattern(pid)
            if p:
                print(f"  [{pid:3d}] {p['name']}")
    
    elif cmd == "hubs":
        print("Hub patterns (highest connectivity):")
        hubs = [(30, 24), (249, 24), (142, 23), (107, 21), (100, 20)]
        for pid, degree in hubs:
            p = get_pattern(pid)
            if p:
                print(f"  [{pid:3d}] {p['name']} (degree: {degree})")
    
    elif cmd == "path" and len(sys.argv) > 3:
        start = int(sys.argv[2])
        end = int(sys.argv[3])
        path = find_path(start, end)
        if path:
            print(f"Path from {start} to {end}:")
            print(" → ".join(str(p) for p in path))
        else:
            print(f"No path found from {start} to {end}")
    
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
