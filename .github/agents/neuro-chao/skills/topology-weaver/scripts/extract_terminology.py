#!/usr/bin/env python3
"""
Terminology Extractor for Topology Weaver
Extracts key terms, relations, and semantic clusters from source context.
"""

import sys
import json
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional


@dataclass
class Term:
    """A terminology term with metadata."""
    name: str
    category: str  # noun, verb, adjective, concept
    frequency: int
    context_snippets: List[str]
    related_terms: List[str]


@dataclass
class Relation:
    """A relation between terms."""
    source: str
    target: str
    relation_type: str  # is_a, has_a, acts_on, transforms_to, etc.
    evidence: str


@dataclass
class SemanticCluster:
    """A cluster of semantically related terms."""
    name: str
    terms: List[str]
    central_concept: str
    architectural_mapping: Optional[str] = None


class TerminologyExtractor:
    """Extract terminology from source context."""
    
    # Patterns for identifying key architectural concepts
    CONCEPT_PATTERNS = {
        'particle': r'\b(particle|point|discrete|local|unit|neuron|feature)\b',
        'wave': r'\b(wave|field|distributed|continuous|pattern|activation)\b',
        'transformation': r'\b(transform|project|map|convert|evolve|propagate)\b',
        'interaction': r'\b(interact|couple|interfere|combine|merge|mix)\b',
        'measurement': r'\b(measure|collapse|sample|select|gate|threshold)\b',
        'state': r'\b(state|configuration|representation|embedding|hidden)\b',
        'flow': r'\b(flow|stream|pass|forward|backward|residual)\b',
        'composition': r'\b(compose|nest|stack|layer|hierarchy|level)\b',
    }
    
    # Relation patterns
    RELATION_PATTERNS = [
        (r'(\w+)\s+(?:is|are)\s+(?:a|an)\s+(\w+)', 'is_a'),
        (r'(\w+)\s+(?:has|have|contains?)\s+(\w+)', 'has_a'),
        (r'(\w+)\s+(?:acts?\s+on|affects?|modifies?)\s+(\w+)', 'acts_on'),
        (r'(\w+)\s+(?:becomes?|transforms?\s+(?:to|into))\s+(\w+)', 'transforms_to'),
        (r'(\w+)\s+(?:connects?\s+to|links?\s+to)\s+(\w+)', 'connects_to'),
        (r'(\w+)\s+→\s+(\w+)', 'maps_to'),
    ]
    
    def __init__(self):
        self.terms: Dict[str, Term] = {}
        self.relations: List[Relation] = []
        self.clusters: List[SemanticCluster] = []
    
    def extract_from_file(self, filepath: str) -> dict:
        """Extract terminology from a file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        content = path.read_text()
        return self.extract_from_text(content)
    
    def extract_from_text(self, text: str) -> dict:
        """Extract terminology from text content."""
        # Normalize text
        text_lower = text.lower()
        sentences = self._split_sentences(text)
        
        # Extract terms by category
        self._extract_concept_terms(text_lower, sentences)
        
        # Extract relations
        self._extract_relations(text)
        
        # Build semantic clusters
        self._build_clusters()
        
        # Suggest architectural mappings
        self._suggest_mappings()
        
        return self._to_dict()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        return re.split(r'[.!?]+', text)
    
    def _extract_concept_terms(self, text: str, sentences: List[str]):
        """Extract terms matching concept patterns."""
        for category, pattern in self.CONCEPT_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                term_name = match.lower()
                if term_name not in self.terms:
                    # Find context snippets
                    snippets = [s.strip() for s in sentences 
                               if term_name in s.lower()][:3]
                    
                    self.terms[term_name] = Term(
                        name=term_name,
                        category=category,
                        frequency=text.count(term_name),
                        context_snippets=snippets,
                        related_terms=[]
                    )
                else:
                    self.terms[term_name].frequency += 1
    
    def _extract_relations(self, text: str):
        """Extract relations between terms."""
        for pattern, rel_type in self.RELATION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                source, target = match[0].lower(), match[1].lower()
                if source in self.terms or target in self.terms:
                    self.relations.append(Relation(
                        source=source,
                        target=target,
                        relation_type=rel_type,
                        evidence=f"Pattern: {pattern}"
                    ))
                    
                    # Update related terms
                    if source in self.terms:
                        if target not in self.terms[source].related_terms:
                            self.terms[source].related_terms.append(target)
                    if target in self.terms:
                        if source not in self.terms[target].related_terms:
                            self.terms[target].related_terms.append(source)
    
    def _build_clusters(self):
        """Build semantic clusters from terms and relations."""
        # Group by category
        category_groups = defaultdict(list)
        for term in self.terms.values():
            category_groups[term.category].append(term.name)
        
        # Create clusters
        for category, terms in category_groups.items():
            if len(terms) >= 2:
                # Find most frequent term as central concept
                central = max(terms, key=lambda t: self.terms[t].frequency)
                self.clusters.append(SemanticCluster(
                    name=f"{category}_cluster",
                    terms=terms,
                    central_concept=central
                ))
    
    def _suggest_mappings(self):
        """Suggest architectural mappings for clusters."""
        mapping_suggestions = {
            'particle': 'mlp_neuron',
            'wave': 'attention_pattern',
            'transformation': 'linear_projection',
            'interaction': 'weight_matrix',
            'measurement': 'activation_function',
            'state': 'hidden_state',
            'flow': 'residual_stream',
            'composition': 'layer_stack',
        }
        
        for cluster in self.clusters:
            category = cluster.name.replace('_cluster', '')
            if category in mapping_suggestions:
                cluster.architectural_mapping = mapping_suggestions[category]
    
    def _to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            'terms': {k: asdict(v) for k, v in self.terms.items()},
            'relations': [asdict(r) for r in self.relations],
            'clusters': [asdict(c) for c in self.clusters],
            'summary': {
                'total_terms': len(self.terms),
                'total_relations': len(self.relations),
                'total_clusters': len(self.clusters),
                'categories': list(set(t.category for t in self.terms.values()))
            }
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_terminology.py <context_file> [output_file]")
        print("\nExtracts terminology from source context for topology generation.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "terminology.json"
    
    extractor = TerminologyExtractor()
    
    try:
        result = extractor.extract_from_file(input_file)
        
        # Write output
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✓ Extracted {result['summary']['total_terms']} terms")
        print(f"✓ Found {result['summary']['total_relations']} relations")
        print(f"✓ Built {result['summary']['total_clusters']} semantic clusters")
        print(f"✓ Output written to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
