#!/usr/bin/env bash
# dev-check.sh — Run the standard OpenCog development checks
# Usage: bash {baseDir}/scripts/dev-check.sh [repo_path]
#
# Runs format check, type check, lint, and LOC check.
# Exits with non-zero if any check fails.

set -euo pipefail

REPO_DIR="${1:-$(pwd)}"
cd "$REPO_DIR"

echo "=== OpenCog Dev Check ==="
echo "Repository: $REPO_DIR"
echo ""

echo "--- Format Check ---"
pnpm format:check || { echo "❌ Format check failed. Run: pnpm format"; exit 1; }
echo "✅ Format OK"
echo ""

echo "--- Type Check ---"
pnpm tsgo || { echo "❌ Type check failed."; exit 1; }
echo "✅ Types OK"
echo ""

echo "--- Lint ---"
pnpm lint || { echo "❌ Lint failed."; exit 1; }
echo "✅ Lint OK"
echo ""

echo "--- LOC Check (max 500 per file) ---"
pnpm check:loc || { echo "❌ LOC check failed. Some files exceed 500 lines."; exit 1; }
echo "✅ LOC OK"
echo ""

echo "--- Git State ---"
if git diff --quiet && git diff --cached --quiet; then
  if git ls-files --others --exclude-standard | grep -q .; then
    echo "⚠️  Untracked files present"
  else
    echo "✅ Git state clean"
  fi
else
  echo "⚠️  Uncommitted changes present"
fi

echo ""
echo "=== All checks passed ==="
