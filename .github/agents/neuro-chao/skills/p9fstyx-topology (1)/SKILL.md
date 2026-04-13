---
name: p9fstyx-topology
description: Model and analyze the Marduk ML SDK cognitive architecture (mad9ml + p9fstyx + OpenCog) as a topological assembly using RTSA. Composes runtime-topological-self-assembly with orgitcog/p9fstyx to map P9Fstyx modules, OpenCog AtomSpace, and Marduk cognitive subsystems to simplicial complexes with Betti number constraints. Use for validating wrangler.jsonc binding topology, detecting orphaned cognitive modules, verifying redundant processing paths, planning reconfiguration of the Cloudflare Worker cognitive mesh, or analyzing the structural health of the marduk-ml-sdk deployment.
---

# P9Fstyx Topology

Composition: `runtime-topological-self-assembly( orgitcog/p9fstyx )`

Models the Marduk ML SDK Cloudflare Worker as a self-assembling topological mesh where each cognitive module (P9Fstyx, OpenCog, Marduk) is a component with typed ports, and their bindings form a simplicial complex monitored by Betti numbers.

## Prerequisites

```bash
sudo pip3 install numpy scipy networkx matplotlib -q
```

## Quick Start

Validate the current assembly topology:

```bash
python3 /home/ubuntu/skills/p9fstyx-topology/scripts/analyze_marduk_topology.py
```

Outputs: topological analysis report, dashboard PNG, analysis JSON.

## Architecture

14 components across 5 layers, verified via live cogops test worker:

| Layer | Components | KV Binding |
|---|---|---|
| **core** | atomspace, pattern_matcher, ecan_attention, marduk_memory | ATOMSPACE_KV, MARDUK_KV |
| **infra** | styx_server | P9FSTYX_STATE |
| **compute** | micro_kernel_network, wave_field, gauge_kernel, differential_engine | (via P9FSTYX_STATE) |
| **orchestration** | powerscribe, lambda_promises | (via P9FSTYX_STATE) |
| **optimization** | grip_optimizer, powerskill, moses_evolution | TASK_METRICS |

Verified invariants: **beta_0 = 1** (connected), **beta_1 = 5** (5 independent cycles), **3 triangles**, **chi = -4**.

## Core Workflow

1. **Load assembly** from `templates/marduk_p9fstyx_assembly.json`
2. **Compute invariants**: beta_0, beta_1, persistence pairs via RTSA engine
3. **Check constraints**: beta_0 == 1, beta_1 >= 3
4. **Visualize**: Dashboard PNG with topology graph + persistence diagram
5. **Reconfigure**: Add/remove modules with dry-run validation

## Reconfiguration

Add a new cognitive module safely:

```python
import sys, json
sys.path.insert(0, '/home/ubuntu/skills/runtime-topological-self-assembly/scripts')
from rtsa import Assembly

with open('/home/ubuntu/skills/p9fstyx-topology/templates/marduk_p9fstyx_assembly.json') as f:
    assembly = Assembly.from_dict(json.load(f))

plan = [
    {"action": "register", "cid": "new_module", "ports": [
        {"name": "in", "kind": "SINK", "dtype": "atom"}
    ]},
    {"action": "bind", "cids": ["atomspace", "new_module"]}
]

result = assembly.reconfigure(plan, dry_run=True)
if result["success"]:
    assembly.reconfigure(plan)
```

## Live Verification

CogOps test worker at `https://marduk-cogops-test.dan-cdc.workers.dev`:

- `POST /cogops/run-all` — Full 8-phase cognitive cycle (~7.6s)
- `GET /cogops/topology` — Binding connectivity + beta_0 check
- `GET /cogops/{memory,atomspace,p9fstyx,ecan,wave,gauge,metrics}` — Individual subsystem tests
- `GET /cogops/status` — Health check with last cycle summary

For detailed test results, read `references/cogops_verification.md`.

## Bundled Resources

| Path | Purpose | When to Read |
|---|---|---|
| `scripts/analyze_marduk_topology.py` | Full analysis: load, compute, visualize | Run to validate topology |
| `templates/marduk_p9fstyx_assembly.json` | Assembly config (14 components, 20 edges, 3 triangles) | Input for analysis or reconfiguration |
| `references/p9fstyx_architecture.md` | Module-to-component mapping, KV binding table, env var mapping, cogops endpoints | When mapping wrangler.jsonc bindings to topology |
| `references/cogops_verification.md` | Live test results from deployed cogops worker | When verifying deployment health |

## Wrangler.jsonc Integration

The assembly config maps 1:1 to `ReZorg/marduk-ml-sdk/wrangler.jsonc` bindings. Each KV namespace corresponds to a component cluster, and each env var maps to component metadata. For the complete mapping table, read `references/p9fstyx_architecture.md`.

When modifying `wrangler.jsonc` bindings, re-run the analyzer to verify the topology remains connected (beta_0 = 1) and fault-tolerant (beta_1 >= 3).
