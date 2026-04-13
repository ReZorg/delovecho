# Deployment Guide

## Table of Contents

1. [Python Simulation Mode](#python-simulation-mode)
2. [C Kernel Simulation Build](#c-kernel-simulation-build)
3. [Inferno Kernel Integration](#inferno-kernel-integration)
4. [Limbo User-Space Module](#limbo-user-space-module)
5. [Project Scaffolding](#project-scaffolding)

## Python Simulation Mode

The Python daemon provides a full-fidelity simulation of the kernel without requiring Inferno.

```bash
# Run interactive CLI
python3 scripts/glyph_noetic_kernel_daemon.py --cli

# Execute a single sentence
python3 scripts/glyph_noetic_kernel_daemon.py -e "[K:STATUS]?"

# Run full test suite (19 tests)
python3 scripts/glyph_noetic_kernel_daemon.py --test

# Run health check (all subsystems)
python3 scripts/glyph_noetic_kernel_daemon.py --health
```

No dependencies beyond Python 3.8+ standard library.

## C Kernel Simulation Build

Build the C kernel modules in simulation mode (standard Linux, no Inferno required):

```bash
cd kernel/
make clean && make all
./build/glyph_kernel_test   # 23 tests
```

Requires: `gcc`, `make`, `libc`. The `GLYPH_KERNEL_SIMULATION` define enables standard C headers instead of Inferno's `lib9.h`/`kernel.h`.

## Inferno Kernel Integration

To compile for a real Inferno kernel, remove the `GLYPH_KERNEL_SIMULATION` define and link against Inferno's kernel libraries:

1. Place `kernel/src/*.c` and `kernel/include/glyph.h` in the Inferno source tree under `os/port/`
2. Add to the kernel configuration: `dev glyph devglyph.c glyph.c temporal.c p9topo.c atomspace.c promises.c`
3. Rebuild the Inferno kernel with `mk`

The `/dev/glyph` device will appear automatically. The `/n/glyph` namespace is mounted at boot.

## Limbo User-Space Module

Compile and use the Limbo module:

```sh
limbo limbo/module/cogkernel_glyph.b
cogkernel_glyph --health          # Full health check
cogkernel_glyph "[T:ASSEMBLY]?"   # Single query
cogkernel_glyph --glyphs          # List all glyphs
cogkernel_glyph --topology        # Topology status
cogkernel_glyph --autognosis      # Self-awareness status
```

## Project Scaffolding

To scaffold a new glyph-noetic-inferno-engine project from the skill templates:

```bash
DEST=/path/to/project
cp -r /home/ubuntu/skills/glyph-noetic-inferno-engine/templates/* "$DEST/"
cp /home/ubuntu/skills/glyph-noetic-inferno-engine/scripts/glyph_noetic_kernel_daemon.py "$DEST/scripts/"
```

This creates the full project structure:
```
$DEST/
├── docs/topology.mmd
├── kernel/
│   ├── Makefile
│   ├── include/glyph.h
│   └── src/{glyph,temporal,p9topo,atomspace,promises,devglyph}.c
├── limbo/module/cogkernel_glyph.b
├── scripts/glyph_noetic_kernel_daemon.py
└── tests/test_main.c
```
