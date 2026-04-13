#!/usr/bin/env python3
"""
Demo script showing OpenCog Atomese Pattern Language features.

This script demonstrates the generated Atomese files and shows example
pattern matching queries that could be used in OpenCog.
"""

from pathlib import Path
import re


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def show_file_statistics():
    """Display statistics about the generated Atomese files."""
    print_header("Atomese Files Statistics")
    
    atomese_dir = Path("opencog_atomese")
    if not atomese_dir.exists():
        print("❌ opencog_atomese/ directory not found")
        print("Run: python3 generate_opencog_atomese.py")
        return
    
    scm_files = list(atomese_dir.glob("*.scm"))
    
    for scm_file in sorted(scm_files):
        with open(scm_file, 'r') as f:
            content = f.read()
            lines = len(content.split('\n'))
            
            # Count different node types
            concept_nodes = len(re.findall(r'\(ConceptNode', content))
            predicate_nodes = len(re.findall(r'\(PredicateNode', content))
            
            # Count different link types
            eval_links = len(re.findall(r'\(EvaluationLink', content))
            inherit_links = len(re.findall(r'\(InheritanceLink', content))
            member_links = len(re.findall(r'\(MemberLink', content))
            implication_links = len(re.findall(r'\(ImplicationLink', content))
            
            print(f"\n📄 {scm_file.name}")
            print(f"   Lines: {lines:,}")
            print(f"   ConceptNodes: {concept_nodes:,}")
            print(f"   PredicateNodes: {predicate_nodes:,}")
            print(f"   Links: EvaluationLink({eval_links}), InheritanceLink({inherit_links}), "
                  f"MemberLink({member_links}), ImplicationLink({implication_links})")


def show_atomese_examples():
    """Show examples of Atomese patterns from the generated files."""
    print_header("Atomese Structure Examples")
    
    atomese_dir = Path("opencog_atomese")
    
    # Show meta-pattern example
    print("\n🏛️  Meta-Pattern Example (Pattern-0-Pattern Language):")
    print("-" * 60)
    meta_file = atomese_dir / "meta_pattern.scm"
    if meta_file.exists():
        with open(meta_file, 'r') as f:
            lines = f.readlines()
            # Show first 30 lines
            for line in lines[:30]:
                print(line.rstrip())
    
    # Show category example
    print("\n\n🏘️  Category Example (Category-Towns):")
    print("-" * 60)
    cat_file = atomese_dir / "categories.scm"
    if cat_file.exists():
        with open(cat_file, 'r') as f:
            lines = f.readlines()
            # Show first 40 lines
            for line in lines[:40]:
                print(line.rstrip())
    
    # Show sequence example
    print("\n\n📝 Sequence Example (Sequence-1):")
    print("-" * 60)
    seq_file = atomese_dir / "sequences.scm"
    if seq_file.exists():
        with open(seq_file, 'r') as f:
            lines = f.readlines()
            # Show first 40 lines
            for line in lines[:40]:
                print(line.rstrip())


def show_pattern_matching_queries():
    """Display example pattern matching queries for OpenCog."""
    print_header("Pattern Matching Query Examples")
    
    queries = [
        {
            "title": "Find all patterns in the Towns category",
            "description": "Query to retrieve all patterns that inherit from Category-Towns",
            "query": """(GetLink
  (VariableNode "$pattern")
  (InheritanceLink
    (VariableNode "$pattern")
    (ConceptNode "Category-Towns")))"""
        },
        {
            "title": "Find patterns in a specific sequence",
            "description": "Query to find all patterns that are members of Sequence-7 (Local centers)",
            "query": """(GetLink
  (VariableNode "$pattern")
  (MemberLink
    (VariableNode "$pattern")
    (ConceptNode "Sequence-7-Local centers")))"""
        },
        {
            "title": "Find patterns that follow from Pattern-0",
            "description": "Query to discover all patterns implied by the meta-pattern",
            "query": """(GetLink
  (VariableNode "$next")
  (ImplicationLink
    (ConceptNode "Pattern-0-Pattern Language")
    (VariableNode "$next")))"""
        },
        {
            "title": "Find pattern properties",
            "description": "Query to retrieve the solution for a specific pattern",
            "query": """(GetLink
  (VariableNode "$solution")
  (EvaluationLink
    (PredicateNode "has-solution")
    (ListLink
      (ConceptNode "Pattern-0-Pattern Language")
      (VariableNode "$solution"))))"""
        },
        {
            "title": "Find sequences by category",
            "description": "Query to find all sequences in the Buildings category",
            "query": """(GetLink
  (VariableNode "$sequence")
  (InheritanceLink
    (VariableNode "$sequence")
    (ConceptNode "Category-Buildings")))"""
        },
        {
            "title": "Find sequences with specific emergent phenomena",
            "description": "Query to find sequences based on their emergent phenomena descriptions",
            "query": """(GetLink
  (TypedVariableLink
    (VariableNode "$sequence")
    (TypeNode "ConceptNode"))
  (EvaluationLink
    (PredicateNode "has-emergent-phenomena")
    (ListLink
      (VariableNode "$sequence")
      (VariableNode "$phenomena"))))"""
        }
    ]
    
    for i, query_info in enumerate(queries, 1):
        print(f"\n{i}. {query_info['title']}")
        print(f"   {query_info['description']}")
        print("\n   ```scheme")
        for line in query_info['query'].split('\n'):
            print(f"   {line}")
        print("   ```")


def show_use_cases():
    """Display use cases for the Atomese Pattern Language."""
    print_header("Use Cases for OpenCog Atomese Pattern Language")
    
    use_cases = [
        {
            "title": "🔍 Pattern Discovery",
            "description": "Query patterns by properties, categories, or relationships to discover relevant design patterns for a specific problem domain."
        },
        {
            "title": "🧠 Reasoning and Inference",
            "description": "Use OpenCog's reasoning engines to infer pattern relationships, dependencies, and applicable sequences for a design problem."
        },
        {
            "title": "🌐 Knowledge Graph Navigation",
            "description": "Traverse the pattern hypergraph to explore related patterns, emergent phenomena, and design sequences."
        },
        {
            "title": "🤖 AI/AGI Integration",
            "description": "Integrate pattern language knowledge into AI systems for automated design assistance, pattern recommendation, and problem-solving."
        },
        {
            "title": "📊 Pattern Analytics",
            "description": "Analyze pattern usage, relationships, and effectiveness using graph algorithms and machine learning."
        },
        {
            "title": "🔗 Cross-Domain Mapping",
            "description": "Map patterns across different domains (architecture, software, organization) by analyzing structural similarities in the hypergraph."
        }
    ]
    
    for use_case in use_cases:
        print(f"\n{use_case['title']}")
        print(f"  {use_case['description']}")


def show_loading_instructions():
    """Display instructions for loading into OpenCog."""
    print_header("Loading into OpenCog AtomSpace")
    
    print("""
To use these Atomese files in OpenCog, you need to:

1. Install OpenCog:
   - Follow instructions at: https://github.com/opencog/atomspace
   - Or use Docker: docker pull opencog/opencog-dev

2. Start an OpenCog Scheme REPL:
   $ guile
   
3. Load the OpenCog modules:
   scheme@(guile-user)> (use-modules (opencog))
   scheme@(guile-user)> (use-modules (opencog exec))
   
4. Load the Pattern Language:
   scheme@(guile-user)> (load "opencog_atomese/pattern_language.scm")
   
5. Query patterns:
   scheme@(guile-user)> (cog-execute! 
                          (GetLink
                            (VariableNode "$pattern")
                            (InheritanceLink
                              (VariableNode "$pattern")
                              (ConceptNode "Category-Towns"))))

This will return a SetLink containing all patterns in the Towns category.

For more advanced queries, use the pattern matcher documentation:
https://wiki.opencog.org/w/Pattern_Matcher
    """)


def main():
    """Run the demonstration."""
    print("\n🏛️  OpenCog Atomese Pattern Language Demo")
    print("Christopher Alexander's 'A Pattern Language' in hypergraph format")
    
    show_file_statistics()
    show_atomese_examples()
    show_pattern_matching_queries()
    show_use_cases()
    show_loading_instructions()
    
    print("\n" + "="*60)
    print("  Demo Complete")
    print("="*60)
    print("\nFor more information, see:")
    print("  • opencog_atomese/README.md - Detailed documentation")
    print("  • https://opencog.org - OpenCog project")
    print("  • https://wiki.opencog.org/w/Atomese - Atomese documentation")
    print()


if __name__ == "__main__":
    main()
