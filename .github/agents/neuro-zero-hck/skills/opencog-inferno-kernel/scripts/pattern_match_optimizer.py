#!/usr/bin/env python3
"""
Pattern Matching Optimization Script
Analyzes and optimizes pattern matching queries for the AtomSpace
"""

import sys
import json
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from enum import Enum


class PatternType(Enum):
    """Types of pattern matching queries"""
    EXACT = "exact"           # Exact atom match
    TYPE = "type"             # Match by atom type
    VARIABLE = "variable"     # Contains variables
    RECURSIVE = "recursive"   # Recursive pattern
    COMPLEX = "complex"       # Multiple constraints


@dataclass
class PatternQuery:
    """Represents a pattern matching query"""
    query_id: str
    pattern: str
    variables: List[str]
    constraints: List[str]
    estimated_matches: int = 0


class PatternOptimizer:
    """Optimizes pattern matching queries"""
    
    def __init__(self):
        self.query_cache: Dict[str, Any] = {}
        self.index_hints: Dict[str, str] = {}
    
    def analyze_pattern(self, query: PatternQuery) -> Dict[str, Any]:
        """Analyze a pattern query and suggest optimizations"""
        
        analysis = {
            "query_id": query.query_id,
            "pattern_type": self._classify_pattern(query),
            "complexity": self._calculate_complexity(query),
            "optimizations": [],
            "index_suggestions": []
        }
        
        # Suggest optimizations based on pattern type
        if len(query.variables) > 3:
            analysis["optimizations"].append({
                "type": "reduce_variables",
                "description": "Consider breaking query into smaller sub-queries",
                "impact": "high"
            })
        
        if query.estimated_matches > 1000:
            analysis["optimizations"].append({
                "type": "add_constraints",
                "description": "Add more specific constraints to reduce match set",
                "impact": "high"
            })
        
        # Suggest indices
        if self._needs_type_index(query):
            analysis["index_suggestions"].append({
                "index_type": "type_index",
                "description": "Create type-based index for faster lookups"
            })
        
        if self._needs_name_index(query):
            analysis["index_suggestions"].append({
                "index_type": "name_index",
                "description": "Create name-based index for node lookups"
            })
        
        return analysis
    
    def _classify_pattern(self, query: PatternQuery) -> str:
        """Classify the pattern type"""
        if not query.variables:
            return PatternType.EXACT.value
        elif len(query.variables) == 1 and not query.constraints:
            return PatternType.TYPE.value
        elif len(query.constraints) > 2:
            return PatternType.COMPLEX.value
        elif "recursive" in query.pattern.lower():
            return PatternType.RECURSIVE.value
        else:
            return PatternType.VARIABLE.value
    
    def _calculate_complexity(self, query: PatternQuery) -> int:
        """Calculate query complexity score (0-100)"""
        score = 0
        
        # Variables increase complexity
        score += len(query.variables) * 10
        
        # Constraints increase complexity
        score += len(query.constraints) * 5
        
        # Estimated matches affect complexity
        if query.estimated_matches > 100:
            score += 20
        elif query.estimated_matches > 1000:
            score += 40
        
        return min(score, 100)
    
    def _needs_type_index(self, query: PatternQuery) -> bool:
        """Check if query would benefit from type index"""
        return "type" in query.pattern.lower() or len(query.variables) > 1
    
    def _needs_name_index(self, query: PatternQuery) -> bool:
        """Check if query would benefit from name index"""
        return "name" in query.pattern.lower() or "concept" in query.pattern.lower()
    
    def suggest_query_rewrite(self, query: PatternQuery) -> str:
        """Suggest an optimized version of the query"""
        suggestions = []
        
        # Suggest ordering variables by selectivity
        if len(query.variables) > 1:
            suggestions.append("Order variables by selectivity (most specific first)")
        
        # Suggest using type constraints
        if not any("type" in c.lower() for c in query.constraints):
            suggestions.append("Add type constraints to narrow search space")
        
        # Suggest caching for repeated queries
        if query.query_id in self.query_cache:
            suggestions.append("Query result can be cached")
        
        return "\n".join(suggestions) if suggestions else "Query is already optimal"


def main():
    """Example usage of pattern optimizer"""
    
    optimizer = PatternOptimizer()
    
    # Example queries
    queries = [
        PatternQuery(
            query_id="q1",
            pattern="InheritanceLink($X, $Y)",
            variables=["$X", "$Y"],
            constraints=[],
            estimated_matches=500
        ),
        PatternQuery(
            query_id="q2",
            pattern="EvaluationLink(PredicateNode('likes'), ListLink($X, $Y))",
            variables=["$X", "$Y"],
            constraints=["type($X, ConceptNode)", "type($Y, ConceptNode)"],
            estimated_matches=2000
        ),
        PatternQuery(
            query_id="q3",
            pattern="ConceptNode('Cat')",
            variables=[],
            constraints=[],
            estimated_matches=1
        )
    ]
    
    print("=== Pattern Matching Optimization Analysis ===\n")
    
    for query in queries:
        analysis = optimizer.analyze_pattern(query)
        rewrite_suggestions = optimizer.suggest_query_rewrite(query)
        
        print(f"Query: {query.query_id}")
        print(f"Pattern: {query.pattern}")
        print(f"Analysis:")
        print(json.dumps(analysis, indent=2))
        print(f"\nRewrite Suggestions:")
        print(rewrite_suggestions)
        print("\n" + "="*50 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
