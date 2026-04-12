# Archetypal Pattern Schema

This document describes the Archetypal Pattern Schema generated from the UIA (Union of International Associations) patterns in the `markdown/arc/` directory.

## Overview

The Archetypal Pattern Schema provides a formal specification for the 102 archetypal patterns extracted from UIA templates. These patterns use a generic-domain-specific-generic format with placeholders that can be transformed across different domains:

- **Physical** - Spatial, material, architectural domains
- **Social** - Organizational, community, institutional domains  
- **Conceptual** - Knowledge, theoretical, paradigmatic domains
- **Psychic** - Awareness, consciousness, mental domains

## Format

Archetypal patterns follow the format:
```
"generic-terms {{domain-specific-placeholder}} more-generic-terms"
```

### Example

**Archetypal Pattern:**
```
Balance between {{domains}} will not be achieved unless each one is small 
and autonomous enough to be an independent sphere of {{influence-type}}.
```

**Domain Transformations:**
- **Physical**: "Balance between regions/areas will not be achieved..."
- **Social**: "Balance between functional domains/communities will not be achieved..."
- **Conceptual**: "Balance between knowledge domains will not be achieved..."
- **Psychic**: "Balance between modes of awareness will not be achieved..."

## Generated Files

### 1. archetypal_pattern_schema.json

JSON Schema definition for archetypal patterns. Defines the structure and validation rules for:
- `ArchetypalPattern` - Individual pattern structure
- `DomainMapping` - Placeholder to domain-specific term mappings
- `ArchetypalPatternCollection` - Complete collection structure

**Key Fields:**
- `pattern_id` - UIA pattern identifier (e.g., "12610010")
- `name` - Pattern name
- `archetypal_pattern` - Pattern text with {{placeholder}} format
- `original_template` - Original template without placeholders
- `placeholders` - List of placeholder names used
- `domain_mappings` - Mapping of placeholders to domain terms
- `domain_specific_content` - Full domain-specific implementations from UIA patterns
  - `physical` - Physical domain implementation (spatial, material, architectural)
  - `social` - Social domain implementation (organizational, community, institutional)
  - `conceptual` - Conceptual domain implementation (knowledge, theoretical, paradigmatic)
  - `psychic` - Psychic domain implementation (awareness, consciousness, mental)
- `source_file` - Source markdown file
- `broader_patterns` - Pattern IDs of broader (more general) patterns
- `narrower_patterns` - Pattern IDs of narrower (more specific) patterns

### 2. archetypal_patterns.json

Complete collection of all 253 archetypal patterns with metadata, domain mappings, and full domain-specific content from UIA patterns.

**Structure:**
```json
{
  "meta": {
    "title": "UIA Archetypal Patterns",
    "total_patterns": 253,
    "source_directory": "markdown/arc",
    "format": "generic {{domain-specific}} generic",
    "includes_domain_content": true,
    "patterns_with_domain_content": 253
  },
  "patterns": [ ... ],
  "placeholder_definitions": [ ... ]
}
```

**Pattern Structure:**
Each pattern includes:
- **Archetypal pattern** with placeholders
- **Domain mappings** for placeholder substitution
- **Domain-specific content** - Full implementations for each domain from UIA source
- **Pattern relationships** - Broader and narrower patterns

**Usage:**
```python
import json

with open('archetypal_patterns.json') as f:
    data = json.load(f)

# Access patterns
patterns = data['patterns']
first_pattern = patterns[0]

# Get archetypal pattern with placeholders
archetypal = first_pattern['archetypal_pattern']

# Get domain-specific content (from UIA source)
if 'domain_specific_content' in first_pattern:
    physical = first_pattern['domain_specific_content']['physical']
    social = first_pattern['domain_specific_content'].get('social', '')
    conceptual = first_pattern['domain_specific_content'].get('conceptual', '')
    psychic = first_pattern['domain_specific_content'].get('psychic', '')

# Or, transform archetypal pattern using domain mappings
mappings = first_pattern['domain_mappings']
physical_version = archetypal
for placeholder, domains in mappings.items():
    if 'physical' in domains:
        physical_version = physical_version.replace(
            f'{{{{{placeholder}}}}}', 
            domains['physical']
        )
```

### 3. archetypal_placeholders.json

Comprehensive reference of all placeholders with their domain mappings and usage.

**Structure:**
```json
{
  "title": "Archetypal Pattern Placeholder Reference",
  "total_placeholders": 10,
  "placeholders": [
    {
      "placeholder": "domains",
      "domains": {
        "physical": "regions/areas",
        "social": "functional domains/communities",
        "conceptual": "knowledge domains",
        "psychic": "modes of awareness"
      },
      "used_in_patterns": [ ... ]
    }
  ]
}
```

## Placeholder Types

The schema defines 10 core placeholders used across patterns:

| Placeholder | Physical | Social | Conceptual | Psychic |
|------------|----------|--------|------------|---------|
| `{{domains}}` | regions/areas | functional domains/communities | knowledge domains | modes of awareness |
| `{{frameworks}}` | cities/infrastructure | institutions/systems | paradigms/theories | mental structures |
| `{{elements}}` | materials/spaces | members/participants | concepts/ideas | perceptions/insights |
| `{{organization-type}}` | building/development | institution/community | framework/theory | structured awareness |
| `{{resources}}` | land/agriculture | social resources | creative resources | psychic resources |
| `{{influence-type}}` | influence | influence | insight | influence |
| `{{areas}}` | land/regions | functional areas | domains | modes of awareness |
| `{{positions}}` | central locations | central organizations | central frameworks | ordered modes |
| `{{patterns}}` | urban environments | organizational patterns | knowledge patterns | awareness patterns |
| `{{modes}}` | environments | modes of organization | modes of organization | modes of awareness |

## Pattern Statistics

- **Total Patterns:** 253 (all UIA patterns)
- **Archetypal Patterns (with templates):** 102
- **Source Files:** markdown/arc/arc_*.md and markdown/uia/*.md
- **Unique Placeholders:** 10
- **Domain Coverage:** Physical (253), Social (67), Conceptual (67), Psychic (67)
- **Patterns with All 4 Domains:** 67
- **Patterns with Physical Only:** 186

## Usage Examples

### Generate Archetypal Patterns

```bash
# Generate the schema and pattern specifications
python3 generate_archetypal_schema.py
```

This creates:
- `archetypal_pattern_schema.json` - Schema definition
- `archetypal_patterns.json` - Pattern collection  
- `archetypal_placeholders.json` - Placeholder reference

### Test the Schema

```bash
# Run validation tests
python3 test_archetypal_schema.py
```

Tests verify:
- Schema structure and validity
- Pattern completeness and format
- Domain mapping correctness
- Placeholder consistency

### Demonstrate Usage

```bash
# Run interactive demonstration
python3 demo_archetypal_schema.py
```

Demonstrates:
- Loading archetypal patterns
- Transforming to specific domains
- Querying by placeholder
- Multi-domain comparison
- Placeholder mapping reference

## Programmatic Usage

### Load and Transform Patterns

```python
import json

# Load patterns
with open('archetypal_patterns.json') as f:
    data = json.load(f)

# Get a pattern
pattern = data['patterns'][0]

# Transform to physical domain
def transform_pattern(pattern, domain):
    text = pattern['archetypal_pattern']
    for placeholder, mappings in pattern['domain_mappings'].items():
        if domain in mappings:
            text = text.replace(
                f'{{{{{placeholder}}}}}',
                mappings[domain]
            )
    return text

physical = transform_pattern(pattern, 'physical')
social = transform_pattern(pattern, 'social')
```

### Query Patterns

```python
# Find patterns using specific placeholder
def find_by_placeholder(patterns, placeholder):
    return [p for p in patterns 
            if placeholder in p['placeholders']]

# Find patterns about frameworks
framework_patterns = find_by_placeholder(
    data['patterns'], 
    'frameworks'
)

print(f"Found {len(framework_patterns)} patterns using frameworks")
```

### Generate Domain-Specific Collections

```python
# Generate all patterns for a specific domain
def generate_domain_collection(patterns, domain):
    return {
        'domain': domain,
        'patterns': [
            {
                'id': p['pattern_id'],
                'name': p['name'],
                'text': transform_pattern(p, domain)
            }
            for p in patterns
        ]
    }

physical_patterns = generate_domain_collection(
    data['patterns'], 
    'physical'
)
```

## Integration with Existing Schema

The Archetypal Pattern Schema complements the existing Pattern Language Schema:

- **Pattern Language Schema** (`pattern_schema.json`) - APL architectural patterns
- **Archetypal Pattern Schema** (`archetypal_pattern_schema.json`) - UIA organizational patterns

Both schemas follow similar structural principles but serve different purposes:
- APL patterns are concrete, domain-specific solutions
- Archetypal patterns are abstract templates that transform across domains

## Validation

The schema includes validation for:
- Pattern ID format (numeric string)
- Required fields presence
- Placeholder consistency
- Domain mapping completeness
- Array uniqueness

## Future Extensions

Potential extensions to the schema:

1. **Extended Domains** - Add network, cellular, OS, LLM domains
2. **Pattern Relationships** - Cross-reference related patterns
3. **Transformation Rules** - Formal rules for domain transformations
4. **Pattern Sequences** - Group patterns into meaningful sequences
5. **Emergent Properties** - Document emergent phenomena from pattern combinations

## Contributing

To add or modify archetypal patterns:

1. Update markdown files in `markdown/arc/`
2. Regenerate schema: `python3 generate_archetypal_schema.py`
3. Run tests: `python3 test_archetypal_schema.py`
4. Update documentation as needed

## References

- **Source**: Union of International Associations "Patterns & Metaphors" (253 patterns)
- **Format**: Based on Christopher Alexander's pattern language methodology
- **Directory**: `markdown/arc/` contains all archetypal pattern markdown files
- **README**: See `markdown/arc/README.md` for pattern generation details

## License

See LICENSE file in repository root.

---

*Generated from 102 UIA archetypal patterns with domain-specific placeholders*
