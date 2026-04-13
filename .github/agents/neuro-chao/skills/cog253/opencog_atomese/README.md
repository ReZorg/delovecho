# OpenCog Atomese Pattern Language

This directory contains OpenCog Atomese representations of Christopher Alexander's "A Pattern Language" converted from the JSON schema.

## Files

- `pattern_language.scm` - Complete Atomese representation (all patterns, categories, sequences)
- `meta_pattern.scm` - The Pattern Language meta-pattern
- `categories.scm` - The three categories (Towns, Buildings, Construction)
- `sequences.scm` - All 36 pattern sequences

## Atomese Structure

### Node Types

- **ConceptNode**: Represents patterns, categories, sequences, and values
- **PredicateNode**: Represents relationships and properties

### Link Types

- **EvaluationLink**: Property assertions (e.g., has-name, has-problem-summary)
- **InheritanceLink**: Category memberships (pattern belongs to category)
- **ImplicationLink**: Pattern dependencies (preceding/following patterns)
- **MemberLink**: Sequence membership (pattern belongs to sequence)
- **ListLink**: Ordered collections for EvaluationLink arguments

## Usage with OpenCog

Load these files into an OpenCog AtomSpace:

```scheme
(load "pattern_language.scm")
```

Or load individual components:

```scheme
(load "meta_pattern.scm")
(load "categories.scm")
(load "sequences.scm")
```

## Pattern Matching Examples

Query patterns by category:

```scheme
(GetLink
  (VariableNode "$pattern")
  (InheritanceLink
    (VariableNode "$pattern")
    (ConceptNode "Category-Towns")))
```

Query patterns in a sequence:

```scheme
(GetLink
  (VariableNode "$pattern")
  (MemberLink
    (VariableNode "$pattern")
    (ConceptNode "Sequence-1-Regions instead of countries")))
```

Find pattern dependencies:

```scheme
(GetLink
  (VariableNode "$next")
  (ImplicationLink
    (ConceptNode "Pattern-0-Pattern Language")
    (VariableNode "$next")))
```

## Hypergraph Properties

The Atomese representation creates a knowledge hypergraph where:

- Patterns are interconnected through ImplicationLinks (dependencies)
- Categories organize patterns hierarchically via InheritanceLinks
- Sequences group related patterns via MemberLinks
- Properties are attached via EvaluationLinks
- The structure supports pattern matching, reasoning, and inference

This enables OpenCog to:
- Query patterns by properties, relationships, or context
- Infer pattern dependencies and sequences
- Reason about design problems and solutions
- Navigate the pattern network for design guidance
