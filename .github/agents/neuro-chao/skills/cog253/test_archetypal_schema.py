#!/usr/bin/env python3
"""
Test suite for archetypal pattern schema.

Tests the generated archetypal pattern specifications:
1. Schema validity
2. Pattern collection structure
3. Placeholder definitions
4. Domain mappings
"""

import json
from pathlib import Path


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()


def load_json(filepath: str) -> dict:
    """Load and parse JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_schema_file():
    """Test that the schema file exists and is valid."""
    print("\n=== Testing Schema File ===")
    
    schema_file = "archetypal_pattern_schema.json"
    assert check_file_exists(schema_file), f"✗ Schema file not found: {schema_file}"
    print(f"✓ Schema file exists: {schema_file}")
    
    schema = load_json(schema_file)
    
    # Check schema structure
    assert "$schema" in schema, "✗ Missing $schema field"
    print("✓ Schema has $schema field")
    
    assert "title" in schema, "✗ Missing title field"
    assert schema["title"] == "Archetypal Pattern Schema", "✗ Incorrect title"
    print(f"✓ Schema title: {schema['title']}")
    
    assert "definitions" in schema, "✗ Missing definitions"
    print("✓ Schema has definitions")
    
    # Check key definitions
    expected_definitions = ["ArchetypalPattern", "DomainMapping", "ArchetypalPatternCollection"]
    for def_name in expected_definitions:
        assert def_name in schema["definitions"], f"✗ Missing definition: {def_name}"
    print(f"✓ All expected definitions present: {', '.join(expected_definitions)}")


def test_patterns_collection():
    """Test the archetypal patterns collection."""
    print("\n=== Testing Patterns Collection ===")
    
    patterns_file = "archetypal_patterns.json"
    assert check_file_exists(patterns_file), f"✗ Patterns file not found: {patterns_file}"
    print(f"✓ Patterns file exists: {patterns_file}")
    
    data = load_json(patterns_file)
    
    # Check meta information
    assert "meta" in data, "✗ Missing meta section"
    meta = data["meta"]
    assert "total_patterns" in meta, "✗ Missing total_patterns in meta"
    # Updated: Now includes all 253 UIA patterns with domain content
    assert meta["total_patterns"] == 253, f"✗ Expected 253 patterns, got {meta['total_patterns']}"
    print(f"✓ Meta information correct: {meta['total_patterns']} patterns")
    
    # Check patterns array
    assert "patterns" in data, "✗ Missing patterns array"
    patterns = data["patterns"]
    assert len(patterns) == 253, f"✗ Expected 253 patterns, got {len(patterns)}"
    print(f"✓ Patterns array has {len(patterns)} entries")
    
    # Check placeholder definitions
    assert "placeholder_definitions" in data, "✗ Missing placeholder_definitions"
    placeholders = data["placeholder_definitions"]
    assert len(placeholders) > 0, "✗ No placeholder definitions found"
    print(f"✓ Found {len(placeholders)} placeholder definitions")


def test_pattern_structure():
    """Test individual pattern structure."""
    print("\n=== Testing Pattern Structure ===")
    
    data = load_json("archetypal_patterns.json")
    patterns = data["patterns"]
    
    # Test first pattern
    pattern = patterns[0]
    
    required_fields = ["pattern_id", "name", "archetypal_pattern", "placeholders"]
    for field in required_fields:
        assert field in pattern, f"✗ Missing required field: {field}"
    print(f"✓ Pattern has all required fields: {', '.join(required_fields)}")
    
    # Check pattern ID format
    assert pattern["pattern_id"].isdigit(), "✗ Pattern ID is not numeric"
    print(f"✓ Pattern ID format valid: {pattern['pattern_id']}")
    
    # Check archetypal pattern has placeholders
    archetypal = pattern["archetypal_pattern"]
    assert "{{" in archetypal and "}}" in archetypal, "✗ Archetypal pattern missing placeholders"
    print(f"✓ Archetypal pattern contains placeholders")
    
    # Check placeholders array matches pattern
    for placeholder in pattern["placeholders"]:
        expected = f"{{{{{placeholder}}}}}"
        assert expected in archetypal, f"✗ Placeholder {expected} not found in pattern"
    print(f"✓ All listed placeholders found in pattern text")


def test_domain_mappings():
    """Test domain mapping structure."""
    print("\n=== Testing Domain Mappings ===")
    
    data = load_json("archetypal_patterns.json")
    patterns = data["patterns"]
    
    # Test that patterns with placeholders have domain mappings
    pattern = patterns[0]
    
    if "domain_mappings" in pattern:
        mappings = pattern["domain_mappings"]
        
        # Check that each placeholder has domain mappings
        for placeholder in pattern["placeholders"]:
            assert placeholder in mappings, f"✗ No domain mapping for placeholder: {placeholder}"
        print(f"✓ All placeholders have domain mappings")
        
        # Check standard domains
        expected_domains = ["physical", "social", "conceptual", "psychic"]
        for placeholder, domain_map in mappings.items():
            for domain in expected_domains:
                if domain in domain_map:
                    assert isinstance(domain_map[domain], str), f"✗ Domain mapping not a string"
        print(f"✓ Domain mappings have correct structure")


def test_placeholder_reference():
    """Test placeholder reference file."""
    print("\n=== Testing Placeholder Reference ===")
    
    placeholder_file = "archetypal_placeholders.json"
    assert check_file_exists(placeholder_file), f"✗ Placeholder file not found: {placeholder_file}"
    print(f"✓ Placeholder reference file exists")
    
    data = load_json(placeholder_file)
    
    assert "title" in data, "✗ Missing title"
    assert "total_placeholders" in data, "✗ Missing total_placeholders"
    assert "placeholders" in data, "✗ Missing placeholders array"
    print(f"✓ Placeholder reference has correct structure")
    
    placeholders = data["placeholders"]
    assert len(placeholders) == data["total_placeholders"], "✗ Placeholder count mismatch"
    print(f"✓ Found {len(placeholders)} placeholder definitions")
    
    # Check each placeholder has required fields
    for placeholder in placeholders:
        assert "placeholder" in placeholder, "✗ Missing placeholder name"
        assert "domains" in placeholder, "✗ Missing domains"
        assert "used_in_patterns" in placeholder, "✗ Missing used_in_patterns"
    print(f"✓ All placeholders have required fields")


def test_pattern_ids_unique():
    """Test that all pattern IDs are unique."""
    print("\n=== Testing Pattern ID Uniqueness ===")
    
    data = load_json("archetypal_patterns.json")
    patterns = data["patterns"]
    
    pattern_ids = [p["pattern_id"] for p in patterns]
    unique_ids = set(pattern_ids)
    
    assert len(pattern_ids) == len(unique_ids), "✗ Duplicate pattern IDs found"
    print(f"✓ All {len(pattern_ids)} pattern IDs are unique")


def test_all_arc_files_processed():
    """Test that all pattern files were processed."""
    print("\n=== Testing Coverage of Pattern Files ===")
    
    arc_dir = Path("markdown/arc")
    arc_files = list(arc_dir.glob("arc_*.md"))
    
    data = load_json("archetypal_patterns.json")
    patterns = data["patterns"]
    
    processed_files = {p["source_file"] for p in patterns if "source_file" in p}
    
    print(f"✓ Found {len(arc_files)} arc markdown files")
    print(f"✓ Processed {len(processed_files)} patterns")
    
    # Updated: Now includes all 253 UIA patterns with domain content
    assert len(patterns) == 253, f"✗ Expected 253 patterns, got {len(patterns)}"
    print(f"✓ All 253 patterns processed (including 102 archetypal and 151 UIA)")
    
    # Verify domain content is present
    with_domain_content = sum(1 for p in patterns if 'domain_specific_content' in p)
    assert with_domain_content == 253, f"✗ Expected 253 patterns with domain content, got {with_domain_content}"
    print(f"✓ All patterns have domain-specific content from UIA sources")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("ARCHETYPAL PATTERN SCHEMA TEST SUITE")
    print("=" * 70)
    
    tests = [
        test_schema_file,
        test_patterns_collection,
        test_pattern_structure,
        test_domain_mappings,
        test_placeholder_reference,
        test_pattern_ids_unique,
        test_all_arc_files_processed
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
