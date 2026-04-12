#!/usr/bin/env python3
"""
Analyze UIA patterns to understand which sections they contain
"""

import os
import re
import glob
from pathlib import Path
from collections import defaultdict, Counter

def analyze_pattern_sections(file_path):
    """Analyze what sections a UIA pattern contains"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title
        title_match = re.search(r'^# (\d+) - (.+)$', content, re.MULTILINE)
        if not title_match:
            return None
        
        pattern_id = title_match.group(1)
        pattern_name = title_match.group(2)
        
        # Find all section headers
        section_matches = re.findall(r'^## (.+)$', content, re.MULTILINE)
        sections = [s for s in section_matches if s not in ['Broader Patterns', 'Narrower Patterns']]
        
        return {
            'id': pattern_id,
            'name': pattern_name,
            'sections': sections,
            'has_template': 'Template' in sections
        }
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    """Analyze all UIA patterns"""
    uia_dir = Path("/home/runner/work/p235/p235/markdown/uia")
    uia_files = sorted(uia_dir.glob("*.md"))
    
    patterns = []
    section_stats = Counter()
    
    for file_path in uia_files:
        result = analyze_pattern_sections(file_path)
        if result:
            patterns.append(result)
            section_stats.update(result['sections'])
    
    print(f"Total patterns analyzed: {len(patterns)}")
    print(f"Patterns with Template section: {sum(1 for p in patterns if p['has_template'])}")
    print(f"Patterns without Template section: {sum(1 for p in patterns if not p['has_template'])}")
    
    print(f"\nSection statistics:")
    for section, count in section_stats.most_common():
        print(f"  {section}: {count}")
    
    # Show examples of patterns with different section combinations
    section_combos = defaultdict(list)
    for p in patterns:
        combo = tuple(sorted(p['sections']))
        section_combos[combo].append(p)
    
    print(f"\nSection combinations (first 10):")
    for i, (combo, patterns_list) in enumerate(sorted(section_combos.items(), key=lambda x: -len(x[1]))[:10]):
        print(f"  {combo}: {len(patterns_list)} patterns")
        print(f"    Example: {patterns_list[0]['id']} - {patterns_list[0]['name'][:50]}...")

if __name__ == "__main__":
    main()