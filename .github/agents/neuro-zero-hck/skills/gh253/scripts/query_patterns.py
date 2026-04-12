#!/usr/bin/env python3
"""
Query and navigate gh253 patterns.
Usage:
    python3 query_patterns.py get <pattern_num>
    python3 query_patterns.py search <keyword>
    python3 query_patterns.py broader <pattern_num>
    python3 query_patterns.py narrower <pattern_num>
    python3 query_patterns.py path <from_num> <to_num>
    python3 query_patterns.py list [category]
"""

import json
import os
import re
import sys
from pathlib import Path

GH_BASE = Path(__file__).parent.parent / "patterns"
MAPPINGS_FILE = Path(__file__).parent.parent / "gh253_domain_mappings.json"

# Load mappings
with open(MAPPINGS_FILE) as f:
    MAPPINGS = json.load(f)

PATTERN_NAME_MAPPINGS = MAPPINGS["pattern_name_transformations"]

def get_gh_pattern_name(pattern_num: int) -> str:
    """Get the GitHub domain pattern name."""
    key = str(pattern_num)
    if key in PATTERN_NAME_MAPPINGS:
        return PATTERN_NAME_MAPPINGS[key]["gh"]
    return f"PATTERN {pattern_num}"

def get_category_for_pattern(pattern_num: int) -> str:
    """Determine which category a pattern belongs to."""
    if 1 <= pattern_num <= 94:
        return "cat1-enterprises"
    elif 95 <= pattern_num <= 204:
        return "cat2-organisations"
    else:
        return "cat3-repositories"

def find_pattern_file(pattern_num: int) -> Path:
    """Find the gh253 pattern file for a given pattern number."""
    category = get_category_for_pattern(pattern_num)
    category_dir = GH_BASE / category
    
    for f in category_dir.glob(f"gh{pattern_num:03d}-*.md"):
        return f
    return None

def cmd_get(pattern_num: int):
    """Get and display a pattern."""
    pattern_file = find_pattern_file(pattern_num)
    if not pattern_file:
        print(f"Pattern {pattern_num} not found")
        return
    
    gh_name = get_gh_pattern_name(pattern_num)
    print(f"[{pattern_num}] {gh_name}")
    print(f"Path: {pattern_file}")
    print("-" * 50)
    
    with open(pattern_file) as f:
        print(f.read())

def cmd_search(keyword: str):
    """Search for patterns matching a keyword."""
    keyword_lower = keyword.lower()
    matches = []
    
    for category_dir in GH_BASE.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith('.'):
            continue
        
        for pattern_file in category_dir.glob("gh*.md"):
            with open(pattern_file) as f:
                content = f.read().lower()
            
            if keyword_lower in content:
                # Extract pattern number
                match = re.search(r'gh(\d{3})', pattern_file.name)
                if match:
                    pattern_num = int(match.group(1))
                    matches.append((pattern_num, get_gh_pattern_name(pattern_num)))
    
    print(f"Found {len(matches)} patterns matching '{keyword}':")
    for num, name in sorted(matches):
        print(f"  [{num:3d}] {name}")

def cmd_broader(pattern_num: int):
    """Get broader (parent) patterns."""
    category = get_category_for_pattern(pattern_num)
    broader_file = GH_BASE / category / f"gh{pattern_num:03d}" / "broader.md"
    
    if not broader_file.exists():
        print(f"No broader patterns found for pattern {pattern_num}")
        return
    
    gh_name = get_gh_pattern_name(pattern_num)
    print(f"Broader patterns for [{pattern_num}] {gh_name}:")
    print("-" * 50)
    
    with open(broader_file) as f:
        content = f.read()
    
    # Extract pattern references
    for match in re.finditer(r'gh(\d{3}): (.+)', content):
        num = int(match.group(1))
        name = match.group(2)
        print(f"  [{num:3d}] {name}")

def cmd_narrower(pattern_num: int):
    """Get narrower (child) patterns."""
    category = get_category_for_pattern(pattern_num)
    narrower_file = GH_BASE / category / f"gh{pattern_num:03d}" / "narrower.md"
    
    if not narrower_file.exists():
        print(f"No narrower patterns found for pattern {pattern_num}")
        return
    
    gh_name = get_gh_pattern_name(pattern_num)
    print(f"Narrower patterns for [{pattern_num}] {gh_name}:")
    print("-" * 50)
    
    with open(narrower_file) as f:
        content = f.read()
    
    # Extract pattern references
    for match in re.finditer(r'gh(\d{3}): (.+)', content):
        num = int(match.group(1))
        name = match.group(2)
        print(f"  [{num:3d}] {name}")

def cmd_list(category: str = None):
    """List all patterns, optionally filtered by category."""
    categories = ["cat1-enterprises", "cat2-organisations", "cat3-repositories"]
    
    if category:
        if category in ["1", "enterprises", "cat1"]:
            categories = ["cat1-enterprises"]
        elif category in ["2", "organisations", "cat2"]:
            categories = ["cat2-organisations"]
        elif category in ["3", "repositories", "cat3"]:
            categories = ["cat3-repositories"]
    
    for cat in categories:
        cat_dir = GH_BASE / cat
        if not cat_dir.exists():
            continue
        
        print(f"\n{cat.upper()}:")
        print("-" * 50)
        
        patterns = []
        for pattern_file in cat_dir.glob("gh*.md"):
            match = re.search(r'gh(\d{3})', pattern_file.name)
            if match:
                num = int(match.group(1))
                patterns.append((num, get_gh_pattern_name(num)))
        
        for num, name in sorted(patterns):
            print(f"  [{num:3d}] {name}")

def cmd_path(from_num: int, to_num: int):
    """Find a path between two patterns (simplified BFS)."""
    # Build adjacency graph from narrower relationships
    graph = {}
    
    for category_dir in GH_BASE.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith('.'):
            continue
        
        for rel_dir in category_dir.iterdir():
            if not rel_dir.is_dir():
                continue
            
            match = re.search(r'gh(\d{3})', rel_dir.name)
            if not match:
                continue
            
            pattern_num = int(match.group(1))
            narrower_file = rel_dir / "narrower.md"
            
            if narrower_file.exists():
                with open(narrower_file) as f:
                    content = f.read()
                
                children = [int(m.group(1)) for m in re.finditer(r'gh(\d{3})', content)]
                graph[pattern_num] = children
    
    # BFS to find path
    from collections import deque
    
    queue = deque([(from_num, [from_num])])
    visited = {from_num}
    
    while queue:
        current, path = queue.popleft()
        
        if current == to_num:
            print(f"Path from {from_num} to {to_num} ({len(path)-1} steps):")
            for i, num in enumerate(path):
                indent = "  " * i
                print(f"{indent}[{num}] {get_gh_pattern_name(num)}")
            return
        
        for child in graph.get(current, []):
            if child not in visited:
                visited.add(child)
                queue.append((child, path + [child]))
    
    print(f"No path found from {from_num} to {to_num}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "get" and len(sys.argv) >= 3:
        cmd_get(int(sys.argv[2]))
    elif cmd == "search" and len(sys.argv) >= 3:
        cmd_search(sys.argv[2])
    elif cmd == "broader" and len(sys.argv) >= 3:
        cmd_broader(int(sys.argv[2]))
    elif cmd == "narrower" and len(sys.argv) >= 3:
        cmd_narrower(int(sys.argv[2]))
    elif cmd == "list":
        category = sys.argv[2] if len(sys.argv) >= 3 else None
        cmd_list(category)
    elif cmd == "path" and len(sys.argv) >= 4:
        cmd_path(int(sys.argv[2]), int(sys.argv[3]))
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
