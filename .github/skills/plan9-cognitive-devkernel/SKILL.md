---
name: plan9-cognitive-devkernel
description: "Plan 9 from Bell Labs cognitive development kernel with per-process namespace-based cognitive architecture. Use when setting up Plan 9 or 9front development environments, configuring acme/sam IDE toolchains, deploying distributed CPU server grids, building cognitive kernel modules in Plan 9 C, managing 9P2000 cognitive namespaces, running autognosis self-monitoring cycles, checking temporal hierarchy status, or verifying kernel promise constraints. Provides QEMU-based devcontainer, grid orchestration, cognitive namespace management, and self-aware kernel validation. Transformed from inferno-devcontainer(manuscog-cognitive-devkernel) via function-creator to plan9-analogue."
---

# Plan 9 Cognitive DevKernel

A self-aware cognitive development kernel for Plan 9 from Bell Labs, synthesized from the composition:

```
skill-creator(
  function-creator(
    inferno-devcontainer(
      manuscog-cognitive-devkernel
    ) => "plan9-analogue"
  )
)
```

Plan 9's per-process namespaces, 9P2000 protocol, and union directories provide a natural substrate for cognitive architectures. Every cognitive service is a file server; every namespace binding is a cognitive connection.

## Composition Layers

| Layer | Source Skill | Plan 9 Analogue |
|-------|-------------|-----------------|
| Infrastructure | inferno-devcontainer | QEMU devcontainer with Plan 9/9front, acme IDE, CPU grid |
| Constraints | promise-lambda-attention | 8 kernel promises validate Plan 9 configuration |
| File System | function-creator(tc) | TC file ops → cognitive 9P2000 namespace operations |
| Temporal | function-creator(time-crystal-nn) | 9-level time crystal → kernel service scheduling |
| Self-Awareness | Autognosis | 3-level hierarchical self-image via /proc introspection |
| Convergence | skill-infinity | Self-referential fixed-point checking |

**For the full composition architecture and data flow**, read `references/composition_architecture.md`.

## Quick Start

### 1. Validate a Kernel Configuration

Check that a Plan9Cog repository satisfies all 8 kernel promises:

```bash
python3 /home/ubuntu/skills/plan9-cognitive-devkernel/scripts/cognitive_plan9kernel.py validate /path/to/plan9cog
```

### 2. View Kernel Self-Image

Display the Autognosis hierarchical self-image with temporal hierarchy status:

```bash
python3 /home/ubuntu/skills/plan9-cognitive-devkernel/scripts/cognitive_plan9kernel.py status
```

### 3. Run Autognosis Cycle

Execute 5 self-improvement cycles and check for fixed-point convergence:

```bash
python3 /home/ubuntu/skills/plan9-cognitive-devkernel/scripts/cognitive_plan9kernel.py cycle
```

### 4. View Domain Transforms

Display the tc → Cognitive Namespace and time-crystal-nn → Temporal Hierarchy mappings:

```bash
python3 /home/ubuntu/skills/plan9-cognitive-devkernel/scripts/cognitive_plan9kernel.py transform
```

### 5. Set Up Development Environment

Copy templates into your project and launch the QEMU-based Plan 9 devcontainer:

```bash
cp -r /home/ubuntu/skills/plan9-cognitive-devkernel/templates/.plan9-devenv /path/to/project/
cp /home/ubuntu/skills/plan9-cognitive-devkernel/templates/grid-compose.yml /path/to/project/
```

## Promise-Lambda Attention

The kernel validates its configuration through 8 promises:

| Promise | λ Constraint | KV Source |
|---------|-------------|----------|
| `plan9-kernel` | Plan 9 kernel or QEMU image present | OpenCog-Plan9 |
| `plan9-cc` | Plan 9 C compiler (6c/8c) available | Plan 9 toolchain |
| `9p-listener` | 9P2000 port 564 configured | plan9-devenv |
| `grid-compose` | plan9-registry in grid-compose.yml | plan9-devenv |
| `cognitive-ns` | /cognitive/ namespace defined | OpenCog-Plan9 |
| `devenv-config` | PLAN9 root in environment | plan9-devenv |
| `autognosis-loop` | Verification in termrc | Autognosis |
| `temporal-levels` | 9+ temporal levels defined | time-crystal-nn |

## Cognitive Namespace (tc Transform)

TC file operations are mapped to cognitive 9P2000 namespace operations:

```
/cognitive/
├── atomspace/{atoms, types, indices}
├── inference/{rules, queue, results}
├── attention/{bank, agents}
├── learning/{populations, fitness}
├── temporal/{levels, phases}
└── autognosis/{images, insights, metrics}
```

Each path is a 9P2000 file server. `read` queries values, `write` updates them, `stat` returns metadata. Plan 9's `bind` and `mount` compose namespaces across CPU servers.

**For the full namespace reference and 9P2000 operation mapping**, read `references/cognitive_namespace.md`.

## Temporal Hierarchy (time-crystal-nn Transform)

The 9-level time crystal neuron architecture maps to kernel service scheduling:

| Level | Service | Period | Plan 9 Mechanism |
|-------|---------|--------|------------------|
| L0 | AtomSpace CRUD | 8ms | /srv file read/write |
| L1 | Pattern matching | 26ms | grep over /cognitive/atomspace |
| L2 | PLN inference | 52ms | /cognitive/inference file server |
| L3 | ECAN attention | 110ms | /cognitive/attention agents |
| L4 | MOSES learning | 160ms | /cognitive/learning populations |
| L5 | Namespace sync | 250ms | mount/bind across CPU servers |
| L6 | Grid heartbeat | 330ms | /net/tcp keepalive |
| L7 | Autognosis observation | 500ms | /proc introspection |
| L8 | Self-image rebuild | 1000ms | Full namespace walk |

## Autognosis Self-Image

Three hierarchical levels of self-monitoring (mapped to Plan 9 /proc):

| Level | Name | What It Observes |
|-------|------|------------------|
| 0 | Direct Observation | Promise satisfaction, temporal levels, namespace paths |
| 1 | Pattern Analysis | Configuration completeness, grid status |
| 2 | Meta-Cognitive | Self-awareness quality, convergence factor |

## skill-infinity Convergence

The system converges to a fixed point when:

```
|self_awareness(cycle_n) - self_awareness(cycle_{n-1})| < 0.001
```

## Plan 9 Development Environment

The devcontainer provides a complete Plan 9 development setup via QEMU:

| Component | Description |
|-----------|-------------|
| **Plan 9 / 9front** | Full system via QEMU (cpu, rc, mk, acme) |
| **acme IDE** | Plan 9 native programmer's IDE |
| **Grid CLI** | `plan9-grid` for start/stop/status/connect |
| **Build CLI** | `plan9-build` for compile/run/check/clean |
| **Grid Monitor** | Flask dashboard on port 9090 |
| **9P2000 Networking** | Ports 564-566 for distributed namespaces |

### CLI: plan9-grid

```bash
plan9-grid start [--nodes N]    # Start CPU server grid (default: 3)
plan9-grid stop                 # Stop all nodes
plan9-grid status               # Show grid status
plan9-grid connect <node-id>    # Connect via 9P2000
plan9-grid deploy <file.out>    # Deploy executable to all nodes
plan9-grid logs [node-id]       # Tail logs
```

### CLI: plan9-build

```bash
plan9-build compile src/hello.c  # Compile with 6c/6l
plan9-build run src/hello.c      # Compile and run
plan9-build check src/hello.c    # Type-check only
plan9-build clean                # Remove .6 and .out files
```

**For cluster topologies and 9P2000 networking patterns**, read `references/distributed_grid_patterns.md`.

## Bundled Resources

- **`scripts/`**
  - `cognitive_plan9kernel.py` — Unified CLI: status, validate, promise, transform, cycle
  - `grid_monitor.py` — Flask-based grid dashboard (port 9090)
  - `validate_plan9env.py` — Validate Plan 9 devcontainer configuration
- **`references/`**
  - `composition_architecture.md` — Full parse tree, layer architecture, data flow
  - `cognitive_namespace.md` — 9P2000 namespace hierarchy, tc transform, temporal binding
  - `distributed_grid_patterns.md` — Grid topologies, 9P2000 networking, scaling
- **`templates/`**
  - `.plan9-devenv/` — Devcontainer config (Dockerfile, devcontainer.json, scripts)
  - `grid-compose.yml` — Multi-node CPU server grid deployment
  - `src/cogkernel.c` — Sample cognitive kernel in Plan 9 C
  - `src/cogkernel_autognosis.c` — Autognosis module in Plan 9 C
  - `mkfile` — Plan 9 build file template
  - `transform_spec.yaml` — Function-creator transform specification

## Composition with Other Skills

| Skill | Relationship |
|-------|-------------|
| **inferno-devcontainer** | Source infrastructure — transformed to Plan 9 analogue |
| **manuscog-cognitive-devkernel** | Source cognitive architecture — enriches Plan 9 kernel |
| **opencog-inferno-kernel** | Cognitive services — mapped to 9P2000 file servers |
| **promise-lambda-attention** | Constraint mechanism — promise validation |
| **function-creator** | Transform engine — Inferno → Plan 9 domain mapping |
| **tc** | Source domain — file management → namespace operations |
| **time-crystal-nn** | Source domain — temporal hierarchy architecture |
| **Autognosis** | Self-awareness — /proc-based hierarchical self-image |
| **skill-infinity** | Convergence — self-referential fixed point |
| **skill-creator** | Packaging — skill structure and validation |
