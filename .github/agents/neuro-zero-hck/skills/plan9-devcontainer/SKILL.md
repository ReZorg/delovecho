---
name: plan9-devcontainer
description: "Optimal devcontainer configuration for Plan 9 from Bell Labs / 9front development. Use when setting up Plan 9 development environments, configuring acme/sam IDE toolchains, deploying distributed CPU server grids via QEMU, building Plan 9 C programs with mk, or creating devcontainer.json for Plan 9 projects. Provides Dockerfile with plan9port and QEMU, docker-compose for CPU server grids, CLI tools, and grid management. Transformed from inferno-devcontainer via function-creator."
---

# Plan 9 Devcontainer

Provision a complete Plan 9 from Bell Labs development environment inside a devcontainer with plan9port tools (acme, sam, mk, rc), QEMU for running native Plan 9/9front, distributed CPU server grid support, and CLI tools.

```
function-creator(inferno-devcontainer) => plan9-devcontainer
```

## Quick Start

1. **Copy templates** into your project:
   ```bash
   cp -r /home/ubuntu/skills/plan9-devcontainer/templates/.devcontainer /path/to/project/
   cp /home/ubuntu/skills/plan9-devcontainer/templates/docker-compose.grid.yml /path/to/project/
   cp /home/ubuntu/skills/plan9-devcontainer/templates/.editorconfig /path/to/project/
   ```

2. **Open in VS Code** with the Dev Containers extension, or run:
   ```bash
   devcontainer up --workspace-folder /path/to/project
   ```

3. **Start the CPU server grid** inside the container:
   ```bash
   plan9-grid start
   ```

## What the Devcontainer Provides

| Component | Description |
|-----------|-------------|
| **plan9port** | Full build from `9fans/plan9port` (acme, sam, mk, rc, 9P tools) |
| **QEMU** | Run native Plan 9 / 9front inside the container |
| **acme IDE** | VS Code with Plan 9 C file associations + native acme via plan9port |
| **Grid CLI** | `plan9-grid` for start/stop/status/connect/deploy |
| **Build CLI** | `plan9-build` for compile/run/check/clean via plan9port |
| **Grid Monitor** | Flask dashboard on port 9090 |
| **Docker-in-Docker** | Nested containers for multi-node CPU server grids |
| **9P2000 Networking** | Pre-configured ports 564-566 for distributed namespaces |

## devcontainer.json Architecture

### 1. Build Configuration

Multi-stage Dockerfile: builds plan9port from source, installs QEMU:
- **Stage 1 (builder):** Clones and compiles plan9port on Ubuntu 22.04
- **Stage 2 (development):** Runtime with QEMU, dev tools, plan9port binaries

Build arguments control grid size and GUI support:
```json
"build": {
    "args": {
        "PLAN9": "/usr/local/plan9",
        "GRID_NODES": "3",
        "ENABLE_GUI": "true"
    }
}
```

### 2. Devcontainer Features

Pre-installed features:
- `common-utils` — Bash, non-root user (glenda)
- `docker-in-docker` — Docker Compose v2 for grid deployment
- `git`, `github-cli` — Version control
- `python` — Grid monitor scripts
- `node` — Tooling support

### 3. VS Code Customizations

File associations map Plan 9 C extensions (`.c`, `.h`) and build files (`mkfile`, `mkconfig`). Extensions include C/C++ tools, Makefile tools, Docker, Git Graph, and error lens. Tab width is set to 8 (Plan 9 convention).

### 4. Port Forwarding

| Port | Service |
|------|--------|
| 564-566 | 9P2000 listeners (one per grid node) |
| 8080 | Plan 9 web interface |
| 9090 | Grid monitor dashboard |

### 5. Lifecycle Scripts

- **post-create.sh** — Runs once: verifies plan9port + QEMU, creates workspace, configures grid, installs CLIs
- **post-start.sh** — Runs on every start: verifies PATH, ensures Docker network, displays status

## CLI Tools

### plan9-grid

Manage the distributed Plan 9 CPU server grid:

```bash
plan9-grid start [--nodes N]    # Start grid (default: 3 nodes)
plan9-grid stop                 # Stop all nodes
plan9-grid status               # Show node status table
plan9-grid connect <node-id>    # Connect to a node via 9P2000
plan9-grid deploy <file.out>    # Deploy executable to all nodes
plan9-grid logs [node-id]       # Tail logs
```

### plan9-build

Compile and run Plan 9 C programs via plan9port:

```bash
plan9-build compile src/hello.c  # Compile with 9c/9l
plan9-build run src/hello.c      # Compile and run
plan9-build check src/hello.c    # Syntax check only
plan9-build clean                # Remove .o and .out files
```

## Distributed CPU Server Grid

The grid uses Docker Compose with QEMU-based Plan 9 instances:

| Service | Role | Scaling |
|---------|------|---------|
| `plan9-registry` | Auth/name server, coordinator | 1 (fixed) |
| `plan9-cpu` | CPU server, distributed processing | N (scalable) |
| `plan9-monitor` | Web dashboard | 1 (fixed) |

Scale CPU servers:
```bash
docker compose -f docker-compose.grid.yml --scale plan9-cpu=10 up -d
```

**For grid topologies and 9P2000 networking patterns**, read `references/distributed_grid_patterns.md`.

## IDE Options

| IDE | Launch | Best For |
|-----|--------|----------|
| **VS Code** | Automatic via devcontainer | Modern editing, extensions, tasks |
| **acme** | `9 acme /workspace/src` | Native Plan 9 mouse-driven IDE |
| **sam** | `9 sam file.c` | Structural regex editing |

**For detailed IDE setup, keybindings, and compiler flags**, read `references/plan9c_ide_guide.md`.

## Customization

Modify `devcontainer.json` build args, ports, and features to match your needs.

**For the full customization reference**, read `references/devcontainer_customization.md`.

## Validation

Validate your devcontainer configuration:

```bash
python3 /home/ubuntu/skills/plan9-devcontainer/scripts/validate_devcontainer.py /path/to/project
```

## Bundled Resources

- **`scripts/`**
  - `grid_monitor.py` — Flask-based grid dashboard (port 9090)
  - `validate_devcontainer.py` — Validate devcontainer configuration
- **`references/`**
  - `distributed_grid_patterns.md` — Grid topologies, 9P2000 networking, scaling strategies
  - `plan9c_ide_guide.md` — acme, sam, VS Code, compiler flags, debugging
  - `devcontainer_customization.md` — All devcontainer.json fields and options
- **`templates/`**
  - `.devcontainer/` — Complete devcontainer config (Dockerfile, devcontainer.json, scripts)
  - `docker-compose.grid.yml` — Multi-node CPU server grid deployment
  - `src/hello.c` — Sample Plan 9 C program
  - `mkfile` — Plan 9 build file template
  - `.editorconfig` — Editor formatting rules (tab width 8)

## Composition with Other Skills

| Skill | Composition |
|-------|------------|
| **inferno-devcontainer** | Source skill — transformed to Plan 9 analogue |
| **plan9-cognitive-devkernel** | Enriched version with cognitive architecture |
| **function-creator** | This skill was generated via function-creator transformation |
| **skill-creator** | Used for packaging and validation |
