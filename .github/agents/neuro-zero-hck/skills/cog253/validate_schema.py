#!/usr/bin/env python3
"""
Validate the generated Pattern Language schema and data files.
"""

import json
from pathlib import Path

def validate_pattern_structure(pattern, name="Pattern"):
    """Validate a pattern object structure."""
    required_fields = ["number", "name", "problem_summary", "solution"]
    optional_fields = ["asterisks", "context", "problem_details", "diagram", "connections", "preceding_patterns", "following_patterns"]
    
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in pattern:
            errors.append(f"{name}: Missing required field '{field}'")
    
    # Check field types
    if "number" in pattern and not isinstance(pattern["number"], int):
        errors.append(f"{name}: 'number' must be integer")
    
    if "name" in pattern and not isinstance(pattern["name"], str):
        errors.append(f"{name}: 'name' must be string")
        
    if "asterisks" in pattern and not isinstance(pattern["asterisks"], int):
        errors.append(f"{name}: 'asterisks' must be integer")
    
    if "asterisks" in pattern and not (0 <= pattern["asterisks"] <= 2):
        errors.append(f"{name}: 'asterisks' must be 0, 1, or 2")
    
    return errors

def validate_category_structure(category, name="Category"):
    """Validate a category object structure."""
    required_fields = ["name", "description", "pattern_range"]
    
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in category:
            errors.append(f"{name}: Missing required field '{field}'")
    
    # Check category name
    if "name" in category and category["name"] not in ["Towns", "Buildings", "Construction"]:
        errors.append(f"{name}: Invalid category name '{category['name']}'")
    
    # Check pattern range
    if "pattern_range" in category:
        if not isinstance(category["pattern_range"], dict):
            errors.append(f"{name}: 'pattern_range' must be object")
        elif "start" not in category["pattern_range"] or "end" not in category["pattern_range"]:
            errors.append(f"{name}: 'pattern_range' must have 'start' and 'end'")
    
    return errors

def validate_sequence_structure(sequence, name="Sequence"):
    """Validate a sequence object structure.""" 
    required_fields = ["id", "heading", "category", "patterns"]
    
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in sequence:
            errors.append(f"{name}: Missing required field '{field}'")
    
    # Check sequence ID
    if "id" in sequence and not (1 <= sequence["id"] <= 36):
        errors.append(f"{name}: 'id' must be between 1 and 36")
    
    # Check category
    if "category" in sequence and sequence["category"] not in ["Towns", "Buildings", "Construction"]:
        errors.append(f"{name}: Invalid category '{sequence['category']}'")
    
    # Check patterns is array
    if "patterns" in sequence and not isinstance(sequence["patterns"], list):
        errors.append(f"{name}: 'patterns' must be array")
    
    return errors

def main():
    """Main validation function."""
    
    print("=== Pattern Language Schema Validation ===\n")
    
    errors = []
    
    # Validate main pattern language file
    pattern_lang_file = Path("pattern_language_generated.json")
    if pattern_lang_file.exists():
        print("✓ Found pattern_language_generated.json")
        
        with open(pattern_lang_file) as f:
            pattern_language = json.load(f)
        
        # Validate meta-pattern
        if "meta_pattern" in pattern_language:
            meta_errors = validate_pattern_structure(pattern_language["meta_pattern"], "Meta-pattern")
            errors.extend(meta_errors)
            if not meta_errors:
                print("✓ Meta-pattern structure is valid")
            else:
                print("✗ Meta-pattern has structure errors")
        
        # Validate categories
        if "categories" in pattern_language:
            if len(pattern_language["categories"]) == 3:
                print("✓ Found 3 categories")
                for i, category in enumerate(pattern_language["categories"]):
                    cat_errors = validate_category_structure(category, f"Category {i+1}")
                    errors.extend(cat_errors)
                if not any(errors):
                    print("✓ All categories have valid structure")
            else:
                errors.append(f"Expected 3 categories, found {len(pattern_language['categories'])}")
        
        # Validate sequences
        if "sequences" in pattern_language:
            if len(pattern_language["sequences"]) == 36:
                print("✓ Found 36 sequences")
                for sequence in pattern_language["sequences"]:
                    seq_errors = validate_sequence_structure(sequence, f"Sequence {sequence.get('id', '?')}")
                    errors.extend(seq_errors)
                if not any(seq_errors for sequence in pattern_language["sequences"] 
                          for seq_errors in [validate_sequence_structure(sequence)]):
                    print("✓ All sequences have valid structure")
            else:
                errors.append(f"Expected 36 sequences, found {len(pattern_language['sequences'])}")
        
        # Check usage instructions
        if "usage_instructions" in pattern_language:
            print("✓ Found usage instructions")
        else:
            errors.append("Missing usage_instructions")
    
    else:
        errors.append("Missing pattern_language_generated.json")
    
    # Validate individual files
    individual_files = [
        "pattern_schema.json",
        "category_towns.json", 
        "category_buildings.json",
        "category_construction.json",
        "pattern_sequences.json"
    ]
    
    print(f"\n=== Individual Files ===")
    
    for file_name in individual_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✓ Found {file_name}")
            try:
                with open(file_path) as f:
                    json.load(f)  # Validate JSON format
                print(f"✓ {file_name} is valid JSON")
            except json.JSONDecodeError as e:
                errors.append(f"{file_name}: Invalid JSON - {e}")
                print(f"✗ {file_name} has JSON errors")
        else:
            errors.append(f"Missing {file_name}")
            print(f"✗ Missing {file_name}")
    
    # Summary
    print(f"\n=== Validation Summary ===")
    if errors:
        print(f"❌ Found {len(errors)} errors:")
        for error in errors:
            print(f"  • {error}")
        return 1
    else:
        print("✅ All validations passed!")
        print("\nGenerated files structure:")
        print("  📋 pattern_schema.json - Base JSON schema definition")
        print("  🌍 pattern_language_generated.json - Complete pattern language")
        print("  🏘️  category_towns.json - Towns category (patterns 1-94)")
        print("  🏢 category_buildings.json - Buildings category (patterns 95-204)")
        print("  🔨 category_construction.json - Construction category (patterns 205-253)")
        print("  📝 pattern_sequences.json - All 36 pattern sequences")
        return 0

if __name__ == "__main__":
    exit(main())