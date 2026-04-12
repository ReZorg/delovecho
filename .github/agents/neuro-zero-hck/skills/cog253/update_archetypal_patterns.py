#!/usr/bin/env python3
"""
Update archetypal_patterns.json with all 253 patterns and their relationships.
"""

import json
from pathlib import Path

def load_existing_archetypal():
    """Load the existing archetypal_patterns.json"""
    with open('archetypal_patterns.json') as f:
        return json.load(f)

def load_extracted_patterns():
    """Load the patterns_extracted.json"""
    with open('patterns_extracted.json') as f:
        return json.load(f)

def merge_patterns(archetypal_data, extracted_data):
    """Merge extracted patterns with archetypal data."""
    
    # Create a lookup dict for existing archetypal patterns
    existing = {p['pattern_id']: p for p in archetypal_data['patterns']}
    
    # Create new patterns list with all 253 patterns
    new_patterns = []
    
    for extracted in extracted_data['patterns']:
        pattern_id = extracted['pattern_id']
        
        if pattern_id in existing:
            # Use existing archetypal pattern data and add relationships
            pattern = existing[pattern_id].copy()
            pattern['broader_patterns'] = extracted['broader_patterns']
            pattern['narrower_patterns'] = extracted['narrower_patterns']
        else:
            # Create new pattern entry with basic data
            pattern = {
                'pattern_id': pattern_id,
                'name': extracted['name'],
                'archetypal_pattern': extracted['template'],
                'original_template': extracted['template'],
                'placeholders': [],  # Will be filled by analysis later
                'domain_mappings': {},  # Will be filled by analysis later
                'broader_patterns': extracted['broader_patterns'],
                'narrower_patterns': extracted['narrower_patterns']
            }
        
        new_patterns.append(pattern)
    
    # Update metadata
    archetypal_data['meta']['total_patterns'] = len(new_patterns)
    archetypal_data['meta']['description'] = 'All 253 archetypal patterns with relationships'
    archetypal_data['patterns'] = new_patterns
    
    return archetypal_data

def main():
    """Main function to update archetypal_patterns.json"""
    
    print("Loading existing archetypal patterns...")
    archetypal_data = load_existing_archetypal()
    print(f"  Loaded {len(archetypal_data['patterns'])} patterns")
    
    print("\nLoading extracted patterns...")
    extracted_data = load_extracted_patterns()
    print(f"  Loaded {len(extracted_data['patterns'])} patterns")
    
    print("\nMerging patterns...")
    merged_data = merge_patterns(archetypal_data, extracted_data)
    print(f"  Created {len(merged_data['patterns'])} patterns")
    
    # Count patterns with relationships
    with_broader = sum(1 for p in merged_data['patterns'] if p.get('broader_patterns'))
    with_narrower = sum(1 for p in merged_data['patterns'] if p.get('narrower_patterns'))
    with_archetypal = sum(1 for p in merged_data['patterns'] if p.get('archetypal_pattern'))
    
    print(f"\nRelationship statistics:")
    print(f"  Patterns with broader relationships: {with_broader}")
    print(f"  Patterns with narrower relationships: {with_narrower}")
    print(f"  Patterns with archetypal templates: {with_archetypal}")
    
    # Backup old file
    import shutil
    shutil.copy('archetypal_patterns.json', 'archetypal_patterns.json.backup')
    print("\n  Backed up original to archetypal_patterns.json.backup")
    
    # Save updated file
    with open('archetypal_patterns.json', 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print("\nSaved updated archetypal_patterns.json")
    print(f"  Total patterns: {len(merged_data['patterns'])}")

if __name__ == '__main__':
    main()
