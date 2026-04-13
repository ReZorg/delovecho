# Distributed Inferno VM Cluster Patterns

## Table of Contents

1. [Cluster Topologies](#cluster-topologies)
2. [9P/Styx Networking](#9pstyx-networking)
3. [Namespace Composition](#namespace-composition)
4. [Cognitive Service Distribution](#cognitive-service-distribution)
5. [Scaling Strategies](#scaling-strategies)

## Cluster Topologies

### Star Topology (Default)

A registry node coordinates all worker nodes. Simplest to deploy and manage.

```
         ┌──────────┐
    ┌────│ Registry  │────┐
    │    │ (Node 0)  │    │
    │    └──────────┘    │
    │         │          │
┌───┴──┐ ┌───┴──┐ ┌───┴──┐
│Node 1│ │Node 2│ │Node 3│
└──────┘ └──────┘ └──────┘
```

**When to use:** Small clusters (2-10 nodes), development, testing.

**Deploy:**
```bash
inferno-cluster start --nodes 4
```

### Mesh Topology

Every node connects to every other node. Maximum redundancy.

```
┌──────┐───┌──────┐
│Node 0│   │Node 1│
└──┬───┘───└───┬──┘
   │    ╲  ╱   │
   │     ╲╱    │
   │     ╱╲    │
   │    ╱  ╲   │
┌──┴───┐───┌───┴──┐
│Node 2│   │Node 3│
└──────┘───└──────┘
```

**When to use:** High-availability, fault-tolerant deployments.

**Deploy:**
```bash
# In each node's startup script:
for peer in $PEER_LIST; do
    mount tcp!${peer}!6666 /mnt/peers/${peer}
done
```

### Hierarchical Topology

Multi-level tree for large-scale deployments.

```
           ┌──────────┐
           │  Root     │
           │ Registry  │
           └────┬─────┘
        ┌───────┴───────┐
   ┌────┴────┐    ┌────┴────┐
   │Region A │    │Region B │
   └────┬────┘    └────┬────┘
   ┌──┬─┴─┬──┐   ┌──┬─┴─┬──┐
   │W1│W2 │W3│   │W4│W5 │W6│
   └──┘└──┘└──┘   └──┘└──┘└──┘
```

**When to use:** Large clusters (10+ nodes), geographic distribution.

## 9P/Styx Networking

### Exporting a Namespace

Make local resources available to remote nodes:

```sh
# Inside Inferno shell
bind '#I' /net
listen -A tcp!*!6666 { export / & }
```

### Mounting Remote Resources

Import resources from another node:

```sh
# Mount node-1's namespace at /mnt/node1
mount tcp!node-1!6667 /mnt/node1

# Access remote files transparently
ls /mnt/node1/cognitive/atomspace
cat /mnt/node1/cognitive/inference/status
```

### Authenticated Connections

For production clusters, use Inferno's authentication:

```sh
# Generate keys
auth/createsignerkey mykey
auth/changelogin inferno

# Listen with authentication
listen tcp!*!6666 { auth/authsrv & export / & }

# Connect with authentication
mount -A tcp!node-1!6666 /mnt/secure
```

## Namespace Composition

Inferno's namespace composition is the key to distributed cognitive processing. Each node constructs its own view of the distributed system.

### Cognitive Namespace Layout

```
/
├── cognitive/
│   ├── atomspace/          ← Local AtomSpace partition
│   │   ├── atoms/          ← Atom storage
│   │   ├── types/          ← Type hierarchy
│   │   └── indices/        ← Lookup indices
│   ├── inference/          ← PLN inference engine
│   │   ├── rules/          ← Inference rules
│   │   ├── queue/          ← Inference task queue
│   │   └── results/        ← Inference results
│   ├── attention/          ← ECAN attention allocation
│   │   ├── bank/           ← Attention bank
│   │   └── agents/         ← Attention agents
│   └── learning/           ← MOSES learning
│       ├── populations/    ← Current populations
│       └── fitness/        ← Fitness evaluators
├── mnt/
│   ├── node-0/             ← Mounted remote namespaces
│   ├── node-1/
│   └── node-2/
└── net/
    └── tcp/                ← Network connections
```

### Composing Distributed AtomSpace

```sh
# On each worker node, mount the registry's AtomSpace
mount tcp!registry!6666 /mnt/registry

# Bind remote atoms into local namespace
bind /mnt/registry/cognitive/atomspace/atoms /cognitive/atomspace/remote

# Now local queries can transparently access remote atoms
```

## Cognitive Service Distribution

### Pattern: Partitioned AtomSpace

Distribute atoms across nodes by domain:

| Node | Partition | Port |
|------|-----------|------|
| node-0 | Registry + General knowledge | 6666 |
| node-1 | Domain A (e.g., perception) | 6667 |
| node-2 | Domain B (e.g., language) | 6668 |
| node-3 | Domain C (e.g., reasoning) | 6669 |

### Pattern: Replicated Inference

Run the same inference rules on multiple nodes for redundancy:

```sh
# Deploy inference rules to all nodes
inferno-cluster deploy /workspace/dis/inference_rules.dis

# Each node runs inference on its local partition
# Results are aggregated at the registry
```

### Pattern: Pipeline Processing

Chain cognitive services across nodes:

```
Input → [Node 1: Perception] → [Node 2: Language] → [Node 3: Reasoning] → Output
```

## Scaling Strategies

### Horizontal Scaling

Add more worker nodes:

```bash
# Scale to 10 worker nodes
docker compose -f docker-compose.cluster.yml --scale inferno-node=10 up -d
```

### Vertical Scaling

Increase resources per node:

```yaml
# In docker-compose.cluster.yml
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
| AtomSpace size | >80% capacity | <20% capacity |
| Inference queue depth | >100 pending | <10 pending |
| CPU utilization | >80% sustained | <20% sustained |
| 9P connection count | >50 per node | <5 per node |
