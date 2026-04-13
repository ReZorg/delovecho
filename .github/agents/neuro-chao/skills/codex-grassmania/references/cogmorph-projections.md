# CogMorph Projection Specifications

## Projection Types

### Hardware Projection
Maps cognitive state to VirtualPCB MMIO registers. Each atom maps to a register address, truth values to register contents, attention values to DMA priority levels.

```cpp
class HardwareProjection : public CognitiveProjection {
    void project(const CognitiveState& state, VirtualPCB& pcb);
    CognitiveState reconstruct(const VirtualPCB& pcb);
};
```

### Library Projection
Maps cognitive state to C++ API objects (AtomSpace, TruthValue, AttentionValue). Standard OpenCog API.

### Static Projection (CGGUF)
Cognitive GGUF format — extends GGUF with cognitive metadata headers for serializing AtomSpace snapshots, endocrine state, and reservoir weights.

**CGGUF Header Extensions:**
- `cog.atomspace.atom_count` (uint64)
- `cog.atomspace.link_count` (uint64)
- `cog.endocrine.state` (float[16])
- `cog.endocrine.mode` (uint8)
- `cog.reservoir.weights` (tensor)
- `cog.reservoir.state` (tensor)

### Network Projection
Wire protocol for distributed cognitive state sharing. Uses protobuf-style encoding with cognitive-specific message types.

### Glyph Projection
Visual/font-based storage where cognitive state is encoded in glyph properties (position, size, color, opacity map to atom properties).

## Transform Registry

Transforms are registered bidirectionally:

```cpp
TransformRegistry registry;
registry.register_transform<HardwareProjection, LibraryProjection>(
    hw_to_lib_transform, lib_to_hw_transform);
registry.register_transform<LibraryProjection, StaticProjection>(
    lib_to_static_transform, static_to_lib_transform);

// Chain transforms automatically
auto result = registry.transform<HardwareProjection, StaticProjection>(hw_state);
```

## ASSD — AtomSpace State Drive

Virtual block device at `0x40004000` optimized for hypergraph storage:

| Offset | Register | Description |
|--------|----------|-------------|
| 0x00 | REG_CMD | Command (READ_ATOM, WRITE_ATOM, QUERY, SYNC) |
| 0x04 | REG_STATUS | Status register |
| 0x08 | REG_ATOM_ID | Atom ID for operations |
| 0x10 | REG_BLOCK_ADDR | Block address |
| 0x18 | REG_DMA_ADDR | DMA buffer address |
| 0x20 | REG_XFER_SIZE | Transfer size |
| 0x28 | REG_ATOM_COUNT | Total atom count (read-only) |

ASFS (AtomSpace File System) provides hierarchical namespace for atom storage with O(1) lookup by atom ID and O(log n) pattern queries.
