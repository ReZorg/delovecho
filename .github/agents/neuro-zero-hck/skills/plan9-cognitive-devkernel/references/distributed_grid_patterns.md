# Distributed Plan 9 CPU Server Grid Patterns

## Table of Contents

1. Grid Topologies
2. 9P2000 Networking
3. Namespace Composition
4. Cognitive Service Distribution
5. Scaling Strategies

## Grid Topologies

### Star Topology (Default)

An auth/name server coordinates all CPU servers. Simplest to deploy.

```
           +------------+
      +----| Auth/Name  |----+
      |    | (cpu0)     |    |
      |    +------------+    |
      |         |            |
  +---+--+ +---+--+  +---+--+
  |cpu1  | |cpu2  |  |cpu3  |
  +------+ +------+  +------+
```

**When to use:** Small grids (2-10 CPU servers), development, testing.

**Deploy:**
```bash
plan9-grid start --nodes 4
```

### Mesh Topology

Every CPU server connects to every other. Maximum redundancy.

```
+------+---+------+
|cpu0  |   |cpu1  |
+--+---+---+---+--+
   |    \ /    |
   |     X     |
   |    / \    |
+--+---+---+---+--+
|cpu2  |   |cpu3  |
+------+---+------+
```

**When to use:** High-availability, fault-tolerant deployments.

**Deploy:**
```sh
# On each CPU server, import all peers:
for(peer in $PEER_LIST) {
    import $peer / /mnt/peers/$peer
}
```

### Hierarchical Topology

Multi-level tree for large-scale deployments.

```
           +----------+
           |  Root    |
           | Auth/NS  |
           +----+-----+
        +-------+-------+
   +----+----+    +----+----+
   |Region A |    |Region B |
   +----+----+    +----+----+
   +--+-+-+--+   +--+-+-+--+
   |C1|C2|C3|   |C4|C5|C6|
   +--+--+--+   +--+--+--+
```

**When to use:** Large grids (10+ CPU servers), geographic distribution.

## 9P2000 Networking

### Exporting a Namespace

Make local resources available to remote CPU servers:

```sh
# Inside Plan 9 rc shell
bind '#I' /net
aux/listen1 -t tcp!*!564 /bin/exportfs -r /
```

### Importing Remote Resources

Import resources from another CPU server:

```sh
# Import cpu1's namespace at /mnt/cpu1
import cpu1 / /mnt/cpu1

# Access remote files transparently
ls /mnt/cpu1/cognitive/atomspace
cat /mnt/cpu1/cognitive/inference/status
```

### Authenticated Connections (factotum)

Plan 9 uses factotum for all authentication:

```sh
# Configure factotum with credentials
echo 'key proto=p9sk1 dom=plan9cog.local user=glenda !password=secret' > /mnt/factotum/ctl

# Import with authentication (automatic via factotum)
import -a cpu1 /cognitive /mnt/cpu1/cognitive

# CPU command (authenticated remote execution)
cpu cpu1
```

## Namespace Composition

Plan 9's per-process namespace composition is the key to distributed cognitive processing.

### Cognitive Namespace Layout

```
/
├── cognitive/
│   ├── atomspace/          <- Local AtomSpace partition
│   │   ├── atoms/          <- Atom storage
│   │   ├── types/          <- Type hierarchy
│   │   └── indices/        <- Lookup indices
│   ├── inference/          <- PLN inference engine
│   │   ├── rules/          <- Inference rules
│   │   ├── queue/          <- Inference task queue
│   │   └── results/        <- Inference results
│   ├── attention/          <- ECAN attention allocation
│   │   ├── bank/           <- Attention bank
│   │   └── agents/         <- Attention agents
│   └── learning/           <- MOSES learning
│       ├── populations/    <- Current populations
│       └── fitness/        <- Fitness evaluators
├── mnt/
│   ├── cpu0/               <- Imported remote namespaces
│   ├── cpu1/
│   └── cpu2/
├── srv/
│   ├── cogfs              <- Cognitive file server
│   ├── fossil             <- Fossil file system
│   └── factotum           <- Authentication agent
├── proc/                   <- Process introspection (autognosis)
└── net/
    └── tcp/                <- Network connections
```

### Composing Distributed AtomSpace

```sh
# On each CPU server, import the auth server's AtomSpace
import cpu0 /cognitive/atomspace /mnt/auth/atomspace

# Bind remote atoms into local namespace (union)
bind -a /mnt/auth/atomspace/atoms /cognitive/atomspace/atoms

# Now local queries transparently access remote atoms
```

## Cognitive Service Distribution

### Pattern: Partitioned AtomSpace

Distribute atoms across CPU servers by domain:

| CPU Server | Partition | 9P2000 Port |
|-----------|-----------|-------------|
| cpu0 | Auth/Name + General knowledge | 564 |
| cpu1 | Domain A (perception) | 565 |
| cpu2 | Domain B (language) | 566 |
| cpu3 | Domain C (reasoning) | 567 |

### Pattern: Replicated Inference

Run the same inference rules on multiple CPU servers:

```sh
# Deploy inference rules to all CPU servers
plan9-grid deploy /bin/inference_rules

# Each server runs inference on its local partition
# Results are aggregated at the auth server
```

### Pattern: Pipeline Processing

Chain cognitive services across CPU servers:

```
Input -> [cpu1: Perception] -> [cpu2: Language] -> [cpu3: Reasoning] -> Output
```

Each stage imports the previous stage's output namespace:

```sh
# On cpu2 (Language):
import cpu1 /cognitive/inference/results /mnt/perception/results
bind /mnt/perception/results /cognitive/language/input
```

## Scaling Strategies

### Horizontal Scaling

Add more CPU servers to the grid:

```bash
# Scale to 10 CPU servers
plan9-grid start --nodes 10
```

### Vertical Scaling

Increase resources per QEMU VM:

```yaml
# In grid-compose.yml
deploy:
  resources:
    limits:
      cpus: "4"
      memory: 8G
```

### Auto-Scaling Triggers

| Metric | Scale Up When | Scale Down When |
|--------|--------------|-----------------|
| AtomSpace size | >80% capacity | <20% capacity |
| Inference queue depth | >100 pending | <10 pending |
| CPU utilization | >80% sustained | <20% sustained |
| 9P2000 connection count | >50 per server | <5 per server |
