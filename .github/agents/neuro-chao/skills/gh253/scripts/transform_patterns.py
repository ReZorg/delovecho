#!/usr/bin/env python3
"""
Transform APL253 patterns to gh253 GitHub domain patterns.
"""

import json
import os
import re
from pathlib import Path

# Load domain mappings
MAPPINGS_FILE = Path(__file__).parent.parent / "gh253_domain_mappings.json"
with open(MAPPINGS_FILE) as f:
    MAPPINGS = json.load(f)

CONCEPT_MAPPINGS = MAPPINGS["concept_mappings"]
PATTERN_NAME_MAPPINGS = MAPPINGS["pattern_name_transformations"]

def get_category_for_pattern(pattern_num: int) -> str:
    """Determine which category a pattern belongs to."""
    if 1 <= pattern_num <= 94:
        return "cat1-enterprises"
    elif 95 <= pattern_num <= 204:
        return "cat2-organisations"
    else:
        return "cat3-repositories"

def get_gh_pattern_name(pattern_num: int) -> str:
    """Get the GitHub domain pattern name."""
    key = str(pattern_num)
    if key in PATTERN_NAME_MAPPINGS:
        return PATTERN_NAME_MAPPINGS[key]["gh"]
    return f"PATTERN {pattern_num}"

def transform_concept(text: str) -> str:
    """Transform architectural concepts to GitHub concepts."""
    result = text
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_concepts = sorted(CONCEPT_MAPPINGS.items(), key=lambda x: len(x[0]), reverse=True)
    
    for apl_concept, gh_concept in sorted_concepts:
        # Case-insensitive replacement with word boundaries
        pattern = re.compile(r'\b' + re.escape(apl_concept) + r'\b', re.IGNORECASE)
        
        def replace_match(match):
            original = match.group(0)
            replacement = gh_concept.replace('_', ' ')
            # Preserve case
            if original.isupper():
                return replacement.upper()
            elif original[0].isupper():
                return replacement.title()
            return replacement
        
        result = pattern.sub(replace_match, result)
    
    return result

def transform_pattern_references(text: str) -> str:
    """Transform pattern references from APL to gh format."""
    # Match patterns like [PATTERN NAME (123)] or apl123
    def replace_apl_ref(match):
        pattern_num = int(match.group(1))
        gh_name = get_gh_pattern_name(pattern_num)
        return f"[{gh_name} ({pattern_num})]"
    
    # Replace [NAME (NUM)] format
    result = re.sub(r'\[([^\]]+)\s+\((\d+)\)\]', 
                    lambda m: f"[{get_gh_pattern_name(int(m.group(2)))} ({m.group(2)})]", 
                    text)
    
    # Replace apl### format
    result = re.sub(r'\bapl(\d{3})\b', 
                    lambda m: f"gh{m.group(1)}", 
                    result)
    
    return result

def transform_pattern_content(content: str, pattern_num: int) -> str:
    """Transform a full pattern file content."""
    gh_name = get_gh_pattern_name(pattern_num)
    
    # Transform the frontmatter
    content = re.sub(r'name: apl(\d+)', f'name: gh{pattern_num:03d}', content)
    content = re.sub(r'description: "?\d+ - [^"\n]+"?', 
                     f'description: "{pattern_num} - {gh_name}"', content)
    
    # Transform the title
    content = re.sub(r'# APL\d+ Instructions', f'# {gh_name}', content)
    
    # Transform pattern references
    content = transform_pattern_references(content)
    
    # Transform concepts in the body (but preserve code blocks and frontmatter)
    lines = content.split('\n')
    in_frontmatter = False
    in_code_block = False
    transformed_lines = []
    
    for line in lines:
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            transformed_lines.append(line)
        elif line.startswith('```'):
            in_code_block = not in_code_block
            transformed_lines.append(line)
        elif in_frontmatter or in_code_block:
            transformed_lines.append(line)
        elif line.startswith('#'):
            # Don't transform headers (already handled)
            transformed_lines.append(line)
        else:
            transformed_lines.append(transform_concept(line))
    
    return '\n'.join(transformed_lines)

def create_gh_pattern(apl_file: Path, output_dir: Path) -> Path:
    """Create a gh253 pattern from an APL253 pattern file."""
    # Extract pattern number from filename
    match = re.search(r'apl(\d+)\.md', apl_file.name)
    if not match:
        return None
    
    pattern_num = int(match.group(1))
    category = get_category_for_pattern(pattern_num)
    gh_name = get_gh_pattern_name(pattern_num)
    
    # Read and transform content
    with open(apl_file) as f:
        content = f.read()
    
    transformed = transform_pattern_content(content, pattern_num)
    
    # Create output filename
    slug = gh_name.lower().replace(' ', '-').replace("'", '')
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    output_file = output_dir / category / f"gh{pattern_num:03d}-{slug}.md"
    
    # Ensure directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write transformed content
    with open(output_file, 'w') as f:
        f.write(transformed)
    
    return output_file

def main():
    """Main transformation function."""
    import sys
    
    apl_base = Path("/home/ubuntu/apl253-reference/APL-253/.github/agents/apl0/dim0")
    output_base = Path("/home/ubuntu/gh253/patterns")
    
    # Find all APL pattern files
    pattern_files = sorted(apl_base.glob("**/apl*.md"))
    
    # Filter to only main pattern files (not broader/narrower)
    pattern_files = [f for f in pattern_files if f.parent.name.startswith("seq")]
    
    print(f"Found {len(pattern_files)} APL patterns to transform")
    
    transformed = 0
    for apl_file in pattern_files:
        try:
            output_file = create_gh_pattern(apl_file, output_base)
            if output_file:
                transformed += 1
                print(f"  Transformed: {apl_file.name} -> {output_file.name}")
        except Exception as e:
            print(f"  Error transforming {apl_file}: {e}")
    
    print(f"\nTransformed {transformed} patterns successfully")

if __name__ == "__main__":
    main()
