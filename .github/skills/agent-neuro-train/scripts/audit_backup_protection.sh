#!/bin/bash
# audit_backup_protection.sh - Verify all backup-critical steps have if: always()
# Usage: bash audit_backup_protection.sh [WORKFLOW_FILE]
#
# Checks that backup, upload, commit, and push steps are protected

set -euo pipefail

WORKFLOW="${1:-.github/workflows/agent-neuro-train.yml}"

echo "=== Backup Protection Audit ==="
echo "Workflow: $WORKFLOW"
echo ""

if [ ! -f "$WORKFLOW" ]; then
    echo "ERROR: Workflow file not found: $WORKFLOW"
    exit 1
fi

ISSUES=0

# Critical step names that MUST have if: always()
CRITICAL_STEPS=(
    "Backup model to multiple locations"
    "Upload checkpoint backup artifact"
    "Commit and Push Training Progress"
    "Upload emergency"
)

for step in "${CRITICAL_STEPS[@]}"; do
    # Find the step and check if the next few lines contain "if: always()"
    LINE=$(grep -n "$step" "$WORKFLOW" | head -1 | cut -d: -f1)
    if [ -z "$LINE" ]; then
        echo "WARNING: Step '$step' not found in workflow"
        continue
    fi
    
    # Check lines around the step name for if: always()
    CONTEXT=$(sed -n "$((LINE-2)),$((LINE+3))p" "$WORKFLOW")
    if echo "$CONTEXT" | grep -q "if: always()"; then
        echo "PASS: '$step' (line $LINE) has if: always()"
    else
        echo "FAIL: '$step' (line $LINE) MISSING if: always()"
        ISSUES=$((ISSUES + 1))
    fi
done

echo ""

# Also check all upload-artifact steps
echo "--- Upload Artifact Steps ---"
grep -n "upload-artifact" "$WORKFLOW" | while read -r line; do
    LINENUM=$(echo "$line" | cut -d: -f1)
    PREV_LINES=$(sed -n "$((LINENUM-3)),${LINENUM}p" "$WORKFLOW")
    if echo "$PREV_LINES" | grep -q "if: always()"; then
        echo "PASS: upload-artifact at line $LINENUM has if: always()"
    else
        STEP_NAME=$(sed -n "$((LINENUM-2)),$((LINENUM-1))p" "$WORKFLOW" | grep "name:" | head -1 | sed 's/.*name: //')
        echo "WARN: upload-artifact at line $LINENUM ($STEP_NAME) may lack if: always()"
    fi
done

echo ""
if [ $ISSUES -eq 0 ]; then
    echo "=== AUDIT PASSED ==="
else
    echo "=== AUDIT FAILED: $ISSUES critical steps missing if: always() ==="
    exit 1
fi
