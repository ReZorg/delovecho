#!/usr/bin/env python3
"""
Validate domain-specific content in archetypal patterns.
Checks that all patterns have appropriate domain content from UIA sources.
"""

import json
import sys

def validate_domain_content():
    """Validate domain-specific content completeness."""
    
    print("=" * 70)
    print("DOMAIN-SPECIFIC CONTENT VALIDATION")
    print("=" * 70)
    
    # Load archetypal patterns
    try:
        with open('archetypal_patterns.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("✗ Error: archetypal_patterns.json not found")
        return False
    
    patterns = data.get('patterns', [])
    print(f"\n✓ Loaded {len(patterns)} patterns")
    
    # Check metadata
    meta = data.get('meta', {})
    if 'includes_domain_content' in meta:
        print(f"✓ Metadata indicates domain content included: {meta['includes_domain_content']}")
        print(f"✓ Patterns with domain content: {meta.get('patterns_with_domain_content', 0)}")
    else:
        print("✗ Warning: Metadata missing domain content flags")
    
    # Validate domain content
    print("\n=== Domain Content Validation ===")
    
    with_content = 0
    without_content = 0
    domain_counts = {
        'physical': 0,
        'social': 0,
        'conceptual': 0,
        'psychic': 0
    }
    
    patterns_all_domains = []
    patterns_physical_only = []
    patterns_no_content = []
    
    for pattern in patterns:
        pattern_id = pattern.get('pattern_id', 'unknown')
        
        if 'domain_specific_content' not in pattern:
            without_content += 1
            patterns_no_content.append(pattern_id)
            continue
        
        with_content += 1
        content = pattern['domain_specific_content']
        
        # Count domains present
        domains_present = []
        for domain in ['physical', 'social', 'conceptual', 'psychic']:
            if domain in content:
                domain_counts[domain] += 1
                domains_present.append(domain)
        
        # Categorize patterns
        if len(domains_present) == 4:
            patterns_all_domains.append(pattern_id)
        elif len(domains_present) == 1 and 'physical' in domains_present:
            patterns_physical_only.append(pattern_id)
    
    print(f"\n✓ Patterns with domain_specific_content: {with_content}")
    print(f"  Patterns without domain_specific_content: {without_content}")
    
    if without_content > 0:
        print(f"\n✗ Warning: {without_content} patterns missing domain content:")
        for pid in patterns_no_content[:5]:
            print(f"    - {pid}")
        if len(patterns_no_content) > 5:
            print(f"    ... and {len(patterns_no_content) - 5} more")
    
    print(f"\n=== Domain Coverage ===")
    for domain, count in domain_counts.items():
        percentage = (count / len(patterns) * 100) if patterns else 0
        print(f"  {domain:12}: {count:3} patterns ({percentage:5.1f}%)")
    
    print(f"\n=== Pattern Distribution ===")
    print(f"  Patterns with all 4 domains: {len(patterns_all_domains)}")
    print(f"  Patterns with physical only: {len(patterns_physical_only)}")
    
    # Validate content quality
    print(f"\n=== Content Quality Checks ===")
    
    empty_content = []
    short_content = []
    
    for pattern in patterns:
        if 'domain_specific_content' not in pattern:
            continue
        
        pattern_id = pattern.get('pattern_id', 'unknown')
        content = pattern['domain_specific_content']
        
        for domain, text in content.items():
            if not text or len(text.strip()) == 0:
                empty_content.append(f"{pattern_id}/{domain}")
            elif len(text.strip()) < 20:
                short_content.append(f"{pattern_id}/{domain}")
    
    if empty_content:
        print(f"\n✗ Warning: {len(empty_content)} empty domain contents found:")
        for item in empty_content[:5]:
            print(f"    - {item}")
        if len(empty_content) > 5:
            print(f"    ... and {len(empty_content) - 5} more")
    else:
        print(f"\n✓ No empty domain contents found")
    
    if short_content:
        print(f"\n⚠ Note: {len(short_content)} very short domain contents (< 20 chars)")
    else:
        print(f"\n✓ All domain contents have reasonable length")
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    all_pass = True
    
    if without_content > 0:
        print(f"✗ {without_content} patterns missing domain content")
        all_pass = False
    else:
        print(f"✓ All patterns have domain content")
    
    if domain_counts['physical'] == len(patterns):
        print(f"✓ All patterns have physical domain content")
    else:
        print(f"✗ Only {domain_counts['physical']}/{len(patterns)} have physical content")
        all_pass = False
    
    if empty_content:
        print(f"✗ {len(empty_content)} empty domain contents found")
        all_pass = False
    else:
        print(f"✓ No empty domain contents")
    
    if all_pass:
        print("\n✓✓✓ ALL VALIDATIONS PASSED ✓✓✓")
        return True
    else:
        print("\n⚠ Some validations failed (see above)")
        return False

if __name__ == '__main__':
    success = validate_domain_content()
    sys.exit(0 if success else 1)
