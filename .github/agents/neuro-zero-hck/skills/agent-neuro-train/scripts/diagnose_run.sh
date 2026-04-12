#!/bin/bash
# diagnose_run.sh - Diagnose agent-neuro-train workflow failures
# Usage: bash diagnose_run.sh [RUN_ID] [--repo 9cog/echoself]
#
# If RUN_ID is omitted, checks the most recent run.

set -euo pipefail

REPO="${3:-9cog/echoself}"
RUN_ID="${1:-}"

echo "=== Agent-Neuro Train Diagnostic ==="
echo ""

# Get latest run if not specified
if [ -z "$RUN_ID" ]; then
    echo "No RUN_ID specified, checking latest run..."
    RUN_ID=$(gh run list --repo "$REPO" --workflow=agent-neuro-train.yml --json databaseId --limit 1 -q '.[0].databaseId')
    if [ -z "$RUN_ID" ]; then
        echo "ERROR: No agent-neuro-train runs found"
        exit 1
    fi
fi

echo "Run ID: $RUN_ID"
echo ""

# Get run status
echo "=== Run Status ==="
gh run view "$RUN_ID" --repo "$REPO" --json status,conclusion,startedAt,updatedAt,event 2>&1 || true
echo ""

# Check for failed steps
echo "=== Failed Steps ==="
gh run view "$RUN_ID" --repo "$REPO" --log-failed 2>&1 | head -100 || echo "No failed steps (or run still in progress)"
echo ""

# Check for backup-related steps
echo "=== Backup Step Status ==="
gh run view "$RUN_ID" --repo "$REPO" 2>&1 | grep -i "backup\|upload\|commit\|push\|emergency" || echo "No backup steps found in output"
echo ""

# Check for torch.load errors
echo "=== torch.load Errors ==="
gh run view "$RUN_ID" --repo "$REPO" --log 2>&1 | grep -i "UnpicklingError\|weights_only\|WeightsUnpickler" | head -10 || echo "No torch.load errors found"
echo ""

# Check for checkpoint issues
echo "=== Checkpoint Issues ==="
gh run view "$RUN_ID" --repo "$REPO" --log 2>&1 | grep -i "no checkpoint\|checkpoint not found\|CRITICAL ERROR" | head -10 || echo "No checkpoint issues found"
echo ""

# Check artifacts
echo "=== Artifacts ==="
gh run view "$RUN_ID" --repo "$REPO" --json artifacts 2>&1 || true
echo ""

echo "=== Diagnostic Complete ==="
echo "For full logs: gh run view $RUN_ID --repo $REPO --log"
