# Devcontainer Customization Guide

## Table of Contents

1. [devcontainer.json Key Fields](#devcontainerjson-key-fields)
2. [Build Arguments](#build-arguments)
3. [Feature Configuration](#feature-configuration)
4. [Port Mapping](#port-mapping)
5. [Volume Mounts](#volume-mounts)
6. [Environment Variables](#environment-variables)
7. [Lifecycle Scripts](#lifecycle-scripts)

## devcontainer.json Key Fields

| Field | Purpose | Default |
|-------|---------|---------|
| `name` | Container display name | "Inferno-OS Cognitive Kernel Development" |
| `build.dockerfile` | Path to Dockerfile | "Dockerfile" |
| `build.args.CLUSTER_NODES` | Number of cluster nodes | 3 |
| `build.args.ENABLE_GUI` | Enable X11/GUI support | true |
| `features` | Devcontainer features to install | common-utils, docker-in-docker, git, python |
| `forwardPorts` | Ports to forward to host | [6666-6668, 8080, 9090] |
| `containerEnv` | Environment variables | INFERNO_ROOT, EMU, LIMBO, PATH |
| `postCreateCommand` | Run after container creation | post-create.sh |
| `postStartCommand` | Run on every container start | post-start.sh |
| `remoteUser` | Default user inside container | "inferno" |
| `hostRequirements` | Minimum host resources | 4 CPUs, 8GB RAM, 32GB storage |

## Build Arguments

Customize the build by modifying `build.args` in devcontainer.json:

```json
"build": {
    "args": {
        "INFERNO_ROOT": "/usr/inferno",
        "CLUSTER_NODES": "5",
        "ENABLE_GUI": "false"
    }
}
```

| Argument | Type | Description |
|----------|------|-------------|
| `INFERNO_ROOT` | path | Inferno installation directory |
| `CLUSTER_NODES` | integer | Number of pre-configured cluster nodes |
| `ENABLE_GUI` | boolean | Install X11 libraries for GUI support |

## Feature Configuration

### Docker-in-Docker

Required for running cluster nodes as nested containers:

```json
"ghcr.io/devcontainers/features/docker-in-docker:2": {
    "dockerDashComposeVersion": "v2"
}
```

### Python

Required for cognitive kernel scripts and cluster monitor:

```json
"ghcr.io/devcontainers/features/python:1": {
    "version": "3.11"
}
```

### Adding Custom Features

To add more features, append to the `features` object:

```json
"ghcr.io/devcontainers/features/rust:1": {},
"ghcr.io/devcontainers/features/go:1": {}
```

## Port Mapping

### Default Ports

| Port | Service | Protocol |
|------|---------|----------|
| 6666 | 9P/Styx — Node 0 (Registry) | TCP |
| 6667 | 9P/Styx — Node 1 | TCP |
| 6668 | 9P/Styx — Node 2 | TCP |
| 8080 | Inferno Web Interface | HTTP |
| 9090 | Cluster Monitor Dashboard | HTTP |

### Adding Ports for More Nodes

For clusters larger than 3 nodes, add ports:

```json
"forwardPorts": [6666, 6667, 6668, 6669, 6670, 8080, 9090]
```

## Volume Mounts

### Persistent Volumes

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `inferno-devcontainer-home` | `/home/inferno` | User home directory persistence |
| `inferno-cluster-data` | `/var/inferno/cluster` | Cluster state and logs |

### Adding Custom Mounts

```json
"mounts": [
    "source=my-data,target=/data,type=volume",
    "source=${localWorkspaceFolder}/config,target=/workspace/config,type=bind"
]
```

## Environment Variables

### Required Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `INFERNO_ROOT` | `/usr/inferno` | Inferno installation root |
| `EMU` | `${INFERNO_ROOT}/Linux/amd64/bin/emu` | Path to emu binary |
| `LIMBO` | `${INFERNO_ROOT}/Linux/amd64/bin/limbo` | Path to Limbo compiler |
| `PATH` | Prepend `${INFERNO_ROOT}/Linux/amd64/bin` | Include Inferno tools in PATH |

### Cluster Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `INFERNO_CLUSTER_NODES` | `3` | Number of cluster nodes |
| `INFERNO_9P_PORT` | `6666` | Base port for 9P listeners |
| `DISPLAY` | `:0` | X11 display for GUI applications |

## Lifecycle Scripts

### post-create.sh (runs once)

1. Verifies Inferno installation (emu, limbo)
2. Creates workspace directory structure
3. Generates sample Limbo source files and module templates
4. Configures cluster node directories
5. Installs `inferno-cluster` and `limbo-build` CLI tools

### post-start.sh (runs on every start)

1. Verifies PATH includes Inferno binaries
2. Ensures Docker network exists for cluster
3. Creates missing cluster directories
4. Displays environment summary
