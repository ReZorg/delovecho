#!/usr/bin/env python3
"""
Build broader/narrower relationship files for gh253 patterns.
Reads from APL253 reference and creates gh253 relationship structure.
"""

import json
import os
import re
from pathlib import Path

# Load domain mappings
MAPPINGS_FILE = Path(__file__).parent.parent / "gh253_domain_mappings.json"
with open(MAPPINGS_FILE) as f:
    MAPPINGS = json.load(f)

PATTERN_NAME_MAPPINGS = MAPPINGS["pattern_name_transformations"]

APL_BASE = Path("/home/ubuntu/apl253-reference/APL-253/.github/agents/apl0/dim0")
GH_BASE = Path("/home/ubuntu/gh253/patterns")

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

def parse_relationship_file(filepath: Path) -> list:
    """Parse a broader or narrower file and extract pattern references."""
    if not filepath.exists():
        return []
    
    with open(filepath) as f:
        content = f.read()
    
    # Extract pattern numbers from apl### references
    pattern_nums = re.findall(r'apl(\d{3})', content)
    return [int(n) for n in pattern_nums]

def create_relationship_file(pattern_num: int, rel_type: str, related_patterns: list) -> str:
    """Create content for a broader or narrower relationship file."""
    gh_name = get_gh_pattern_name(pattern_num)
    
    content = f"""---
name: {rel_type}
description: {rel_type.title()} Patterns for gh{pattern_num:03d}
---

# {rel_type.upper()} Instructions

"""
    
    if rel_type == "broader":
        content += "These patterns provide context and are typically applied before this pattern:\n\n"
    else:
        content += "These patterns provide detail and are typically applied after this pattern:\n\n"
    
    for rel_num in related_patterns:
        rel_name = get_gh_pattern_name(rel_num)
        content += f"- gh{rel_num:03d}: {rel_name}\n"
    
    return content

def build_all_relationships():
    """Build relationship files for all patterns."""
    # Find all APL pattern directories with broader/narrower files
    apl_pattern_dirs = list(APL_BASE.glob("**/apl*/"))
    
    # Filter to only pattern directories (not seq directories)
    apl_pattern_dirs = [d for d in apl_pattern_dirs if re.match(r'apl\d{3}$', d.name)]
    
    print(f"Found {len(apl_pattern_dirs)} APL pattern directories with relationships")
    
    created = 0
    for apl_dir in apl_pattern_dirs:
        # Extract pattern number
        match = re.search(r'apl(\d{3})', apl_dir.name)
        if not match:
            continue
        
        pattern_num = int(match.group(1))
        gh_file = find_pattern_file(pattern_num)
        
        if not gh_file:
            print(f"  Warning: No gh253 file found for pattern {pattern_num}")
            continue
        
        # Create relationship directory
        rel_dir = gh_file.parent / f"gh{pattern_num:03d}"
        rel_dir.mkdir(exist_ok=True)
        
        # Process broader relationships
        broader_file = apl_dir / "broader.md"
        broader_patterns = parse_relationship_file(broader_file)
        if broader_patterns:
            content = create_relationship_file(pattern_num, "broader", broader_patterns)
            with open(rel_dir / "broader.md", 'w') as f:
                f.write(content)
            created += 1
        
        # Process narrower relationships
        narrower_file = apl_dir / "narrower.md"
        narrower_patterns = parse_relationship_file(narrower_file)
        if narrower_patterns:
            content = create_relationship_file(pattern_num, "narrower", narrower_patterns)
            with open(rel_dir / "narrower.md", 'w') as f:
                f.write(content)
            created += 1
    
    print(f"Created {created} relationship files")

if __name__ == "__main__":
    build_all_relationships()
