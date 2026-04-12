#!/bin/bash
# =============================================================================
# Plan 9 Devcontainer — Post-Start Script
# Runs on every container start.
# Verifies PATH, ensures Docker network, displays status.
# =============================================================================

echo "Plan 9 Devcontainer — Starting..."

# Verify PATH includes plan9port
PLAN9="${PLAN9:-/usr/local/plan9}"
if echo "$PATH" | grep -q "$PLAN9/bin"; then
    echo "  + PATH includes plan9port"
else
    export PATH="$PLAN9/bin:$PATH"
    echo "  + Added plan9port to PATH"
fi

# Ensure Docker network exists for grid
if command -v docker &>/dev/null; then
    docker network inspect plan9-net &>/dev/null 2>&1 || \
        docker network create --subnet=172.28.0.0/16 plan9-net &>/dev/null 2>&1
    echo "  + Docker network plan9-net ready"
fi

# Create missing grid directories
GRID_DIR="/var/plan9/grid"
GRID_NODES="${PLAN9_GRID_NODES:-3}"
for i in $(seq 0 $((GRID_NODES - 1))); do
    mkdir -p "$GRID_DIR/cpu-$i/registry" "$GRID_DIR/cpu-$i/log" 2>/dev/null
done
echo "  + Grid directories verified ($GRID_NODES nodes)"

# Display status
echo ""
echo "  Plan 9 Development Environment"
echo "  ==============================="
echo "  PLAN9:     $PLAN9"
echo "  Workspace: /workspace"
echo "  Grid:      $GRID_NODES nodes configured"
echo "  Ready."
