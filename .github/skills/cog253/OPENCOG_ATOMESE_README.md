# OpenCog Atomese Pattern Language Implementation

## Overview

This implementation converts Christopher Alexander's "A Pattern Language" into OpenCog's Atomese format, enabling knowledge representation, pattern matching, and reasoning capabilities within the OpenCog cognitive architecture.

## What is Atomese?

Atomese is OpenCog's knowledge representation language that represents information as a hypergraph (metagraph) where:
- **Nodes** represent concepts, predicates, and variables
- **Links** represent relationships between nodes
- The hypergraph structure enables sophisticated pattern matching and inference

## Implementation Details

### Architecture

```
JSON Schema (pattern_language_generated.json)
    ↓
Atomese Converter (generate_opencog_atomese.py)
    ↓
Atomese Files (.scm format)
    ↓
OpenCog AtomSpace (hypergraph database)
```

### Generated Files

Located in `opencog_atomese/`:

1. **pattern_language.scm** (4,714 lines)
   - Complete Atomese representation
   - All patterns, categories, and sequences
   - Ready for direct loading into OpenCog

2. **meta_pattern.scm** (1,319 lines)
   - Pattern Language meta-pattern (Pattern-0)
   - ImplicationLinks to all 253 patterns

3. **categories.scm** (1,126 lines)
   - Towns, Buildings, Construction categories
   - InheritanceLinks for pattern categorization

4. **sequences.scm** (2,267 lines)
   - All 36 pattern sequences
   - MemberLinks for sequence membership
   - Emergent phenomena descriptions

5. **README.md**
   - Usage documentation
   - Pattern matching examples
   - OpenCog integration guide

### Atomese Structure

#### Node Types Used

- **ConceptNode**: Represents patterns, categories, sequences, and values
  ```scheme
  (ConceptNode "Pattern-0-Pattern Language")
  (ConceptNode "Category-Towns")
  (ConceptNode "Sequence-7-Local centers")
  ```

- **PredicateNode**: Represents properties and relationships
  ```scheme
  (PredicateNode "has-name")
  (PredicateNode "has-problem-summary")
  (PredicateNode "has-solution")
  (PredicateNode "has-emergent-phenomena")
  ```

#### Link Types Used

- **EvaluationLink**: Property assertions
  ```scheme
  (EvaluationLink
    (PredicateNode "has-name")
    (ListLink
      (ConceptNode "Pattern-0-Pattern Language")
      (ConceptNode "Pattern Language")))
  ```

- **InheritanceLink**: Category memberships
  ```scheme
  (InheritanceLink
    (ConceptNode "Pattern-42")
    (ConceptNode "Category-Towns"))
  ```

- **ImplicationLink**: Pattern dependencies
  ```scheme
  (ImplicationLink
    (ConceptNode "Pattern-0-Pattern Language")
    (ConceptNode "Pattern-1"))
  ```

- **MemberLink**: Sequence memberships
  ```scheme
  (MemberLink
    (ConceptNode "Pattern-28")
    (ConceptNode "Sequence-7-Local centers"))
  ```

- **ListLink**: Ordered collections for arguments
  ```scheme
  (ListLink
    (ConceptNode "Pattern-0-Pattern Language")
    (ConceptNode "Pattern Language"))
  ```

### Hypergraph Properties

The generated Atomese creates a rich knowledge hypergraph:

- **253 Patterns** represented as ConceptNodes with properties
- **3 Categories** organizing patterns hierarchically
- **36 Sequences** grouping related patterns
- **253 ImplicationLinks** from meta-pattern to all patterns
- **253 InheritanceLinks** for pattern-category relationships
- **260 MemberLinks** for pattern-sequence relationships
- **126+ EvaluationLinks** for property assertions

Total: ~1,900 nodes and ~800 links

## Usage

### Generation

Generate Atomese files from JSON schema:
```bash
python3 generate_opencog_atomese.py
```

### Validation

Validate generated Atomese files:
```bash
python3 test_opencog_atomese.py
```

### Demonstration

View examples and statistics:
```bash
python3 demo_opencog_atomese.py
```

### Query Examples

Run example queries:
```bash
python3 example_atomese_queries.py
```

## OpenCog Integration

### Loading into AtomSpace

```scheme
; Start Guile Scheme REPL
$ guile

; Load OpenCog modules
(use-modules (opencog))
(use-modules (opencog exec))

; Load Pattern Language
(load "opencog_atomese/pattern_language.scm")
```

### Pattern Matching Queries

**Query 1: Find all patterns in Towns category**
```scheme
(cog-execute!
  (GetLink
    (VariableNode "$pattern")
    (InheritanceLink
      (VariableNode "$pattern")
      (ConceptNode "Category-Towns"))))
```

**Query 2: Find patterns in a specific sequence**
```scheme
(cog-execute!
  (GetLink
    (VariableNode "$pattern")
    (MemberLink
      (VariableNode "$pattern")
      (ConceptNode "Sequence-7-Local centers"))))
```

**Query 3: Find pattern dependencies**
```scheme
(cog-execute!
  (GetLink
    (VariableNode "$next")
    (ImplicationLink
      (ConceptNode "Pattern-0-Pattern Language")
      (VariableNode "$next"))))
```

**Query 4: Get pattern properties**
```scheme
(cog-execute!
  (GetLink
    (VariableNode "$solution")
    (EvaluationLink
      (PredicateNode "has-solution")
      (ListLink
        (ConceptNode "Pattern-0-Pattern Language")
        (VariableNode "$solution")))))
```

## Use Cases

### 1. Pattern Discovery
Query patterns by properties, categories, or relationships to discover relevant design patterns for specific problem domains.

### 2. Reasoning and Inference
Use OpenCog's reasoning engines (PLN, URE) to infer pattern relationships, dependencies, and applicable sequences.

### 3. Knowledge Graph Navigation
Traverse the pattern hypergraph to explore related patterns, emergent phenomena, and design sequences.

### 4. AI/AGI Integration
Integrate pattern language knowledge into AI systems for automated design assistance, pattern recommendation, and problem-solving.

### 5. Pattern Analytics
Analyze pattern usage, relationships, and effectiveness using graph algorithms and machine learning.

### 6. Cross-Domain Mapping
Map patterns across different domains by analyzing structural similarities in the hypergraph.

## Technical Specifications

### File Statistics

| File | Lines | ConceptNodes | PredicateNodes | Links |
|------|-------|--------------|----------------|-------|
| pattern_language.scm | 4,714 | 1,896 | 126 | 779 |
| meta_pattern.scm | 1,319 | 519 | 6 | 259 |
| categories.scm | 1,126 | 533 | 12 | 265 |
| sequences.scm | 2,267 | 844 | 108 | 404 |
| **Total** | **9,426** | **3,792** | **252** | **1,707** |

### Validation Status

✅ All Scheme syntax valid (balanced parentheses)
✅ All expected node types present
✅ All expected link types present
✅ Structure consistent with source JSON
✅ All 253 patterns represented
✅ All 3 categories represented
✅ All 36 sequences represented

## Scripts and Tools

### Core Implementation
- `generate_opencog_atomese.py` - Main converter (384 lines)
- Converts JSON schema to Atomese format
- Generates 4 .scm files + README

### Testing and Validation
- `test_opencog_atomese.py` - Validation suite (221 lines)
- Checks syntax, structure, and consistency
- Ensures OpenCog compatibility

### Demonstrations
- `demo_opencog_atomese.py` - Interactive demo (261 lines)
- Shows file statistics and structure examples
- Demonstrates pattern matching queries

### Examples
- `example_atomese_queries.py` - Query examples (215 lines)
- 6 different query types demonstrated
- Pattern matching capability showcase

## Benefits of Atomese Representation

1. **Uniform Representation**: Patterns, categories, and sequences represented consistently
2. **Pattern Matching**: Built-in support for complex graph queries
3. **Reasoning**: Integration with PLN and other reasoning engines
4. **Scalability**: Efficient hypergraph storage and retrieval
5. **Interoperability**: Standard format for OpenCog ecosystem
6. **Extensibility**: Easy to add new patterns and relationships
7. **Graph Algorithms**: Native support for graph traversal and analysis

## Comparison with JSON Schema

| Aspect | JSON Schema | Atomese |
|--------|-------------|---------|
| Format | Hierarchical JSON | Hypergraph (Scheme) |
| Queries | Manual parsing | Pattern matcher |
| Reasoning | Not supported | PLN, URE engines |
| Graph ops | Manual implementation | Native support |
| AI integration | Custom code needed | Built-in |
| Scalability | File-based | Database-backed |

## Future Enhancements

Potential extensions to this implementation:

1. **Individual Pattern Files**: Generate separate .scm files for each pattern
2. **Pattern Properties**: Add more detailed pattern properties (diagrams, examples)
3. **Relationships**: Encode additional pattern relationships (conflicts, complements)
4. **Reasoning Rules**: Add PLN rules for pattern inference
5. **Visualizations**: Generate graph visualizations of pattern relationships
6. **Query Interface**: Web API for pattern queries
7. **Integration Examples**: Demonstrate integration with OpenCog reasoning engines

## References

- [OpenCog](https://opencog.org/) - OpenCog project homepage
- [Atomese Documentation](https://wiki.opencog.org/w/Atomese) - Atomese language guide
- [Pattern Matcher](https://wiki.opencog.org/w/Pattern_Matcher) - OpenCog pattern matching
- [AtomSpace](https://github.com/opencog/atomspace) - OpenCog hypergraph database
- [A Pattern Language](http://www.patternlanguage.com/) - Christopher Alexander's work

## License

This implementation follows the same license as the parent repository. The generated Atomese files are derived from Christopher Alexander's "A Pattern Language" and maintain appropriate attribution.

## Contributors

Generated as part of the cog253 repository to enable OpenCog integration with Christopher Alexander's Pattern Language.
