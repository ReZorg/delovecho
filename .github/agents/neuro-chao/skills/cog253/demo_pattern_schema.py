#!/usr/bin/env python3
"""
Demo script showing how to use the generated Pattern Language schema.
"""

import json
from pathlib import Path

def demo_meta_pattern():
    """Demonstrate the meta-pattern structure."""
    print("=== Pattern Language Meta-Pattern ===")
    
    with open('pattern_language_generated.json') as f:
        data = json.load(f)
    
    meta = data['meta_pattern']
    print(f"Name: {meta['name']}")
    print(f"Evidence Level: {'★' * meta['asterisks']} ({meta['asterisks']} asterisks)")
    print(f"Problem: {meta['problem_summary'][:100]}...")
    print(f"Solution: {meta['solution'][:100]}...")
    print(f"Connects to: {len(meta['following_patterns'])} patterns")
    print()

def demo_categories():
    """Demonstrate the three main categories."""
    print("=== Pattern Categories ===")
    
    with open('pattern_language_generated.json') as f:
        data = json.load(f)
    
    for category in data['categories']:
        range_info = category['pattern_range']
        sequence_count = len(category['sequences'])
        print(f"{category['name']:12} | Patterns {range_info['start']:3}-{range_info['end']:3} | {sequence_count:2} sequences")
        print(f"             | {category['description'][:80]}...")
        print()

def demo_sequences():
    """Demonstrate pattern sequences and their emergent phenomena."""
    print("=== Pattern Sequences (Sample) ===")
    
    with open('pattern_sequences.json') as f:
        data = json.load(f)
    
    # Show first 5 sequences from each category
    categories = ['Towns', 'Buildings', 'Construction']
    
    for category in categories:
        print(f"\n{category} Sequences:")
        sequences = [s for s in data['sequences'] if s['category'] == category][:5]
        
        for seq in sequences:
            print(f"  {seq['id']:2}. {seq['heading']}")
            print(f"      Patterns: {seq['patterns']}")
            print(f"      Emerges: {seq['emergent_phenomena'][:60]}...")
            print()

def demo_usage_instructions():
    """Demonstrate the usage instructions."""
    print("=== Usage Instructions ===")
    
    with open('pattern_language_generated.json') as f:
        data = json.load(f)
    
    instructions = data['usage_instructions']
    
    print("How to Use Patterns:")
    for i, instruction in enumerate(instructions['how_to_use'], 1):
        print(f"  {i}. {instruction}")
    
    print("\nPattern Evidence Levels:")
    hierarchies = instructions['pattern_hierarchies']
    print(f"  ★★  {hierarchies['two_asterisks'][:60]}...")
    print(f"  ★   {hierarchies['one_asterisk'][:60]}...")
    print(f"  (none) {hierarchies['no_asterisks'][:60]}...")
    print()

def demo_emergent_phenomena():
    """Show examples of emergent phenomena from pattern sequences."""
    print("=== Emergent Phenomena Examples ===")
    
    with open('pattern_sequences.json') as f:
        data = json.load(f)
    
    # Select interesting examples
    examples = [
        (1, "Regional level"),
        (7, "Local centers"),
        (20, "Spatial gradients"), 
        (36, "Building completion")
    ]
    
    for seq_id, description in examples:
        sequence = next(s for s in data['sequences'] if s['id'] == seq_id)
        print(f"{description:18} | {sequence['heading']}")
        print(f"{'':20}   Emerges: {sequence['emergent_phenomena']}")
        print()

def demo_json_schema_usage():
    """Show how to use the JSON schema for validation."""
    print("=== JSON Schema Usage ===")
    
    # Example pattern structure
    example_pattern = {
        "number": 42,
        "name": "Example Pattern",
        "asterisks": 1,
        "problem_summary": "This is an example problem that needs solving.",
        "solution": "This is the proposed solution to the problem.",
        "preceding_patterns": [30, 35],
        "following_patterns": [50, 55, 60]
    }
    
    print("Example Pattern Structure:")
    print(json.dumps(example_pattern, indent=2))
    print()
    
    try:
        import jsonschema
        
        with open('pattern_schema.json') as f:
            schema = json.load(f)
        
        jsonschema.validate(example_pattern, schema['definitions']['Pattern'])
        print("✓ Example pattern validates against the schema")
        
    except ImportError:
        print("ℹ Install jsonschema package to validate patterns: pip install jsonschema")
    except Exception as e:
        print(f"✗ Validation error: {e}")
    
    print()

def main():
    """Run all demonstrations."""
    print("🏛️  Pattern Language Schema Demo")
    print("=" * 50)
    print()
    
    # Check that files exist
    required_files = [
        'pattern_language_generated.json',
        'pattern_sequences.json', 
        'pattern_schema.json'
    ]
    
    missing = [f for f in required_files if not Path(f).exists()]
    if missing:
        print(f"❌ Missing files: {missing}")
        print("Run 'python3 generate_pattern_schema.py' first")
        return
    
    # Run demonstrations
    demo_meta_pattern()
    demo_categories()
    demo_sequences()
    demo_usage_instructions()
    demo_emergent_phenomena()
    demo_json_schema_usage()
    
    print("🎯 Schema Summary:")
    print("   • 1 meta-pattern expressing Pattern Language itself")
    print("   • 3 categories: Towns, Buildings, Construction") 
    print("   • 36 sequences capturing emergent phenomena")
    print("   • 253 patterns total (framework for all patterns)")
    print("   • Complete usage instructions and validation schema")
    print()
    print("📁 Files: pattern_schema.json, pattern_language_generated.json,")
    print("         category_*.json, pattern_sequences.json")

if __name__ == "__main__":
    main()