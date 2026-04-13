# MIG (Mach Interface Generator) Locations

## Table of Contents

1. [Overview](#overview)
2. [Location Map](#location-map)
3. [Unified Build Entry Point](#unified-build-entry-point)
4. [HurdCog MIG References](#hurdcog-mig-references)

## Overview

MIG (Mach Interface Generator) is a critical build tool required by both CogNUMach (Layer 1) and HurdCog (Layer 2). It generates C code from Mach interface definition files (`.defs`). Due to the multi-subsystem architecture, MIG source exists in multiple locations that must be kept in sync.

## Location Map

| Location | Type | Role |
|----------|------|------|
| `build-tools/mig/CMakeLists.txt` | CMake wrapper | **Unified build entry point** |
| `core/microkernel/cognumach/mig/` | Full source | Primary MIG source with migcom.c |
| `core/microkernel/mig/` | Full source | Mirror of cognumach MIG |
| `core/os/hurdcog/mig.backup/` | Full source | HurdCog backup copy |
| `core/os/mig.backup/` | Full source | Root-level backup copy |
| `core/os/hurdcog/external/hurd-repos/mig` | Git ref | External reference to upstream MIG |
| `core/microkernel/cognumach/Makerules.mig.am` | Build rules | Autotools MIG rules for cognumach |
| `core/microkernel/Makerules.mig.am` | Build rules | Autotools MIG rules (mirror) |

## Unified Build Entry Point

The `build-tools/mig/CMakeLists.txt` automatically searches all known locations in priority order:

1. `core/microkernel/cognumach/mig/` (preferred)
2. `core/microkernel/mig/`
3. `core/os/hurdcog/mig.backup/`
4. `core/os/mig.backup/`

It supports both autotools-native build (`MIG_USE_AUTOTOOLS=ON`) and a simplified direct CMake build.

## HurdCog MIG References

HurdCog uses MIG extensively through `mig-decls.h` and `mig-mutate.h` files in many subsystem directories:

```
core/os/hurdcog/auth/mig-{decls,mutate}.h
core/os/hurdcog/boot/mig-{decls,mutate}.h
core/os/hurdcog/exec/mig-decls.h
core/os/hurdcog/eth-multiplexer/mig-{decls,mutate}.h
core/os/hurdcog/acpi/mig-mutate.h
core/os/hurdcog/devnode/mig-mutate.h
```

These files configure how MIG-generated stubs are customized for each Hurd server/translator. They depend on MIG being installed and available in the build path.

Key MIG-related kernel files:
- `core/microkernel/cognumach/kern/ipc_mig.{c,h}` — IPC MIG integration
- `core/microkernel/cognumach/include/mach/mig_{errors,support}.h` — MIG headers
- `core/microkernel/cognumach/scripts/fix-mig-64bit.sh` — 64-bit MIG fixes
- `core/microkernel/cognumach/scripts/mig-wrapper.sh` — MIG wrapper script
