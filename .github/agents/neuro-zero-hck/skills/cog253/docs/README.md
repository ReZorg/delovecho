# Pattern Language System - Formal Specifications

This directory contains comprehensive technical architecture documentation and Z++ formal specifications for the Pattern Language System.

## Overview

The Pattern Language System implements Christopher Alexander's "A Pattern Language" (APL) and the Union of International Associations' "Patterns & Metaphors" (UIA) with formal mathematical specifications and cross-domain transformation capabilities.

## Documentation Structure

### 1. Architecture Documentation

**`architecture_overview.md`** - Complete system architecture with Mermaid diagrams
- High-level system architecture
- Component interactions
- Data flow diagrams
- Technology stack
- Pattern language components
- Domain transformation architecture
- Integration boundaries
- Performance characteristics

### 2. Z++ Formal Specifications

The formal specifications provide mathematically rigorous definitions of:

#### **`data_model.zpp`** - Data Layer Formalization
- Base types and enumerations (PatternNumber, Domain, PlaceholderName)
- APL Pattern Language structures (Pattern, PatternSequence, PatternCategory)
- Archetypal Pattern structures (ArchetypalPattern, DomainMapping)
- Domain transformation structures (TransformedPattern)
- Validation predicates (ValidPattern, ValidArchetypalPattern)

**Key Invariants:**
- Pattern numbers: 0-253 (0 = meta-pattern)
- Asterisk levels: 0-2 (evidence quality)
- 3 categories: Towns (1-94), Buildings (95-204), Construction (205-253)
- 36 pattern sequences with emergent phenomena
- 102 archetypal patterns with 4-domain mappings

#### **`system_state.zpp`** - System State Specification
- Pattern collection state (PatternRegistry, CategoryRegistry, SequenceRegistry)
- Archetypal pattern state (ArchetypalRegistry, DomainMappingCache)
- Schema and validation state (SchemaRegistry, ValidationState)
- File system state (FileSystemState)
- Transformation context (TransformationContext)
- Complete system state (PatternLanguageSystem)

**State Invariants:**
- All 253 APL patterns indexed and validated
- All 102 archetypal patterns with complete domain mappings
- Cross-registry consistency (patterns exist in all referencing registries)
- System completeness (all expected patterns loaded)
- Schema validation consistency

#### **`operations.zpp`** - Operations Specification
- Pattern loading operations (LoadPattern, LoadMetaPattern, LoadArchetypalPattern)
- Pattern query operations (GetPattern, GetPatternsInSequence, GetPatternsInCategory)
- Domain transformation operations (TransformToDomain, TransformToPhysical)
- Schema generation operations (GeneratePatternSchema, GenerateArchetypalSchema)
- Validation operations (ValidatePattern, ValidateArchetypalPattern)
- Batch operations (LoadAllPatterns, ValidateAllPatterns, TransformAllToAllDomains)

**Operational Contracts:**
- Pre-conditions: Input validation requirements
- Post-conditions: State changes and output guarantees
- Success criteria: Validation and error handling
- State transformation: Δ (delta) notation for state changes
- Read-only operations: Ξ (xi) notation

#### **`integrations.zpp`** - External Integration Contracts
- File system integration (ReadMarkdownFile, WriteJSONFile)
- Markdown parsing (ParseMarkdownPattern, ParseArchetypalMarkdown)
- JSON schema validation (ValidateAgainstSchema, SerializeToJSON)
- OpenCog Atomese generation (GenerateAtomesePattern, GenerateAtomeseArchetypal)
- Helper functions (ValidJSON, ValidScheme, ApplySubstitutions)

**Integration Invariants:**
- File system consistency (generated files newer than sources)
- Schema validation consistency (all cached results current)
- JSON compliance (all outputs validate against schemas)
- Atomese validity (all generated Scheme code is valid)

## Key Concepts

### Pattern Language Hierarchy

```
Meta-Pattern (0)
├── Towns Category (1-94)
│   ├── Sequence 1-15
│   └── Patterns 1-94
├── Buildings Category (95-204)
│   ├── Sequence 16-28
│   └── Patterns 95-204
└── Construction Category (205-253)
    ├── Sequence 29-36
    └── Patterns 205-253
```

### Archetypal Pattern Transformation

```
Archetypal Template:
  "Balance between {{domains}} requires {{frameworks}}"

Domain Transformations:
  Physical:    "Balance between regions/areas requires cities/infrastructure"
  Social:      "Balance between communities requires institutions/systems"
  Conceptual:  "Balance between knowledge domains requires paradigms/theories"
  Psychic:     "Balance between modes of awareness requires mental structures"
```

### Domain Placeholder Dictionary

**Core Placeholders (10+ types):**
1. `{{domains}}` - Organizational units at highest level
2. `{{frameworks}}` - Structural systems and architectures
3. `{{elements}}` - Basic building blocks
4. `{{resources}}` - Available assets and capabilities
5. `{{organization-type}}` - Nature of organizing structure
6. `{{influence-type}}` - Type of effect or impact
7. `{{areas}}` - Regions or zones of activity
8. `{{positions}}` - Central or key locations
9. `{{patterns}}` - Recurring configurations
10. `{{modes}}` - Operating states or methods

Each placeholder maps to 4 domains: Physical, Social, Conceptual, Psychic

## Using the Specifications

### Understanding Z++ Notation

**State Schemas:**
- `Pattern` - Defines structure with fields and invariants
- `where` clause - Specifies constraints and invariants

**Operations:**
- `Δ` (Delta) - Operation modifies state (e.g., `ΔPatternRegistry`)
- `Ξ` (Xi) - Operation reads state without modification
- `?` suffix - Input parameter (e.g., `pattern_number?`)
- `!` suffix - Output parameter (e.g., `pattern!`)
- `'` (prime) - State after operation (e.g., `registry'`)

**Logical Operators:**
- `∧` - Logical AND
- `∨` - Logical OR
- `¬` - Logical NOT
- `⇒` - Implies
- `⟺` - If and only if

**Set Operators:**
- `∈` - Element of
- `∉` - Not element of
- `⊆` - Subset of
- `∪` - Union
- `∩` - Intersection
- `∅` - Empty set
- `ℙ` - Power set

**Sequence Operators:**
- `⟨⟩` - Empty sequence
- `⌢` - Sequence concatenation
- `#` - Cardinality/length

**Function Operators:**
- `⇶` - Partial function
- `→` - Total function
- `⊕` - Function override
- `dom` - Domain of function
- `ran` - Range of function

### Verification Examples

**Example 1: Verify pattern validity**
```
Given: Pattern p with number 42
Verify: ValidPattern(p)

Check:
  p.name ≠ "" ✓
  p.problem_summary ≠ "" ✓
  p.solution ≠ "" ✓
  p.number = 42 ✓ (in range 0-253)
  p.asterisks ∈ {0, 1, 2} ✓
  ∀ preceding ∈ p.preceding_patterns • preceding < 42 ✓
  ∀ following ∈ p.following_patterns • following > 42 ✓
```

**Example 2: Verify domain transformation**
```
Given: ArchetypalPattern ap with pattern_id "12610010"
Operation: TransformToDomain[ap, Physical]

Pre-conditions:
  ap ∈ dom archetypal_registry.patterns ✓
  ap.placeholders ≠ ⟨⟩ ✓
  ∀ ph ∈ ap.placeholders • ph ∈ dom domain_mappings ✓

Post-conditions:
  transformed.source_pattern_id = "12610010" ✓
  transformed.target_domain = Physical ✓
  ¬(transformed.transformed_text contains "{{") ✓
  success! = true ✓
```

## System Guarantees

### Completeness Guarantees
- ✅ All 253 APL patterns with validated structure
- ✅ All 102 archetypal patterns with 4-domain mappings
- ✅ All 36 sequences covering all patterns
- ✅ All 3 categories with correct pattern ranges

### Consistency Guarantees
- ✅ Pattern references resolve to existing patterns
- ✅ Sequences contain only patterns in their category
- ✅ Domain mappings complete for all placeholders
- ✅ Generated JSON validates against schemas

### Transformation Guarantees
- ✅ All placeholders replaced in successful transformations
- ✅ Domain mappings exist for all 4 domains
- ✅ Archetypal patterns preserve semantic structure
- ✅ 408 total transformations (102 patterns × 4 domains)

## References

### Source Materials
- Christopher Alexander, "A Pattern Language" (1977)
- Union of International Associations, "Patterns and Metaphors"
- OpenCog Atomese knowledge representation format

### Related Documentation in Repository
- `../README.md` - Repository overview
- `../PATTERN_SCHEMA_README.md` - APL schema documentation
- `../ARCHETYPAL_SCHEMA_README.md` - Archetypal pattern documentation
- `../ARCHETYPAL_PATTERNS_SUMMARY.md` - Pattern generation summary
- `../generic_vs_domain_specific_analysis.md` - Domain analysis
- `../domain_analysis_report.md` - Vocabulary analysis
- `../OPENCOG_ATOMESE_README.md` - Atomese representation guide

### Python Implementation
- `../generate_pattern_schema.py` - APL schema generator
- `../generate_archetypal_schema.py` - Archetypal pattern generator
- `../validate_schema.py` - Schema validator
- `../test_archetypal_schema.py` - Archetypal pattern tests
- `../generate_opencog_atomese.py` - Atomese generator

## Maintenance Notes

### Updating Specifications

When modifying the system:
1. Update data model first (`data_model.zpp`)
2. Update system state to reflect new structures (`system_state.zpp`)
3. Update operations that use modified structures (`operations.zpp`)
4. Update integration contracts if external interfaces change (`integrations.zpp`)
5. Verify all invariants still hold
6. Update architecture diagrams in `architecture_overview.md`

### Verification Checklist
- [ ] All invariants verified for modified schemas
- [ ] Operation pre/post-conditions still satisfied
- [ ] State transitions preserve system consistency
- [ ] Integration contracts remain valid
- [ ] Test implementations updated to match specs
- [ ] Architecture diagrams reflect current state

## License

These specifications document the Pattern Language System implementation in the cog253 repository.

---

*Generated: 2025-11-08*
*Version: 1.0*
*Format: Z++ Formal Specification Language*
