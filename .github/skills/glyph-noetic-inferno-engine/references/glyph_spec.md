# Glyph Specification

## Table of Contents

1. [Sentence Syntax](#sentence-syntax)
2. [Complete Glyph Map](#complete-glyph-map)
3. [Response Format](#response-format)
4. [Composition Examples](#composition-examples)

## Sentence Syntax

A noetic sentence is a string written to `/dev/glyph` that triggers a cognitive operation.

```
[GLYPH_ID]OPERATOR [ARGS...]
```

- **GLYPH_ID**: Bracketed identifier (e.g., `K:STATUS`, `T~q`, `C:PLN`)
- **OPERATOR**: `?` (query), `!` (action), `->` (flow), `|` (pipe)
- **ARGS**: Optional space-separated arguments

Examples:
```
[K:STATUS]?                    # Query engine status
[C:PLN]!                       # Trigger PLN inference cycle
[T~q]?                         # Query quantum resonance level
[S:ATOMSPACE]? type=ConceptNode # Query with filter
[T:ASSEMBLY]?                  # Query topology assembly
```

## Complete Glyph Map

30 registered glyphs across 7 categories:

### Kernel (K:)
| Glyph | Description | Temporal Level |
|-------|-------------|----------------|
| `[K:STATUS]` | Engine status overview | — |
| `[K:GLYPHS]` | List all registered glyphs | — |
| `[K:PROMISES]` | Kernel promise status | — |

### Temporal (T)
| Glyph | Description | Temporal Level |
|-------|-------------|----------------|
| `[T-HIERARCHY]` | Full 12-level hierarchy | — |
| `[T~q]` | Quantum resonance (1μs) | 0 |
| `[T~p]` | Protein dynamics (8ms) | 1 |
| `[T~i]` | Ion channel gating (26ms) | 2 |
| `[T~m]` | Membrane dynamics (52ms) | 3 |
| `[T~a]` | Axon initial segment (110ms) | 4 |
| `[T~d]` | Dendritic integration (160ms) | 5 |
| `[T~s]` | Synaptic plasticity (250ms) | 6 |
| `[T~o]` | Soma processing (330ms) | 7 |
| `[T~n]` | Network sync (500ms) | 8 |
| `[T~g]` | Global rhythm (1000ms) | 9 |
| `[T~c]` | Circadian modulation (60s) | 10 |
| `[T~h]` | Homeostatic regulation (3600s) | 11 |

### Cognitive (C:)
| Glyph | Description | Temporal Level |
|-------|-------------|----------------|
| `[C:PLN]` | Probabilistic Logic Networks | 2 (ion channel) |
| `[C:MOSES]` | Meta-Optimizing Semantic ES | 4 (axon) |
| `[C:PATTERN]` | Pattern matching engine | 1 (protein) |
| `[C:ATTN]` | ECAN attention allocation | 3 (membrane) |

### Structural (S:)
| Glyph | Description | Temporal Level |
|-------|-------------|----------------|
| `[S:ATOMSPACE]` | AtomSpace hypergraph store | 0 (quantum) |

### Noetic (N:)
| Glyph | Description | Temporal Level |
|-------|-------------|----------------|
| `[N:DECISION]` | Autognosis self-image | 9 (global) |

### Protocol (P:)
| Glyph | Description | Temporal Level |
|-------|-------------|----------------|
| `[P:FS]` | File server components | — |
| `[P:CPU]` | CPU server components | — |
| `[P:NS]` | Cognitive namespace map | — |

### Topology (T:)
| Glyph | Description | Temporal Level |
|-------|-------------|----------------|
| `[T:ASSEMBLY]` | Full topology assembly | — |
| `[T:BETA0]` | Betti-0 (connectivity) | — |
| `[T:BETA1]` | Betti-1 (cycles) | — |
| `[T:PERSIST]` | Persistence diagram | — |

## Response Format

All responses are JSON objects with three fields:

```json
{
  "glyph": "[GLYPH_ID]",
  "operator": "?",
  "result": { ... }
}
```

Error responses:
```json
{
  "glyph": "[UNKNOWN]",
  "operator": "?",
  "error": "Unknown glyph: UNKNOWN"
}
```

## Composition Examples

Pipe output from one glyph to another:
```
[C:PLN]? | [S:ATOMSPACE]!     # PLN results -> AtomSpace update
[T:ASSEMBLY]? | [K:STATUS]!   # Topology check -> Status update
```

Flow data between modules:
```
[C:PATTERN]? -> [C:PLN]!      # Pattern results flow to PLN
```
