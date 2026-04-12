# Distributed Plan 9 CPU Server Grid Patterns

## Table of Contents

1. [Grid Topologies](#grid-topologies)
2. [9P2000 Networking](#9p2000-networking)
3. [Namespace Composition](#namespace-composition)
4. [Service Distribution](#service-distribution)
5. [Scaling Strategies](#scaling-strategies)

## Grid Topologies

### Star Topology (Default)

An auth/name server coordinates all CPU servers. Simplest to deploy and manage.

```
         ┌──────────┐
    ┌────│  Auth     │────┐
    │    │ (CPU 0)   │    │
    │    └──────────┘    │
    │         │          │
┌───┴──┐ ┌───┴──┐ ┌───┴──┐
│CPU 1 │ │CPU 2 │ │CPU 3 │
└──────┘ └──────┘ └──────┘
```

**When to use:** Small grids (2-10 nodes), development, testing.

**Deploy:**
```bash
plan9-grid start --nodes 4
```

### Mesh Topology

Every node connects to every other node. Maximum redundancy.

```
┌──────┐───┌──────┐
│CPU 0 │   │CPU 1 │
└──┬───┘───└───┬──┘
   │    ╲  ╱   │
   │     ╲╱    │
   │     ╱╲    │
   │    ╱  ╲   │
┌──┴───┐───┌───┴──┐
│CPU 2 │   │CPU 3 │
└──────┘───└──────┘
```

**When to use:** High-availability, fault-tolerant deployments.

**Deploy:**
```sh
# In each node's namespace script:
for peer in $PEER_LIST; do
    9 mount tcp!${peer}!564 /mnt/peers/${peer}
done
```

### Hierarchical Topology

Multi-level tree for large-scale deployments.

```
           ┌──────────┐
           │  Root     │
           │  Auth     │
           └────┬─────┘
        ┌───────┴───────┐
   ┌────┴────┐    ┌────┴────┐
   │Region A │    │Region B │
   └────┬────┘    └────┬────┘
   ┌──┬─┴─┬──┐   ┌──┬─┴─┬──┐
   │C1│C2 │C3│   │C4│C5 │C6│
   └──┘└──┘└──┘   └──┘└──┘└──┘
```

**When to use:** Large grids (10+ nodes), geographic distribution.

## 9P2000 Networking

### Exporting a Namespace

Make local resources available to remote nodes:

```sh
# On a Plan 9 CPU server
bind -a '#I' /net
aux/listen1 -t tcp!*!564 /bin/exportfs -r /
```

### Mounting Remote Resources

Import resources from another node:

```sh
# Mount cpu-1's namespace at /mnt/cpu1
mount /srv/tcp!cpu-1!564 /mnt/cpu1

# Access remote files transparently
ls /mnt/cpu1/proc
cat /mnt/cpu1/dev/sysstat
```

### Authenticated Connections

For production grids, use Plan 9's factotum:

```sh
# On the auth server
auth/keyfs
auth/changeuser glenda

# On CPU servers — factotum handles auth transparently
cpu -h cpu-1
```

## Namespace Composition

Plan 9's per-process namespaces are the key to distributed processing. Each node constructs its own view of the distributed system.

### Standard Namespace Layout

```
/
├── dev/
│   ├── cons                ← Console
│   ├── sysstat             ← CPU stats
│   └── sysname             ← Node identity
├── proc/                   ← Process table
├── srv/                    ← Service registry
├── mnt/
│   ├── cpu-0/              ← Mounted remote namespaces
│   ├── cpu-1/
│   └── cpu-2/
├── net/
│   └── tcp/                ← Network connections
└── tmp/                    ← Temporary files
```

### Composing Distributed Namespaces

```sh
# On each CPU server, mount the auth server's namespace
mount /srv/tcp!plan9-registry!564 /mnt/registry

# Bind remote resources into local namespace
bind /mnt/registry/srv /srv/remote

# Union directories for transparent access
bind -a /mnt/cpu-1/lib /lib
```

## Service Distribution

### Pattern: Partitioned Workload

Distribute work across nodes by domain:

| Node | Partition | Port |
|------|-----------|------|
| cpu-0 | Auth/name server + coordination | 564 |
| cpu-1 | Domain A processing | 565 |
| cpu-2 | Domain B processing | 566 |
| cpu-3 | Domain C processing | 567 |

### Pattern: Replicated Service

Run the same service on multiple nodes for redundancy:

```sh
# Deploy binary to all nodes
plan9-grid deploy /workspace/bin/myservice.out

# Each node runs the service on its local data
# Results are aggregated at the auth server
```

### Pattern: Pipeline Processing

Chain services across nodes:

```
Input → [CPU 1: Parse] → [CPU 2: Transform] → [CPU 3: Output] → Result
```

## Scaling Strategies

### Horizontal Scaling

Add more CPU server nodes:

```bash
# Scale to 10 CPU servers
docker compose -f docker-compose.grid.yml --scale plan9-cpu=10 up -d
```

### Vertical Scaling

Increase resources per node:

```yaml
# In docker-compose.grid.yml
deploy:
  resources:
    limits:
      cpus: "4"
      memory: 8G
```

### Auto-Scaling Triggers

Monitor these metrics for scaling decisions:

| Metric | Scale Up When | Scale Down When |
|--------|--------------|-----------------|
| CPU utilization | >80% sustained | <20% sustained |
| 9P2000 connection count | >50 per node | <5 per node |
| Process count | >200 per node | <10 per node |
| Memory utilization | >80% sustained | <20% sustained |
