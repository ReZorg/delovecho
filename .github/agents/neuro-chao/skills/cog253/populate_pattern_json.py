#!/usr/bin/env python3
"""
Populate pattern_language_generated.json with data from all 253 APL markdown files.
This reads the markdown files and extracts:
- Pattern number
- Pattern name
- Problem statement
- Context
- Solution
- Related patterns
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Constants for pattern categorization
PATTERN_TOWNS_END = 94  # Patterns 1-94 are Towns (** asterisks)
PATTERN_BUILDINGS_END = 204  # Patterns 95-204 are Buildings (* asterisks)
PATTERN_TOTAL = 253  # Total number of patterns (205-253 are Construction, no asterisks)


def extract_pattern_from_markdown(filepath: Path) -> Optional[Dict[str, Any]]:
    """Extract pattern information from a markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    # Extract pattern number and name from title (# 1 - INDEPENDENT REGIONS)
    title_match = re.search(r'^#\s+(\d+)\s+-\s+(.*)$', content, re.MULTILINE)
    if not title_match:
        print(f"Warning: Could not parse title in {filepath}")
        return None
    
    pattern_num = int(title_match.group(1))
    pattern_name = title_match.group(2).strip()
    
    # Determine asterisks based on pattern number ranges (from APL hierarchy)
    # ** = patterns 1-94 (Towns - most important)
    # * = patterns 95-204 (Buildings)
    # no asterisk = patterns 205-253 (Construction)
    if pattern_num <= PATTERN_TOWNS_END:
        asterisks = 2
    elif pattern_num <= PATTERN_BUILDINGS_END:
        asterisks = 1
    else:
        asterisks = 0
    
    # Extract Problem section
    problem = ""
    solution = ""
    problem_match = re.search(r'^##\s+Problem\s*\n\n(.*?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    if problem_match:
        problem_section = problem_match.group(1).strip()
        # In APL, the pattern often has:
        # Paragraph 1: The problem statement
        # Paragraph 2: The solution (in bold in original)
        # Split by double newline to get paragraphs
        paragraphs = [p.strip() for p in problem_section.split('\n\n') if p.strip()]
        if len(paragraphs) >= 1:
            problem = paragraphs[0]
        if len(paragraphs) >= 2:
            # Second paragraph is often the solution
            solution = paragraphs[1]
    
    # Extract Context section
    context = ""
    context_match = re.search(r'^##\s+Context\s*\n\n(.*?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    if context_match:
        context = context_match.group(1).strip()
    
    # Extract Discussion section
    discussion = ""
    discussion_match = re.search(r'^##\s+Discussion\s*\n\n(.*?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    if discussion_match:
        discussion = discussion_match.group(1).strip()
        
        # If we have discussion but no context, extract context from discussion
        # (the first paragraph before the main text, starting with ". . .")
        if not context and discussion.startswith('. . .'):
            context_end = discussion.find('\n\n')
            if context_end > 0:
                context = discussion[:context_end].strip()
    
        # Look for "Therefore:" in discussion to extract solution if not found
        if not solution:
            solution_match = re.search(r'Therefore:?\s*\n\n(.*?)(?=\n##|\Z)', discussion, re.DOTALL)
            if solution_match:
                solution = solution_match.group(1).strip()
    
    # Extract related patterns
    related_patterns = []
    related_match = re.search(r'^##\s+Related Patterns\s*\n\n(.*?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    if related_match:
        related_text = related_match.group(1)
        # Extract pattern numbers from various formats
        # Format 1: [PATTERN NAME (N)]
        pattern_refs = re.findall(r'\[(?:[^\]]*?)\((\d+)\)\]', related_text)
        # Format 2: - Pattern N
        pattern_refs.extend(re.findall(r'-\s+Pattern\s+(\d+)', related_text))
        # Format 3: [Pattern Name](N)
        pattern_refs.extend(re.findall(r'\]\((\d+)\)', related_text))
        
        for ref in pattern_refs:
            num = int(ref)
            if num != pattern_num and num not in related_patterns:
                related_patterns.append(num)
        
        related_patterns.sort()
    
    # Build pattern data structure
    pattern = {
        "id": f"apl{pattern_num}",
        "number": pattern_num,
        "name": pattern_name,
        "asterisks": asterisks,
        "context": context,
        "problem": problem,
        "solution": solution,
        "preceding_patterns": [],  # Will be populated from related patterns
        "following_patterns": []   # Will be populated from related patterns
    }
    
    # Store raw related patterns for later processing
    pattern["_related_patterns"] = related_patterns
    
    return pattern


def link_pattern_relationships(patterns: List[Dict[str, Any]]):
    """Link patterns based on their relationships."""
    pattern_dict = {p["number"]: p for p in patterns}
    
    for pattern in patterns:
        pattern_num = pattern["number"]
        related = pattern.get("_related_patterns", [])
        
        # Patterns with lower numbers are "preceding" (larger scale)
        # Patterns with higher numbers are "following" (smaller scale)
        for related_num in related:
            if related_num in pattern_dict:
                if related_num < pattern_num:
                    pattern["preceding_patterns"].append(related_num)
                elif related_num > pattern_num:
                    pattern["following_patterns"].append(related_num)
        
        # Remove temporary field
        if "_related_patterns" in pattern:
            del pattern["_related_patterns"]
        
        # Sort for consistency
        pattern["preceding_patterns"].sort()
        pattern["following_patterns"].sort()


def populate_category_files(patterns: List[Dict[str, Any]]):
    """Populate individual category files with their patterns."""
    
    # Define category ranges
    categories = [
        {
            "name": "Towns",
            "range": (1, PATTERN_TOWNS_END),
            "description": "Patterns that define towns and communities. These patterns can never be designed or built in one fell swoop - but patient piecemeal growth, designed in such a way that every individual act is always helping to create or generate these larger global patterns, will, slowly and surely, over the months and years, make a community that has these global patterns in it."
        },
        {
            "name": "Buildings", 
            "range": (PATTERN_TOWNS_END + 1, PATTERN_BUILDINGS_END),
            "description": "Patterns that give shape to groups of buildings and individual buildings in three dimensions."
        },
        {
            "name": "Construction",
            "range": (PATTERN_BUILDINGS_END + 1, PATTERN_TOTAL),
            "description": "Patterns that create buildable buildings directly from rough schemes of spaces. These patterns give you the exact geometry of the built up elements which define the spaces."
        }
    ]
    
    for category in categories:
        # Filter patterns in this category's range
        category_patterns = [
            p for p in patterns 
            if category["range"][0] <= p["number"] <= category["range"][1]
        ]
        
        category_data = {
            "name": category["name"],
            "description": category["description"],
            "pattern_range": {
                "start": category["range"][0],
                "end": category["range"][1]
            },
            "patterns": category_patterns
        }
        
        # Save category file
        filename = Path(f"category_{category['name'].lower()}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2)
        
        print(f"  ✓ Generated {filename} with {len(category_patterns)} patterns")


def populate_pattern_json():
    """Populate pattern_language_generated.json with all 253 patterns."""
    print("Populating pattern_language_generated.json...")
    print("=" * 70)
    
    # Load existing JSON to preserve meta_pattern
    json_file = Path('pattern_language_generated.json')
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    
    # Extract patterns from markdown files
    markdown_dir = Path('markdown/apl')
    patterns = []
    
    for i in range(1, PATTERN_TOTAL + 1):
        md_file = markdown_dir / f"apl{i:03d}.md"
        if md_file.exists():
            pattern = extract_pattern_from_markdown(md_file)
            if pattern:
                patterns.append(pattern)
                if i % 50 == 0:
                    print(f"Processed {i} patterns...")
        else:
            print(f"Warning: Missing file {md_file}")
    
    print(f"\nExtracted {len(patterns)} patterns")
    
    # Link pattern relationships
    print("Linking pattern relationships...")
    link_pattern_relationships(patterns)
    
    # Add patterns to JSON data
    data["patterns"] = patterns
    
    # Save updated JSON
    print(f"Saving to {json_file}...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Successfully populated {len(patterns)} patterns!")
    print(f"✓ JSON file saved: {json_file}")
    
    # Generate category files
    print("\nGenerating category files...")
    populate_category_files(patterns)
    
    # Validation
    print("\nValidation:")
    print(f"  - Total patterns: {len(patterns)}")
    print(f"  - Expected: {PATTERN_TOTAL}")
    print(f"  - Match: {'✓ YES' if len(patterns) == PATTERN_TOTAL else '✗ NO'}")
    
    # Show content statistics in a single pass
    with_problem = 0
    with_solution = 0
    with_context = 0
    
    for p in patterns:
        if p.get('problem'):
            with_problem += 1
        if p.get('solution'):
            with_solution += 1
        if p.get('context'):
            with_context += 1
    
    print(f"\nContent statistics:")
    print(f"  - Patterns with problem: {with_problem}/{len(patterns)}")
    print(f"  - Patterns with solution: {with_solution}/{len(patterns)}")
    print(f"  - Patterns with context: {with_context}/{len(patterns)}")
    
    print("\n" + "=" * 70)
    print("✅ Pattern population complete!")
    print("=" * 70)


def main():
    """Main entry point."""
    populate_pattern_json()


if __name__ == '__main__':
    main()
