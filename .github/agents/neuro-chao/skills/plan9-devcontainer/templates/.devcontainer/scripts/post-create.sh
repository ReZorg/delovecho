#!/bin/bash
# =============================================================================
# Plan 9 Devcontainer — Post-Create Script
# Runs once after the container is created.
# Verifies plan9port + QEMU, creates workspace, configures grid, installs CLIs.
# =============================================================================

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Plan 9 Devcontainer — Post-Create Setup                ║"
echo "╚══════════════════════════════════════════════════════════╝"

# ---------------------------------------------------------------------------
# 1. Verify plan9port
# ---------------------------------------------------------------------------
echo ""
echo "[1/6] Verifying plan9port installation..."

PLAN9="${PLAN9:-/usr/local/plan9}"

if [ ! -d "$PLAN9" ]; then
    echo "  ERROR: PLAN9 directory not found at $PLAN9"
    exit 1
fi

for tool in acme sam mk rc 9p; do
    if [ -f "$PLAN9/bin/$tool" ]; then
        echo "  + $tool found"
    else
        echo "  ! $tool not found (may be optional)"
    fi
done

# ---------------------------------------------------------------------------
# 2. Verify QEMU
# ---------------------------------------------------------------------------
echo ""
echo "[2/6] Verifying QEMU installation..."

if command -v qemu-system-x86_64 &>/dev/null; then
    QEMU_VER=$(qemu-system-x86_64 --version | head -1)
    echo "  + $QEMU_VER"
else
    echo "  ! QEMU not found — native Plan 9 execution unavailable"
fi

# ---------------------------------------------------------------------------
# 3. Create workspace structure
# ---------------------------------------------------------------------------
echo ""
echo "[3/6] Creating workspace structure..."

WORKSPACE="/workspace"
mkdir -p "$WORKSPACE/src" "$WORKSPACE/bin" "$WORKSPACE/lib" "$WORKSPACE/man"
echo "  + Created src/ bin/ lib/ man/"

# Generate sample hello.c if not present
if [ ! -f "$WORKSPACE/src/hello.c" ]; then
    cat > "$WORKSPACE/src/hello.c" << 'PLAN9C'
#include <u.h>
#include <libc.h>

void
main(void)
{
	print("Hello from Plan 9!\n");
	exits(0);
}
PLAN9C
    echo "  + Generated sample src/hello.c"
fi

# Generate mkfile if not present
if [ ! -f "$WORKSPACE/mkfile" ]; then
    cat > "$WORKSPACE/mkfile" << 'MKFILE'
</$PLAN9/src/mkmk.proto

TARG=hello
OFILES=\
	src/hello.$O\

</usr/local/plan9/src/mkone
MKFILE
    echo "  + Generated sample mkfile"
fi

# ---------------------------------------------------------------------------
# 4. Configure grid directories
# ---------------------------------------------------------------------------
echo ""
echo "[4/6] Configuring grid directories..."

GRID_DIR="/var/plan9/grid"
GRID_NODES="${PLAN9_GRID_NODES:-3}"

for i in $(seq 0 $((GRID_NODES - 1))); do
    NODE_DIR="$GRID_DIR/cpu-$i"
    mkdir -p "$NODE_DIR/registry" "$NODE_DIR/log"
    echo "  + cpu-$i directory ready"
done

# ---------------------------------------------------------------------------
# 5. Install CLI tools
# ---------------------------------------------------------------------------
echo ""
echo "[5/6] Installing CLI tools..."

# plan9-grid CLI
sudo tee /usr/local/bin/plan9-grid > /dev/null << 'GRIDCLI'
#!/bin/bash
# Plan 9 CPU Server Grid CLI
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.grid.yml}"
GRID_NODES="${PLAN9_GRID_NODES:-3}"

case "${1:-help}" in
    start)
        NODES="${3:-$GRID_NODES}"
        echo "Starting Plan 9 CPU server grid ($NODES nodes)..."
        docker compose -f "$COMPOSE_FILE" --scale plan9-cpu=$NODES up -d
        ;;
    stop)
        echo "Stopping Plan 9 CPU server grid..."
        docker compose -f "$COMPOSE_FILE" down
        ;;
    status)
        echo "Plan 9 CPU Server Grid Status"
        echo "=============================="
        docker compose -f "$COMPOSE_FILE" ps
        ;;
    connect)
        NODE_ID="${2:-0}"
        PORT=$((564 + NODE_ID))
        echo "Connecting to cpu-$NODE_ID via 9P2000 (port $PORT)..."
        9 9p -a "tcp!localhost!$PORT" ls /
        ;;
    deploy)
        FILE="$2"
        echo "Deploying $FILE to all grid nodes..."
        for i in $(seq 0 $((GRID_NODES - 1))); do
            docker compose -f "$COMPOSE_FILE" exec plan9-cpu-$i cp "$FILE" /usr/local/plan9/bin/
        done
        ;;
    logs)
        NODE_ID="$2"
        if [ -n "$NODE_ID" ]; then
            docker compose -f "$COMPOSE_FILE" logs -f "plan9-cpu-$NODE_ID"
        else
            docker compose -f "$COMPOSE_FILE" logs -f
        fi
        ;;
    *)
        echo "Usage: plan9-grid {start|stop|status|connect|deploy|logs}"
        echo ""
        echo "Commands:"
        echo "  start [--nodes N]    Start grid (default: $GRID_NODES nodes)"
        echo "  stop                 Stop all nodes"
        echo "  status               Show grid status"
        echo "  connect <node-id>    Connect via 9P2000"
        echo "  deploy <file.out>    Deploy to all nodes"
        echo "  logs [node-id]       Tail logs"
        ;;
esac
GRIDCLI
sudo chmod +x /usr/local/bin/plan9-grid

# plan9-build CLI
sudo tee /usr/local/bin/plan9-build > /dev/null << 'BUILDCLI'
#!/bin/bash
# Plan 9 C Build CLI (via plan9port)
PLAN9="${PLAN9:-/usr/local/plan9}"

case "${1:-help}" in
    compile)
        FILE="$2"
        echo "Compiling $FILE..."
        9 9c "$FILE" && echo "  + Compiled to ${FILE%.c}.o"
        ;;
    run)
        FILE="$2"
        echo "Compiling and running $FILE..."
        OBJ="${FILE%.c}.o"
        OUT="${FILE%.c}.out"
        9 9c "$FILE" && 9 9l -o "$OUT" "$OBJ" && "./$OUT"
        ;;
    check)
        FILE="$2"
        echo "Syntax checking $FILE..."
        9 9c -w "$FILE" && echo "  + No errors found"
        ;;
    clean)
        echo "Cleaning build artifacts..."
        find . -name "*.o" -o -name "*.out" | xargs rm -f
        echo "  + Cleaned .o and .out files"
        ;;
    *)
        echo "Usage: plan9-build {compile|run|check|clean} [file]"
        echo ""
        echo "Commands:"
        echo "  compile <file.c>   Compile with 9c"
        echo "  run <file.c>       Compile and run"
        echo "  check <file.c>     Syntax check only"
        echo "  clean              Remove .o and .out files"
        ;;
esac
BUILDCLI
sudo chmod +x /usr/local/bin/plan9-build

echo "  + plan9-grid installed"
echo "  + plan9-build installed"

# ---------------------------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------------------------
echo ""
echo "[6/6] Setup complete!"
echo ""
echo "  Plan 9 Development Environment"
echo "  ==============================="
echo "  PLAN9:       $PLAN9"
echo "  Workspace:   $WORKSPACE"
echo "  Grid nodes:  $GRID_NODES"
echo "  9P2000 base: port 564"
echo ""
echo "  Quick commands:"
echo "    plan9-build compile src/hello.c"
echo "    plan9-grid start"
echo "    9 acme /workspace/src"
echo ""
