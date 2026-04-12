# AGI-OS Subsystem Architecture

## Table of Contents

1. [Layer Architecture](#layer-architecture)
2. [CogNUMach (Layer 1)](#cognumach-layer-1)
3. [HurdCog (Layer 2)](#hurdcog-layer-2)
4. [OpenCog Collection (Layer 3)](#opencog-collection-layer-3)
5. [Integration Layer](#integration-layer)
6. [Supporting Subsystems](#supporting-subsystems)

## Layer Architecture

```
┌──────────────────────────────────────────────────────────┐
│ Layer 4: CogBolt (AI-Powered IDE)                        │
├──────────────────────────────────────────────────────────┤
│ Layer 3: OpenCog Collection (OCC)                        │
│  cogutil → atomspace → atomspace-storage → cogserver     │
│  ure → pln, miner, attention, learn, generate            │
│  moses → asmoses, agi-bio, vision                        │
├──────────────────────────────────────────────────────────┤
│ Integration: cognitive-grip, unified-cog-interface        │
├──────────────────────────────────────────────────────────┤
│ Layer 2: HurdCog (Cognitive GNU Hurd)                    │
│  cogkernel, machspace, atomspace-bridge, dashboard       │
├──────────────────────────────────────────────────────────┤
│ Layer 1: CogNUMach (Cognitive GNU Mach Microkernel)      │
│  IPC, VM, scheduling, device drivers, SMP               │
├──────────────────────────────────────────────────────────┤
│ Layer 0: Inferno Kernel + MIG                            │
│  9P protocol, Vortex-Morphule-Egregore, GGML tensors    │
└──────────────────────────────────────────────────────────┘
```

## CogNUMach (Layer 1)

**Location**: `core/microkernel/cognumach/`
**Build**: Autotools (autoconf/automake/libtool)
**Architecture**: i386 (32-bit), x86_64 (experimental), aarch64 (experimental)

Key directories:
- `kern/` — Kernel core (IPC, scheduling, threads)
- `vm/` — Virtual memory management
- `ipc/` — Inter-process communication
- `i386/` — x86 architecture support
- `x86_64/` — 64-bit port (experimental)
- `aarch64/` — ARM64 port (experimental)
- `mig/` — Mach Interface Generator
- `scripts/` — Build, test, and validation scripts
- `tests/` — Kernel test suite

Cognitive extensions:
- SMP threading enhancements
- ASLR implementation
- VM map red-black tree optimization
- IPC virtual copy implementation
- Performance analysis framework

## HurdCog (Layer 2)

**Location**: `core/os/hurdcog/`
**Build**: Autotools + CMake hybrid
**Dependencies**: CogNUMach, MIG, cogutil, atomspace

Key components:
- `cogkernel/` — Cognitive kernel extensions (Scheme + C)
  - `atomspace/` — OS-level AtomSpace integration
  - `attention/` — ECAN attention allocation
  - `reasoning/` — PLN reasoning at OS level
  - `agents/` — Cognitive agent framework
  - `meta-cognition/` — Self-monitoring
  - `security/` — Security framework
  - `visualization/` — Cognitive visualization
- `external/` — Upstream Hurd and GNU Mach repos
- `docs/` — Architecture documentation
- `mig.backup/` — MIG backup

Cognitive features:
- Cognitive Fusion Reactor for multi-paradigm AI
- Master Control Dashboard (web-based monitoring)
- MachSpace (AtomSpace at OS level)
- Distributed cognitive processing via Hurd translators
- Plan 9 namespace integration
- Inferno integration

## OpenCog Collection (Layer 3)

**Location**: `core/cognition/`
**Build**: CMake
**Root CMakeLists.txt**: Orchestrates all OCC components

### Foundation (`core/cognition/foundation/`)
- `cogutil/` — Utility library (logging, config, threading)
- `atomspace/` — Hypergraph database (core data structure)
- `atomspace-storage/` — Storage backends (CRITICAL for CogServer)
- `cogserver/` — Network server for AtomSpace access
- `learn/` — Symbolic learning (language learning pipeline)
- `agents/` — Interactive agent framework
- `attention/` — ECAN attention allocation

### Storage (`core/cognition/storage/`)
- `atomspace-metta/` — MeTTa language integration
- `atomspace-bridge/` — Cross-AtomSpace bridge
- `atomspace-accelerator/` — Inference engine accelerator

### Reasoning (`core/cognition/reasoning/`)
- PLN (Probabilistic Logic Networks)
- URE (Unified Rule Engine)

### Generation (`core/cognition/generation/`)
- `agentic-chatbots/` — LLM-integrated chatbots

### Language (`core/cognition/language/`)
- `link-grammar/` — Link Grammar parser

### LLM (`core/cognition/llm/`)
- `aphroditecho/` — LLM inference integration

## Integration Layer

### cognitive-grip (`core/integration/cognitive-grip/`)
Unified C++ abstraction layer providing:
- `cognitive_grip.cpp` — Main initialization and AtomSpace management
- `inferno_bridge.cpp` — Inferno Kernel bridge
- `machspace_bridge.cpp` — MachSpace (HurdCog AtomSpace) bridge
- `hurdcog_bridge.cpp` — HurdCog OS bridge
- `cognumach_bridge.cpp` — CogNUMach microkernel bridge
- `cogbolt_bridge.cpp` — CogBolt IDE bridge
- `unified_config.cpp` — Unified configuration

### unified-cog-interface (`core/integration/unified-cog-interface/`)
9P-based cognitive interface providing file-system-like access to cognitive services.

## Supporting Subsystems

### CogBolt (`cogbolt/`)
AI-powered IDE core with GGML integration.

### Consciousness (`consciousness/`)
LLM inference engine (Go-based, Ollama-derived) with Deep Tree Echo memory.

### CogPilot (`cogpilot/`)
Julia-based differential equations and reservoir computing for cognitive modeling.

### Personification (`personification/`)
AI character/persona framework with VTuber integration.

### GGML (`ggml/`)
Tensor computation library variants (llama.cpp, kobold.cpp, rwkv.cpp).

### Inferno Kernel (`core/inferno-kernel/`)
9P protocol, Vortex-Morphule-Egregore architecture, agentic cognitive grammar.
