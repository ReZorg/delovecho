# Individual Pattern Files

This directory contains individual OpenCog Atomese (.scm) files for each pattern in Christopher Alexander's "A Pattern Language".

## Purpose

Individual pattern files allow you to:
- **Load specific patterns** without loading the entire knowledge base
- **Navigate patterns easily** with a simple file-per-pattern structure
- **Reduce memory footprint** for focused applications
- **Modular integration** with other systems

## File Naming Convention

Files are named using the pattern: `pattern_XXX.scm`

Where `XXX` is the zero-padded pattern number:
- `pattern_000.scm` - Pattern 0: Pattern Language (meta-pattern)
- `pattern_001.scm` - Pattern 1: Independent Regions
- `pattern_007.scm` - Pattern 7: The Countryside
- etc.

## File Contents

Each file contains the complete Atomese representation of a single pattern, including:

### Standard Properties
- `has-number`: Pattern number
- `has-name`: Pattern name
- `has-evidence-level`: Evidence level (asterisks)
- `has-problem-summary`: Brief problem description
- `has-solution`: Solution description
- `has-context`: Context information

### Enhanced Properties
- `has-problem-details`: Detailed problem description
- `has-diagram`: Reference to pattern diagram
- `has-connections`: Examples and connections to other patterns

### Relationships
- `ImplicationLink`: Dependencies (preceding/following patterns)
- Can be extended with relationship types (see `../relationship_types.scm`)

## Usage

### Loading a Single Pattern

```scheme
; Load Pattern 0 (the meta-pattern)
(load "opencog_atomese/patterns/pattern_000.scm")
```

### Loading Multiple Patterns

```scheme
; Load a specific set of patterns
(load "opencog_atomese/patterns/pattern_000.scm")
(load "opencog_atomese/patterns/pattern_001.scm")
(load "opencog_atomese/patterns/pattern_007.scm")
```

### Loading All Patterns Programmatically

```scheme
; Load all individual pattern files (Scheme)
(define (load-all-patterns directory)
  (for-each
    (lambda (file)
      (when (string-suffix? ".scm" file)
        (load (string-append directory "/" file))))
    (directory-files directory)))

; Use it
(load-all-patterns "opencog_atomese/patterns")
```

### Python Helper to Load Patterns

```python
from pathlib import Path

def load_patterns(atomspace, patterns_dir="opencog_atomese/patterns"):
    """Load individual pattern files into an AtomSpace."""
    patterns_path = Path(patterns_dir)
    pattern_files = sorted(patterns_path.glob("pattern_*.scm"))
    
    for pattern_file in pattern_files:
        atomspace.load_file(str(pattern_file))
    
    return len(pattern_files)

# Usage with OpenCog Python bindings
from opencog.atomspace import AtomSpace
atomspace = AtomSpace()
num_loaded = load_patterns(atomspace)
print(f"Loaded {num_loaded} patterns")
```

## Query Examples

Once patterns are loaded, you can query them:

### Find Pattern by Number

```scheme
(GetLink
  (VariableNode "$pattern")
  (EvaluationLink
    (PredicateNode "has-number")
    (ListLink
      (VariableNode "$pattern")
      (ConceptNode "7"))))
```

### Find Pattern by Name

```scheme
(GetLink
  (VariableNode "$pattern")
  (EvaluationLink
    (PredicateNode "has-name")
    (ListLink
      (VariableNode "$pattern")
      (ConceptNode "The Countryside"))))
```

### Get Pattern's Solution

```scheme
(GetLink
  (VariableNode "$solution")
  (EvaluationLink
    (PredicateNode "has-solution")
    (ListLink
      (ConceptNode "Pattern-7-The Countryside")
      (VariableNode "$solution"))))
```

## Integration with Full Knowledge Base

Individual pattern files are compatible with the complete pattern_language.scm file. You can:

1. **Use individual files for development**: Test with specific patterns
2. **Use complete file for production**: Load entire knowledge base at once
3. **Mix both approaches**: Load base file, then override specific patterns

```scheme
; Approach 1: Individual patterns only
(load "opencog_atomese/patterns/pattern_000.scm")
(load "opencog_atomese/patterns/pattern_001.scm")

; Approach 2: Complete knowledge base
(load "opencog_atomese/pattern_language.scm")

; Approach 3: Base + specific patterns
(load "opencog_atomese/pattern_language.scm")
; Override or extend specific patterns if needed
```

## Benefits for Different Use Cases

### Research & Development
- Load only patterns relevant to your study
- Iterate quickly on pattern modifications
- Easy to compare different pattern versions

### AI & Reasoning Systems
- Selective knowledge base loading
- Memory-efficient for resource-constrained systems
- Dynamic pattern loading based on context

### Educational Tools
- Progressive pattern introduction
- Focus on specific pattern categories
- Build custom learning sequences

### Pattern Language Extensions
- Easy to add new patterns
- Override patterns with domain-specific versions
- Maintain separate pattern collections

## File Statistics

Current status:
- **1 pattern file** available (meta-pattern)
- Additional patterns can be generated by extending `generate_enhanced_atomese.py`

To generate all 253 individual pattern files, the generator script needs access to the complete pattern data.

## See Also

- `../pattern_language_enhanced.scm` - Enhanced properties for all patterns
- `../relationship_types.scm` - Pattern relationship type definitions
- `../ENHANCEMENTS.md` - Documentation for all enhancements
- `../../README.md` - Main project documentation
- `../../IMPLEMENTATION_SUMMARY.md` - Implementation overview
