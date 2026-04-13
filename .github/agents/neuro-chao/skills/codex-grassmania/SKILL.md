---
name: codex-grassmania
description: >
  Implement CogMorph cognitive state transformation framework and ASSD AtomSpace storage devices.
  Use when building isomorphic projections between hardware, library, static, network, and glyph
  representations of cognitive state, implementing CGGUF cognitive serialization format,
  creating AtomSpace State Drive virtual block devices, or bridging OpenCog symbolic systems
  with NPU virtual hardware. Triggers on mentions of CogMorph, cognitive state transforms,
  CGGUF format, ASSD, AtomSpace State Drive, isomorphic projections, or cognitive serialization.
---

# Codex GrassMania

CogMorph cognitive state transformation framework with ASSD persistent storage. Enables the same cognitive state to be viewed, manipulated, and persisted through five isomorphic projections while maintaining semantic fidelity.

## Core Insight

> All projections represent the SAME cognitive state. Transforms are bidirectional and preserve cognitive semantics.

```
Hardware ←→ Library ←→ Static ←→ Network ←→ Glyph
 (MMIO)     (C++ API)   (CGGUF)   (Wire)    (Visual)
    ↕           ↕          ↕         ↕          ↕
              CognitiveState (canonical)
```

## Five Projections

| Projection | Representation | Primary Use |
|------------|---------------|-------------|
| **Hardware** | MMIO registers on VirtualPCB | Real-time debugging, hardware-level control |
| **Library** | C++ objects (AtomSpace, TruthValue) | Application development, standard API |
| **Static** | CGGUF binary format | Checkpointing, persistence, model sharing |
| **Network** | Wire protocol messages | Distributed cognitive systems |
| **Glyph** | Visual font-based encoding | Human inspection, visualization |

For full projection specifications and transform registry, read `references/cogmorph-projections.md`.

## CognitiveState (Canonical Form)

The canonical form from which all projections derive:

```cpp
struct CognitiveState {
    // AtomSpace snapshot
    std::vector<AtomRecord> atoms;
    std::vector<LinkRecord> links;
    
    // Endocrine state (16 hormone channels)
    EndocrineState endocrine;
    CognitiveMode current_mode;
    
    // Reservoir state
    Eigen::MatrixXf reservoir_weights;
    Eigen::VectorXf reservoir_state;
    
    // Attention values
    std::vector<AttentionRecord> attention;
    
    // Valence memory
    std::vector<ValenceRecord> valence_tags;
    
    // Metadata
    uint64_t tick_count;
    float timestamp;
};
```

## CGGUF — Cognitive GGUF Format

Extends the GGUF model format with cognitive metadata headers:

| Header Key | Type | Description |
|-----------|------|-------------|
| `cog.version` | uint32 | CGGUF format version |
| `cog.atomspace.atom_count` | uint64 | Number of atoms |
| `cog.atomspace.link_count` | uint64 | Number of links |
| `cog.endocrine.state` | float[16] | Hormone concentrations |
| `cog.endocrine.mode` | uint8 | Current cognitive mode |
| `cog.reservoir.size` | uint32 | Reservoir neuron count |
| `cog.reservoir.spectral_radius` | float | ESN spectral radius |
| `cog.evolution.stage` | uint8 | Ontogenetic stage |
| `cog.wisdom.score` | float | Aggregate wisdom metric |

```cpp
// Save cognitive checkpoint
CognitiveState state = CogMorph::capture(atomspace, endo, reservoir);
CGGUFWriter writer("checkpoint.cgguf");
writer.write_header(state);
writer.write_atoms(state.atoms);
writer.write_tensors(state.reservoir_weights, state.reservoir_state);
writer.finalize();

// Load cognitive checkpoint
auto state = CGGUFReader::load("checkpoint.cgguf");
CogMorph::restore(atomspace, endo, reservoir, state);
```

## ASSD — AtomSpace State Drive

Virtual block device at `0x40004000` optimized for hypergraph storage patterns. Implements ASFS (AtomSpace File System) with O(1) atom lookup and O(log n) pattern queries.

```cpp
// Hardware-style atom operations
pcb.write32(ASSD_BASE + REG_ATOM_ID, atom_handle);
pcb.write32(ASSD_BASE + REG_CMD, CMD_READ_ATOM);
while (!(pcb.read32(ASSD_BASE + REG_STATUS) & STATUS_READY)) {}
// Atom data available in DMA buffer

// Bulk operations via DMA
pcb.write32(ASSD_BASE + REG_DMA_ADDR, buffer_addr);
pcb.write32(ASSD_BASE + REG_XFER_SIZE, atom_count * sizeof(AtomRecord));
pcb.write32(ASSD_BASE + REG_CMD, CMD_BULK_WRITE);
```

For full ASSD register layout, read `references/cogmorph-projections.md`.

## Transform Workflow

### Checkpoint a Running System

```cpp
// 1. Capture from library projection (running AtomSpace)
auto lib_state = LibraryProjection::capture(atomspace, endo, reservoir);

// 2. Transform to static projection
auto static_state = CogMorphTransform::library_to_static(lib_state);

// 3. Write to CGGUF file
static_state.save_cgguf("echo_angel_v1.cgguf");

// 4. Also persist to ASSD for fast hardware-level access
auto hw_state = CogMorphTransform::library_to_hardware(lib_state);
hw_state.write_to_assd(pcb, ASSD_BASE);
```

### Inspect State Visually

```cpp
// Transform to glyph projection for human inspection
auto glyph_state = CogMorphTransform::library_to_glyph(lib_state);
glyph_state.render_to_svg("cognitive_state.svg");
// Each atom rendered as a glyph with position=importance, size=STI, color=valence
```

## Composition

| Skill | Integration |
|-------|-------------|
| `npu` | Hardware projection targets NPU VirtualPCB registers |
| `virtual-endocrine-system` | Endocrine state serialized in CGGUF headers |
| `unreal-echo` | Cognitive cycle checkpointed via CGGUF |
| `meta-echo-dna` | Expression state included in cognitive snapshots |
| `deep-tree-echo-core-self` | Identity mesh persisted in ASSD |
| `echo-introspect` | Glyph projection enables visual self-inspection |
