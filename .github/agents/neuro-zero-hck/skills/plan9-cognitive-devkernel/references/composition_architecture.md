# Composition Architecture — Plan 9 Analogue

This document describes how the skill composition expression is parsed, evaluated, and instantiated for the Plan 9 from Bell Labs cognitive development kernel.

## Expression Grammar

```
skill-creator(
  function-creator(
    inferno-devcontainer(
      manuscog-cognitive-devkernel
    ) => "plan9-analogue"
  )
)
```

## Parse Tree

| Operator | Meaning | Example |
|----------|---------|---------|
| `f(x)` | Apply: f wraps/transforms x | `function-creator(...)` transforms to Plan 9 domain |
| `(a(b))` | Nesting: b enriches a | `inferno-devcontainer(manuscog)` — cognitive enrichment |
| `=> "d"` | Domain target: output mapped to domain d | `=> "plan9-analogue"` — target is Plan 9 |
| `skill-creator(...)` | Package: wrap result as deliverable skill | Final packaging step |

## Layer Architecture

### Layer 0: Infrastructure Substrate (inferno-devcontainer → Plan 9 devenv)

The inferno-devcontainer provides the structural template. Under the Plan 9 analogue transform, its components map as follows:

| Inferno Component | Plan 9 Analogue | Rationale |
|-------------------|-----------------|-----------|
| emu (Inferno emulator) | QEMU running Plan 9/9front | Both provide hosted execution |
| Limbo language | Plan 9 C (dialect of ANSI C) | Native system language |
| Dis VM bytecode | Native executables (.out) | Plan 9 has no VM layer |
| Styx protocol | 9P2000 protocol | Styx is Inferno's name for 9P |
| Docker cluster | QEMU VM grid / CPU servers | Distributed execution |
| devcontainer.json | devcontainer.json (QEMU-based) | Same container spec, different base |
| VS Code + Limbo | acme + Plan 9 C | Native IDE |
| post-create.sh | cpurc | Plan 9 CPU server startup |
| post-start.sh | termrc | Plan 9 terminal startup |
| Port 6666 | Port 564 | Standard 9P2000 port |

### Layer 1: Cognitive Enrichment (manuscog-cognitive-devkernel)

The manuscog-cognitive-devkernel contributes:

- **Promise-Lambda Attention**: 8 kernel promises adapted for Plan 9 configuration validation
- **Cognitive File System**: TC file operations → 9P2000 namespace operations
- **Temporal Hierarchy**: 9-level time crystal → Plan 9 service scheduling
- **Autognosis**: Hierarchical self-image building via Plan 9 /proc
- **skill-infinity**: Self-referential fixed-point convergence

### Layer 2: Domain Transform (function-creator => "plan9-analogue")

The function-creator maps every Inferno concept to its Plan 9 equivalent:

**Protocol mapping**: Styx → 9P2000 (they are the same protocol family; Styx is Inferno's dialect of 9P)

**Namespace mapping**: Inferno's namespace operations map directly to Plan 9:

| Inferno | Plan 9 | Notes |
|---------|--------|-------|
| `bind '#I' /net` | `bind '#I' /net` | Identical syntax |
| `mount tcp!host!port /mnt` | `mount /srv/host /mnt` | Slightly different addressing |
| `listen -A tcp!*!6666` | `aux/listen1 tcp!*!564` | Different listener daemon |
| `export /` | `exportfs` | Same concept, different tool |

**Build system mapping**: Both use mk (mk originated in Plan 9):

| Inferno | Plan 9 | Notes |
|---------|--------|-------|
| `limbo file.b` | `6c file.c && 6l -o file file.6` | Compile + link |
| `mkfile` | `mkfile` | Identical build system |
| `mk install` | `mk install` | Same command |

### Layer 3: Packaging (skill-creator)

The final skill-creator wrapping produces:
- SKILL.md with Plan 9-specific triggers and instructions
- Scripts adapted for Plan 9 toolchain validation
- Templates with Plan 9 devcontainer configuration
- References documenting Plan 9 namespace patterns

## Data Flow

```
                    +-----------------------------+
                    |   skill-creator              |
                    |   (package as skill)         |
                    +-------------+---------------+
                                  |
                    +-------------v---------------+
                    |   function-creator            |
                    |   (Inferno -> Plan 9 mapping) |
                    +-------------+---------------+
                                  |
              +-------------------v-------------------+
              |   inferno-devcontainer                 |
              |   (infrastructure template)            |
              +-------------------+-------------------+
                                  |
              +-------------------v-------------------+
              |   manuscog-cognitive-devkernel          |
              |   (cognitive architecture enrichment)   |
              +---+-------+-------+-------+-----------+
                  |       |       |       |
            +-----v-+ +--v----+ +v------+ +v---------+
            | PLA   | | CogFS | | Temp  | | Autog    |
            | 8     | | tc->  | | tc-nn | | self-    |
            | prom  | | 9P2K  | | ->svc | | image    |
            +-------+ +-------+ +-------+ +----------+
```

## Plan 9 Namespace as Cognitive Substrate

Plan 9's design philosophy — "everything is a file server" — makes it a natural substrate for cognitive architectures. Each cognitive service is a 9P2000 file server that can be:

1. **Mounted** into any process's namespace: `mount /srv/atomspace /cognitive/atomspace`
2. **Bound** for union directories: `bind -a /mnt/cpu2/cognitive /cognitive`
3. **Exported** across the network: `exportfs -r /cognitive`
4. **Composed** per-process: each cognitive agent sees its own namespace view

This is fundamentally different from Inferno (which also uses 9P/Styx) because Plan 9 runs natively on hardware with per-process kernel namespaces, while Inferno runs in a hosted VM with per-process virtual namespaces. The cognitive architecture maps more directly to Plan 9's kernel-level namespace support.
