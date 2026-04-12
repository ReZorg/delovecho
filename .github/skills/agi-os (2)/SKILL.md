---
name: agi-os
description: Analyze, build, fix, and evolve the agi-os repository — an autonomous AGI operating system integrating OpenCog (OCC), CogNUMach microkernel, HurdCog cognitive OS, Inferno Kernel, CogBolt IDE, and Deep Tree Echo. Use when working on the o9nn/agi-os GitHub repository, fixing build errors, completing Debian packaging, managing build dependency order, integrating MIG across subsystems, or evolving the repo toward unified cognitive synergy. Triggers on mentions of agi-os, cognumach, hurdcog, opencog collection, occ, cogbolt, inferno kernel, cognitive grip, MIG mach interface generator, debian packaging for cognitive OS components, koboldcpp-cog, or cognitive LLM inference.
---

# AGI-OS Skill

Manage, build, fix, and evolve the `o9nn/agi-os` repository — a multi-layer autonomous AGI operating system.

## Repository Structure

```
agi-os/
├── build-tools/mig/          # Unified MIG build entry point
├── config/
│   ├── cogserver/             # CogServer + Guile shell configuration
│   │   ├── cogserver.conf     # Network config (port 17001)
│   │   └── agi-os-init.scm   # Guile init, module loading, assistants
│   └── assistants/            # KoboldCpp-powered AI assistants
│       ├── agi-os-assistant   # Unified launcher
│       ├── engineer_assistant.py
│       ├── dev_assistant.py
│       └── mgmt_assistant.py
├── core/
│   ├── microkernel/cognumach/ # Layer 1: CogNUMach (autotools)
│   ├── os/hurdcog/            # Layer 2: HurdCog cognitive OS
│   ├── cognition/
│   │   ├── foundation/        # cogutil, atomspace, cogserver, etc.
│   │   ├── reasoning/         # PLN, URE
│   │   └── llm/koboldcpp-cog/ # Layer 3.7: Cognitive LLM bridge
│   ├── integration/           # cognitive-grip, unified-cog-interface
│   └── inferno-kernel/        # Layer 0: Inferno Kernel + 9P
├── cogbolt/                   # Layer 4: AI-Powered IDE
├── infrastructure/packaging/  # Debian packaging (52 packages)
├── .github/
│   ├── scripts/component-paths.sh  # Canonical path mapping
│   └── workflows/agi-os-bootstrap.yml  # Unified build pipeline
└── CMakeLists.txt             # Root build orchestration
```

## Build Layers

| Layer | Component | Build System | Key Dependencies |
|-------|-----------|-------------|------------------|
| 0 | Inferno Kernel, MIG | CMake/Autotools | None |
| 1 | CogNUMach | Autotools | MIG |
| 2 | HurdCog | Autotools+CMake | CogNUMach, cogutil, atomspace |
| 3 | OpenCog Collection | CMake | cogutil → atomspace → storage → cogserver |
| 3.7 | KoboldCpp-Cog | CMake | cogutil, atomspace, ggml-tensor |
| 4 | CogBolt | CMake | cogutil, atomspace |

## CogServer Guile Shell

Start: `cogserver -c config/cogserver/cogserver.conf` then `rlwrap telnet localhost 17001`

The Guile shell (`agi-os-init.scm`) loads OpenCog modules with graceful degradation and provides:

| Command | Purpose |
|---------|---------|
| `(agi-os-status)` | Show all subsystem status |
| `(agi-os-help)` | List available commands |
| `(agi-os-ask "question")` | Cognitive query via KoboldCpp |
| `(agi-os-engineer "q")` | Engineering assistant |
| `(agi-os-dev "q")` | Development assistant |
| `(agi-os-manage "cmd")` | Management assistant |

## KoboldCpp Assistants

Three Python assistants powered by KoboldCpp-Cog, plus a unified launcher:

```bash
config/assistants/agi-os-assistant engineer "How do I add a CogServer module?"
config/assistants/agi-os-assistant dev "Write a PLN rule for inheritance"
config/assistants/agi-os-assistant manage health
config/assistants/agi-os-assistant manage build-order
config/assistants/agi-os-assistant manage packaging
config/assistants/agi-os-assistant manage workflows
config/assistants/agi-os-assistant manage recommend
```

The **management assistant** (`mgmt_assistant.py`) provides offline subsystem monitoring: health checks (14 subsystems), packaging validation (52 packages), workflow analysis (43 workflows), and dependency-resolved build order.

## GitHub Actions

**Root cause of failures**: Workflows reference root-level paths (`cogutil/`, `atomspace/`) but actual paths are nested (`core/cognition/foundation/cogutil/`). Use `.github/scripts/component-paths.sh` for canonical mapping.

**`agi-os-bootstrap.yml`**: Correct 6-stage pipeline — CogUtil → AtomSpace → Storage+CogServer → URE+PLN+Attention → KoboldCpp-Cog → Integration.

## Common Workflows

### Fix and validate Debian packaging
1. Run `cd infrastructure/packaging/debian && bash validate-packaging.sh`
2. Fix missing files (control, rules, changelog, compat, copyright, source/format)
3. Update `resolve-dependencies.sh` with new packages

### Fix truncated shell scripts
Search: `grep -rn 'while \[\[ \$\s*$' --include='*.sh' . | grep -v '.git/'`
Pattern: `while [[ $` → `while [[ $# -gt 0 ]]; do`

### Push workflow files
The default GitHub App token lacks `workflows` scope. Use `DEVORG` PAT: `git remote set-url origin "https://x-access-token:${DEVORG}@github.com/o9nn/agi-os.git"`

## Key References

- **Build dependency order**: See `references/build-dependency-order.md`
- **MIG locations**: See `references/mig-locations.md`
- **Subsystem architecture**: See `references/subsystem-architecture.md`
