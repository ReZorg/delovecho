# Glyph-Noetic Engine: Glyph Specification

This document defines the visual language of glyphs used to interact with the Glyph-Noetic Engine. Glyphs are symbolic representations of the engine's internal components and states. They are composed into **noetic sentences** to issue commands.

## 1. Glyph Categories

Glyphs are organized into four primary categories:

| Category | Description | Color Code |
| :--- | :--- | :--- |
| **Temporal** | Represents the time crystal hierarchy and its rhythms. | Blue |
| **Cognitive** | Represents high-level cognitive processes and modules. | Purple |
| **Structural** | Represents the underlying architectural components. | Green |
| **Noetic** | Represents states of knowledge, belief, or attention. | Orange |

## 2. Glyph Dictionary

### Temporal Glyphs (Blue)

| Glyph ID | Description | ASCII Representation |
| :--- | :--- | :--- |
| `tc_hierarchy` | The entire 12-level time crystal hierarchy. | `[T-HIERARCHY]` |
| `level_0_resonance` | Quantum Resonance (1μs) | `[T~q]` |
| `level_1_dynamics` | Protein Dynamics (8ms) | `[T~p]` |
| `level_5_integration` | Dendritic Integration (160ms) | `[T~d]` |
| `level_9_rhythm` | Global Rhythm (1s) | `[T~g]` |
| `level_11_regulation`| Homeostatic Regulation (1hr) | `[T~h]` |

### Cognitive Glyphs (Purple)

| Glyph ID | Description | ASCII Representation |
| :--- | :--- | :--- |
| `pln_inference` | The Probabilistic Logic Networks module. | `[C:PLN]` |
| `moses_learning` | The MOSES program evolution module. | `[C:MOSES]` |
| `pattern_matching` | The pattern matching module. | `[C:PATTERN]` |
| `attention_allocation`| The attention allocation module. | `[C:ATTN]` |

### Structural Glyphs (Green)

| Glyph ID | Description | ASCII Representation |
| :--- | :--- | :--- |
| `atomspace` | The entire AtomSpace hypergraph. | `[S:ATOMSPACE]` |
| `atom` | A single atom. | `[S:atom]` |
| `link` | A link between atoms. | `[S:link]` |
| `hypergraph_attention`| The hypergraph attention mechanism. | `[S:H-ATTN]` |

### Noetic Glyphs (Orange)

| Glyph ID | Description | ASCII Representation |
| :--- | :--- | :--- |
| `truth_value` | The truth value (strength, confidence) of an atom. | `[N:TV]` |
| `attention_value` | The attention value (STI, LTI) of an atom. | `[N:AV]` |
| `decision` | A decision made by the engine. | `[N:DECISION]` |
| `anomaly` | A detected anomaly. | `[N:ANOMALY]` |

## 3. Noetic Sentences: Composition and Syntax

Noetic sentences are composed by linking glyphs with operators. The `glyph-cli` parses these sentences into commands for the daemon.

### Operators

| Operator | Name | Description |
| :--- | :--- | :--- |
| `->` | **Flow/Connection** | Links two glyphs, indicating data flow or relationship. | `[T~g] -> [C:PLN]` |
| `?` | **Query** | Requests information about a glyph. | `[C:PLN]?` |
| `!` | **Action/Execution**| Triggers an action on a glyph. | `[C:PLN]!` |
| `|` | **Pipe** | Pipes the output of one query into another. | `[S:ATOMSPACE]? | grep(high_av)` |

### Example Sentences

- **Query the status of the PLN module:**
  ```
  > [C:PLN]?
  ```

- **Show the relationship between the global rhythm and PLN:**
  ```
  > [T~g] -> [C:PLN]
  ```

- **Pause the pattern matching module:**
  ```
  > pause [C:PATTERN]!
  ```

- **Find all atoms with high attention value:**
  ```
  > [S:ATOMSPACE]? | filter(av.sti > 100)
  ```

- **Explain a specific decision:**
  ```
  > explain [N:DECISION:12345]?
  ```

This glyph-based language provides a powerful, intuitive, and symbolic way to interact with the complex, sub-symbolic dynamics of the cognitive engine.


### Protocol/Topology Glyphs (Cyan)

| Glyph ID | Description | ASCII Representation |
| :--- | :--- | :--- |
| `p9_fs` | A Plan 9 File Server. | `[P:FS]` |
| `p9_cpu` | A Plan 9 CPU Server. | `[P:CPU]` |
| `p9_namespace` | A 9P namespace (e.g., `/n/cognitive`). | `[P:NS]` |
| `p9_auth` | The authentication server (`faktotum`). | `[P:AUTH]` |
| `p9_read` | A 9P `read` operation. | `[P:READ]` |
| `p9_write` | A 9P `write` operation. | `[P:WRITE]` |
| `topo_assembly` | The entire topological assembly of the cluster. | `[T:ASSEMBLY]` |
| `topo_beta0` | Betti-0: Number of connected components. | `[T:BETA0]` |
| `topo_beta1` | Betti-1: Number of independent cycles/redundant paths. | `[T:BETA1]` |
| `topo_simplex` | A k-simplex representing a binding between k+1 components. | `[T:SIMPLEX]` |
