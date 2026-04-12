# Plan 9 Topology Glyph: Architecture Reference

This document describes the architecture of the 9P glyph extension to the Glyph-Noetic Engine, synthesized from the composition:

> `/glyph-noetic-engine ( /plan9-file-server [ /p9fstyx-topology ] )`

## 1. Composition Semantics

The composition expression has a precise meaning. The outer function, `/glyph-noetic-engine`, is the host architecture that provides the glyph language and daemon infrastructure. The inner argument, `/plan9-file-server`, provides the **semantic domain** — the concepts of file servers, CPU servers, namespaces, and the 9P2000 protocol. The sidecar, `/p9fstyx-topology`, provides the **analytical lens** — the ability to model the cluster as a topological assembly and measure its structural health using Betti numbers and persistence diagrams from the `runtime-topological-self-assembly` (RTSA) framework.

The result is a set of glyphs that allow a user to interact with a Plan 9 cluster's structure and health through the noetic interface, as if it were a first-class cognitive entity within the engine.

## 2. The Plan 9 Cluster as a Topological Assembly

The cluster is modeled as an RTSA `Assembly` object, defined in the `plan9_cluster_assembly.json` template. Each node in the cluster (file server, auth server, CPU server) is a **component** with typed **ports**. The connections between them (9P mounts, auth bindings, cognitive namespace exports) are **simplices**.

| Cluster Node | RTSA Component | Ports | Layer |
| :--- | :--- | :--- | :--- |
| File Server | `fs` | `9p_auth` (BIDI), `9p_storage` (BIDI), `cognitive_export` (SOURCE) | storage |
| Auth Server | `auth` | `auth_service` (SINK) | storage |
| CPU Server 1 | `cpu1` | `9p_mount` (SINK), `cognitive_import` (SINK) | compute |
| CPU Server N | `cpuN` | `9p_mount` (SINK), `cognitive_import` (SINK) | compute |

The topological constraints enforce two structural invariants:

| Constraint | Betti Number | Condition | Meaning |
| :--- | :--- | :--- | :--- |
| `connected_cluster` | β₀ | `== 1` | All nodes form a single connected mesh. No orphaned servers. |
| `storage_redundancy` | β₁ | `>= 1` | At least one independent cycle exists, providing a redundant path for data access. |

## 3. Glyph-to-IDL Mapping

The new glyphs are mapped to IDL commands within the `GlyphNoeticDaemon`. The `Plan9TopologyModule` class handles the execution of these commands by querying the RTSA `Assembly` object.

| Glyph | IDL Command | Description |
| :--- | :--- | :--- |
| `[T:ASSEMBLY]?` | `get_topology_status` | Returns Betti numbers, component count, and constraint satisfaction status. |
| `[T:BETA0]?` | `get_topology_status` | Returns the same, with β₀ highlighted. |
| `[T:BETA1]?` | `get_topology_status` | Returns the same, with β₁ highlighted. |
| `[P:FS]?` | `list_p9_components` | Lists all components and their metadata. |
| `[P:CPU]?` | `list_p9_components` | Lists all components and their metadata. |

## 4. Cognitive Namespace Mapping

The Plan 9 file server's `/cognitive/` namespace tree maps directly to the engine's internal structure. This creates a powerful correspondence where the file system *is* the cognitive architecture.

| Namespace Path | Engine Component | Glyph |
| :--- | :--- | :--- |
| `/cognitive/atomspace/` | AtomSpace | `[S:ATOMSPACE]` |
| `/cognitive/inference/` | PLN Module | `[C:PLN]` |
| `/cognitive/attention/` | ECAN Module | `[C:ATTN]` |
| `/cognitive/temporal/` | Time Crystal Hierarchy | `[T-HIERARCHY]` |
| `/cognitive/autognosis/` | Self-Image | `[N:DECISION]` |

This mapping means that a 9P `read` on `/cognitive/temporal/levels/9` is semantically equivalent to the glyph query `[T~g]?`. The file server becomes the persistent, distributed backing store for the entire noetic engine.

## 5. Standalone Analysis

The `analyze_plan9_topology.py` script can be run independently to validate the cluster's topological health:

```bash
python3 /home/ubuntu/skills/glyph-noetic-engine/scripts/analyze_plan9_topology.py
```

This will load the assembly from `templates/plan9_cluster_assembly.json`, compute Betti numbers, check constraints, and generate a visual dashboard PNG.
