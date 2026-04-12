# p235

This repository contains collections of design patterns and organizational metaphors with formal specifications.

## 📖 Documentation

### Formal Specifications
- **[Formal Specification Summary](FORMAL_SPECIFICATION_SUMMARY.md)** - Complete overview of architecture and Z++ specifications
- **[docs/](docs/)** - Comprehensive technical documentation (2,328 lines)
  - Architecture overview with Mermaid diagrams
  - Z++ formal specifications (data model, system state, operations, integrations)
  - Usage guide for specifications

### Pattern Collections

- **APL**: Christopher Alexander's "A Pattern Language" (253 patterns) - architectural and urban design patterns
- **UIA**: Union of International Associations "Patterns & Metaphors" (253 patterns) - organizational and conceptual patterns

## Markdown Versions

The `markdown/` directory contains converted versions of all APL and UIA pages in markdown format for improved readability and accessibility:

- **`markdown/apl/`**: 253 A Pattern Language patterns (apl001.md - apl253.md)
- **`markdown/uia/`**: 253 UIA Patterns & Metaphors (12610010.md - 12612530.md)
- **`markdown/arc/`**: 102 Archetypal Patterns extracted from UIA templates with domain-specific placeholders

See `markdown/README.md` for detailed information about the conversion process and markdown structure.

## Pattern Language Schema

The repository includes formalized JSON schemas for both the Pattern Language and Archetypal Patterns:

### APL Pattern Language Schema

- **Pattern Language Schema** (`pattern_language_generated.json`) - Complete meta-pattern, categories, and sequences
- **Pattern Sequences** (`pattern_sequences.json`) - All 36 pattern sequences with emergent phenomena
- **Categories** (`category_*.json`) - Towns, Buildings, and Construction categories

See `PATTERN_SCHEMA_README.md` for detailed information about the APL schema structure.

### Archetypal Pattern Schema

- **Archetypal Pattern Schema** (`archetypal_pattern_schema.json`) - JSON schema for archetypal patterns
- **Archetypal Patterns** (`archetypal_patterns.json`) - All 102 archetypal patterns with domain mappings
- **Placeholder Reference** (`archetypal_placeholders.json`) - Complete placeholder documentation

Archetypal patterns use the format: `"generic {{domain-specific}} generic"` and can be transformed across:
- **Physical** - Spatial, material, architectural domains
- **Social** - Organizational, community, institutional domains
- **Conceptual** - Knowledge, theoretical, paradigmatic domains
- **Psychic** - Awareness, consciousness, mental domains

See `ARCHETYPAL_SCHEMA_README.md` for detailed information about the archetypal pattern schema.

### Generating Schemas

```bash
# Generate APL Pattern Language schema
python3 generate_pattern_schema.py

# Generate Archetypal Pattern schema
python3 generate_archetypal_schema.py
```

### Testing Schemas

```bash
# Test APL schema (if tests exist)
python3 validate_schema.py

# Test Archetypal schema
python3 test_archetypal_schema.py
```

### Demo Schemas

```bash
# Demo APL schema
python3 demo_pattern_schema.py

# Demo Archetypal schema
python3 demo_archetypal_schema.py
```

## OpenCog Atomese Representation

The Pattern Language has been converted to OpenCog's Atomese format for knowledge representation and pattern matching:

- **`opencog_atomese/`** - Complete Atomese hypergraph representation in Scheme format
  - `pattern_language.scm` - Complete representation
  - `meta_pattern.scm` - Meta-pattern
  - `categories.scm` - Categories with InheritanceLinks
  - `sequences.scm` - Sequences with MemberLinks
  - **Enhanced Features:**
    - `pattern_language_enhanced.scm` - Enhanced with diagrams, details, and connections
    - `relationship_types.scm` - Pattern relationship types (complement, conflict, alternative)
    - `patterns/` - Individual .scm files for modular loading

The Atomese format enables:
- Pattern matching and reasoning in OpenCog
- Hypergraph queries for pattern relationships
- Knowledge graph navigation and inference
- Integration with AI/AGI systems

See `opencog_atomese/README.md` for usage examples and `opencog_atomese/ENHANCEMENTS.md` for enhanced features documentation.

### Generating Atomese Files

```bash
# Generate base Atomese files
python3 generate_opencog_atomese.py

# Generate enhanced features
python3 generate_enhanced_atomese.py
```

### Testing Atomese Files

```bash
# Test base files
python3 test_opencog_atomese.py

# Test enhanced features
python3 test_enhanced_atomese.py
```

### Demo Enhanced Features

```bash
python3 demo_enhanced_atomese.py
```