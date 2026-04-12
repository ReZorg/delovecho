#!/usr/bin/env python3
"""
Extract all 253 patterns from markdown/uia/*.md files with their relationships.
"""

import os
import re
import json
from pathlib import Path

def extract_pattern_info(filepath):
    """Extract pattern ID, name, template, and relationships from a markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract pattern ID and name from title
    title_match = re.search(r'^#\s+(\d+)\s+-\s+(.*)$', content, re.MULTILINE)
    if not title_match:
        return None
    
    pattern_id = title_match.group(1)
    name = title_match.group(2).strip()
    
    # Extract template section
    template_match = re.search(r'^##\s+Template\s*\n\n(.*?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    template = template_match.group(1).strip() if template_match else ""
    
    # Extract broader patterns
    broader_patterns = []
    broader_match = re.search(r'^##\s+Broader Patterns\s*\n\n(.*?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    if broader_match:
        broader_text = broader_match.group(1)
        # Extract pattern IDs from links like [Pattern Name](12610020)
        pattern_links = re.findall(r'\[([^\]]+)\]\((\d+)\)', broader_text)
        broader_patterns = [pid for _, pid in pattern_links]
    
    # Extract narrower patterns
    narrower_patterns = []
    narrower_match = re.search(r'^##\s+Narrower Patterns\s*\n\n(.*?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    if narrower_match:
        narrower_text = narrower_match.group(1)
        # Extract pattern IDs from links like [Pattern Name](12610020)
        pattern_links = re.findall(r'\[([^\]]+)\]\((\d+)\)', narrower_text)
        narrower_patterns = [pid for _, pid in pattern_links]
    
    return {
        'pattern_id': pattern_id,
        'name': name,
        'template': template,
        'broader_patterns': broader_patterns,
        'narrower_patterns': narrower_patterns
    }

def main():
    """Extract all patterns from markdown/uia/*.md files."""
    uia_dir = Path('markdown/uia')
    
    # Get all markdown files
    pattern_files = sorted(uia_dir.glob('*.md'))
    
    patterns = []
    for filepath in pattern_files:
        info = extract_pattern_info(filepath)
        if info:
            patterns.append(info)
    
    print(f"Extracted {len(patterns)} patterns")
    
    # Print patterns without names (incomplete)
    incomplete = [p for p in patterns if not p['name']]
    if incomplete:
        print(f"\nFound {len(incomplete)} patterns without names:")
        for p in incomplete:
            print(f"  - {p['pattern_id']}")
    
    # Print patterns missing relationships
    missing_broader = [p for p in patterns if not p['broader_patterns'] and p['pattern_id'] != '12610010']
    missing_narrower = [p for p in patterns if not p['narrower_patterns']]
    
    print(f"\nPatterns missing broader patterns: {len(missing_broader)}")
    for p in missing_broader[:10]:
        print(f"  - {p['pattern_id']}: {p['name']}")
    
    print(f"\nPatterns missing narrower patterns: {len(missing_narrower)}")
    for p in missing_narrower[:10]:
        print(f"  - {p['pattern_id']}: {p['name']}")
    
    # Save to JSON
    output = {
        'meta': {
            'title': 'UIA Archetypal Patterns - Complete',
            'description': 'All 253 archetypal patterns with relationships',
            'total_patterns': len(patterns),
            'source_directory': 'markdown/uia'
        },
        'patterns': patterns
    }
    
    with open('patterns_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(patterns)} patterns to patterns_extracted.json")

if __name__ == '__main__':
    main()
