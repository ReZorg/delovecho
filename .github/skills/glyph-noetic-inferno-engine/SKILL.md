---
name: glyph-noetic-inferno-engine
description: Build, test, and deploy the Glyph-Noetic Inferno Kernel — a cognitive OS where intelligence is a native kernel service exposed through glyph-addressed file I/O. Composes glyph-noetic-engine + manuscog-cognitive-devkernel + opencog-inferno-kernel + p9fstyx-topology + promise-lambda-attention. Use for implementing cognitive kernel architectures with neuro-symbolic reasoning, 12-level time-crystal temporal hierarchies, Plan 9 cluster topology with RTSA, kernel-resident AtomSpace, autognosis self-awareness, or 9P-native cognitive namespaces. Triggers on mentions of glyph-noetic, cognitive inferno kernel, /dev/glyph, time-crystal scheduler, cognitive OS, noetic sentence, kernel-level AtomSpace, or autognosis kernel.
---

# Glyph-Noetic Inferno Engine

Cognitive architecture where intelligence is a native Inferno kernel service, addressable through a glyph-based symbolic interface and the Plan 9 file protocol. The file system IS the API to intelligence.

## Composition

```
/glyph-noetic-inferno-engine = /neuro-symbolic-engine(
    /time-crystal-nn(/time-crystal-neuron)
    [/time-crystal-daemon]
) ( /plan9-file-server [/p9fstyx-topology] )
```

## Workflow

1. **Scaffold** — Copy templates to create a new project
2. **Simulate (Python)** — Run `scripts/glyph_noetic_kernel_daemon.py` for rapid testing
3. **Build (C)** — Compile kernel modules with `make all` in `kernel/`
4. **Deploy (Inferno)** — Integrate into an Inferno kernel source tree

## 1. Scaffold a New Project

```bash
DEST=/path/to/project
mkdir -p "$DEST/scripts"
cp -r /home/ubuntu/skills/glyph-noetic-inferno-engine/templates/* "$DEST/"
cp /home/ubuntu/skills/glyph-noetic-inferno-engine/scripts/glyph_noetic_kernel_daemon.py "$DEST/scripts/"
```

Result:
```
$DEST/
├── docs/topology.mmd
├── kernel/{Makefile, include/glyph.h, src/*.c}
├── limbo/module/cogkernel_glyph.b
├── scripts/glyph_noetic_kernel_daemon.py
└── tests/test_main.c
```

## 2. Python Simulation

The daemon mirrors the full C kernel. No dependencies beyond Python 3.8+ stdlib.

```bash
# Full test suite (19 tests)
python3 scripts/glyph_noetic_kernel_daemon.py --test

# Health check (all subsystems)
python3 scripts/glyph_noetic_kernel_daemon.py --health

# Interactive CLI
python3 scripts/glyph_noetic_kernel_daemon.py --cli

# Single sentence
python3 scripts/glyph_noetic_kernel_daemon.py -e "[T:ASSEMBLY]?"
```

## 3. C Kernel Build

Requires `gcc` and `make`. Builds in simulation mode (`GLYPH_KERNEL_SIMULATION` define).

```bash
cd kernel/
make clean && make all
./build/glyph_kernel_test   # 23 tests
```

## 4. Key Noetic Sentences

Interact with the kernel by writing sentences to `/dev/glyph`:

| Sentence | Description |
|----------|-------------|
| `[K:STATUS]?` | Engine status (version, uptime, glyph count, topology health) |
| `[T-HIERARCHY]?` | Full 12-level temporal hierarchy |
| `[C:PLN]?` | PLN inference module status |
| `[S:ATOMSPACE]?` | AtomSpace hypergraph status |
| `[T:ASSEMBLY]?` | Topology assembly with Betti numbers |
| `[N:DECISION]?` | Autognosis self-image and awareness score |
| `[K:PROMISES]?` | All 11 kernel promise statuses |

## 5. Reference Documents

Read these for in-depth details:

- **`references/architecture.md`** — System components, temporal hierarchy (12 levels), topology model (Betti numbers), kernel promises (11), autognosis formula. **Read first for system understanding.**
- **`references/glyph_spec.md`** — Complete map of all 30 glyphs, sentence syntax, response format, composition/pipe examples.
- **`references/deployment.md`** — Detailed deployment for all modes: Python simulation, C simulation, Inferno kernel integration, Limbo user-space module.

## 6. Extending the Engine

**Add a new glyph:**
1. Define the handler function matching `GlyphHandler` signature: `int handler(GlyphEngine *engine, GlyphResult *result, int argc, char **argv)`
2. Register in `register_default_glyphs()` in `glyph.c` with category, description, and temporal level
3. Add the corresponding Python handler in the daemon's `GlyphNoeticKernelEngine` class
4. Add test cases in both `test_main.c` and the daemon's `--test` suite

**Add a new cognitive module:**
1. Create a `CogModule` with `tick()` and `query()` functions
2. Register with a temporal level via `temporal_register_module()`
3. Add a glyph for querying its status
4. Seed relevant atoms in the AtomSpace

**Add a topology constraint:**
1. Add a `TopoConstraint` in `topo_init()` specifying the Betti dimension, operator, and value
2. Add a corresponding kernel promise in `promises.c`
