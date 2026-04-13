#!/bin/bash
# audit_torch_load.sh - Find unpatched torch.load calls in echoself repo
# Usage: bash audit_torch_load.sh [REPO_PATH]
#
# Checks all Python and YAML files for torch.load calls missing weights_only=False

set -euo pipefail

REPO_PATH="${1:-.}"

echo "=== torch.load Audit for PyTorch 2.6+ Compatibility ==="
echo "Scanning: $REPO_PATH"
echo ""

# Find all torch.load calls
echo "--- All torch.load calls ---"
grep -rn "torch\.load" "$REPO_PATH" --include="*.py" --include="*.yml" --include="*.yaml" 2>/dev/null || true
echo ""

# Find unpatched calls (missing weights_only=False)
echo "--- UNPATCHED calls (missing weights_only=False) ---"
UNPATCHED=$(grep -rn "torch\.load" "$REPO_PATH" --include="*.py" --include="*.yml" --include="*.yaml" 2>/dev/null | grep -v "weights_only=False" | grep -v "^Binary" || true)

if [ -z "$UNPATCHED" ]; then
    echo "All torch.load calls are patched with weights_only=False"
    echo ""
    echo "=== AUDIT PASSED ==="
else
    echo "$UNPATCHED"
    echo ""
    echo "=== AUDIT FAILED ==="
    echo "The above torch.load calls need weights_only=False added."
    echo "Without this, PyTorch 2.6+ will reject numpy scalar types in checkpoints."
    exit 1
fi
