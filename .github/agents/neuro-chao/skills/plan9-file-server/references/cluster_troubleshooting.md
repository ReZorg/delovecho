# Cluster Troubleshooting Reference

## Diagnostic Commands

```sh
# Network
ip/ping <host>                    # Test connectivity
ndb/query sys <hostname>          # Look up host in ndb
netstat -n | grep <port>          # Check listening ports

# File server console
con -l /srv/fscons                # Connect to FS console
>>> fsys main sync                # Sync filesystem
>>> fsys main snap                # Take snapshot
>>> fsys main halt                # Halt filesystem (maintenance)

# Authentication
auth/debug tcp!<host>!567         # Debug auth handshake
cat /mnt/factotum/ctl             # List factotum keys

# CPU operations
cpu -h <host>                     # Remote login
cpu -h <host> echo $sysname       # Test remote exec

# Mounting
srv tcp!<host>!564 <name>         # Create /srv/<name>
mount /srv/<name> /mnt/<point>    # Mount service
ls /mnt/<point>                   # Verify mount
```

## Common Issues

### 1. Auth Server Won't Start

**Symptom:** `auth/keyfs` fails or CPU servers can't authenticate.

**Causes and fixes:**

```sh
# Missing auth service link
ls /rc/bin/service.auth/tcp567
# If missing:
mv /rc/bin/service.auth/authsrv.tcp567 /rc/bin/service.auth/tcp567

# Key database not initialized
auth/keyfs
# If fails, initialize:
echo 'key proto=p9sk1 dom=DOMAIN user=bootes !password=SECRET' \
    > /mnt/factotum/ctl

# Listener not running
aux/listen -q -t /rc/bin/service.auth -d /rc/bin/service tcp
```

### 2. CPU Server Can't Mount File Server

**Symptom:** `srv tcp!fs.domain!564 fscons` hangs or fails.

**Checklist:**

```sh
# 1. Verify network
ip/ping fs.domain

# 2. Check file server is exporting
# On file server:
netstat -n | grep 564

# 3. Check auth domain matches
# On CPU server:
cat /lib/ndb/local | grep authdom
# Must match file server's authdom

# 4. Check factotum has correct key
cat /mnt/factotum/ctl
# Should show: key proto=p9sk1 dom=DOMAIN user=...
```

### 3. Cognitive Namespace Not Visible

**Symptom:** `/cognitive/` empty or not mounted on CPU server.

```sh
# 1. Check file server is exporting cognitive namespace
# On file server:
netstat -n | grep 5640

# 2. Check cognitive export script ran
ls /cognitive/atomspace

# 3. Manual mount from CPU server
srv tcp!fs.domain!5640 cogfs
mount /srv/cogfs /cognitive
ls /cognitive/
```

### 4. Union Mount Shows Partial Data

**Symptom:** `bind -a` doesn't show all remote atoms.

```sh
# Verify each remote mount individually
for(host in cpu1 cpu2 cpu3){
    echo 'Testing '$host'...'
    srv tcp!$host.domain!5641 test-$host
    mount /srv/test-$host /mnt/test-$host
    ls /mnt/test-$host/cognitive/atomspace/atoms | wc -l
    unmount /mnt/test-$host
}

# Check for name conflicts (same atom name on multiple servers)
# Union mount shows first match; use bind -b to change priority
```

### 5. File System Corruption

**Symptom:** Errors reading/writing files, unexpected data.

```sh
# hjfs
disk/kfscmd -n hjfs.cmd check

# cwfs
con -l /srv/fscons
>>> fsys main check

# fossil
fossil/flchk -v /dev/sdC0/fossil

# Recovery: restore from snapshot
con -l /srv/fscons
>>> fsys main snap -a    # List snapshots
# Boot from snapshot via plan9.ini: bootdisk=sdC0/fossil@YYYYMMDD
```

### 6. Docker Compose Issues

**Symptom:** Containers fail to start or can't reach each other.

```sh
# Check container status
docker compose -f docker-compose.fileserver.yml ps

# Check network
docker network inspect plan9-net

# Check file server health
docker compose -f docker-compose.fileserver.yml logs plan9-fileserver

# Restart with fresh state
docker compose -f docker-compose.fileserver.yml down -v
docker compose -f docker-compose.fileserver.yml up -d
```

### 7. Performance Issues

**Symptom:** Slow 9P2000 operations, high latency.

```sh
# Check network latency
ip/ping -n 100 fs.domain

# Check file server load
# On file server:
cat /dev/sysstat

# Reduce 9P message size for high-latency links
mount -M 8192 /srv/cogfs /cognitive

# Use local caching
bind -bc /tmp/cognitive-cache /cognitive
```
