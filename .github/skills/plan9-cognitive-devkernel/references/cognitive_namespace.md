# Cognitive Namespace Reference — Plan 9

The cognitive namespace maps TC file management operations to Plan 9's native 9P2000 namespace for cognitive kernel services. In Plan 9, every resource is a file server — this makes the cognitive namespace a first-class citizen of the operating system.

## Transform Mapping: tc → Plan 9 Cognitive 9P2000

| TC Concept | Plan 9 Cognitive Equivalent | Plan 9 Command |
|-----------|---------------------------|----------------|
| File system tree | `/cognitive/` namespace hierarchy | `ls -lR /cognitive/` |
| Directory | Cognitive service group | `mkdir /cognitive/newservice` |
| File | Individual atom, rule, or config | `echo data > /cognitive/atomspace/atoms/cat` |
| File properties | Atom metadata (type, STI, LTI, TV) | `stat /cognitive/atomspace/atoms/cat` |
| Search (wildcard) | Pattern matching across namespaces | `grep -r pattern /cognitive/` |
| Copy | Atom replication to remote CPU | `cp /cognitive/src /mnt/cpu2/cognitive/dst` |
| Move | Atom migration between partitions | `mv /cognitive/src /cognitive/dst` |
| Archive pack | Namespace snapshot via fossil | `fossil/flchk -v /dev/sdC0/fossil` |
| Archive unpack | Namespace restore from venti | `fossil/conf -w /dev/sdC0/fossil < snap.conf` |
| Batch rename | Bulk atom type conversion | `for(f in /cognitive/atomspace/atoms/*) mv $f $f.new` |
| Union mount | Multi-source knowledge integration | `bind -a /mnt/cpu2/cognitive /cognitive` |

## Namespace Hierarchy

```
/cognitive/
├── atomspace/
│   ├── atoms/          # ConceptNode, PredicateNode, LinkType instances
│   ├── types/          # Type hierarchy (inherits-from relations)
│   └── indices/        # Hash indices, type indices for fast lookup
├── inference/
│   ├── rules/          # PLN rules (ModusPonens, DeductionRule, etc.)
│   ├── queue/          # Pending inference tasks
│   └── results/        # Cached inference results with truth values
├── attention/
│   ├── bank/           # STI/LTI values per atom
│   └── agents/         # HebbianUpdating, ImportanceSpreading agents
├── learning/
│   ├── populations/    # MOSES candidate program populations
│   └── fitness/        # Fitness function configurations
├── temporal/
│   ├── levels/         # 9 time crystal hierarchy level configs
│   └── phases/         # Current phase state per level
└── autognosis/
    ├── images/         # Hierarchical self-images (Level 0, 1, 2+)
    ├── insights/       # Meta-cognitive insight records
    └── metrics/        # Self-monitoring metric time series
```

## 9P2000 Protocol Operations

Each namespace path is served by a 9P2000 file server. Plan 9's native file operations map directly to cognitive operations:

| Plan 9 Operation | 9P2000 Message | Cognitive Meaning |
|-----------------|----------------|-------------------|
| `open` | Topen | Acquire handle to cognitive resource |
| `read` | Tread | Query atom value, rule definition, or metric |
| `write` | Twrite | Update atom truth value, submit inference task |
| `create` | Tcreate | Create new atom, rule, or agent |
| `remove` | Tremove | Delete atom or deactivate agent |
| `stat` | Tstat | Get atom metadata (type, STI, LTI, creation time) |
| `walk` | Twalk | Navigate namespace hierarchy |
| `clunk` | Tclunk | Release handle to cognitive resource |

## Plan 9 Namespace Composition

Plan 9's namespace primitives enable powerful cognitive architecture patterns:

### bind — Local namespace composition

```sh
# Overlay remote atomspace into local cognitive namespace
bind -a /mnt/cpu2/cognitive/atomspace /cognitive/atomspace

# Before-bind for priority (local atoms take precedence)
bind -b /cognitive/atomspace/local /cognitive/atomspace

# Replace-bind for exclusive access
bind /mnt/cpu1/cognitive/inference /cognitive/inference
```

### mount — Remote 9P2000 file server

```sh
# Mount a remote cognitive service
mount /srv/cogfs /cognitive

# Mount with authentication via factotum
mount -a /srv/cogfs /cognitive

# Mount specific CPU server's namespace
import cpu1 /cognitive /mnt/cpu1/cognitive
```

### union directories — Multi-source knowledge

```sh
# Create union of all CPU servers' atomspaces
for(cpu in cpu1 cpu2 cpu3) {
    import $cpu /cognitive/atomspace /mnt/$cpu/atomspace
    bind -a /mnt/$cpu/atomspace /cognitive/atomspace
}
# Now /cognitive/atomspace shows atoms from ALL servers
```

## Temporal Binding

Each namespace path is bound to a temporal level from the time-crystal-nn hierarchy:

| Namespace | Temporal Level | Update Period | Plan 9 Mechanism |
|-----------|---------------|---------------|------------------|
| `/cognitive/atomspace/` | L0-L1 | 8-26ms | /srv file read/write |
| `/cognitive/inference/` | L2 | 52ms | Dedicated file server |
| `/cognitive/attention/` | L3 | 110ms | Agent processes |
| `/cognitive/learning/` | L4 | 160ms | Batch population updates |
| `/cognitive/temporal/` | L5-L6 | 250-330ms | mount/bind sync |
| `/cognitive/autognosis/` | L7-L8 | 500-1000ms | /proc introspection |

## Plan 9 /proc as Autognosis Substrate

Plan 9's /proc filesystem exposes process state as files:

```
/proc/<pid>/
├── ctl        # Process control (write "stop", "start", "kill")
├── status     # Process status line
├── note       # Send notes (signals) to process
├── mem        # Process memory
├── text       # Executable text
├── fd         # Open file descriptors
└── ns         # Process namespace (list of mounts and binds)
```

The Autognosis engine reads `/proc/*/ns` to understand the cognitive namespace composition of each process, and `/proc/*/status` to monitor cognitive service health. This is the Plan 9 analogue of Inferno's channel-based observation.

## CLI Operations

```bash
# Display cognitive namespace tree
python cognitive_plan9kernel.py transform

# Validate all namespace paths are configured
python cognitive_plan9kernel.py validate .

# Show kernel self-image (includes namespace status)
python cognitive_plan9kernel.py status
```
