---
name: inferno-devcontainer
description: "Optimal devcontainer configuration for Inferno-OS cognitive kernel development. Use when setting up Inferno-OS development environments, configuring Limbo IDE toolchains, deploying distributed Inferno VM clusters, building OpenCog-Inferno kernel modules, or creating devcontainer.json for Inferno/Limbo projects. Provides Dockerfile, docker-compose, CLI tools, and cluster management. Transformed from opencog-inferno-kernel via function-creator."
---

# Inferno-OS Cognitive Kernel Devcontainer

Provision a complete Inferno-OS development environment inside a devcontainer with a Limbo IDE, distributed VM cluster support, and CLI tools for the OpenCog-Inferno cognitive kernel.

## Quick Start

1. **Copy templates** into your project:
   ```bash
   cp -r /home/ubuntu/skills/inferno-devcontainer/templates/.devcontainer /path/to/project/
   cp /home/ubuntu/skills/inferno-devcontainer/templates/docker-compose.cluster.yml /path/to/project/
   cp /home/ubuntu/skills/inferno-devcontainer/templates/.editorconfig /path/to/project/
   ```

2. **Open in VS Code** with the Dev Containers extension, or run:
   ```bash
   devcontainer up --workspace-folder /path/to/project
   ```

3. **Start the cluster** inside the container:
   ```bash
   inferno-cluster start
   ```

## What the Devcontainer Provides

| Component | Description |
|-----------|-------------|
| **Inferno-OS** | Full build from `inferno-os/inferno-os` (emu, limbo, mk, Acme) |
| **Limbo IDE** | VS Code with Limbo file associations + Acme inside emu |
| **Cluster CLI** | `inferno-cluster` for start/stop/status/deploy/connect |
| **Build CLI** | `limbo-build` for compile/run/check/clean |
| **Cluster Monitor** | Flask dashboard on port 9090 |
| **Docker-in-Docker** | Nested containers for multi-node clusters |
| **9P/Styx Networking** | Pre-configured ports 6666-6668 for distributed namespaces |

## devcontainer.json Architecture

The `devcontainer.json` is structured around five key areas:

### 1. Build Configuration

Multi-stage Dockerfile derived from the official `inferno-os/inferno-os` Dockerfile:
- **Stage 1 (builder):** Clones and compiles Inferno from source on Ubuntu 22.04
- **Stage 2 (development):** Runtime with dev tools, copies built binaries

Build arguments control cluster size and GUI support:
```json
"build": {
    "args": {
        "INFERNO_ROOT": "/usr/inferno",
        "CLUSTER_NODES": "3",
        "ENABLE_GUI": "true"
    }
}
```

### 2. Devcontainer Features

Pre-installed features for a complete development environment:
- `common-utils` — Zsh, Oh My Zsh, non-root user
- `docker-in-docker` — Docker Compose v2 for cluster deployment
- `git`, `github-cli` — Version control
- `python` — Cognitive kernel scripts, cluster monitor
- `node` — Tooling support

### 3. VS Code Customizations

File associations map Limbo extensions (`.b`, `.m`) and Inferno build files (`mkfile`, `mkconfig`). Extensions include C/C++ tools, Makefile tools, Docker, Git Graph, and error lens.

### 4. Port Forwarding

| Port | Service |
|------|--------|
| 6666-6668 | 9P/Styx listeners (one per cluster node) |
| 8080 | Inferno web interface |
| 9090 | Cluster monitor dashboard |

### 5. Lifecycle Scripts

- **post-create.sh** — Runs once: verifies Inferno, creates workspace, configures cluster, installs CLIs
- **post-start.sh** — Runs on every start: verifies PATH, ensures Docker network, displays status

## CLI Tools

### inferno-cluster

Manage the distributed Inferno VM cluster:

```bash
inferno-cluster start [--nodes N]    # Start cluster (default: 3 nodes)
inferno-cluster stop                 # Stop all nodes
inferno-cluster status               # Show node status table
inferno-cluster connect <node-id>    # Connect to a node via 9P
inferno-cluster deploy <file.dis>    # Deploy Dis module to all nodes
inferno-cluster logs [node-id]       # Tail logs
```

### limbo-build

Compile and run Limbo programs:

```bash
limbo-build compile src/hello.b      # Compile to .dis
limbo-build run src/hello.b          # Compile and run in emu
limbo-build check src/hello.b        # Type-check only
limbo-build clean                    # Remove .dis and .sbl files
```

## Distributed VM Cluster

The cluster uses Docker Compose with three service types:

| Service | Role | Scaling |
|---------|------|---------|
| `inferno-registry` | Coordinator, name registry | 1 (fixed) |
| `inferno-node` | Worker, cognitive processing | N (scalable) |
| `inferno-monitor` | Web dashboard | 1 (fixed) |

Scale workers:
```bash
docker compose -f docker-compose.cluster.yml --scale inferno-node=10 up -d
```

**For cluster topologies and 9P networking patterns**, read `references/distributed_vm_patterns.md`.

## Limbo IDE Options

The devcontainer supports multiple IDE workflows:

| IDE | Launch | Best For |
|-----|--------|----------|
| **VS Code** | Automatic via devcontainer | Modern editing, extensions, tasks |
| **Acme** | `emu -c1 "wm/wm; acme"` | Native Inferno mouse-driven IDE |
| **Vim** | `vim file.b` | Terminal-based editing |

**For detailed IDE setup, keybindings, and compiler flags**, read `references/limbo_ide_guide.md`.

## Customization

Modify `devcontainer.json` build args, ports, and features to match your needs.

**For the full customization reference**, read `references/devcontainer_customization.md`.

## Validation

Validate your devcontainer configuration:

```bash
python3 /home/ubuntu/skills/inferno-devcontainer/scripts/validate_devcontainer.py /path/to/project
```

## Bundled Resources

- **`scripts/`**
  - `cluster_monitor.py` — Flask-based cluster dashboard (port 9090)
  - `validate_devcontainer.py` — Validate devcontainer configuration
- **`references/`**
  - `distributed_vm_patterns.md` — Cluster topologies, 9P networking, scaling strategies
  - `limbo_ide_guide.md` — Acme, VS Code, compiler flags, debugging
  - `devcontainer_customization.md` — All devcontainer.json fields and options
- **`templates/`**
  - `.devcontainer/` — Complete devcontainer configuration (Dockerfile, devcontainer.json, scripts, Limbo syntax)
  - `docker-compose.cluster.yml` — Multi-node cluster deployment
  - `src/cogkernel.b` — Sample cognitive kernel Limbo module
  - `mkfile` — Inferno build file template
  - `.editorconfig` — Editor formatting rules

## Composition with Other Skills

| Skill | Composition |
|-------|------------|
| **opencog-inferno-kernel** | Source skill — kernel C code runs inside this devcontainer |
| **function-creator** | This skill was generated via function-creator transformation |
| **skill-creator** | Used for packaging and validation |
| **gh253** | GitHub repository patterns for the manuscog project |
