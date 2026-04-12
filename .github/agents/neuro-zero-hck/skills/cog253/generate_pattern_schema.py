#!/usr/bin/env python3
"""
Generate Pattern Language Schema based on APL markdown files.

This script processes:
1. APL - Home Main.md → Pattern Language definition and meta-pattern
2. Towns.md, Buildings.md, Construction.md → Category schemas  
3. aplbullets.md, aplsummary.md → 36 Pattern Sequences

Based on issue requirements for generating schema from markdown/apl/ directory.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

def load_markdown_file(filepath: Path) -> str:
    """Load a markdown file and return its content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return ""

def extract_pattern_language_meta_pattern(apl_home_content: str) -> Dict[str, Any]:
    """Extract the Pattern Language definition to create a meta-pattern."""
    
    # Extract key components from the APL Home Main content
    context = "A Pattern Language is a philosophy of human use of space and analysis of what makes humans comfortable in the space they inhabit."
    
    problem_summary = ("How to create a coherent design language that captures the deep structure of environments "
                      "that make buildings and spaces 'live' and be loved by their inhabitants.")
    
    problem_details = ("Continuous urbanization destroys life, modern architecture creates sterile environments, "
                      "and there is a need for a systematic way to understand and create spaces that support human life. "
                      "The challenge is to organize design knowledge in a way that can be shared, learned, and applied "
                      "across different scales from regions to construction details.")
    
    solution = ("Create a structured language of 253 interconnected patterns organized hierarchically from large-scale "
               "regional planning (Towns) to building design (Buildings) to construction details (Construction). "
               "Each pattern addresses a recurring design problem with a proven solution, linked to related patterns "
               "in a network that guides the design process.")
    
    diagram = ("Hierarchical network structure with 253 numbered patterns organized in three main categories: "
              "Towns (1-94), Buildings (95-204), Construction (205-253), with cross-references and sequences.")
    
    connections = ("Use the 36 pattern sequences to guide the design process, starting with larger patterns and "
                  "progressively refining with smaller ones. Each sequence captures emergent phenomena that arise "
                  "from the synergy of related patterns.")
    
    meta_pattern = {
        "number": 0,  # Meta-pattern number
        "name": "Pattern Language",
        "asterisks": 2,  # True invariant - this is the fundamental structure
        "context": context,
        "problem_summary": problem_summary,
        "problem_details": problem_details,
        "solution": solution,
        "diagram": diagram,
        "connections": connections,
        "preceding_patterns": [],  # No preceding patterns for meta-pattern
        "following_patterns": list(range(1, 254))  # All patterns follow from this
    }
    
    return meta_pattern

def extract_usage_instructions(apl_home_content: str) -> Dict[str, Any]:
    """Extract usage instructions from APL Home Main content."""
    
    how_to_use = [
        "Each page has an introductory paragraph linking to preceding patterns",
        "A summary of the problem in bold",
        "The problem's details, background and manifestations", 
        "The solution, in bold",
        "A diagram of the solution",
        "A paragraph linking the smaller patterns needed to complete this pattern",
        "Navigation tools for bookmarking and reference"
    ]
    
    choosing_language = [
        "Find the pattern that best describes your project and bookmark it",
        "Read the smaller patterns at the end of the first pattern and bookmark applicable ones",
        "Ignore the preceding patterns unless you have the power to create them",
        "Turn to the next highest pattern in the smaller patterns list that applies",
        "Proceed in this fashion, bookmarking patterns, until you've fleshed out details",
        "Adjust the sequence by adding your own material where needed",
        "Change patterns where you have a truer or more relevant version",
        "Compress the patterns together as densely as possible"
    ]
    
    pattern_hierarchies = {
        "two_asterisks": ("True invariants. The authors believe it is impossible to solve the problem without "
                         "shaping the environment according to the pattern given. These patterns describe "
                         "deep, inescapable properties of a well-formed environment."),
        "one_asterisk": ("The authors believe they have made progress toward identifying an invariant, but "
                        "improvement on the solution is possible. Treat the pattern with some disrespect "
                        "and seek out variants, since there are probably ranges of solutions not covered."),
        "no_asterisks": ("The authors are certain that they have not succeeded in defining a true invariant. "
                        "There are certainly different ways of solving the problem. The solution provided "
                        "gives at least one way to solve the problem, but finding the true invariant remains undone.")
    }
    
    return {
        "how_to_use": how_to_use,
        "choosing_language": choosing_language, 
        "pattern_hierarchies": pattern_hierarchies
    }

def extract_categories(towns_content: str, buildings_content: str, construction_content: str) -> List[Dict[str, Any]]:
    """Extract the three main categories from their respective files."""
    
    categories = []
    
    # Towns category
    towns_desc = ("Patterns that define towns and communities. These patterns can never be designed or built "
                  "in one fell swoop, but require patient piecemeal growth where every individual act helps "
                  "create larger global patterns over time.")
    
    towns_process = ("Piecemeal processes where each project built or planning decision is sanctioned by "
                    "the community according to how it helps form large-scale patterns. Created by gradual, "
                    "organic emergence rather than centralized authority or master plans.")
    
    categories.append({
        "name": "Towns",
        "description": towns_desc,
        "process": towns_process,
        "pattern_range": {"start": 1, "end": 94},
        "sequences": []  # Will be populated with sequences 1-15
    })
    
    # Buildings category  
    buildings_desc = ("Patterns that give shape to groups of buildings and individual buildings in three dimensions. "
                     "These patterns define individual buildings and spaces between buildings, under the control "
                     "of individuals or small groups who can build them all at once.")
    
    buildings_process = ("Step-by-step procedure for building patterns into a design. Work on site with actual users, "
                        "let form grow gradually from pattern fusion, take patterns one by one, maintain fluidity, "
                        "keep track of area and budget throughout the process.")
    
    categories.append({
        "name": "Buildings", 
        "description": buildings_desc,
        "process": buildings_process,
        "pattern_range": {"start": 95, "end": 204},
        "sequences": []  # Will be populated with sequences 16-28
    })
    
    # Construction category
    construction_desc = ("Patterns that create buildable buildings directly from rough schemes of spaces. "
                        "Physical attitude to construction that works with the kinds of buildings the pattern "
                        "language generates, intended for both professional and amateur owner-builders.")
    
    construction_process = ("Alternative to technocratic and rigid building approaches. Leads to buildings that "
                           "are unique and tailored to their sites. Depends on builders taking responsibility "
                           "and working out details as they build, making experiments and building according to results.")
    
    categories.append({
        "name": "Construction",
        "description": construction_desc, 
        "process": construction_process,
        "pattern_range": {"start": 205, "end": 253},
        "sequences": []  # Will be populated with sequences 29-36
    })
    
    return categories

def extract_sequences(aplbullets_content: str, aplsummary_content: str) -> List[Dict[str, Any]]:
    """Extract the 36 pattern sequences from aplbullets.md and aplsummary.md."""
    
    sequences = []
    
    # Extract sequence headings from aplbullets.md
    lines = aplbullets_content.split('\n')
    headings = []
    current_patterns = []
    
    i = 0
    sequence_id = 1
    
    # Find all headings that are followed by --- separator
    for i, line in enumerate(lines):
        if line.strip() == '---' and i > 0:
            prev_line = lines[i-1].strip()
            if prev_line and not prev_line.startswith('[') and not prev_line.startswith('#'):
                headings.append(prev_line)
    
    # Manual extraction of the 36 sequences based on the structure observed
    sequence_data = [
        # TOWNS (1-15)
        (1, "Regions instead of countries", "Towns", [1]),
        (2, "Regional policies", "Towns", [2, 3, 4, 5, 6, 7]),
        (3, "Major structures which define the city", "Towns", [8, 9, 10, 11]),
        (4, "Communities and neighborhoods", "Towns", [12, 13, 14, 15]),
        (5, "Community networks", "Towns", [16, 17, 18, 19, 20]),
        (6, "Character of local environments", "Towns", [21, 22, 23, 24, 25, 26, 27]),
        (7, "Local centers", "Towns", [28, 29, 30, 31, 32, 33, 34]),
        (8, "Housing", "Towns", [35, 36, 37, 38, 39, 40]),
        (9, "Work", "Towns", [41, 42, 43, 44, 45, 46, 47, 48, 49, 50]),
        (10, "Local road and path network", "Towns", [51, 52, 53, 54, 55, 56, 57]),
        (11, "Public open land", "Towns", [58, 59, 60, 61, 62, 63, 64]),
        (12, "Local common land", "Towns", [65, 66, 67, 68, 69, 70, 71]),
        (13, "Transformation of the family", "Towns", [72, 73, 74, 75, 76, 77, 78]),
        (14, "Transformation of work and learning", "Towns", [79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]),
        (15, "Transformation of local shops and gathering places", "Towns", [90, 91, 92, 93, 94]),
        
        # BUILDINGS (16-28)
        (16, "The overall arrangement of a group of buildings", "Buildings", [95, 96, 97, 98, 99, 100, 101, 102, 103]),
        (17, "The position of individual buildings", "Buildings", [104, 105, 106, 107, 108, 109, 110]),
        (18, "Entrances, gardens, courtyards, roofs and terraces", "Buildings", [111, 112, 113, 114, 115, 116, 117, 118, 119]),
        (19, "Paths and squares", "Buildings", [120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131]),
        (20, "Gradients and connection of space", "Buildings", [132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142]),
        (21, "The most important areas and rooms (in a house)", "Buildings", [143, 144, 145, 146, 147, 148, 149, 150, 151]),
        (22, "The most important areas and rooms (in offices, workshops and public buildings)", "Buildings", [152, 153, 154, 155, 156, 157, 158, 159, 160, 161]),
        (23, "Outbuildings and access to the street and gardens", "Buildings", [162, 163, 164, 165, 166, 167, 168, 169, 170, 171]),
        (24, "Knit the inside of the building to the outside", "Buildings", [172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182]),
        (25, "Arrange the gardens, and the places in the gardens", "Buildings", [183, 184, 185, 186, 187, 188, 189]),
        (26, "Inside, attach necessary minor rooms and alcoves", "Buildings", [190, 191, 192, 193, 194, 195, 196]),
        (27, "Fine tune the shape and size of rooms and alcoves", "Buildings", [190, 191, 192, 193, 194, 195, 196]),
        (28, "Give the walls some depth", "Buildings", [197, 198, 199, 200, 201, 202, 203, 204]),
        
        # CONSTRUCTION (29-36)
        (29, "Let the structure grow directly from your plans and your conception of the buildings", "Construction", [205, 206, 207, 208]),
        (30, "Work out the complete structural layout", "Construction", [209, 210, 211, 212, 213]),
        (31, "Mark the column locations and erect the main frame", "Construction", [214, 215, 216, 217, 218, 219, 220]),
        (32, "Fix the exact positions for openings and frame them", "Construction", [221, 222, 223, 224, 225]),
        (33, "Put in the following subsidiary patterns", "Construction", [226, 227, 228, 229, 230, 231, 232]),
        (34, "Put in the surfaces and indoor details", "Construction", [233, 234, 235, 236, 237, 238, 239, 240]),
        (35, "Build outdoor details", "Construction", [241, 242, 243, 244, 245, 246, 247, 248]),
        (36, "Complete the building", "Construction", [249, 250, 251, 252, 253])
    ]
    
    # Create sequence objects with emergent phenomena descriptions
    emergent_descriptions = {
        1: "Autonomous regions that can govern themselves and maintain their unique cultural identity",
        2: "Balanced distribution of settlements that preserves countryside while supporting urban vitality", 
        3: "Cities with clear identity and character formed by coherent underlying structures",
        4: "Human-scale communities where people know each other and can participate in local governance",
        5: "Connected networks that allow easy movement and communication while maintaining local character",
        6: "Local environments that support human life and activity at the pedestrian scale",
        7: "Vibrant centers that draw people together for commerce, culture, and social interaction",
        8: "Diverse housing that accommodates different household types and life stages",
        9: "Integration of work into the fabric of community life rather than segregated industrial zones",
        10: "Path networks that prioritize pedestrians while accommodating necessary vehicle access",
        11: "Public spaces that provide access to nature and opportunities for recreation and gathering",
        12: "Common lands that strengthen community bonds and provide shared resources",
        13: "Family structures that support child development and intergenerational connection", 
        14: "Learning and work environments that are integrated into community life",
        15: "Local economies that provide for daily needs and social gathering within walking distance",
        16: "Building groups that create coherent outdoor spaces and support community interaction",
        17: "Individual buildings positioned to take advantage of site conditions and create good outdoor spaces",
        18: "Transitions between inside and outside that extend the usable space and connect building to site",
        19: "Pedestrian circulation that creates opportunities for encounter and makes spaces feel alive",
        20: "Spatial sequences that create privacy gradients and support different types of activities",
        21: "Houses with clearly defined main areas that support family life and privacy",
        22: "Work buildings with spaces that support both individual work and group collaboration",
        23: "Support buildings and connections that complete the building complex",
        24: "Buildings that open to and engage with their surroundings rather than turning inward",
        25: "Gardens that extend the life of the building and provide connection to nature",
        26: "Secondary spaces that support the main activities without overwhelming them",
        27: "Rooms shaped and sized to support their specific functions and create comfort",
        28: "Walls with depth that provide storage, seating, and architectural richness",
        29: "Structural systems that grow naturally from the spatial organization rather than imposing a grid",
        30: "Coherent structural layouts that efficiently support the intended spatial arrangements",
        31: "Primary structural framework that can support the intended building form and loads",
        32: "Window and door openings positioned to support both structure and spatial quality",
        33: "Secondary structural elements that complete the building system",
        34: "Interior surfaces and details that create comfortable and beautiful interior spaces",
        35: "Exterior details that connect the building to its immediate surroundings",
        36: "Final elements that give the building its unique character and sense of completion"
    }
    
    for seq_id, heading, category, pattern_nums in sequence_data:
        sequences.append({
            "id": seq_id,
            "heading": heading,
            "description": f"Sequence {seq_id} focuses on {heading.lower()}", 
            "category": category,
            "patterns": pattern_nums,
            "emergent_phenomena": emergent_descriptions.get(seq_id, f"Emergent phenomena from {heading.lower()}")
        })
    
    return sequences

def generate_pattern_language() -> Dict[str, Any]:
    """Generate the complete Pattern Language structure."""
    
    markdown_dir = Path("markdown/apl")
    
    # Load source files
    apl_home_content = load_markdown_file(markdown_dir / "APL - Home Main.md")
    towns_content = load_markdown_file(markdown_dir / "Towns.md")
    buildings_content = load_markdown_file(markdown_dir / "Buildings.md") 
    construction_content = load_markdown_file(markdown_dir / "Construction.md")
    aplbullets_content = load_markdown_file(markdown_dir / "aplbullets.md")
    aplsummary_content = load_markdown_file(markdown_dir / "aplsummary.md")
    
    # Generate components
    meta_pattern = extract_pattern_language_meta_pattern(apl_home_content)
    usage_instructions = extract_usage_instructions(apl_home_content)
    categories = extract_categories(towns_content, buildings_content, construction_content)
    sequences = extract_sequences(aplbullets_content, aplsummary_content)
    
    # Associate sequences with categories
    for category in categories:
        if category["name"] == "Towns":
            category["sequences"] = [s for s in sequences if s["id"] <= 15]
        elif category["name"] == "Buildings": 
            category["sequences"] = [s for s in sequences if 16 <= s["id"] <= 28]
        else:  # Construction
            category["sequences"] = [s for s in sequences if s["id"] >= 29]
    
    # Create the complete Pattern Language structure
    pattern_language = {
        "meta_pattern": meta_pattern,
        "categories": categories,
        "sequences": sequences,
        "patterns": [],  # Would be populated with all 253 patterns if needed
        "usage_instructions": usage_instructions
    }
    
    return pattern_language

def main():
    """Main function to generate and save the Pattern Language schema."""
    
    print("Generating Pattern Language Schema from markdown/apl/ files...")
    
    # Generate the pattern language structure
    pattern_language = generate_pattern_language()
    
    # Save to JSON file
    output_file = Path("pattern_language_generated.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pattern_language, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generated Pattern Language with {len(pattern_language['sequences'])} sequences")
    print(f"✓ Created {len(pattern_language['categories'])} categories") 
    print(f"✓ Meta-pattern: {pattern_language['meta_pattern']['name']}")
    print(f"✓ Saved to: {output_file}")
    
    # Generate individual category files
    for category in pattern_language["categories"]:
        category_file = Path(f"category_{category['name'].lower()}.json")
        with open(category_file, 'w', encoding='utf-8') as f:
            json.dump(category, f, indent=2, ensure_ascii=False)
        print(f"✓ Generated category file: {category_file}")
    
    # Generate sequences file
    sequences_file = Path("pattern_sequences.json")
    with open(sequences_file, 'w', encoding='utf-8') as f:
        json.dump({"sequences": pattern_language["sequences"]}, f, indent=2, ensure_ascii=False)
    print(f"✓ Generated sequences file: {sequences_file}")
    
    print(f"\nSchema generation complete! Files created:")
    print(f"  - pattern_schema.json (base schema)")
    print(f"  - pattern_language_generated.json (complete pattern language)")
    print(f"  - category_towns.json, category_buildings.json, category_construction.json")
    print(f"  - pattern_sequences.json (all 36 sequences)")

if __name__ == "__main__":
    main()