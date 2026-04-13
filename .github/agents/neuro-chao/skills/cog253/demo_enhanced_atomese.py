#!/usr/bin/env python3
"""
Demo script for Enhanced OpenCog Atomese features.

Demonstrates the three future enhancements:
1. Individual pattern files
2. Additional pattern properties (diagrams, examples)
3. Pattern relationship types (conflicts, complements)
"""

from pathlib import Path
import re


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def print_subsection(title: str):
    """Print a subsection header."""
    print(f"\n{title}")
    print('-' * len(title))


def demo_individual_pattern_files():
    """Demonstrate Enhancement #1: Individual Pattern Files."""
    print_section("Enhancement #1: Individual Pattern Files")
    
    print("\nIndividual pattern files allow you to:")
    print("  ✓ Load specific patterns without loading the entire knowledge base")
    print("  ✓ Navigate and maintain patterns more easily")
    print("  ✓ Reduce memory footprint for focused applications")
    
    print_subsection("Directory Structure")
    patterns_dir = Path("opencog_atomese/patterns")
    if patterns_dir.exists():
        pattern_files = sorted(patterns_dir.glob("*.scm"))
        print(f"\nFound {len(pattern_files)} individual pattern file(s):")
        for pf in pattern_files:
            size = pf.stat().st_size
            print(f"  • {pf.name} ({size:,} bytes)")
    
    print_subsection("Example: Loading a Specific Pattern")
    print("\n```scheme")
    print("; Load only Pattern 0 (the meta-pattern)")
    print("(load \"opencog_atomese/patterns/pattern_000.scm\")")
    print("```")
    
    print_subsection("Sample Content")
    pattern_000 = Path("opencog_atomese/patterns/pattern_000.scm")
    if pattern_000.exists():
        with open(pattern_000, 'r') as f:
            lines = f.readlines()
        print("\nFirst 20 lines of pattern_000.scm:")
        for i, line in enumerate(lines[:20], 1):
            print(f"  {i:2d} | {line.rstrip()}")


def demo_enhanced_properties():
    """Demonstrate Enhancement #2: Additional Pattern Properties."""
    print_section("Enhancement #2: Additional Pattern Properties")
    
    print("\nEnhanced properties include:")
    print("  ✓ has-problem-details: Detailed problem description")
    print("  ✓ has-diagram: Reference to pattern diagrams")
    print("  ✓ has-connections: Examples and connections to other patterns")
    
    enhanced_file = Path("opencog_atomese/pattern_language_enhanced.scm")
    if enhanced_file.exists():
        with open(enhanced_file, 'r') as f:
            content = f.read()
        
        print_subsection("Properties Found")
        properties = {
            'has-problem-details': content.count('has-problem-details'),
            'has-diagram': content.count('has-diagram'),
            'has-connections': content.count('has-connections'),
            'has-problem-summary': content.count('has-problem-summary'),
            'has-solution': content.count('has-solution'),
            'has-context': content.count('has-context')
        }
        
        print("\nProperty occurrence counts:")
        for prop, count in properties.items():
            status = "Enhanced" if prop.startswith('has-problem-details') or \
                                   prop.startswith('has-diagram') or \
                                   prop.startswith('has-connections') else "Standard"
            print(f"  • {prop:25s}: {count:3d} occurrences [{status}]")
    
    print_subsection("Example: Querying Enhanced Properties")
    print("\n```scheme")
    print("; Query pattern diagrams")
    print("(GetLink")
    print("  (VariableNode \"$diagram\")")
    print("  (EvaluationLink")
    print("    (PredicateNode \"has-diagram\")")
    print("    (ListLink")
    print("      (ConceptNode \"Pattern-0-Pattern Language\")")
    print("      (VariableNode \"$diagram\"))))")
    print("```")
    
    print_subsection("Sample Enhanced Content")
    with open(enhanced_file, 'r') as f:
        lines = f.readlines()
    
    # Find and display a problem-details section
    in_problem_details = False
    detail_lines = []
    for i, line in enumerate(lines):
        if 'has-problem-details' in line:
            in_problem_details = True
            detail_lines.append(f"Line {i+1:3d}: {line.rstrip()}")
        elif in_problem_details:
            detail_lines.append(f"Line {i+1:3d}: {line.rstrip()}")
            if line.strip() == ')':
                in_problem_details = False
                break
    
    if detail_lines:
        print("\nExample of has-problem-details property:")
        for line in detail_lines[:10]:  # Show first 10 lines
            print(f"  {line}")


def demo_relationship_types():
    """Demonstrate Enhancement #3: Pattern Relationship Types."""
    print_section("Enhancement #3: Pattern Relationship Types")
    
    print("\nRelationship types extend pattern connections:")
    print("  ✓ Dependency: Sequential pattern relationships")
    print("  ✓ Complement: Patterns that work well together")
    print("  ✓ Conflict: Patterns that contradict each other")
    print("  ✓ Alternative: Patterns providing alternative solutions")
    
    rel_file = Path("opencog_atomese/relationship_types.scm")
    if rel_file.exists():
        with open(rel_file, 'r') as f:
            content = f.read()
        
        print_subsection("Relationship Type Definitions")
        rel_types = [
            'RelationType-Dependency',
            'RelationType-Complement',
            'RelationType-Conflict',
            'RelationType-Alternative'
        ]
        
        print("\nDefined relationship types:")
        for rt in rel_types:
            count = content.count(rt)
            print(f"  • {rt:30s}: {count} references")
    
    print_subsection("Example: Finding Complementary Patterns")
    print("\n```scheme")
    print("; Find all patterns that complement Pattern-1")
    print("(GetLink")
    print("  (VariableNode \"$complement\")")
    print("  (EvaluationLink")
    print("    (PredicateNode \"has-relationship\")")
    print("    (ListLink")
    print("      (ConceptNode \"Pattern-1\")")
    print("      (VariableNode \"$complement\")")
    print("      (ConceptNode \"RelationType-Complement\"))))")
    print("```")
    
    print_subsection("Example: Finding Conflicting Patterns")
    print("\n```scheme")
    print("; Find all patterns that conflict with Pattern-1")
    print("(GetLink")
    print("  (VariableNode \"$conflict\")")
    print("  (EvaluationLink")
    print("    (PredicateNode \"has-relationship\")")
    print("    (ListLink")
    print("      (ConceptNode \"Pattern-1\")")
    print("      (VariableNode \"$conflict\")")
    print("      (ConceptNode \"RelationType-Conflict\"))))")
    print("```")
    
    print_subsection("Sample Relationship Definition")
    with open(rel_file, 'r') as f:
        lines = f.readlines()
    
    print("\nFirst 30 lines of relationship_types.scm:")
    for i, line in enumerate(lines[:30], 1):
        print(f"  {i:2d} | {line.rstrip()}")


def demo_usage_scenarios():
    """Demonstrate practical usage scenarios."""
    print_section("Practical Usage Scenarios")
    
    print_subsection("Scenario 1: Load Only What You Need")
    print("\nUse individual pattern files for targeted applications:")
    print("\n```scheme")
    print("; Load only the meta-pattern and a few specific patterns")
    print("(load \"opencog_atomese/patterns/pattern_000.scm\")")
    print("(load \"opencog_atomese/patterns/pattern_001.scm\")")
    print("(load \"opencog_atomese/patterns/pattern_007.scm\")")
    print("```")
    
    print_subsection("Scenario 2: Enhanced Pattern Discovery")
    print("\nUse enhanced properties to find patterns with specific characteristics:")
    print("\n```scheme")
    print("; Find all patterns that have diagram references")
    print("(GetLink")
    print("  (VariableNode \"$pattern\")")
    print("  (EvaluationLink")
    print("    (PredicateNode \"has-diagram\")")
    print("    (ListLink")
    print("      (VariableNode \"$pattern\")")
    print("      (VariableNode \"$diagram\"))))")
    print("```")
    
    print_subsection("Scenario 3: Intelligent Design Recommendations")
    print("\nUse relationship types to recommend patterns:")
    print("\n```scheme")
    print("; Given a pattern, find complementary patterns to suggest")
    print("; This can power an AI design assistant")
    print("(define (suggest-complements pattern)")
    print("  (GetLink")
    print("    (VariableNode \"$suggestion\")")
    print("    (EvaluationLink")
    print("      (PredicateNode \"has-relationship\")")
    print("      (ListLink")
    print("        pattern")
    print("        (VariableNode \"$suggestion\")")
    print("        (ConceptNode \"RelationType-Complement\")))))")
    print("```")


def demo_file_statistics():
    """Display statistics about generated files."""
    print_section("File Statistics")
    
    files = [
        ("Individual Patterns Dir", "opencog_atomese/patterns"),
        ("Enhanced Properties", "opencog_atomese/pattern_language_enhanced.scm"),
        ("Relationship Types", "opencog_atomese/relationship_types.scm"),
        ("Enhancements Docs", "opencog_atomese/ENHANCEMENTS.md"),
        ("Generator Script", "generate_enhanced_atomese.py"),
        ("Test Suite", "test_enhanced_atomese.py")
    ]
    
    print("\nGenerated Files:")
    print(f"{'File Description':<30} {'Path':<50} {'Size':>12}")
    print("-" * 95)
    
    total_size = 0
    for desc, path in files:
        p = Path(path)
        if p.is_file():
            size = p.stat().st_size
            total_size += size
            print(f"{desc:<30} {path:<50} {size:>10,} B")
        elif p.is_dir():
            dir_size = sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
            total_size += dir_size
            file_count = len(list(p.rglob('*.scm')))
            print(f"{desc:<30} {path:<50} {dir_size:>8,} B ({file_count} files)")
    
    print("-" * 95)
    print(f"{'Total':<30} {'':<50} {total_size:>10,} B")


def main():
    """Main demo entry point."""
    print("\n" + "=" * 70)
    print("  OpenCog Atomese Enhanced Features - Interactive Demo")
    print("=" * 70)
    
    print("\nThis demo showcases three future enhancements implemented:")
    print("  1. Individual pattern files (modular loading)")
    print("  2. Additional pattern properties (richer knowledge)")
    print("  3. Pattern relationship types (semantic connections)")
    
    demo_individual_pattern_files()
    demo_enhanced_properties()
    demo_relationship_types()
    demo_usage_scenarios()
    demo_file_statistics()
    
    print_section("Next Steps")
    print("\n1. Review the generated files:")
    print("   - opencog_atomese/patterns/")
    print("   - opencog_atomese/pattern_language_enhanced.scm")
    print("   - opencog_atomese/relationship_types.scm")
    print("   - opencog_atomese/ENHANCEMENTS.md")
    
    print("\n2. Run tests to validate:")
    print("   python3 test_enhanced_atomese.py")
    
    print("\n3. Load into OpenCog AtomSpace:")
    print("   (load \"opencog_atomese/pattern_language_enhanced.scm\")")
    print("   (load \"opencog_atomese/relationship_types.scm\")")
    
    print("\n4. Explore more enhancements:")
    print("   - See IMPLEMENTATION_SUMMARY.md for remaining extensions")
    print("   - PLN reasoning rules")
    print("   - Graph visualizations")
    print("   - Web query interface")
    
    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
