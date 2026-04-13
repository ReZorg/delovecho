# AGI-OS Build Dependency Order

## Table of Contents

1. [Stage Overview](#stage-overview)
2. [Full Dependency Map](#full-dependency-map)
3. [Debian Package Required Files](#debian-package-required-files)
4. [Validation Commands](#validation-commands)

## Stage Overview

| Stage | Packages |
|-------|----------|
| 0 | cognumach, inferno-kernel |
| 1 | cogutil, ggml-tensor, opennars-native, webvm |
| 2 | atomspace, cognumach-cognitive-scheduler, cogplan9, d81p9p9 |
| 3 | atomspace-cog, atomspace-rocks, atomspace-pgres, atomspace-storage, cogcities-kernel, node-llama-cog |
| 4 | cogserver, ure, atomspace-9p |
| 4.5 | hurdcog, hurdcog-cogkernel-core, hurdcog-machspace, hurdcog-occ-bridge |
| 5 | attention, pln, miner, unify, spacetime, cognitive-grip, hurdcog-atomspace-bridge |
| 6 | learn, generate, cogbolt, das, hyperon-metta |
| 7 | lg-atomese, relex, das-atomspace, aphroditecho, deltecho |
| 8 | moses, asmoses, agi-bio, vision |
| 9 | opencog (meta-package) |
| 10 | agi-os-unified |

## Full Dependency Map

```
cognumach (Stage 0)         → no deps
inferno-kernel (Stage 0)    → no deps
cogutil (Stage 1)           → no deps
ggml-tensor (Stage 1)       → no deps
opennars-native (Stage 1)   → no deps
webvm (Stage 1)             → no deps
atomspace (Stage 2)         → cogutil
cognumach-cog-sched (2)     → cognumach, cogutil
cogplan9 (Stage 2)          → inferno-kernel
d81p9p9 (Stage 2)           → inferno-kernel
atomspace-cog (Stage 3)     → atomspace
atomspace-rocks (Stage 3)   → atomspace
atomspace-pgres (Stage 3)   → atomspace
atomspace-storage (Stage 3) → atomspace
cogcities-kernel (Stage 3)  → cogplan9
node-llama-cog (Stage 3)    → ggml-tensor
cogserver (Stage 4)         → atomspace
ure (Stage 4)               → atomspace
atomspace-9p (Stage 4)      → atomspace, inferno-kernel
hurdcog (Stage 4.5)         → cognumach, cogutil, atomspace
hurdcog-cogkernel (4.5)     → hurdcog
hurdcog-machspace (4.5)     → hurdcog
hurdcog-occ-bridge (4.5)    → hurdcog, atomspace
attention (Stage 5)         → atomspace, cogserver
pln (Stage 5)               → atomspace, ure
miner (Stage 5)             → atomspace, ure
unify (Stage 5)             → atomspace
spacetime (Stage 5)         → atomspace
cognitive-grip (Stage 5)    → cogutil, atomspace, atomspace-storage
hurdcog-as-bridge (5)       → hurdcog, atomspace
learn (Stage 6)             → atomspace, atomspace-rocks, ure
generate (Stage 6)          → atomspace, ure
cogbolt (Stage 6)           → cogutil, atomspace
das (Stage 6)               → atomspace
hyperon-metta (Stage 6)     → atomspace
lg-atomese (Stage 7)        → atomspace
relex (Stage 7)             → no deps
das-atomspace (Stage 7)     → das, atomspace
aphroditecho (Stage 7)      → ggml-tensor, atomspace
deltecho (Stage 7)          → atomspace
moses (Stage 8)             → cogutil, atomspace
asmoses (Stage 8)           → moses, atomspace
agi-bio (Stage 8)           → atomspace, pln, ure
vision (Stage 8)            → atomspace
opencog (Stage 9)           → all core OCC packages
agi-os-unified (Stage 10)   → cognumach, hurdcog, opencog, inferno-kernel
```

## Debian Package Required Files

Every package in `infrastructure/packaging/debian/<pkg>/` must contain:

```
debian/
├── control          # Package metadata and dependencies
├── rules            # Build instructions (must be executable)
├── changelog        # Version history
├── compat           # Debhelper compatibility level
├── copyright        # License information
└── source/
    └── format       # Source format (3.0 quilt)
```

## Validation Commands

```bash
# Validate all packages
cd infrastructure/packaging/debian
bash validate-packaging.sh

# Show build order
bash resolve-dependencies.sh order

# Check for missing package directories
bash resolve-dependencies.sh check

# Generate dependency graph (DOT format)
bash resolve-dependencies.sh graph
```
