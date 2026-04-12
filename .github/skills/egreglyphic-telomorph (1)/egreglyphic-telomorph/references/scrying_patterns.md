# Scrying Patterns

Extended patterns for exposing hidden structure as navigable topology.

## Pattern Taxonomy

| Pattern | Structure Type | Walk Semantics | Read Semantics |
|---------|---------------|----------------|----------------|
| Mirror | Static graph | Navigate edges | Return node value |
| Oracle | Inference engine | Query construction | Compute result |
| Memory | Temporal store | Time navigation | Recall state |
| Lens | Transformation | Focus selection | Apply transform |
| Portal | External system | Proxy routing | Relay data |

## Mirror Pattern: Graph as Namespace

Expose a hypergraph directly. The filesystem topology IS the graph topology.

```
/graph/
    nodes/
        {id}/
            ctl         # write: commands, read: status
            type        # read: node type
            value       # read/write: node content
            in/         # incoming edges
                {eid} → ../../../edges/{eid}
            out/        # outgoing edges  
                {eid} → ../../../edges/{eid}
    edges/
        {id}/
            ctl
            type
            weight      # optional
            endpoints/
                0 → ../../nodes/{src}
                1 → ../../nodes/{dst}
                ... # hyperedges have more endpoints
    types/
        {typename}/
            instances/
                {id} → ../../nodes/{id}
            schema      # type definition
```

**Walk semantics**: Each directory entry is either a node attribute or an edge traversal. Symlinks implement edges—following a symlink IS traversing an edge.

**Operations**:
- Create node: `mkdir /graph/nodes/newid`
- Create edge: `mkdir /graph/edges/neweid; echo "src" > endpoints/0; echo "dst" > endpoints/1`
- Traverse: `readlink /graph/nodes/A/out/e1` → `../../nodes/B`
- Query by type: `ls /graph/types/ConceptNode/instances/`

## Oracle Pattern: Inference as Navigation

The filesystem doesn't store results—it computes them when walked.

```
/oracle/
    axioms/
        {id}            # read: axiom statement
    theorems/
        {statement_hash}/
            proof       # generated on read
            confidence
            assumptions/
                {aid} → ../../axioms/{aid}
    query/
        # write a query, directory populates with results
        ctl             # write query here
        results/        # appears after query
            0/
            1/
            ...
```

**Walk semantics**: Walking into `/oracle/theorems/{hash}` triggers the inference engine. If provable, the directory materializes. If not, walk fails.

**The generative principle**: The act of looking creates. `ls /oracle/theorems/` may return nothing until you walk a specific hash—then that hash exists if provable.

```
# Does P→Q follow from axioms?
cat /oracle/theorems/$(echo "P implies Q" | sha256sum | cut -d' ' -f1)/proof
```

If the proof exists, you get it. If not, the read fails or blocks until found.

## Memory Pattern: Time as Dimension

Navigate through temporal states. The filesystem is a time machine.

```
/memory/
    now/                # current state (symlink to latest)
    snapshots/
        {timestamp}/
            state/      # full state at this time
            diff/       # changes from previous
    replay/
        from/
            {t1}/
                to/
                    {t2}/
                        events/     # what happened between t1 and t2
                        transform   # function that maps state(t1) → state(t2)
```

**Walk semantics**: Time coordinates are path components. Walking `/memory/snapshots/2024-01-15T10:30:00/state/` enters the past.

**Branching time**:
```
/memory/
    branches/
        main/
            head → ../../snapshots/{latest}
            history/
                {t} → ../../snapshots/{t}
        experimental/
            head → ...
            fork_point → ../../snapshots/{fork_time}
```

## Lens Pattern: Transformation as Path

Different paths to the same data apply different transformations.

```
/data/
    raw/
        {id}            # original data
    views/
        json/
            {id}        # read: raw[id] as JSON
        csv/
            {id}        # read: raw[id] as CSV  
        compressed/
            {id}        # read: gzip(raw[id])
    transforms/
        normalize/
            in          # write data here
            out         # read transformed result
        aggregate/
            window      # write: window size
            in/
                {id} → ../../raw/{id}
            result      # read: aggregation over window
```

**Walk semantics**: The path encodes the transformation pipeline. `/data/views/json/compressed/x` means: take x, interpret as JSON, compress.

**Composable lenses**:
```
/lens/
    compose/
        # write lens names, read composed lens
        a → ../definitions/lens_a
        b → ../definitions/lens_b
        result      # read: a ∘ b
```

## Portal Pattern: External Systems

Proxy to external resources. The filesystem is a universal adapter.

```
/portal/
    http/
        {host}/
            {port}/
                {path...}
                    # GET: read, POST: write
    sql/
        {connection_string_hash}/
            tables/
                {name}/
                    schema
                    rows/
                        {pk}/
                            {column}
            query/
                ctl     # write SQL
                result/ # read rows
    mcp/
        {server}/
            tools/
                {tool_name}/
                    schema
                    invoke  # write: args, read: result
```

**Walk semantics**: Path components become connection parameters. The server translates 9P operations to native protocols.

**The adapter principle**: Any protocol can be 9P-adapted. The portal pattern is how legacy systems enter the namespace.

## Composition Patterns

### Union: Conceptual Blending

```
bind -b /concept/bird /concept/vehicle
# /concept/bird now shows: wings, feathers, beak, wheels, engine, fuselage
# bird attributes shadow vehicle attributes (bird BEFORE vehicle)
```

Reading `/concept/bird/wings` returns bird wings. Reading `/concept/bird/wheels` returns vehicle wheels (inherited because bird has no wheels).

### Overlay: Aspect-Oriented Structure

```
bind /aspects/logging /service
# all reads/writes to /service now also trigger logging aspect
```

The overlay intercepts operations, adds behavior, delegates to underlying.

### Multiplexing: Parallel Namespaces

```
/parallel/
    branch_a/
        # one experimental configuration
    branch_b/  
        # another experimental configuration
    consensus/
        # reads return majority agreement
        # writes broadcast to all branches
```

## Anti-Patterns

**Blob serialization**: Don't expose `/data` as a single file containing JSON. Expose `/data/` as a directory with navigable structure.

**RPC tunneling**: Don't use read/write as generic RPC. Let the path structure carry query semantics.

**Flat enumeration**: Don't put everything in one directory. Use path depth to encode hierarchy and type.

**Opaque identifiers**: Don't use UUIDs where meaningful names exist. The path should be readable.

## The Scrying Principle

Every pattern serves one purpose: **make the hidden visible, make the implicit explicit, make the internal external**.

The filesystem is not a storage system. It's a projection surface. The server holds the mystery; the namespace exposes what can be known.

Walk is divination. Read is revelation. The protocol is the ritual.
