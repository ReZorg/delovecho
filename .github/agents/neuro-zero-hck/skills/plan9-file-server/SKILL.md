---
name: plan9-file-server
description: "Set up a Plan 9 file server cluster with multiple CPU servers, authentication, and cognitive namespace integration. Use for deploying distributed Plan 9 environments with persistent storage, centralized auth, and support for cognitive architectures. Extends plan9-devcontainer and plan9-cognitive-devkernel."
---

# Plan 9 File Server Cluster

This skill provides a complete, automated setup for a Plan 9 file server cluster, including a dedicated file/auth server and multiple CPU servers. It integrates persistent storage, centralized authentication, and cognitive namespace exports, building upon the `plan9-devcontainer` and `plan9-cognitive-devkernel` skills.

## Composition

This skill is the result of injecting a detailed file server setup guide into the existing cognitive kernel architecture:

```
skill-creator(
  plan9-devcontainer(
    plan9-cognitive-devkernel[
      {{file-server-guide}}
    ]
  )
)
```

- **`plan9-devcontainer`**: Provides the base QEMU/Docker infrastructure.
- **`plan9-cognitive-devkernel`**: Provides the cognitive architecture (namespaces, promises, temporal hierarchy).
- **`file-server-guide`**: Provides the logic for storage (hjfs/cwfs), authentication (faktotum), and multi-node network configuration.

## Quick Start

Use the bundled `configure_cluster.py` script to manage your cluster configuration.

### 1. Initialize Cluster Configuration

Generate all necessary configuration files for a new cluster.

```bash
# Initialize a cluster with 1 file server and 3 CPU servers
python3 /home/ubuntu/skills/plan9-file-server/scripts/configure_cluster.py init /path/to/project --cpus 3 --domain mylab
```

This creates:
- `docker-compose.fileserver.yml`: For deploying the full cluster.
- `templates/`: Contains all generated config files (`ndb-local.conf`, `cpurc`, `plan9.ini`).
- `cluster.json`: The cluster configuration model.

### 2. Deploy the Cluster

Use the generated Docker Compose file to launch the entire cluster.

```bash
cd /path/to/project
docker compose -f docker-compose.fileserver.yml up -d
```

### 3. Validate the Cluster

Check that the cluster configuration satisfies all 8 file server promises.

```bash
python3 /home/ubuntu/skills/plan9-file-server/scripts/configure_cluster.py validate /path/to/project
```

### 4. View Cluster Status

Display the defined cluster promises.

```bash
python3 /home/ubuntu/skills/plan9-file-server/scripts/configure_cluster.py status
```

## Architecture

The cluster consists of a central file server and multiple CPU servers.

| Component | Role |
|---|---|
| **File Server** | Persistent storage (`hjfs`/`cwfs`), authentication (`keyfs`, `faktotum`), and cognitive namespace hub. |
| **CPU Servers** | Distributed computation, run local cognitive services, mount the file server for storage. |
| **Auth Server** | Co-located with the file server, handles all authentication for the cluster. |
| **Cognitive Namespace** | Exported from the file server (`/cognitive/`) and mounted by all CPU servers. |

**For a detailed breakdown of the architecture, file systems, and auth flow, read `references/file_server_architecture.md`.**

## Promise-Lambda Attention

This skill adds 8 new promises to the `plan9-cognitive-devkernel` validation engine, ensuring a correctly configured file server cluster.

| Promise | Constraint |
|---|---|
| `file-server` | File server node is fully configured (cpurc, plan9.ini, ndb). |
| `auth-server` | Authentication services (keyfs, faktotum) are enabled. |
| `ndb-config` | Network database defines all cluster nodes. |
| `cpu-mount` | CPU servers correctly reference the file server for mounting. |
| `cognitive-export` | The cognitive namespace is exported from the file server via 9P2000. |
| `docker-compose` | `docker-compose.fileserver.yml` defines the `plan9-fileserver` service. |
| `fs-storage` | A valid file system type (`hjfs` or `cwfs`) is configured. |
| `cluster-network` | The cluster network subnet and gateway are defined. |

## Cognitive Namespace Integration

The file server is the heart of the distributed cognitive namespace.

- It exports the canonical `/cognitive/` tree on port `5640`.
- CPU servers mount this shared namespace.
- CPU servers can overlay their own local cognitive services (e.g., a local inference engine) using `bind -b`.

This creates a powerful, layered knowledge fabric where a shared, persistent AtomSpace on the file server is augmented by specialized, distributed processing on the CPU servers.

**For detailed binding patterns and examples, read `references/cognitive_namespace_binding.md`.**

## Bundled Resources

- **`scripts/`**
  - `configure_cluster.py`: Main CLI for initializing and validating cluster configurations.
- **`references/`**
  - `file_server_architecture.md`: Deep dive into the cluster topology, file systems, and auth.
  - `cognitive_namespace_binding.md`: Patterns for composing the distributed cognitive namespace.
  - `cluster_troubleshooting.md`: Guide for diagnosing common cluster issues.
- **`templates/`**
  - `src/atomspace_9p.c`: A 9P file server that exposes an AtomSpace as a file tree.
  - `src/cogfs.c`: A skeleton for the main cognitive file server.
  - `mkfile`: Build file for the C programs.
  - `transform_spec.yaml`: The `function-creator` specification for this skill's composition.

## Composition with Other Skills

| Skill | Relationship |
|---|---|
| **plan9-cognitive-devkernel** | This skill enriches the cognitive kernel with persistent storage and multi-node capabilities. |
| **plan9-devcontainer** | Provides the underlying QEMU and Docker infrastructure for the cluster. |
| **skill-creator** | Used to package this skill. |
| **function-creator** | The conceptual model for this skill's composition. |
