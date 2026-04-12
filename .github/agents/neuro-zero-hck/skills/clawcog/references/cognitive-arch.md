# OpenCog Cognitive Architecture Reference

## Table of Contents
1. Overview
2. AtomSpace
3. Atom Types
4. Truth Values
5. Attention Values
6. Pattern Matcher
7. Usage Examples

## Overview

The cognitive architecture provides a hypergraph knowledge representation system inspired by the [OpenCog](https://opencog.org/) AGI framework. It lives in `src/cognitive/` with four files:

| File | Lines | Purpose |
|------|-------|---------|
| `atom-types.ts` | 193 | Type definitions for atoms, nodes, links, truth/attention values |
| `atomspace.ts` | 355 | AtomSpace hypergraph store with indexing |
| `pattern-matcher.ts` | 345 | Pattern matching and query engine |
| `index.ts` | 37 | Public API exports |

## AtomSpace

The `AtomSpace` class is the central knowledge store. It maintains atoms (nodes and links) in a hypergraph with three indexes:

- **nodeIndex**: `Map<string, string>` — `"type:name"` → atom ID
- **linkIndex**: `Map<string, Set<string>>` — `"type:[outgoing]"` → atom IDs
- **incomingIndex**: `Map<string, Set<string>>` — atom ID → incoming link IDs

### Constructor

```typescript
const atomspace = new AtomSpace({ enableAttention?: boolean });
```

### Core Methods

```typescript
// Nodes
addNode(type: AtomType, name: string, truthValue?: TruthValue, value?: number): Node
getNode(type: AtomType, name: string): Node | undefined

// Links
addLink(type: AtomType, outgoing: string[], truthValue?: TruthValue): Link
getLink(type: AtomType, outgoing: string[]): Link | undefined

// Traversal
getAtom(id: string): Atom | undefined
getIncoming(atomId: string): Link[]
getOutgoing(linkId: string): Atom[]

// Query
query(criteria: { type?: AtomType, name?: string, outgoing?: string[] }): Atom[]
getAllAtoms(): Atom[]
size(): number

// Mutation
deleteAtom(id: string): boolean
clear(): void
updateTruthValue(atomId: string, tv: TruthValue): boolean
updateAttention(atomId: string, av: AttentionValue): boolean
```

## Atom Types

### Nodes (Vertices)

| Type | Purpose |
|------|---------|
| `CONCEPT_NODE` | Concepts, entities, objects |
| `PREDICATE_NODE` | Properties or relations |
| `VARIABLE_NODE` | Unbound variables for pattern matching |
| `NUMBER_NODE` | Numeric values (uses `value` field) |
| `SCHEMA_NODE` | Procedures or functions |

### Links (Edges)

| Type | Purpose |
|------|---------|
| `INHERITANCE_LINK` | "is-a" relationships |
| `SIMILARITY_LINK` | Semantic similarity |
| `MEMBER_LINK` | Set membership |
| `EVALUATION_LINK` | Predicate evaluation on arguments |
| `LIST_LINK` | Group atoms together |
| `AND_LINK` | Logical conjunction |
| `OR_LINK` | Logical disjunction |
| `NOT_LINK` | Logical negation |
| `IMPLICATION_LINK` | Logical implication |
| `EQUIVALENCE_LINK` | Logical equivalence |
| `EXECUTION_LINK` | Schema execution |

## Truth Values

Represent uncertain knowledge with strength (0-1) and confidence (0-1):

```typescript
import { TruthValueHelpers } from "@/cognitive";

const tv = TruthValueHelpers.create(0.8, 0.9);  // 80% strength, 90% confidence
const unknown = TruthValueHelpers.unknown();      // strength: 0, confidence: 0
const merged = TruthValueHelpers.merge(tv1, tv2); // Combine from multiple sources
```

## Attention Values

For Economic Attention Networks (ECAN). Requires `enableAttention: true`:

```typescript
import { AttentionValueHelpers } from "@/cognitive";

const av = AttentionValueHelpers.create(
  100,   // STI (Short-Term Importance)
  50,    // LTI (Long-Term Importance)
  false  // VLTI (Very Long-Term Importance)
);
const defaultAv = AttentionValueHelpers.default(); // STI: 0, LTI: 0, VLTI: false
```

## Pattern Matcher

The `PatternMatcher` class provides structured queries over the AtomSpace:

```typescript
import { PatternMatcher } from "@/cognitive";

const matcher = new PatternMatcher(atomspace);
```

### Key Methods

```typescript
// Find all X where X inherits from parent
findInheritors(parentId: string): Node[]

// Find all parents that X inherits from
findParents(childId: string): Node[]

// Find predicate evaluations for an atom
findPredicatesFor(atomId: string): Array<{ predicate: Node, args: Atom[] }>

// Pattern matching with variables
matchPattern(pattern: PatternSpec): BindingSet[]
```

### Pattern Matching Example

```typescript
// Find: "What inherits from Animal?"
const animal = atomspace.getNode(AtomType.CONCEPT_NODE, "Animal");
const inheritors = matcher.findInheritors(animal.id);
// Returns: [Cat, Dog, Bird, ...]

// Find: "What predicates apply to Cat?"
const cat = atomspace.getNode(AtomType.CONCEPT_NODE, "Cat");
const predicates = matcher.findPredicatesFor(cat.id);
// Returns: [{ predicate: "color", args: ["black"] }, ...]
```

## Usage Examples

### Knowledge Graph Construction

```typescript
const atomspace = new AtomSpace();
const cat = atomspace.addNode(AtomType.CONCEPT_NODE, "Cat");
const animal = atomspace.addNode(AtomType.CONCEPT_NODE, "Animal");
atomspace.addLink(AtomType.INHERITANCE_LINK, [cat.id, animal.id]);

// Predicate evaluation
const color = atomspace.addNode(AtomType.PREDICATE_NODE, "hasColor");
const black = atomspace.addNode(AtomType.CONCEPT_NODE, "Black");
const list = atomspace.addLink(AtomType.LIST_LINK, [cat.id, black.id]);
atomspace.addLink(AtomType.EVALUATION_LINK, [color.id, list.id],
  TruthValueHelpers.create(1.0, 1.0));
```

### Integration with Memory System

```typescript
async function extractKnowledge(sessionId: string) {
  const memory = loadMemory(sessionId);
  for (const entry of memory.entries) {
    const entities = await extractEntities(entry.content);
    for (const entity of entities) {
      atomspace.addNode(AtomType.CONCEPT_NODE, entity.name);
    }
  }
}
```

### Performance Tips

1. Batch atom creation before querying
2. Cache node references and reuse IDs
3. Use specific patterns to reduce search space
4. Periodically prune low-attention atoms when using ECAN
