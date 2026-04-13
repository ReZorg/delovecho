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
| `name` | Container display name | "Plan 9 Development" |
| `build.dockerfile` | Path to Dockerfile | "Dockerfile" |
| `build.args.GRID_NODES` | Number of grid nodes | 3 |
| `build.args.ENABLE_GUI` | Enable X11/GUI support | true |
| `features` | Devcontainer features to install | common-utils, docker-in-docker, git, python |
| `forwardPorts` | Ports to forward to host | [564-566, 8080, 9090] |
| `containerEnv` | Environment variables | PLAN9, PATH |
| `postCreateCommand` | Run after container creation | post-create.sh |
| `postStartCommand` | Run on every container start | post-start.sh |
| `remoteUser` | Default user inside container | "glenda" |
| `hostRequirements` | Minimum host resources | 4 CPUs, 8GB RAM, 32GB storage |

## Build Arguments

Customize the build by modifying `build.args` in devcontainer.json:

```json
"build": {
    "args": {
        "PLAN9": "/usr/local/plan9",
        "GRID_NODES": "5",
        "ENABLE_GUI": "false"
    }
}
```

| Argument | Type | Description |
|----------|------|-------------|
| `PLAN9` | path | plan9port installation directory |
| `GRID_NODES` | integer | Number of pre-configured grid nodes |
| `ENABLE_GUI` | boolean | Install X11 libraries for GUI support (acme) |

## Feature Configuration

### Docker-in-Docker

Required for running grid nodes as nested containers:

```json
"ghcr.io/devcontainers/features/docker-in-docker:2": {
    "dockerDashComposeVersion": "v2"
}
```

### Python

Required for grid monitor scripts:

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
| 564 | 9P2000 — CPU 0 (Auth/Registry) | TCP |
| 565 | 9P2000 — CPU 1 | TCP |
| 566 | 9P2000 — CPU 2 | TCP |
| 8080 | Plan 9 Web Interface | HTTP |
| 9090 | Grid Monitor Dashboard | HTTP |

### Adding Ports for More Nodes

For grids larger than 3 nodes, add ports:

```json
"forwardPorts": [564, 565, 566, 567, 568, 8080, 9090]
```

## Volume Mounts

### Persistent Volumes

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `plan9-devcontainer-home` | `/home/glenda` | User home directory persistence |
| `plan9-grid-data` | `/var/plan9/grid` | Grid state and logs |

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
| `PLAN9` | `/usr/local/plan9` | plan9port installation root |
| `PATH` | Prepend `$PLAN9/bin` | Include plan9port tools in PATH |

### Grid Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PLAN9_GRID_NODES` | `3` | Number of grid nodes |
| `PLAN9_9P_PORT` | `564` | Base port for 9P2000 listeners |
| `DISPLAY` | `:0` | X11 display for GUI applications (acme) |

## Lifecycle Scripts

### post-create.sh (runs once)

1. Verifies plan9port installation (acme, sam, mk, rc, 9p)
2. Verifies QEMU installation
3. Creates workspace directory structure
4. Generates sample Plan 9 C source files
5. Configures grid node directories
6. Installs `plan9-grid` and `plan9-build` CLI tools

### post-start.sh (runs on every start)

1. Verifies PATH includes plan9port binaries
2. Ensures Docker network exists for grid
3. Creates missing grid directories
4. Displays environment summary
