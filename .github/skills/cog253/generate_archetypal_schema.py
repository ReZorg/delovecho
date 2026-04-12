#!/usr/bin/env python3
"""
Generate Archetypal Pattern Schema from markdown/arc/ directory.

This script processes the archetypal patterns (arc_*.md files) and creates:
1. archetypal_pattern_schema.json - JSON schema definition
2. archetypal_patterns.json - Complete collection of archetypal patterns
3. archetypal_placeholders.json - Placeholder mapping definitions

Based on the archetypal patterns in markdown/arc/ which use the format:
"some-generic {{domain-specific}} more-generic"
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def extract_pattern_id_and_name(content: str) -> tuple[str, str]:
    """Extract pattern ID and name from the markdown header."""
    # Look for pattern like: # 12610010 - Independent domains (Archetypal)
    match = re.search(r'^#\s+(\d+)\s*-\s*([^\(]+)\s*\(Archetypal\)', content, re.MULTILINE)
    if match:
        return match.group(1), match.group(2).strip()
    return "", ""


def extract_archetypal_pattern(content: str) -> str:
    """Extract the archetypal pattern text."""
    # Find text between "## Archetypal Pattern" and "## Domain Placeholders"
    match = re.search(r'## Archetypal Pattern\s+(.+?)\s+## Domain Placeholders', 
                     content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_domain_placeholders(content: str) -> Dict[str, Dict[str, str]]:
    """Extract domain placeholder mappings."""
    placeholders = {}
    
    # Find the Domain Placeholders section
    match = re.search(r'## Domain Placeholders\s+.*?\n\n(.+?)\n\n## Original Template', 
                     content, re.DOTALL)
    if not match:
        return placeholders
    
    placeholder_section = match.group(1)
    
    # Parse each placeholder line like:
    # - `{{domains}}` → Physical: regions/areas | Social: functional domains/communities | ...
    for line in placeholder_section.split('\n'):
        line = line.strip()
        if not line.startswith('- `{{'):
            continue
            
        # Extract placeholder name
        placeholder_match = re.match(r'-\s*`{{([^}]+)}}`\s*→\s*(.+)', line)
        if not placeholder_match:
            continue
            
        placeholder_name = placeholder_match.group(1)
        mappings_text = placeholder_match.group(2)
        
        # Parse domain mappings
        domain_mappings = {}
        for mapping in mappings_text.split('|'):
            mapping = mapping.strip()
            if ':' in mapping:
                domain, value = mapping.split(':', 1)
                domain_mappings[domain.strip().lower()] = value.strip()
        
        placeholders[placeholder_name] = domain_mappings
    
    return placeholders


def extract_original_template(content: str) -> str:
    """Extract the original template text."""
    match = re.search(r'## Original Template\s+(.+?)\s+---', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_placeholders_from_pattern(pattern_text: str) -> List[str]:
    """Extract all placeholder names used in the pattern text."""
    return re.findall(r'{{([^}]+)}}', pattern_text)


def load_archetypal_pattern(filepath: Path) -> Optional[Dict[str, Any]]:
    """Load and parse an archetypal pattern markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern_id, name = extract_pattern_id_and_name(content)
        if not pattern_id:
            return None
        
        archetypal_pattern = extract_archetypal_pattern(content)
        domain_placeholders = extract_domain_placeholders(content)
        original_template = extract_original_template(content)
        placeholders_used = extract_placeholders_from_pattern(archetypal_pattern)
        
        return {
            "pattern_id": pattern_id,
            "name": name,
            "archetypal_pattern": archetypal_pattern,
            "original_template": original_template,
            "placeholders": placeholders_used,
            "domain_mappings": domain_placeholders,
            "source_file": filepath.name
        }
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def generate_archetypal_schema() -> Dict[str, Any]:
    """Generate JSON schema for archetypal patterns."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Archetypal Pattern Schema",
        "description": "Schema for UIA Archetypal Patterns with domain-specific placeholders",
        "type": "object",
        "definitions": {
            "ArchetypalPattern": {
                "type": "object",
                "properties": {
                    "pattern_id": {
                        "type": "string",
                        "pattern": "^\\d+$",
                        "description": "UIA pattern identifier (e.g., '12610010')"
                    },
                    "name": {
                        "type": "string",
                        "description": "Pattern name"
                    },
                    "archetypal_pattern": {
                        "type": "string",
                        "description": "Pattern text with {{placeholder}} format for domain-specific terms"
                    },
                    "original_template": {
                        "type": "string",
                        "description": "Original template text without placeholders"
                    },
                    "placeholders": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of placeholder names used in this pattern"
                    },
                    "domain_mappings": {
                        "type": "object",
                        "description": "Mapping of placeholders to domain-specific terms",
                        "patternProperties": {
                            "^[a-z-]+$": {
                                "type": "object",
                                "patternProperties": {
                                    "^[a-z]+$": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    },
                    "source_file": {
                        "type": "string",
                        "description": "Source markdown file name"
                    }
                },
                "required": ["pattern_id", "name", "archetypal_pattern", "placeholders"],
                "additionalProperties": False
            },
            "DomainMapping": {
                "type": "object",
                "properties": {
                    "placeholder": {
                        "type": "string",
                        "description": "Placeholder name (without {{ }})"
                    },
                    "domains": {
                        "type": "object",
                        "properties": {
                            "physical": {"type": "string"},
                            "social": {"type": "string"},
                            "conceptual": {"type": "string"},
                            "psychic": {"type": "string"}
                        },
                        "description": "Domain-specific mappings for this placeholder"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what this placeholder represents"
                    }
                },
                "required": ["placeholder", "domains"]
            },
            "ArchetypalPatternCollection": {
                "type": "object",
                "properties": {
                    "meta": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "total_patterns": {"type": "integer"},
                            "source_directory": {"type": "string"},
                            "format": {"type": "string"}
                        }
                    },
                    "patterns": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/ArchetypalPattern"
                        }
                    },
                    "placeholder_definitions": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/DomainMapping"
                        }
                    }
                },
                "required": ["meta", "patterns"]
            }
        },
        "oneOf": [
            {"$ref": "#/definitions/ArchetypalPattern"},
            {"$ref": "#/definitions/DomainMapping"},
            {"$ref": "#/definitions/ArchetypalPatternCollection"}
        ]
    }


def aggregate_placeholder_definitions(patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate all unique placeholder definitions from patterns."""
    all_placeholders = {}
    
    for pattern in patterns:
        for placeholder_name, domain_mappings in pattern.get("domain_mappings", {}).items():
            if placeholder_name not in all_placeholders:
                all_placeholders[placeholder_name] = {
                    "placeholder": placeholder_name,
                    "domains": domain_mappings,
                    "description": f"Domain-specific mappings for {placeholder_name}"
                }
    
    return list(all_placeholders.values())


def generate_archetypal_patterns() -> Dict[str, Any]:
    """Generate the complete archetypal pattern collection."""
    arc_dir = Path("markdown/arc")
    
    # Load all archetypal pattern files
    patterns = []
    pattern_files = sorted(arc_dir.glob("arc_*.md"))
    
    print(f"Found {len(pattern_files)} archetypal pattern files")
    
    for filepath in pattern_files:
        pattern = load_archetypal_pattern(filepath)
        if pattern:
            patterns.append(pattern)
    
    print(f"Successfully loaded {len(patterns)} patterns")
    
    # Aggregate placeholder definitions
    placeholder_definitions = aggregate_placeholder_definitions(patterns)
    
    # Create the collection
    collection = {
        "meta": {
            "title": "UIA Archetypal Patterns",
            "description": "Archetypal patterns extracted from UIA templates with domain-specific placeholders",
            "total_patterns": len(patterns),
            "source_directory": "markdown/arc",
            "format": "generic {{domain-specific}} generic"
        },
        "patterns": patterns,
        "placeholder_definitions": placeholder_definitions
    }
    
    return collection


def generate_placeholder_reference() -> Dict[str, Any]:
    """Generate a comprehensive placeholder reference document."""
    arc_dir = Path("markdown/arc")
    
    # Collect all placeholder usage
    placeholder_usage = {}
    pattern_files = sorted(arc_dir.glob("arc_*.md"))
    
    for filepath in pattern_files:
        pattern = load_archetypal_pattern(filepath)
        if not pattern:
            continue
        
        for placeholder_name, domain_mappings in pattern.get("domain_mappings", {}).items():
            if placeholder_name not in placeholder_usage:
                placeholder_usage[placeholder_name] = {
                    "placeholder": placeholder_name,
                    "domains": domain_mappings,
                    "used_in_patterns": []
                }
            
            placeholder_usage[placeholder_name]["used_in_patterns"].append({
                "pattern_id": pattern["pattern_id"],
                "pattern_name": pattern["name"]
            })
    
    return {
        "title": "Archetypal Pattern Placeholder Reference",
        "description": "Complete reference of all placeholders used in archetypal patterns",
        "total_placeholders": len(placeholder_usage),
        "placeholders": list(placeholder_usage.values())
    }


def main():
    """Main function to generate archetypal pattern schema and specifications."""
    print("=" * 70)
    print("Generating Archetypal Pattern Schema from markdown/arc/")
    print("=" * 70)
    
    # Generate schema
    print("\n1. Generating JSON Schema...")
    schema = generate_archetypal_schema()
    schema_file = Path("archetypal_pattern_schema.json")
    with open(schema_file, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {schema_file}")
    
    # Generate pattern collection
    print("\n2. Generating Archetypal Pattern Collection...")
    patterns = generate_archetypal_patterns()
    patterns_file = Path("archetypal_patterns.json")
    with open(patterns_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Loaded {patterns['meta']['total_patterns']} patterns")
    print(f"   ✓ Found {len(patterns['placeholder_definitions'])} unique placeholders")
    print(f"   ✓ Saved to: {patterns_file}")
    
    # Generate placeholder reference
    print("\n3. Generating Placeholder Reference...")
    placeholder_ref = generate_placeholder_reference()
    placeholder_file = Path("archetypal_placeholders.json")
    with open(placeholder_file, 'w', encoding='utf-8') as f:
        json.dump(placeholder_ref, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Documented {placeholder_ref['total_placeholders']} placeholders")
    print(f"   ✓ Saved to: {placeholder_file}")
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"\nFiles created:")
    print(f"  • {schema_file} - JSON schema definition")
    print(f"  • {patterns_file} - All {patterns['meta']['total_patterns']} archetypal patterns")
    print(f"  • {placeholder_file} - Placeholder reference with usage")
    
    print(f"\nPattern Statistics:")
    print(f"  • Total patterns: {patterns['meta']['total_patterns']}")
    print(f"  • Unique placeholders: {len(patterns['placeholder_definitions'])}")
    
    print(f"\nPlaceholder types:")
    for placeholder in sorted(patterns['placeholder_definitions'], key=lambda x: x['placeholder']):
        print(f"  • {{{{{placeholder['placeholder']}}}}} - used in archetypal patterns")
    
    print("\n✓ Schema generation complete!")


if __name__ == "__main__":
    main()
