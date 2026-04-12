#!/usr/bin/env python3
"""
Validate archetypal_patterns.json for completeness and consistency.
"""

import json
import sys

def validate_archetypal_patterns():
    """Validate the archetypal patterns JSON file."""
    
    print("=" * 70)
    print("Archetypal Patterns Validation")
    print("=" * 70)
    print()
    
    # Load the file
    try:
        with open('archetypal_patterns.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("✓ Successfully loaded archetypal_patterns.json")
    except Exception as e:
        print(f"✗ Failed to load archetypal_patterns.json: {e}")
        return False
    
    errors = []
    warnings = []
    
    # Check metadata
    print("\n=== Metadata Validation ===")
    if 'meta' not in data:
        errors.append("Missing 'meta' field")
    else:
        meta = data['meta']
        if meta.get('total_patterns') != 253:
            errors.append(f"Expected total_patterns=253, got {meta.get('total_patterns')}")
        else:
            print(f"✓ Total patterns metadata: {meta['total_patterns']}")
    
    # Check patterns array
    if 'patterns' not in data:
        errors.append("Missing 'patterns' field")
        return False
    
    patterns = data['patterns']
    print(f"✓ Found {len(patterns)} patterns")
    
    if len(patterns) != 253:
        errors.append(f"Expected 253 patterns, found {len(patterns)}")
    
    # Validate individual patterns
    print("\n=== Pattern Structure Validation ===")
    pattern_ids = set()
    patterns_by_id = {}
    
    for i, pattern in enumerate(patterns):
        pid = pattern.get('pattern_id')
        if not pid:
            errors.append(f"Pattern at index {i} missing pattern_id")
            continue
        
        if pid in pattern_ids:
            errors.append(f"Duplicate pattern_id: {pid}")
        pattern_ids.add(pid)
        patterns_by_id[pid] = pattern
        
        # Check required fields
        if not pattern.get('name'):
            errors.append(f"Pattern {pid} missing name")
        
        if 'broader_patterns' not in pattern:
            warnings.append(f"Pattern {pid} missing broader_patterns field")
        
        if 'narrower_patterns' not in pattern:
            warnings.append(f"Pattern {pid} missing narrower_patterns field")
    
    print(f"✓ All patterns have unique IDs")
    print(f"✓ Checked {len(patterns)} pattern structures")
    
    # Validate relationships
    print("\n=== Relationship Validation ===")
    relationship_errors = 0
    
    for pid, pattern in patterns_by_id.items():
        broader = pattern.get('broader_patterns', [])
        narrower = pattern.get('narrower_patterns', [])
        
        # Check broader patterns exist
        for bp_id in broader:
            if bp_id not in patterns_by_id:
                errors.append(f"Pattern {pid} references non-existent broader pattern {bp_id}")
                relationship_errors += 1
            else:
                # Check bidirectional relationship
                bp = patterns_by_id[bp_id]
                if pid not in bp.get('narrower_patterns', []):
                    errors.append(
                        f"Pattern {pid} lists {bp_id} as broader, "
                        f"but {bp_id} doesn't list {pid} as narrower"
                    )
                    relationship_errors += 1
        
        # Check narrower patterns exist
        for np_id in narrower:
            if np_id not in patterns_by_id:
                errors.append(f"Pattern {pid} references non-existent narrower pattern {np_id}")
                relationship_errors += 1
            else:
                # Check bidirectional relationship
                np = patterns_by_id[np_id]
                if pid not in np.get('broader_patterns', []):
                    errors.append(
                        f"Pattern {pid} lists {np_id} as narrower, "
                        f"but {np_id} doesn't list {pid} as broader"
                    )
                    relationship_errors += 1
    
    if relationship_errors == 0:
        print("✓ All relationships are bidirectional and consistent")
    else:
        print(f"✗ Found {relationship_errors} relationship errors")
    
    # Statistics
    print("\n=== Pattern Statistics ===")
    patterns_with_broader = sum(1 for p in patterns if p.get('broader_patterns'))
    patterns_with_narrower = sum(1 for p in patterns if p.get('narrower_patterns'))
    patterns_with_archetypal = sum(1 for p in patterns if p.get('archetypal_pattern'))
    patterns_with_template = sum(1 for p in patterns if p.get('original_template'))
    
    print(f"  Patterns with broader relationships: {patterns_with_broader}")
    print(f"  Patterns with narrower relationships: {patterns_with_narrower}")
    print(f"  Patterns with archetypal templates: {patterns_with_archetypal}")
    print(f"  Patterns with original templates: {patterns_with_template}")
    
    # Check first and last patterns
    print("\n=== Special Pattern Validation ===")
    first_pattern = patterns_by_id.get('12610010')
    if first_pattern:
        if first_pattern.get('broader_patterns'):
            warnings.append("First pattern (12610010) should have no broader patterns")
        else:
            print("✓ First pattern (12610010) has no broader patterns")
    
    # Summary
    print("\n" + "=" * 70)
    print("Validation Summary")
    print("=" * 70)
    
    if errors:
        print(f"\n✗ Found {len(errors)} errors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    else:
        print("\n✓ No errors found!")
    
    if warnings:
        print(f"\n⚠ Found {len(warnings)} warnings:")
        for warning in warnings[:10]:  # Show first 10 warnings
            print(f"  - {warning}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings")
    
    print()
    return len(errors) == 0

if __name__ == '__main__':
    success = validate_archetypal_patterns()
    sys.exit(0 if success else 1)
