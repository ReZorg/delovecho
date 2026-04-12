#!/usr/bin/env python3
"""
Example queries on the Atomese Pattern Language using Python.

This demonstrates what queries would look like in OpenCog by parsing
the generated .scm files and showing the results. In a real OpenCog
system, these queries would be executed by the pattern matcher.
"""

import re
from pathlib import Path
from typing import List, Set, Dict


class AtomesePatternQuery:
    """Simple parser and query engine for Atomese patterns."""
    
    def __init__(self, atomese_dir: Path = Path("opencog_atomese")):
        """Initialize with the atomese directory."""
        self.atomese_dir = atomese_dir
        self.content = ""
        self._load_files()
    
    def _load_files(self):
        """Load all .scm files."""
        scm_file = self.atomese_dir / "pattern_language.scm"
        if scm_file.exists():
            with open(scm_file, 'r') as f:
                self.content = f.read()
    
    def get_patterns_in_category(self, category: str) -> List[str]:
        """Find all patterns that inherit from a category."""
        pattern = rf'\(InheritanceLink\s+\(ConceptNode "Pattern-(\d+)(?:[^"]*)?"\)\s+\(ConceptNode "Category-{category}"\)'
        matches = re.findall(pattern, self.content)
        return sorted(set(matches), key=int)
    
    def get_patterns_in_sequence(self, sequence_id: int) -> List[str]:
        """Find all patterns in a specific sequence."""
        pattern = rf'\(MemberLink\s+\(ConceptNode "Pattern-(\d+)(?:[^"]*)?"\)\s+\(ConceptNode "Sequence-{sequence_id}-'
        matches = re.findall(pattern, self.content)
        return sorted(set(matches), key=int)
    
    def get_pattern_property(self, pattern_num: int, property_name: str) -> str:
        """Get a specific property of a pattern."""
        # Match EvaluationLink with the property
        pattern = rf'\(EvaluationLink\s+\(PredicateNode "{property_name}"\)\s+\(ListLink\s+\(ConceptNode "Pattern-{pattern_num}[^"]*"\)\s+\(ConceptNode "([^"]*)"\)'
        match = re.search(pattern, self.content, re.DOTALL)
        return match.group(1) if match else ""
    
    def get_sequences_in_category(self, category: str) -> List[Dict[str, str]]:
        """Find all sequences in a category."""
        pattern = rf'\(InheritanceLink\s+\(ConceptNode "Sequence-(\d+)-([^"]+)"\)\s+\(ConceptNode "Category-{category}"\)'
        matches = re.findall(pattern, self.content)
        return [{"id": m[0], "heading": m[1]} for m in matches]
    
    def get_pattern_following_from(self, pattern_num: int) -> List[str]:
        """Find patterns that follow from a given pattern."""
        pattern = rf'\(ImplicationLink\s+\(ConceptNode "Pattern-{pattern_num}[^"]*"\)\s+\(ConceptNode "Pattern-(\d+)'
        matches = re.findall(pattern, self.content)
        return sorted(set(matches), key=int)


def demo_query_patterns_by_category():
    """Demo: Query patterns by category."""
    print("\n" + "="*70)
    print("DEMO 1: Query Patterns by Category")
    print("="*70)
    
    query = AtomesePatternQuery()
    
    for category in ["Towns", "Buildings", "Construction"]:
        patterns = query.get_patterns_in_category(category)
        print(f"\n{category} Category:")
        print(f"  Found {len(patterns)} patterns")
        print(f"  Range: Pattern-{patterns[0]} to Pattern-{patterns[-1]}")
        print(f"  First 5: {', '.join(patterns[:5])}")


def demo_query_sequence_patterns():
    """Demo: Query patterns in specific sequences."""
    print("\n" + "="*70)
    print("DEMO 2: Query Patterns in Sequences")
    print("="*70)
    
    query = AtomesePatternQuery()
    
    sequences_to_check = [1, 7, 20, 36]
    
    for seq_id in sequences_to_check:
        patterns = query.get_patterns_in_sequence(seq_id)
        print(f"\nSequence {seq_id}:")
        print(f"  Patterns: {', '.join(patterns)}")


def demo_query_pattern_properties():
    """Demo: Query specific pattern properties."""
    print("\n" + "="*70)
    print("DEMO 3: Query Pattern Properties")
    print("="*70)
    
    query = AtomesePatternQuery()
    
    # Query meta-pattern
    pattern_num = 0
    print(f"\nPattern-{pattern_num} properties:")
    
    name = query.get_pattern_property(pattern_num, "has-name")
    print(f"  Name: {name}")
    
    problem = query.get_pattern_property(pattern_num, "has-problem-summary")
    print(f"  Problem: {problem[:80]}..." if len(problem) > 80 else f"  Problem: {problem}")
    
    solution = query.get_pattern_property(pattern_num, "has-solution")
    print(f"  Solution: {solution[:80]}..." if len(solution) > 80 else f"  Solution: {solution}")


def demo_query_sequences_by_category():
    """Demo: Query sequences grouped by category."""
    print("\n" + "="*70)
    print("DEMO 4: Query Sequences by Category")
    print("="*70)
    
    query = AtomesePatternQuery()
    
    for category in ["Towns", "Buildings", "Construction"]:
        sequences = query.get_sequences_in_category(category)
        print(f"\n{category} Sequences ({len(sequences)} total):")
        for seq in sequences[:3]:  # Show first 3
            print(f"  Sequence-{seq['id']}: {seq['heading']}")
        if len(sequences) > 3:
            print(f"  ... and {len(sequences) - 3} more")


def demo_query_pattern_implications():
    """Demo: Query pattern dependencies."""
    print("\n" + "="*70)
    print("DEMO 5: Query Pattern Dependencies (ImplicationLinks)")
    print("="*70)
    
    query = AtomesePatternQuery()
    
    # Query what patterns follow from the meta-pattern
    pattern_num = 0
    following = query.get_pattern_following_from(pattern_num)
    
    print(f"\nPattern-{pattern_num} implies {len(following)} patterns:")
    print(f"  First 10: {', '.join(following[:10])}")
    print(f"  Last 10: {', '.join(following[-10:])}")


def demo_combined_query():
    """Demo: Combined query showing the power of the hypergraph."""
    print("\n" + "="*70)
    print("DEMO 6: Combined Query - Towns Local Centers Sequence")
    print("="*70)
    
    query = AtomesePatternQuery()
    
    # Find "Local centers" sequence in Towns
    sequences = query.get_sequences_in_category("Towns")
    local_centers = [s for s in sequences if "Local centers" in s["heading"]]
    
    if local_centers:
        seq = local_centers[0]
        print(f"\nSequence: {seq['heading']} (ID: {seq['id']})")
        
        # Get patterns in this sequence
        patterns = query.get_patterns_in_sequence(int(seq['id']))
        print(f"Patterns in sequence: {', '.join(patterns)}")
        
        # Get properties of first pattern in sequence
        if patterns:
            first_pattern = int(patterns[0])
            name = query.get_pattern_property(first_pattern, "has-name")
            print(f"\nFirst pattern details:")
            print(f"  Pattern-{first_pattern}: {name}")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("OpenCog Atomese Pattern Language - Query Examples")
    print("="*70)
    print("\nThese examples demonstrate pattern matching queries that would")
    print("be executed in OpenCog's AtomSpace. The queries are simulated here")
    print("using Python regex parsing of the generated .scm files.")
    
    demo_query_patterns_by_category()
    demo_query_sequence_patterns()
    demo_query_pattern_properties()
    demo_query_sequences_by_category()
    demo_query_pattern_implications()
    demo_combined_query()
    
    print("\n" + "="*70)
    print("Query Examples Complete")
    print("="*70)
    print("\nIn a real OpenCog system, these queries would be executed using")
    print("the pattern matcher on the AtomSpace hypergraph, enabling:")
    print("  • Reasoning and inference")
    print("  • Graph traversal and exploration")
    print("  • Pattern discovery and recommendation")
    print("  • Knowledge graph analytics")
    print()


if __name__ == "__main__":
    main()
