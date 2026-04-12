# Pattern Language Schema

This directory contains a formalized schema for Christopher Alexander's "A Pattern Language" based on the files in the `markdown/apl/` directory.

## Generated Files

### Core Schema
- **`pattern_schema.json`** - Base JSON Schema definition for Pattern Language structures
- **`pattern_language_generated.json`** - Complete Pattern Language with all components

### Categories (3)
- **`category_towns.json`** - Towns category (Patterns 1-94) with 15 sequences
- **`category_buildings.json`** - Buildings category (Patterns 95-204) with 13 sequences  
- **`category_construction.json`** - Construction category (Patterns 205-253) with 8 sequences

### Sequences
- **`pattern_sequences.json`** - All 36 Pattern Sequences with emergent phenomena descriptions

## Schema Structure

### Pattern Language Meta-Pattern

The Pattern Language itself is expressed as a meta-pattern using the same schema structure:

```json
{
  "number": 0,
  "name": "Pattern Language",
  "asterisks": 2,
  "problem_summary": "How to create a coherent design language that captures the deep structure of environments...",
  "solution": "Create a structured language of 253 interconnected patterns organized hierarchically...",
  "following_patterns": [1, 2, 3, ..., 253]
}
```

### Pattern Categories

Three main categories organize the 253 patterns:

1. **Towns** (1-94): Large-scale urban and regional patterns
2. **Buildings** (95-204): Building and space design patterns  
3. **Construction** (205-253): Building construction and detail patterns

Each category includes:
- Description and design process
- Pattern number range
- Associated sequences
- Emergent phenomena descriptions

### Pattern Sequences (36 Total)

Pattern sequences capture the essence of emergent phenomena produced by groups of related patterns:

#### Towns Sequences (1-15)
1. Regions instead of countries
2. Regional policies  
3. Major structures which define the city
4. Communities and neighborhoods
5. Community networks
6. Character of local environments
7. Local centers
8. Housing
9. Work
10. Local road and path network
11. Public open land
12. Local common land
13. Transformation of the family
14. Transformation of work and learning
15. Transformation of local shops and gathering places

#### Buildings Sequences (16-28)
16. The overall arrangement of a group of buildings
17. The position of individual buildings
18. Entrances, gardens, courtyards, roofs and terraces
19. Paths and squares
20. Gradients and connection of space
21. The most important areas and rooms (in a house)
22. The most important areas and rooms (in offices, workshops and public buildings)
23. Outbuildings and access to the street and gardens
24. Knit the inside of the building to the outside
25. Arrange the gardens, and the places in the gardens
26. Inside, attach necessary minor rooms and alcoves
27. Fine tune the shape and size of rooms and alcoves
28. Give the walls some depth

#### Construction Sequences (29-36)
29. Let the structure grow directly from your plans and your conception of the buildings
30. Work out the complete structural layout
31. Mark the column locations and erect the main frame
32. Fix the exact positions for openings and frame them
33. Put in the following subsidiary patterns
34. Put in the surfaces and indoor details
35. Build outdoor details
36. Complete the building

## Usage Instructions

The schema includes formalized usage instructions from the original Pattern Language:

### How to Use Patterns
1. Each pattern has an introductory paragraph linking to preceding patterns
2. A summary of the problem in bold
3. Problem details, background and manifestations
4. The solution in bold
5. A diagram of the solution
6. Links to smaller patterns needed to complete this pattern

### Choosing a Pattern Language
1. Find the pattern that best describes your project and bookmark it
2. Read the smaller patterns and bookmark applicable ones
3. Ignore preceding patterns unless you have power to create them
4. Proceed through the pattern hierarchy
5. Adjust the sequence by adding your own material where needed
6. Compress patterns together as densely as possible

### Pattern Hierarchies (Evidence Levels)

- **Two asterisks (★★)**: True invariants - impossible to solve without this pattern
- **One asterisk (★)**: Progress made toward invariant - improvement possible
- **No asterisks**: Solution provided but true invariant remains to be found

## Generation Process

This schema was generated from the following source files in `markdown/apl/`:

1. **APL - Home Main.md** → Pattern Language definition and meta-pattern
2. **Towns.md** → Towns category schema  
3. **Buildings.md** → Buildings category schema
4. **Construction.md** → Construction category schema
5. **aplbullets.md** → Pattern sequence headings and structure
6. **aplsummary.md** → Pattern sequence descriptions and context

## Validation

All generated files have been validated for:
- JSON schema compliance
- Required field presence
- Data type correctness
- Value range validation
- Cross-reference consistency

Run `python3 validate_schema.py` to validate the generated files.

## Example Usage

### Loading the Complete Pattern Language
```python
import json

with open('pattern_language_generated.json') as f:
    pattern_language = json.load(f)

# Access meta-pattern
meta = pattern_language['meta_pattern']
print(f"Meta-pattern: {meta['name']}")

# Access categories
for category in pattern_language['categories']:
    print(f"Category: {category['name']} (patterns {category['pattern_range']['start']}-{category['pattern_range']['end']})")

# Access sequences
for sequence in pattern_language['sequences']:
    print(f"Sequence {sequence['id']}: {sequence['heading']} ({sequence['category']})")
```

### Working with Individual Categories
```python
import json

# Load specific category
with open('category_towns.json') as f:
    towns = json.load(f)

print(f"Towns: {towns['description']}")
print(f"Process: {towns['process']}")

# Access sequences within category
for seq in towns['sequences']:
    print(f"  {seq['id']}: {seq['heading']}")
    print(f"    Patterns: {seq['patterns']}")
    print(f"    Emergent phenomena: {seq['emergent_phenomena']}")
```

### Using the JSON Schema for Validation
```python
import json
import jsonschema

# Load schema
with open('pattern_schema.json') as f:
    schema = json.load(f)

# Validate a pattern against schema
pattern = {
    "number": 1,
    "name": "Independent Regions",
    "problem_summary": "Metropolitan regions will not come to balance...",
    "solution": "Wherever possible, work toward the evolution of independent regions..."
}

jsonschema.validate(pattern, schema['definitions']['Pattern'])
```

## Files Generated

- ✅ **pattern_schema.json** (6,631 bytes) - Base JSON schema
- ✅ **pattern_language_generated.json** (41,767 bytes) - Complete structure  
- ✅ **category_towns.json** (6,445 bytes) - Towns category with 15 sequences
- ✅ **category_buildings.json** (6,810 bytes) - Buildings category with 13 sequences
- ✅ **category_construction.json** (4,144 bytes) - Construction category with 8 sequences
- ✅ **pattern_sequences.json** (15,559 bytes) - All 36 sequences

Total: 6 files, 81,356 bytes

## Related Files

- **`generate_pattern_schema.py`** - Generation script
- **`validate_schema.py`** - Validation script
- **Source files in `markdown/apl/`** - Original Pattern Language content