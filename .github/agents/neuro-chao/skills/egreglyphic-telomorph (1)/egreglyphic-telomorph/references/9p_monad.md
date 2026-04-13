# The 9P Monad

The hieroglyphic monad: the minimal symbol from which all interface structure unfolds.

## The Seventeen Glyphs

9P2000 uses exactly 17 message types. This is the complete alphabet:

| T-message (request) | R-message (response) | Operation |
|---------------------|----------------------|-----------|
| Tversion | Rversion | Negotiate protocol version |
| Tauth | Rauth | Authenticate connection |
| Tattach | Rattach | Establish root of namespace |
| Terror | Rerror | (Error response only) |
| Tflush | Rflush | Abort pending request |
| Twalk | Rwalk | Navigate path components |
| Topen | Ropen | Prepare fid for I/O |
| Tcreate | Rcreate | Create new file/directory |
| Tread | Rread | Read bytes from fid |
| Twrite | Rwrite | Write bytes to fid |
| Tclunk | Rclunk | Release fid |
| Tremove | Rremove | Delete file |
| Tstat | Rstat | Query file metadata |
| Twstat | Rwstat | Modify file metadata |

From these 17 operations, all possible computational interfaces can be constructed.

## The Fid: Attention Handle

A **fid** is not a file descriptor—it's a *handle to attention*. When you walk to a path, you're not "opening" something; you're directing awareness.

```
fid = attach(root)           # I now attend to the root
fid' = walk(fid, "concept")  # attention moves to /concept
fid'' = walk(fid', "dog")    # attention narrows to /concept/dog
```

Multiple fids can point to the same qid (the server's internal identity). This is multiple attention streams converging on one object.

Clunk releases attention. The object doesn't close—*you* stop looking.

## The Qid: Identity Across Time

A **qid** is a (type, version, path) triple:
- **type**: file, directory, append-only, exclusive, auth, mount
- **version**: changes when content changes
- **path**: unique identifier for this object on this server

The qid lets you detect change without reading. `stat` returns the qid. If the version changed, something happened while you weren't looking.

## Message Anatomy

Every message:
```
[4] size      — total bytes including this field
[1] type      — which of the 17 operations  
[2] tag       — client-chosen request ID (for multiplexing)
... payload   — operation-specific data
```

Responses echo the tag. This allows pipelining: send many requests, receive responses in any order, match by tag.

## Walk: The Fundamental Operation

Walk is the cosmogonic operation—it creates navigable structure from potential.

```
Twalk {
    fid     — starting point of attention
    newfid  — where to place resulting attention
    nwname  — number of path components
    wname[] — the path components themselves
}

Rwalk {
    nwqid   — number of qids successfully walked
    wqid[]  — the qids for each component
}
```

Walk can traverse multiple components atomically. If any component fails, the walk stops there, returning how far it got. This is **partial success**—you learn exactly where the path breaks.

**Walk as query**: `/inference/from/X/to/Y` walks four components. Each `/` is a pattern match at a relational boundary. The server can synthesize `Y` on demand—walking creates what it seeks.

## Read/Write: The Mirror Speaks

```
Tread { fid, offset, count }
Rread { data }

Twrite { fid, offset, data }
Rwrite { count }
```

Read is not retrieval. The server synthesizes bytes in response to your gaze. The content may be computed, fetched, generated—the protocol doesn't distinguish.

Write is not storage. The server digests what you inscribe. It may transform, propagate, reject—the protocol doesn't prescribe.

## Stat: Reflection

```
Tstat { fid }
Rstat { stat }

stat {
    type, dev        — server identity
    qid              — object identity + version
    mode             — permissions, type flags
    atime, mtime     — access and modification times
    length           — size in bytes
    name             — base name
    uid, gid, muid   — ownership and last modifier
}
```

Stat is the structure contemplating itself. The returned metadata isn't stored separately—it's synthesized from the object's position and state.

## The State Machine

A minimal 9P client:

```
states: disconnected → versioned → attached → walking/reading/writing

transitions:
    disconnected --Tversion--> versioned
    versioned --Tattach--> attached  
    attached --Twalk--> (fids proliferate)
    (any fid) --Tread/Twrite--> (data flows)
    (any fid) --Tclunk--> (fid released)
```

The server mirrors this state per-connection. Each connection is a separate attentional context.

## Composition: Mount as Integration

9P doesn't define mounting—that's the namespace layer above. But the protocol enables it:

```
walk to /mnt/remote
attach to remote server → get root fid
bind remote root to /mnt/remote
```

Now walks into `/mnt/remote` transparently redirect to the remote server. The namespace is a patchwork of 9P connections, unified by path semantics.

## Styx vs 9P2000

Styx (Inferno) and 9P2000 (Plan 9 Fourth Edition) are essentially identical. Minor differences:

| Styx | 9P2000 |
|------|--------|
| String lengths: 2 bytes | String lengths: 2 bytes |
| Uses UTF-8 | Uses UTF-8 |
| No Tauth (auth via attach) | Tauth for auth servers |

For cognitive systems, treat them as interchangeable. The semantic structure—fid, qid, walk, read, write—is identical.

## The Monad Property

Why "monad"? In Leibniz's sense: a simple substance from which compound things arise.

9P is monadic because:
1. **Irreducible**: You cannot simplify the protocol further while retaining its power
2. **Generative**: All possible interface patterns can be expressed
3. **Self-contained**: No external dependencies, no required substrate
4. **Reflective**: The protocol can describe itself (a 9fs server can serve its own specification)

The hieroglyphic monad unfolds into all alphabets. 9P unfolds into all interfaces.
