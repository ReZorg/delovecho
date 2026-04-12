# Cognitive Namespace Binding via File Server

## Overview

The file server acts as the persistent store and coordination point for the cognitive namespace (`/cognitive/`). CPU servers mount this namespace and overlay their local cognitive services, creating a distributed knowledge fabric.

## Binding Patterns

### Pattern 1: Centralized AtomSpace (File Server Authoritative)

All atoms live on the file server. CPU servers read/write via mount.

```sh
# On each CPU server:
srv tcp!fs.domain!5640 cogfs
mount /srv/cogfs /cognitive
# All reads/writes go to file server
```

**Use when:** Small cluster, consistency critical, atoms < 1M.

### Pattern 2: Partitioned AtomSpace (Domain Sharding)

Each CPU server owns a domain partition. File server holds the index.

```sh
# File server exports index:
aux/listen1 -t tcp!*!5640 /bin/exportfs -r /cognitive/atomspace/indices &

# CPU1 owns perception atoms:
aux/listen1 -t tcp!*!5641 /bin/exportfs -r /cognitive/atomspace/atoms/perception &

# CPU2 owns language atoms:
aux/listen1 -t tcp!*!5641 /bin/exportfs -r /cognitive/atomspace/atoms/language &

# Union mount on any node:
srv tcp!cpu1.domain!5641 cpu1-atoms
srv tcp!cpu2.domain!5641 cpu2-atoms
mount /srv/cpu1-atoms /mnt/cpu1/atoms
mount /srv/cpu2-atoms /mnt/cpu2/atoms
bind -a /mnt/cpu1/atoms /cognitive/atomspace/atoms
bind -a /mnt/cpu2/atoms /cognitive/atomspace/atoms
```

**Use when:** Large atom counts, domain-specific processing.

### Pattern 3: Replicated Read, Centralized Write

CPU servers cache read-only copies. Writes go through file server.

```sh
# CPU server mounts file server read-only:
mount -r /srv/cogfs /cognitive

# Local write buffer:
mkdir /tmp/cognitive-writes
bind -b /tmp/cognitive-writes /cognitive/atomspace/atoms

# Periodic sync back to file server:
while(sleep 5){
    for(f in /tmp/cognitive-writes/*){
        cp $f /n/fs/cognitive/atomspace/atoms/
        rm $f
    }
}
```

**Use when:** Read-heavy workloads, eventual consistency acceptable.

### Pattern 4: Pipeline Processing

Chain cognitive services across CPU servers via namespace forwarding.

```
Input → [CPU1: Perception] → [CPU2: Language] → [CPU3: Reasoning] → Output
         exports /results     imports CPU1        imports CPU2
                               exports /results    exports /results
```

```sh
# On CPU2 (Language):
import cpu1 /cognitive/inference/results /mnt/perception/results
bind /mnt/perception/results /cognitive/language/input

# On CPU3 (Reasoning):
import cpu2 /cognitive/inference/results /mnt/language/results
bind /mnt/language/results /cognitive/reasoning/input
```

**Use when:** Sequential processing stages, clear data flow.

## Cognitive Export Script

Run on the file server to initialize and export `/cognitive/`:

```sh
#!/bin/rc
# Create full cognitive namespace
for(dir in atomspace/atoms atomspace/types atomspace/indices \
           inference/rules inference/queue inference/results \
           attention/bank attention/agents \
           learning/populations learning/fitness \
           temporal/levels temporal/phases \
           autognosis/images autognosis/insights autognosis/metrics){
    mkdir -p /cognitive/$dir
}

# Export via 9P2000
aux/listen1 -t tcp!*!5640 /bin/exportfs -r /cognitive &
```

## Union AtomSpace Script

Run from any node to create a unified view of all CPU servers' atoms:

```sh
#!/bin/rc
# Union-mount AtomSpace from all CPU servers
for(host in cpu1.domain cpu2.domain cpu3.domain){
    srv tcp!$host!5641 $host^-cogfs
    mount /srv/$host^-cogfs /mnt/$host/cognitive
    bind -a /mnt/$host/cognitive/atomspace /cognitive/atomspace
}
# /cognitive/atomspace now shows atoms from ALL servers
```

## Temporal Binding via File Server

The file server's `/cognitive/temporal/` directory stores the time crystal hierarchy configuration. CPU servers read this to synchronize their service scheduling:

| Level | File | Content |
|-------|------|---------|
| L0-L1 | `/cognitive/temporal/levels/0`, `/cognitive/temporal/levels/1` | AtomSpace CRUD timing |
| L2 | `/cognitive/temporal/levels/2` | PLN inference period |
| L3 | `/cognitive/temporal/levels/3` | ECAN attention tick |
| L4 | `/cognitive/temporal/levels/4` | MOSES learning batch |
| L5-L6 | `/cognitive/temporal/levels/5`, `/cognitive/temporal/levels/6` | Namespace sync, heartbeat |
| L7-L8 | `/cognitive/temporal/levels/7`, `/cognitive/temporal/levels/8` | Autognosis, self-image |

## Autognosis via File Server

The file server's `/cognitive/autognosis/` directory is the persistent store for self-monitoring data:

- `/cognitive/autognosis/images/` — Hierarchical self-images (JSON files per level)
- `/cognitive/autognosis/insights/` — Meta-cognitive insight records
- `/cognitive/autognosis/metrics/` — Time series of self-monitoring metrics

CPU servers write their local observations here; the autognosis engine on the file server aggregates them into the global self-image.
