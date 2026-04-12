#!/usr/bin/env python3
"""
Test suite for enhanced OpenCog Atomese representation.

Tests the three future enhancements:
1. Individual pattern files
2. Additional pattern properties (diagrams, examples)
3. Pattern relationship types (conflicts, complements)
"""

import os
import re
from pathlib import Path


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()


def check_parentheses_balanced(content: str) -> bool:
    """Check if parentheses are balanced in Scheme code."""
    count = 0
    for char in content:
        if char == '(':
            count += 1
        elif char == ')':
            count -= 1
        if count < 0:
            return False
    return count == 0


def count_pattern_in_file(filepath: str, pattern: str) -> int:
    """Count occurrences of a pattern in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        return len(re.findall(pattern, content))


def test_individual_pattern_files():
    """Test Enhancement #1: Individual pattern files."""
    print("\n=== Testing Enhancement #1: Individual Pattern Files ===")
    
    # Check patterns directory exists
    patterns_dir = "opencog_atomese/patterns"
    assert check_file_exists(patterns_dir), f"✗ Directory not found: {patterns_dir}"
    print(f"✓ Directory exists: {patterns_dir}")
    
    # Check that at least the meta-pattern file exists
    pattern_000 = "opencog_atomese/patterns/pattern_000.scm"
    assert check_file_exists(pattern_000), f"✗ File not found: {pattern_000}"
    print(f"✓ File exists: {pattern_000}")
    
    # Check file structure and syntax
    with open(pattern_000, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert check_parentheses_balanced(content), "✗ Parentheses not balanced"
    print(f"✓ {pattern_000}: Parentheses balanced")
    
    # Check for expected node types
    assert 'ConceptNode' in content, "✗ ConceptNode not found"
    assert 'PredicateNode' in content, "✗ PredicateNode not found"
    print(f"✓ {pattern_000}: Found node types: ConceptNode, PredicateNode")
    
    # Check for expected link types
    assert 'EvaluationLink' in content, "✗ EvaluationLink not found"
    print(f"✓ {pattern_000}: Found link types: EvaluationLink")
    
    # Check for pattern properties
    assert 'has-number' in content, "✗ has-number property not found"
    assert 'has-name' in content, "✗ has-name property not found"
    print(f"✓ {pattern_000}: Contains pattern properties")


def test_enhanced_properties():
    """Test Enhancement #2: Additional pattern properties."""
    print("\n=== Testing Enhancement #2: Additional Pattern Properties ===")
    
    # Check enhanced file exists
    enhanced_file = "opencog_atomese/pattern_language_enhanced.scm"
    assert check_file_exists(enhanced_file), f"✗ File not found: {enhanced_file}"
    print(f"✓ File exists: {enhanced_file}")
    
    # Check file structure and syntax
    with open(enhanced_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert check_parentheses_balanced(content), "✗ Parentheses not balanced"
    print(f"✓ {enhanced_file}: Parentheses balanced")
    
    # Check for enhanced properties
    has_problem_details = 'has-problem-details' in content
    has_diagram = 'has-diagram' in content
    has_connections = 'has-connections' in content
    
    print(f"✓ {enhanced_file}: Enhanced property 'has-problem-details' present: {has_problem_details}")
    print(f"✓ {enhanced_file}: Enhanced property 'has-diagram' present: {has_diagram}")
    print(f"✓ {enhanced_file}: Enhanced property 'has-connections' present: {has_connections}")
    
    # At least one enhanced property should be present
    assert has_problem_details or has_diagram or has_connections, \
        "✗ No enhanced properties found"
    
    # Check for standard properties still present
    assert 'has-number' in content, "✗ has-number property not found"
    assert 'has-name' in content, "✗ has-name property not found"
    assert 'has-solution' in content, "✗ has-solution property not found"
    print(f"✓ {enhanced_file}: Standard properties still present")


def test_relationship_types():
    """Test Enhancement #3: Pattern relationship types."""
    print("\n=== Testing Enhancement #3: Pattern Relationship Types ===")
    
    # Check relationship types file exists
    rel_file = "opencog_atomese/relationship_types.scm"
    assert check_file_exists(rel_file), f"✗ File not found: {rel_file}"
    print(f"✓ File exists: {rel_file}")
    
    # Check file structure and syntax
    with open(rel_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert check_parentheses_balanced(content), "✗ Parentheses not balanced"
    print(f"✓ {rel_file}: Parentheses balanced")
    
    # Check for relationship type definitions
    rel_types = [
        'RelationType-Dependency',
        'RelationType-Complement',
        'RelationType-Conflict',
        'RelationType-Alternative'
    ]
    
    for rel_type in rel_types:
        assert rel_type in content, f"✗ Relationship type not found: {rel_type}"
        print(f"✓ {rel_file}: Found relationship type: {rel_type}")
    
    # Check for relationship predicate
    assert 'has-relationship' in content, "✗ has-relationship predicate not found"
    print(f"✓ {rel_file}: Found relationship predicate: has-relationship")
    
    # Check for descriptions
    assert 'has-description' in content, "✗ has-description predicate not found"
    print(f"✓ {rel_file}: Relationship types have descriptions")


def test_enhancements_documentation():
    """Test that documentation for enhancements exists."""
    print("\n=== Testing Enhancements Documentation ===")
    
    # Check ENHANCEMENTS.md exists
    doc_file = "opencog_atomese/ENHANCEMENTS.md"
    assert check_file_exists(doc_file), f"✗ File not found: {doc_file}"
    print(f"✓ File exists: {doc_file}")
    
    # Check content
    with open(doc_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for documentation of all enhancements
    assert 'Enhancement #1' in content, "✗ Enhancement #1 not documented"
    assert 'Enhancement #2' in content, "✗ Enhancement #2 not documented"
    assert 'Enhancement #3' in content, "✗ Enhancement #3 not documented"
    print(f"✓ {doc_file}: All enhancements documented")
    
    # Check for usage examples
    assert 'Usage:' in content or 'usage:' in content.lower(), "✗ No usage examples"
    print(f"✓ {doc_file}: Contains usage examples")


def test_implementation_summary_updated():
    """Test that IMPLEMENTATION_SUMMARY.md was updated."""
    print("\n=== Testing IMPLEMENTATION_SUMMARY.md Updates ===")
    
    summary_file = "IMPLEMENTATION_SUMMARY.md"
    assert check_file_exists(summary_file), f"✗ File not found: {summary_file}"
    print(f"✓ File exists: {summary_file}")
    
    # Check content
    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for completed enhancements section
    assert 'Completed Enhancements' in content or '✅' in content, \
        "✗ No completed enhancements section found"
    print(f"✓ {summary_file}: Contains completed enhancements section")


def test_file_integrity():
    """Test that all generated files have valid Scheme syntax."""
    print("\n=== Testing File Integrity ===")
    
    # List of files to check
    files_to_check = [
        "opencog_atomese/patterns/pattern_000.scm",
        "opencog_atomese/pattern_language_enhanced.scm",
        "opencog_atomese/relationship_types.scm"
    ]
    
    for filepath in files_to_check:
        if check_file_exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax checks
            assert check_parentheses_balanced(content), \
                f"✗ {filepath}: Parentheses not balanced"
            
            # Check for basic Atomese structure
            assert '(ConceptNode' in content or '(PredicateNode' in content, \
                f"✗ {filepath}: No nodes found"
            
            print(f"✓ {filepath}: Valid Atomese syntax")


def main():
    """Run all tests."""
    print("=== Enhanced OpenCog Atomese Validation ===")
    
    try:
        test_individual_pattern_files()
        test_enhanced_properties()
        test_relationship_types()
        test_enhancements_documentation()
        test_implementation_summary_updated()
        test_file_integrity()
        
        print("\n=== Validation Summary ===")
        print("✅ All enhanced Atomese validation checks passed!")
        print("\nEnhanced features are ready for use with OpenCog.")
        print("\nLoad enhanced files into an AtomSpace with:")
        print("  (load \"opencog_atomese/pattern_language_enhanced.scm\")")
        print("  (load \"opencog_atomese/relationship_types.scm\")")
        print("  (load \"opencog_atomese/patterns/pattern_000.scm\")")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
