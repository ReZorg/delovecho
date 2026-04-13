#!/usr/bin/env python3
"""
Demo script for Archetypal Pattern Schema.

Demonstrates how to use the archetypal pattern specifications to:
1. Load archetypal patterns
2. Apply domain-specific transformations
3. Query patterns by placeholder usage
4. Generate domain-specific versions
"""

import json
from typing import List, Dict, Any


def load_archetypal_patterns() -> Dict[str, Any]:
    """Load the archetypal patterns collection."""
    with open('archetypal_patterns.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def apply_domain_transformation(pattern: Dict[str, Any], domain: str) -> str:
    """Transform an archetypal pattern to a specific domain."""
    archetypal_text = pattern["archetypal_pattern"]
    domain_mappings = pattern.get("domain_mappings", {})
    
    result = archetypal_text
    for placeholder, mappings in domain_mappings.items():
        if domain.lower() in mappings:
            placeholder_pattern = f"{{{{{placeholder}}}}}"
            replacement = mappings[domain.lower()]
            result = result.replace(placeholder_pattern, replacement)
    
    return result


def find_patterns_with_placeholder(patterns: List[Dict[str, Any]], placeholder: str) -> List[Dict[str, Any]]:
    """Find all patterns that use a specific placeholder."""
    return [p for p in patterns if placeholder in p.get("placeholders", [])]


def demo_basic_usage():
    """Demonstrate basic usage of archetypal patterns."""
    print("=" * 80)
    print("DEMO: Basic Usage of Archetypal Patterns")
    print("=" * 80)
    
    data = load_archetypal_patterns()
    patterns = data["patterns"]
    
    print(f"\nLoaded {len(patterns)} archetypal patterns")
    print(f"Total unique placeholders: {len(data['placeholder_definitions'])}")
    
    # Show first pattern
    pattern = patterns[0]
    print(f"\n--- Pattern {pattern['pattern_id']}: {pattern['name']} ---")
    print(f"\nArchetypal Pattern:")
    print(f"  {pattern['archetypal_pattern']}")
    print(f"\nPlaceholders used: {', '.join(pattern['placeholders'])}")


def demo_domain_transformations():
    """Demonstrate transforming patterns to different domains."""
    print("\n" + "=" * 80)
    print("DEMO: Domain-Specific Transformations")
    print("=" * 80)
    
    data = load_archetypal_patterns()
    pattern = data["patterns"][0]  # Independent domains
    
    print(f"\nPattern: {pattern['name']} (ID: {pattern['pattern_id']})")
    print(f"\nArchetypal Pattern:")
    print(f"  {pattern['archetypal_pattern']}")
    
    domains = ["physical", "social", "conceptual", "psychic"]
    
    print(f"\n--- Domain-Specific Versions (via transformation) ---")
    for domain in domains:
        transformed = apply_domain_transformation(pattern, domain)
        print(f"\n{domain.upper()}:")
        print(f"  {transformed}")
    
    # Show domain-specific content from UIA source
    if 'domain_specific_content' in pattern:
        print(f"\n--- Domain-Specific Content (from UIA source) ---")
        for domain in domains:
            if domain in pattern['domain_specific_content']:
                content = pattern['domain_specific_content'][domain]
                # Show first 150 chars
                preview = content[:150] + "..." if len(content) > 150 else content
                print(f"\n{domain.upper()}:")
                print(f"  {preview}")


def demo_domain_content():
    """Demonstrate accessing full domain-specific content from UIA."""
    print("\n" + "=" * 80)
    print("DEMO: Full Domain-Specific Content from UIA")
    print("=" * 80)
    
    data = load_archetypal_patterns()
    pattern = data["patterns"][0]  # Independent domains
    
    print(f"\nPattern: {pattern['name']} (ID: {pattern['pattern_id']})")
    
    if 'domain_specific_content' in pattern:
        print(f"\nAvailable domain content: {list(pattern['domain_specific_content'].keys())}")
        
        # Show full physical content as example
        if 'physical' in pattern['domain_specific_content']:
            print(f"\n--- Full Physical Domain Implementation ---")
            print(pattern['domain_specific_content']['physical'])
    else:
        print("\nNo domain-specific content available for this pattern.")


def demo_placeholder_query():
    """Demonstrate querying patterns by placeholder."""
    print("\n" + "=" * 80)
    print("DEMO: Querying Patterns by Placeholder")
    print("=" * 80)
    
    data = load_archetypal_patterns()
    patterns = data["patterns"]
    
    # Find patterns using 'frameworks' placeholder
    placeholder = "frameworks"
    matching = find_patterns_with_placeholder(patterns, placeholder)
    
    print(f"\nPatterns using '{{{{placeholder}}}}': {len(matching)} found")
    print(f"\nFirst 5 patterns:")
    for i, pattern in enumerate(matching[:5], 1):
        print(f"  {i}. {pattern['pattern_id']}: {pattern['name']}")


def demo_multi_domain_comparison():
    """Demonstrate comparing a pattern across domains."""
    print("\n" + "=" * 80)
    print("DEMO: Multi-Domain Pattern Comparison")
    print("=" * 80)
    
    data = load_archetypal_patterns()
    # Use a more complex pattern
    pattern = data["patterns"][3]  # Regenerative resource cultivation areas
    
    print(f"\nPattern: {pattern['name']} (ID: {pattern['pattern_id']})")
    
    print(f"\n--- Archetypal Template ---")
    print(f"{pattern['archetypal_pattern']}")
    
    domains = ["physical", "social", "conceptual", "psychic"]
    
    print(f"\n--- Domain Transformations ---")
    for domain in domains:
        print(f"\n{domain.upper()} DOMAIN:")
        transformed = apply_domain_transformation(pattern, domain)
        # Wrap text nicely
        words = transformed.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > 75:
                print(f"  {line}")
                line = word
            else:
                line = f"{line} {word}" if line else word
        if line:
            print(f"  {line}")


def demo_placeholder_mappings():
    """Demonstrate placeholder mapping exploration."""
    print("\n" + "=" * 80)
    print("DEMO: Placeholder Mapping Reference")
    print("=" * 80)
    
    with open('archetypal_placeholders.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\nTotal placeholders: {data['total_placeholders']}")
    
    # Show detailed mapping for one placeholder
    placeholder = data["placeholders"][0]
    print(f"\n--- Example: '{placeholder['placeholder']}' ---")
    print(f"Used in {len(placeholder['used_in_patterns'])} patterns")
    
    print(f"\nDomain mappings:")
    for domain, mapping in placeholder["domains"].items():
        print(f"  • {domain:15} → {mapping}")
    
    print(f"\nSample patterns using this placeholder:")
    for i, usage in enumerate(placeholder["used_in_patterns"][:3], 1):
        print(f"  {i}. [{usage['pattern_id']}] {usage['pattern_name']}")


def demo_pattern_instantiation():
    """Demonstrate creating fully instantiated patterns."""
    print("\n" + "=" * 80)
    print("DEMO: Creating Fully Instantiated Patterns")
    print("=" * 80)
    
    data = load_archetypal_patterns()
    pattern = data["patterns"][1]  # Distribution of organization
    
    print(f"\nPattern: {pattern['name']}")
    
    # Create instances for different domains
    instances = []
    for domain in ["physical", "social", "conceptual"]:
        instance = {
            "domain": domain,
            "pattern_id": pattern["pattern_id"],
            "name": f"{pattern['name']} ({domain})",
            "text": apply_domain_transformation(pattern, domain)
        }
        instances.append(instance)
    
    print(f"\n--- Generated {len(instances)} Domain-Specific Instances ---")
    for instance in instances:
        print(f"\n{instance['domain'].upper()} INSTANCE:")
        print(f"  Name: {instance['name']}")
        print(f"  Text: {instance['text'][:100]}...")


def main():
    """Run all demonstrations."""
    print("\n" + "█" * 80)
    print("ARCHETYPAL PATTERN SCHEMA DEMONSTRATION")
    print("█" * 80)
    
    try:
        demo_basic_usage()
        demo_domain_transformations()
        demo_domain_content()  # New demo for domain-specific content
        demo_placeholder_query()
        demo_multi_domain_comparison()
        demo_placeholder_mappings()
        demo_pattern_instantiation()
        
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\n✓ All demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  • Loading archetypal patterns")
        print("  • Transforming patterns to specific domains")
        print("  • Accessing full domain-specific content from UIA")
        print("  • Querying patterns by placeholder")
        print("  • Comparing patterns across domains")
        print("  • Exploring placeholder mappings")
        print("  • Instantiating concrete patterns")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: Required file not found: {e}")
        print("Please run 'python3 generate_archetypal_schema.py' first")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
