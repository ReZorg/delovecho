#!/usr/bin/env python3
"""
Generate OpenCog Atomese representation of Pattern Language.

This script converts the Pattern Language JSON schema into OpenCog's Atomese format,
which represents knowledge as a hypergraph using Scheme syntax.

Atomese uses:
- ConceptNode: Represents concepts (patterns, categories)
- PredicateNode: Represents relationships and properties
- ListLink: Ordered collections
- InheritanceLink: Category/subcategory relationships
- EvaluationLink: Property assertions
- ImplicationLink: Pattern dependencies and sequences
"""

import json
from pathlib import Path
from typing import Dict, List, Any, TextIO


def escape_string(s: str) -> str:
    """Escape a string for use in Atomese."""
    # Escape backslashes first, then quotes
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def write_concept_node(f: TextIO, name: str, indent: int = 0) -> None:
    """Write a ConceptNode to the file."""
    prefix = "  " * indent
    f.write(f'{prefix}(ConceptNode "{escape_string(name)}")\n')


def write_predicate_node(f: TextIO, name: str, indent: int = 0) -> None:
    """Write a PredicateNode to the file."""
    prefix = "  " * indent
    f.write(f'{prefix}(PredicateNode "{escape_string(name)}")\n')


def write_evaluation_link(f: TextIO, predicate: str, concept: str, value: str, indent: int = 0) -> None:
    """Write an EvaluationLink for a property assertion."""
    prefix = "  " * indent
    f.write(f'{prefix}(EvaluationLink\n')
    write_predicate_node(f, predicate, indent + 1)
    f.write(f'{prefix}  (ListLink\n')
    write_concept_node(f, concept, indent + 2)
    write_concept_node(f, value, indent + 2)
    f.write(f'{prefix}  )\n')
    f.write(f'{prefix})\n')


def write_pattern_to_atomese(f: TextIO, pattern: Dict[str, Any]) -> None:
    """Convert a single pattern to Atomese representation."""
    pattern_name = f"Pattern-{pattern['number']}-{pattern['name']}"
    
    # Create the pattern concept
    f.write(f'; Pattern {pattern["number"]}: {pattern["name"]}\n')
    write_concept_node(f, pattern_name, 0)
    f.write('\n')
    
    # Add pattern number
    write_evaluation_link(f, "has-number", pattern_name, str(pattern['number']), 0)
    f.write('\n')
    
    # Add pattern name
    write_evaluation_link(f, "has-name", pattern_name, pattern['name'], 0)
    f.write('\n')
    
    # Add asterisks (evidence level)
    if 'asterisks' in pattern:
        write_evaluation_link(f, "has-evidence-level", pattern_name, str(pattern['asterisks']), 0)
        f.write('\n')
    
    # Add problem summary
    if 'problem_summary' in pattern:
        f.write('(EvaluationLink\n')
        write_predicate_node(f, "has-problem-summary", 1)
        f.write('  (ListLink\n')
        write_concept_node(f, pattern_name, 2)
        f.write(f'    (ConceptNode "{escape_string(pattern["problem_summary"])}")\n')
        f.write('  )\n')
        f.write(')\n\n')
    
    # Add solution
    if 'solution' in pattern:
        f.write('(EvaluationLink\n')
        write_predicate_node(f, "has-solution", 1)
        f.write('  (ListLink\n')
        write_concept_node(f, pattern_name, 2)
        f.write(f'    (ConceptNode "{escape_string(pattern["solution"])}")\n')
        f.write('  )\n')
        f.write(')\n\n')
    
    # Add context
    if 'context' in pattern:
        f.write('(EvaluationLink\n')
        write_predicate_node(f, "has-context", 1)
        f.write('  (ListLink\n')
        write_concept_node(f, pattern_name, 2)
        f.write(f'    (ConceptNode "{escape_string(pattern["context"])}")\n')
        f.write('  )\n')
        f.write(')\n\n')
    
    # Add pattern dependencies (preceding patterns)
    if 'preceding_patterns' in pattern and pattern['preceding_patterns']:
        for preceding in pattern['preceding_patterns']:
            f.write('(ImplicationLink\n')
            write_concept_node(f, f"Pattern-{preceding}", 1)
            write_concept_node(f, pattern_name, 1)
            f.write(')\n\n')
    
    # Add pattern relationships (following patterns)
    if 'following_patterns' in pattern and pattern['following_patterns']:
        for following in pattern['following_patterns']:
            f.write('(ImplicationLink\n')
            write_concept_node(f, pattern_name, 1)
            write_concept_node(f, f"Pattern-{following}", 1)
            f.write(')\n\n')


def write_category_to_atomese(f: TextIO, category: Dict[str, Any]) -> None:
    """Convert a category to Atomese representation."""
    category_name = f"Category-{category['name']}"
    
    f.write(f'; Category: {category["name"]}\n')
    write_concept_node(f, category_name, 0)
    f.write('\n')
    
    # Add category description
    if 'description' in category:
        f.write('(EvaluationLink\n')
        write_predicate_node(f, "has-description", 1)
        f.write('  (ListLink\n')
        write_concept_node(f, category_name, 2)
        f.write(f'    (ConceptNode "{escape_string(category["description"])}")\n')
        f.write('  )\n')
        f.write(')\n\n')
    
    # Add category process
    if 'process' in category:
        f.write('(EvaluationLink\n')
        write_predicate_node(f, "has-process", 1)
        f.write('  (ListLink\n')
        write_concept_node(f, category_name, 2)
        f.write(f'    (ConceptNode "{escape_string(category["process"])}")\n')
        f.write('  )\n')
        f.write(')\n\n')
    
    # Add pattern range
    if 'pattern_range' in category:
        pattern_range = category['pattern_range']
        write_evaluation_link(f, "has-pattern-range-start", category_name, 
                            str(pattern_range['start']), 0)
        f.write('\n')
        write_evaluation_link(f, "has-pattern-range-end", category_name, 
                            str(pattern_range['end']), 0)
        f.write('\n')
    
    # Link patterns to category
    if 'pattern_range' in category:
        start = category['pattern_range']['start']
        end = category['pattern_range']['end']
        for pattern_num in range(start, end + 1):
            f.write('(InheritanceLink\n')
            write_concept_node(f, f"Pattern-{pattern_num}", 1)
            write_concept_node(f, category_name, 1)
            f.write(')\n')
        f.write('\n')


def write_sequence_to_atomese(f: TextIO, sequence: Dict[str, Any]) -> None:
    """Convert a pattern sequence to Atomese representation."""
    sequence_name = f"Sequence-{sequence['id']}-{sequence['heading']}"
    
    f.write(f'; Sequence {sequence["id"]}: {sequence["heading"]}\n')
    write_concept_node(f, sequence_name, 0)
    f.write('\n')
    
    # Add sequence ID
    write_evaluation_link(f, "has-sequence-id", sequence_name, str(sequence['id']), 0)
    f.write('\n')
    
    # Add sequence heading
    if 'heading' in sequence:
        f.write('(EvaluationLink\n')
        write_predicate_node(f, "has-heading", 1)
        f.write('  (ListLink\n')
        write_concept_node(f, sequence_name, 2)
        f.write(f'    (ConceptNode "{escape_string(sequence["heading"])}")\n')
        f.write('  )\n')
        f.write(')\n\n')
    
    # Add emergent phenomena
    if 'emergent_phenomena' in sequence:
        f.write('(EvaluationLink\n')
        write_predicate_node(f, "has-emergent-phenomena", 1)
        f.write('  (ListLink\n')
        write_concept_node(f, sequence_name, 2)
        f.write(f'    (ConceptNode "{escape_string(sequence["emergent_phenomena"])}")\n')
        f.write('  )\n')
        f.write(')\n\n')
    
    # Add category membership
    if 'category' in sequence:
        f.write('(InheritanceLink\n')
        write_concept_node(f, sequence_name, 1)
        write_concept_node(f, f"Category-{sequence['category']}", 1)
        f.write(')\n\n')
    
    # Link patterns in sequence
    if 'patterns' in sequence:
        for pattern_num in sequence['patterns']:
            f.write('(MemberLink\n')
            write_concept_node(f, f"Pattern-{pattern_num}", 1)
            write_concept_node(f, sequence_name, 1)
            f.write(')\n')
        f.write('\n')


def generate_atomese_from_json() -> None:
    """Generate Atomese .scm files from the JSON pattern language schema."""
    
    print("Generating OpenCog Atomese representation from Pattern Language...")
    
    # Load the pattern language JSON
    pattern_lang_file = Path("pattern_language_generated.json")
    if not pattern_lang_file.exists():
        print("Error: pattern_language_generated.json not found")
        print("Run 'python3 generate_pattern_schema.py' first")
        return
    
    with open(pattern_lang_file) as f:
        pattern_language = json.load(f)
    
    # Create output directory
    output_dir = Path("opencog_atomese")
    output_dir.mkdir(exist_ok=True)
    
    # Generate meta-pattern file
    print("Generating meta-pattern...")
    with open(output_dir / "meta_pattern.scm", 'w', encoding='utf-8') as f:
        f.write('; OpenCog Atomese representation of Pattern Language Meta-Pattern\n')
        f.write('; Generated from pattern_language_generated.json\n\n')
        write_pattern_to_atomese(f, pattern_language['meta_pattern'])
    
    # Generate categories file
    print("Generating categories...")
    with open(output_dir / "categories.scm", 'w', encoding='utf-8') as f:
        f.write('; OpenCog Atomese representation of Pattern Language Categories\n')
        f.write('; Generated from pattern_language_generated.json\n\n')
        for category in pattern_language['categories']:
            write_category_to_atomese(f, category)
            f.write('\n')
    
    # Generate sequences file
    print("Generating sequences...")
    with open(output_dir / "sequences.scm", 'w', encoding='utf-8') as f:
        f.write('; OpenCog Atomese representation of Pattern Language Sequences\n')
        f.write('; Generated from pattern_language_generated.json\n\n')
        for sequence in pattern_language['sequences']:
            write_sequence_to_atomese(f, sequence)
            f.write('\n')
    
    # Generate combined file
    print("Generating combined pattern_language.scm...")
    with open(output_dir / "pattern_language.scm", 'w', encoding='utf-8') as f:
        f.write('; OpenCog Atomese representation of Christopher Alexander\'s Pattern Language\n')
        f.write('; Complete hypergraph representation for pattern matching and reasoning\n')
        f.write('; Generated from pattern_language_generated.json\n\n')
        
        f.write('; === META-PATTERN ===\n\n')
        write_pattern_to_atomese(f, pattern_language['meta_pattern'])
        f.write('\n')
        
        f.write('; === CATEGORIES ===\n\n')
        for category in pattern_language['categories']:
            write_category_to_atomese(f, category)
            f.write('\n')
        
        f.write('; === SEQUENCES ===\n\n')
        for sequence in pattern_language['sequences']:
            write_sequence_to_atomese(f, sequence)
            f.write('\n')
    
    # Generate README for the atomese directory
    with open(output_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write("# OpenCog Atomese Pattern Language\n\n")
        f.write("This directory contains OpenCog Atomese representations of Christopher Alexander's ")
        f.write("\"A Pattern Language\" converted from the JSON schema.\n\n")
        f.write("## Files\n\n")
        f.write("- `pattern_language.scm` - Complete Atomese representation (all patterns, categories, sequences)\n")
        f.write("- `meta_pattern.scm` - The Pattern Language meta-pattern\n")
        f.write("- `categories.scm` - The three categories (Towns, Buildings, Construction)\n")
        f.write("- `sequences.scm` - All 36 pattern sequences\n\n")
        f.write("## Atomese Structure\n\n")
        f.write("### Node Types\n\n")
        f.write("- **ConceptNode**: Represents patterns, categories, sequences, and values\n")
        f.write("- **PredicateNode**: Represents relationships and properties\n\n")
        f.write("### Link Types\n\n")
        f.write("- **EvaluationLink**: Property assertions (e.g., has-name, has-problem-summary)\n")
        f.write("- **InheritanceLink**: Category memberships (pattern belongs to category)\n")
        f.write("- **ImplicationLink**: Pattern dependencies (preceding/following patterns)\n")
        f.write("- **MemberLink**: Sequence membership (pattern belongs to sequence)\n")
        f.write("- **ListLink**: Ordered collections for EvaluationLink arguments\n\n")
        f.write("## Usage with OpenCog\n\n")
        f.write("Load these files into an OpenCog AtomSpace:\n\n")
        f.write("```scheme\n")
        f.write("(load \"pattern_language.scm\")\n")
        f.write("```\n\n")
        f.write("Or load individual components:\n\n")
        f.write("```scheme\n")
        f.write("(load \"meta_pattern.scm\")\n")
        f.write("(load \"categories.scm\")\n")
        f.write("(load \"sequences.scm\")\n")
        f.write("```\n\n")
        f.write("## Pattern Matching Examples\n\n")
        f.write("Query patterns by category:\n\n")
        f.write("```scheme\n")
        f.write("(GetLink\n")
        f.write("  (VariableNode \"$pattern\")\n")
        f.write("  (InheritanceLink\n")
        f.write("    (VariableNode \"$pattern\")\n")
        f.write("    (ConceptNode \"Category-Towns\")))\n")
        f.write("```\n\n")
        f.write("Query patterns in a sequence:\n\n")
        f.write("```scheme\n")
        f.write("(GetLink\n")
        f.write("  (VariableNode \"$pattern\")\n")
        f.write("  (MemberLink\n")
        f.write("    (VariableNode \"$pattern\")\n")
        f.write("    (ConceptNode \"Sequence-1-Regions instead of countries\")))\n")
        f.write("```\n\n")
        f.write("Find pattern dependencies:\n\n")
        f.write("```scheme\n")
        f.write("(GetLink\n")
        f.write("  (VariableNode \"$next\")\n")
        f.write("  (ImplicationLink\n")
        f.write("    (ConceptNode \"Pattern-0-Pattern Language\")\n")
        f.write("    (VariableNode \"$next\")))\n")
        f.write("```\n\n")
        f.write("## Hypergraph Properties\n\n")
        f.write("The Atomese representation creates a knowledge hypergraph where:\n\n")
        f.write("- Patterns are interconnected through ImplicationLinks (dependencies)\n")
        f.write("- Categories organize patterns hierarchically via InheritanceLinks\n")
        f.write("- Sequences group related patterns via MemberLinks\n")
        f.write("- Properties are attached via EvaluationLinks\n")
        f.write("- The structure supports pattern matching, reasoning, and inference\n\n")
        f.write("This enables OpenCog to:\n")
        f.write("- Query patterns by properties, relationships, or context\n")
        f.write("- Infer pattern dependencies and sequences\n")
        f.write("- Reason about design problems and solutions\n")
        f.write("- Navigate the pattern network for design guidance\n")
    
    print(f"\n✅ Generated OpenCog Atomese files in '{output_dir}/':")
    print(f"   - pattern_language.scm (complete)")
    print(f"   - meta_pattern.scm")
    print(f"   - categories.scm")
    print(f"   - sequences.scm")
    print(f"   - README.md")
    print(f"\nFiles can be loaded into OpenCog AtomSpace for pattern matching and reasoning.")


def main():
    """Main entry point."""
    generate_atomese_from_json()


if __name__ == "__main__":
    main()
