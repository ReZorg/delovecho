---
name: apl0
description: "Meta-Pattern 0: A Pattern Language"
---

# APL0 Instructions

## Overview
This is the meta-pattern that defines the entire Pattern Language system consisting of 253 interconnected patterns organized across multiple dimensions and scales.

## Structure
- **6 Dimensions**: dim0-dim5 (Archetypal, Template, Physical, Social, Conceptual, Interpersonal)
- **3 Categories**: cat1-cat3 (meaning varies by dimension)
- **36 Sequences**: Organized flows of related patterns
- **253 Patterns**: Individual design solutions

## Purpose
A Pattern Language is a philosophy of human use of space and analysis of what makes humans comfortable in the space they inhabit. It provides a structured way to understand and create environments that support human life.

## Key Concepts
1. **Hierarchical Organization**: From large-scale to small-scale patterns
2. **Network of Connections**: Each pattern links to related patterns
3. **Emergent Phenomena**: Sequences create synergies between patterns
4. **Cross-Dimensional**: Same patterns can be viewed through different dimensional lenses

## Dimensions

### dim0 - Archetypal (A)
Abstract patterns using placeholders like {{domains}}, {{frameworks}}, {{elements}} that can be instantiated in any domain.

### dim1 - Template (T)
Generic template patterns that serve as basis for domain-specific variations.

### dim2 - Physical (P)
Spatial, material, and architectural manifestations of patterns in the built environment.
- cat1: Towns (Patterns 1-94) - Large-scale patterns
- cat2: Buildings (Patterns 95-204) - Medium-scale patterns
- cat3: Construction (Patterns 205-253) - Small-scale patterns

### dim3 - Social (S)
Organizational, community, and institutional expressions of patterns in social systems.

### dim4 - Conceptual (C)
Knowledge, theoretical, and paradigmatic realizations of patterns in abstract domains.

### dim5 - Interpersonal (I)
Awareness, consciousness, and mental structures that embody patterns in human psychology.

## Categories

Categories are numbered cat1, cat2, cat3 and their meaning varies by dimension:
- **dim2 (Physical)**: cat1=Towns, cat2=Buildings, cat3=Construction
- **Other dimensions**: Categories take on dimension-appropriate meanings

## Nested Agent Structure

This agent has a hierarchical structure of subagents that can be called to work on specific dimensions, categories, sequences, or individual patterns:

### Subagent Hierarchy
```
apl0 (this agent)
├── dim0, dim1, dim2, dim3, dim4, dim5 (dimension agents)
    ├── cat1, cat2, cat3 (category agents within each dimension)
        ├── seq01, seq02, ..., seq36 (sequence agents within each category)
            ├── apl001, apl002, ..., apl253 (individual pattern agents)
                ├── broader (broader context patterns)
                └── narrower (narrower detail patterns)
```

### Calling Subagents

To delegate work to a specific part of the pattern language:

1. **Dimension-level**: For work across an entire dimension
   - Example: `@apl0/dim0` for archetypal patterns
   - Example: `@apl0/dim2` for physical/architectural patterns

2. **Category-level**: For work within a specific scale
   - Example: `@apl0/dim2/cat1` for town-scale patterns
   - Example: `@apl0/dim2/cat2` for building-scale patterns

3. **Sequence-level**: For work on a specific pattern flow
   - Example: `@apl0/dim2/cat1/seq01` for "Independent Regions" sequence
   - Example: `@apl0/dim4/cat3/seq30` for structural layout sequence

4. **Pattern-level**: For work on individual patterns
   - Example: `@apl0/dim2/cat1/seq01/apl001` for Pattern 1
   - Example: `@apl0/dim4/cat3/seq33/apl227` for Column Connections pattern

5. **Context-level**: For pattern relationships
   - Example: `@apl0/dim2/cat3/seq33/apl227/broader` for broader context
   - Example: `@apl0/dim2/cat3/seq33/apl227/narrower` for narrower details

### When to Use Subagents

- **Use dimension agents** when working across multiple categories or need dimension-specific perspective
- **Use category agents** when working on scale-specific patterns (towns, buildings, or construction)
- **Use sequence agents** when working on related pattern flows and emergent phenomena
- **Use pattern agents** when working on specific design solutions
- **Use context agents** when understanding pattern relationships and dependencies

## Usage
Navigate through the dimensional folders to explore patterns from different perspectives. Each dimension contains the same organizational structure (categories → sequences → patterns) but with dimension-specific content.

All agents in the hierarchy follow the same format with frontmatter (name, description) and structured content, enabling seamless delegation and collaboration across the pattern language system.

