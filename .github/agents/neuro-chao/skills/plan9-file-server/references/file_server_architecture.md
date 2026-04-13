# File Server Architecture Reference

## Cluster Topology

```
┌─────────────────┐     ┌──────────────────┐
│  File Server    │     │   Auth Server    │
│  (Storage)      │────▶│   (faktotum)     │
│  cwfs/hjfs      │     │   Certificates   │
└────────┬────────┘     └──────────────────┘
         │                        ▲
         │        Network         │
         └────────────┬───────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼──────┐          ┌─────────▼──────┐
│ CPU Server 1 │          │ CPU Server N   │
│ (Compute)    │   ...    │ (Compute)      │
│ + Cognitive  │          │ + Cognitive    │
└──────────────┘          └────────────────┘
```

The file server is the cluster's storage and authentication hub. CPU servers mount the file server's namespace and export their own cognitive services back.

## File System Choices

| FS | Era | Strengths | Use When |
|----|-----|-----------|----------|
| **hjfs** | 9front (modern) | Simple, reliable, single-disk | Development, small clusters |
| **cwfs** | Classic Plan 9 | WORM-based, archival | Production, data integrity |
| **fossil+venti** | Classic Plan 9 | Snapshots, dedup, archival | Large-scale, backup-critical |

### hjfs Setup (9front, recommended for dev)

```sh
disk/fdisk /dev/sdC0/data
disk/prep /dev/sdC0/plan9
hjfs -f /dev/sdC0/fs -m 512 -S
```

### cwfs Setup (classic)

```sh
disk/fdisk /dev/sdC0/data
disk/prep /dev/sdC0/plan9
cwfs64x -f /dev/sdC0/fscache -c /dev/sdC0/fsworm
```

## Authentication Architecture

Plan 9 uses factotum for all authentication. The file server runs auth services:

1. **keyfs** — Key storage daemon
2. **factotum** — Per-process authentication agent
3. **authsrv** — Network authentication service (tcp567)

### Auth Setup Sequence

```sh
# 1. Enable auth services
mv /rc/bin/service.auth/authsrv.tcp567 /rc/bin/service.auth/tcp567

# 2. Start auth listener
aux/listen -q -t /rc/bin/service.auth -d /rc/bin/service tcp

# 3. Configure factotum credentials
echo 'key proto=p9sk1 dom=DOMAIN user=bootes !password=SECRET' \
    > /mnt/factotum/ctl
```

### User Management

```sh
# On file server console (con -l /srv/fscons)
uname bootes :bootes      # Create auth admin
uname glenda :glenda      # Create regular user
uname glenda +sys         # Add to sys group
uname glenda +adm         # Add to adm group
fsys main sync            # Sync changes
```

## Network Database (/lib/ndb/local)

The network database defines all cluster nodes. Each entry specifies:

| Field | Purpose |
|-------|---------|
| `sys` | System name (hostname) |
| `dom` | Fully qualified domain name |
| `ip` | IP address |
| `ether` | MAC address |
| `auth` | Auth server FQDN |
| `authdom` | Authentication domain |
| `fs` | File server FQDN (CPU servers only) |
| `cpu` | CPU server FQDN (CPU servers only) |

## Port Assignments

| Port | Service | Direction |
|------|---------|-----------|
| 564 | 9P2000 (exportfs) | File server → clients |
| 567 | authsrv | File server → clients |
| 17010 | cpu (remote exec) | Bidirectional |
| 17013 | exportfs (remote) | Bidirectional |
| 5640 | Cognitive namespace | File server → CPU servers |
| 5641 | Cognitive results | CPU servers → file server |

## Kernel Compilation

Build the CPU kernel for file server mode:

```sh
cd /sys/src/9/pc
mk 'CONF=pccpuf'
9fat:
cp 9pccpuf /n/9fat/
```

Edit `/n/9fat/plan9.ini`:

```
bootfile=9pccpuf
service=cpu
auth=fs.DOMAIN
authdom=DOMAIN
```

## CPU Server Boot Sequence

1. Boot from local 9fat partition
2. Load CPU kernel (9pccpuf)
3. Run `/cfg/$sysname/cpurc`
4. Configure network via ipconfig
5. Mount file server via `srv tcp!fs!564`
6. Bind file server root: `bind -ac /n/fs /`
7. Start CPU services (listen on 17010, 17013)
8. Mount cognitive namespace (if enabled)

## Cognitive Namespace Integration

The file server exports `/cognitive/` via 9P2000 on port 5640. CPU servers mount this and overlay their local cognitive services:

```sh
# On CPU server:
srv tcp!fs.domain!5640 cogfs
mount /srv/cogfs /cognitive

# Local cognitive services overlay:
bind -b /local/cognitive/inference /cognitive/inference
```

This creates a layered namespace where local results take precedence (bind -b) over the shared file server state.

## Troubleshooting

### Auth Failures

```sh
auth/debug tcp!fs.domain!567    # Debug auth protocol
con -l /srv/fscons               # Check FS console
>>> uname username password NEW  # Reset password
```

### Mount Failures

```sh
ip/ping fs.domain               # Check connectivity
netstat -n | grep 564            # Check port listening
auth/keyfs -wp                   # Check key permissions
```

### File System Issues

```sh
disk/kfscmd check               # Check disk integrity
con -l /srv/fscons
>>> fsys main sync               # Force sync
>>> fsys main snap               # Take snapshot
>>> fsys main halt               # Halt for maintenance
```
