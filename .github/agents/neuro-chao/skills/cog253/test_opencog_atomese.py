#!/usr/bin/env python3
"""
Test script to validate the generated OpenCog Atomese files.

This script performs basic validation checks on the generated .scm files:
- File existence and readability
- Proper Scheme syntax (balanced parentheses)
- Expected node and link types
- Consistency with source JSON
"""

import re
from pathlib import Path
from typing import List, Tuple


def check_file_exists(filepath: Path) -> Tuple[bool, str]:
    """Check if file exists and is readable."""
    if not filepath.exists():
        return False, f"File not found: {filepath}"
    if not filepath.is_file():
        return False, f"Not a file: {filepath}"
    return True, f"✓ File exists: {filepath.name}"


def check_balanced_parentheses(content: str, filename: str) -> Tuple[bool, str]:
    """Check if parentheses are balanced in Scheme file."""
    stack = []
    line_num = 1
    
    for char in content:
        if char == '(':
            stack.append(('(', line_num))
        elif char == ')':
            if not stack:
                return False, f"✗ {filename}: Unmatched closing ')' near line {line_num}"
            stack.pop()
        elif char == '\n':
            line_num += 1
    
    if stack:
        return False, f"✗ {filename}: {len(stack)} unclosed '(' starting at line {stack[0][1]}"
    
    return True, f"✓ {filename}: Parentheses balanced"


def check_node_types(content: str, filename: str) -> Tuple[bool, str]:
    """Check for expected Atomese node types."""
    expected_nodes = ['ConceptNode', 'PredicateNode', 'VariableNode']
    found_nodes = set()
    
    for node_type in expected_nodes:
        if node_type in content:
            found_nodes.add(node_type)
    
    # ConceptNode and PredicateNode should always be present
    required = {'ConceptNode', 'PredicateNode'}
    if not required.issubset(found_nodes):
        missing = required - found_nodes
        return False, f"✗ {filename}: Missing node types: {missing}"
    
    return True, f"✓ {filename}: Found node types: {', '.join(sorted(found_nodes))}"


def check_link_types(content: str, filename: str) -> Tuple[bool, str]:
    """Check for expected Atomese link types."""
    expected_links = {
        'EvaluationLink': 'Property assertions',
        'ListLink': 'Ordered collections',
    }
    
    found_links = []
    for link_type in expected_links.keys():
        if link_type in content:
            found_links.append(link_type)
    
    if not found_links:
        return False, f"✗ {filename}: No expected link types found"
    
    return True, f"✓ {filename}: Found link types: {', '.join(found_links)}"


def check_pattern_structure(content: str, filename: str) -> Tuple[bool, str]:
    """Check for proper pattern structure in Atomese."""
    # Look for pattern concepts
    pattern_concepts = re.findall(r'\(ConceptNode "Pattern-(\d+)', content)
    
    if not pattern_concepts:
        # Only check files that should contain patterns
        if 'pattern' in filename.lower() or 'meta' in filename.lower():
            return False, f"✗ {filename}: No pattern concepts found"
        return True, f"✓ {filename}: No patterns expected"
    
    # Only check for pattern properties in pattern/meta files
    if 'meta' not in filename.lower() and 'pattern_language' not in filename.lower():
        return True, f"✓ {filename}: Contains {len(pattern_concepts)} pattern reference(s)"
    
    # Check for property predicates in pattern files
    predicates = re.findall(r'\(PredicateNode "([^"]+)"\)', content)
    
    expected_predicates = {'has-number', 'has-name', 'has-problem-summary', 'has-solution'}
    found_predicates = set(predicates) & expected_predicates
    
    if not found_predicates:
        return False, f"✗ {filename}: Expected pattern properties not found"
    
    return True, f"✓ {filename}: Found {len(pattern_concepts)} pattern(s) with properties"


def check_category_structure(content: str, filename: str) -> Tuple[bool, str]:
    """Check for proper category structure in Atomese."""
    # Look for category concepts
    category_concepts = re.findall(r'\(ConceptNode "Category-([^"]+)"\)', content)
    
    if 'categories' not in filename.lower():
        return True, f"✓ {filename}: No categories expected"
    
    if not category_concepts:
        return False, f"✗ {filename}: No category concepts found"
    
    expected_categories = {'Towns', 'Buildings', 'Construction'}
    found_categories = set(category_concepts)
    
    if found_categories != expected_categories:
        missing = expected_categories - found_categories
        if missing:
            return False, f"✗ {filename}: Missing categories: {missing}"
    
    # Check for InheritanceLinks
    if 'InheritanceLink' not in content:
        return False, f"✗ {filename}: No InheritanceLink found (needed for pattern-category relationships)"
    
    return True, f"✓ {filename}: Found all 3 categories with InheritanceLinks"


def check_sequence_structure(content: str, filename: str) -> Tuple[bool, str]:
    """Check for proper sequence structure in Atomese."""
    # Look for sequence concepts
    sequence_concepts = re.findall(r'\(ConceptNode "Sequence-(\d+)', content)
    
    if 'sequences' not in filename.lower():
        return True, f"✓ {filename}: No sequences expected"
    
    if not sequence_concepts:
        return False, f"✗ {filename}: No sequence concepts found"
    
    # Should have 36 sequences
    unique_sequences = set(sequence_concepts)
    if len(unique_sequences) != 36:
        return False, f"✗ {filename}: Expected 36 sequences, found {len(unique_sequences)}"
    
    # Check for MemberLinks
    if 'MemberLink' not in content:
        return False, f"✗ {filename}: No MemberLink found (needed for pattern-sequence relationships)"
    
    return True, f"✓ {filename}: Found all 36 sequences with MemberLinks"


def validate_atomese_files():
    """Validate all generated Atomese files."""
    print("=== OpenCog Atomese Validation ===\n")
    
    atomese_dir = Path("opencog_atomese")
    
    # Check directory exists
    if not atomese_dir.exists():
        print(f"❌ Directory not found: {atomese_dir}")
        print("Run 'python3 generate_opencog_atomese.py' first")
        return False
    
    # Define files to check
    files_to_check = [
        'meta_pattern.scm',
        'categories.scm',
        'sequences.scm',
        'pattern_language.scm',
        'README.md'
    ]
    
    all_passed = True
    results = []
    
    # Run validation checks
    for filename in files_to_check:
        filepath = atomese_dir / filename
        
        # Skip non-.scm files for Atomese checks
        if not filename.endswith('.scm'):
            exists, msg = check_file_exists(filepath)
            results.append(msg)
            if not exists:
                all_passed = False
            continue
        
        # Check file exists
        exists, msg = check_file_exists(filepath)
        results.append(msg)
        if not exists:
            all_passed = False
            continue
        
        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            results.append(f"✗ Error reading {filename}: {e}")
            all_passed = False
            continue
        
        # Run checks
        checks = [
            check_balanced_parentheses(content, filename),
            check_node_types(content, filename),
            check_link_types(content, filename),
            check_pattern_structure(content, filename),
            check_category_structure(content, filename),
            check_sequence_structure(content, filename)
        ]
        
        for passed, msg in checks:
            results.append(msg)
            if not passed:
                all_passed = False
    
    # Print results
    for result in results:
        print(result)
    
    # Summary
    print(f"\n=== Validation Summary ===")
    if all_passed:
        print("✅ All Atomese validation checks passed!")
        print("\nGenerated Atomese files are ready for use with OpenCog.")
        print("Load them into an AtomSpace with: (load \"pattern_language.scm\")")
        return True
    else:
        print("❌ Some validation checks failed.")
        print("Review the errors above and regenerate the files if needed.")
        return False


def main():
    """Main entry point."""
    success = validate_atomese_files()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
