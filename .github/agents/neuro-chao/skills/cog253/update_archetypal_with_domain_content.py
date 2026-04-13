#!/usr/bin/env python3
"""
Update archetypal patterns with domain-specific detailed content from UIA markdown files.
This completes missing information by adding Physical, Social, Conceptual, and Psychic
domain variations from the source UIA patterns.
"""

import json
import os
import re
from pathlib import Path

def parse_uia_markdown(filepath):
    """Parse a UIA markdown file to extract domain-specific content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract sections using regex
    sections = {}
    
    # Extract Template
    template_match = re.search(r'## Template\s*\n\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if template_match:
        sections['template'] = template_match.group(1).strip()
    
    # Extract Physical
    physical_match = re.search(r'## Physical\s*\n\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if physical_match:
        sections['physical'] = physical_match.group(1).strip()
    
    # Extract Social
    social_match = re.search(r'## Social\s*\n\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if social_match:
        sections['social'] = social_match.group(1).strip()
    
    # Extract Conceptual
    conceptual_match = re.search(r'## Conceptual\s*\n\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if conceptual_match:
        sections['conceptual'] = conceptual_match.group(1).strip()
    
    # Extract Psychic
    psychic_match = re.search(r'## Psychic\s*\n\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if psychic_match:
        sections['psychic'] = psychic_match.group(1).strip()
    
    return sections

def update_archetypal_patterns():
    """Update archetypal_patterns.json with domain-specific content from UIA markdown."""
    
    # Load current archetypal patterns
    with open('archetypal_patterns.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    patterns_updated = 0
    patterns_with_content = 0
    
    print(f"Processing {len(data['patterns'])} archetypal patterns...")
    
    for pattern in data['patterns']:
        pattern_id = pattern['pattern_id']
        source_file = pattern.get('source_file', '')
        
        # Construct the UIA markdown file path
        uia_file = Path('markdown/uia') / f"{pattern_id}.md"
        
        if not uia_file.exists():
            print(f"Warning: UIA file not found for pattern {pattern_id}: {uia_file}")
            continue
        
        # Parse the UIA markdown file
        sections = parse_uia_markdown(uia_file)
        
        # Check if we have domain-specific content
        has_content = any(k in sections for k in ['physical', 'social', 'conceptual', 'psychic'])
        
        if has_content:
            # Add domain-specific content to the pattern
            if 'domain_specific_content' not in pattern:
                pattern['domain_specific_content'] = {}
            
            if 'physical' in sections:
                pattern['domain_specific_content']['physical'] = sections['physical']
            if 'social' in sections:
                pattern['domain_specific_content']['social'] = sections['social']
            if 'conceptual' in sections:
                pattern['domain_specific_content']['conceptual'] = sections['conceptual']
            if 'psychic' in sections:
                pattern['domain_specific_content']['psychic'] = sections['psychic']
            
            patterns_with_content += 1
            patterns_updated += 1
        
    print(f"\nUpdated {patterns_updated} patterns with domain-specific content")
    print(f"Patterns with domain-specific content: {patterns_with_content}")
    
    # Update metadata
    if 'meta' in data:
        data['meta']['includes_domain_content'] = True
        data['meta']['patterns_with_domain_content'] = patterns_with_content
    
    # Save updated patterns
    with open('archetypal_patterns.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved updated archetypal_patterns.json")
    
    return patterns_updated, patterns_with_content

if __name__ == '__main__':
    updated, with_content = update_archetypal_patterns()
    print(f"\nSummary:")
    print(f"  Total patterns updated: {updated}")
    print(f"  Patterns with domain-specific content: {with_content}")
