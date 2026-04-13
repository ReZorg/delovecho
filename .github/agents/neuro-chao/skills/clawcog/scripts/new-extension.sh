#!/usr/bin/env bash
# new-extension.sh — Scaffold a new OpenCog extension/plugin
# Usage: bash {baseDir}/scripts/new-extension.sh <plugin-name> [repo-dir]
#
# repo-dir defaults to current directory (should be clawcog repo root)

set -euo pipefail

PLUGIN_NAME="${1:?Usage: new-extension.sh <plugin-name> [repo-dir]}"
REPO_DIR="${2:-.}"
EXT_DIR="$REPO_DIR/extensions/$PLUGIN_NAME"

if [ -d "$EXT_DIR" ]; then
  echo "❌ Extension directory already exists: $EXT_DIR"
  exit 1
fi

mkdir -p "$EXT_DIR/src"

# package.json
cat > "$EXT_DIR/package.json" << EOF
{
  "name": "@opencog/$PLUGIN_NAME",
  "version": "2026.2.9",
  "private": true,
  "description": "OpenCog $PLUGIN_NAME extension",
  "type": "module",
  "devDependencies": {
    "opencog": "workspace:*"
  },
  "opencog": {
    "extensions": ["./index.ts"]
  }
}
EOF

# Plugin manifest
cat > "$EXT_DIR/openclaw.plugin.json" << EOF
{
  "id": "$PLUGIN_NAME",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
EOF

# Entry point
cat > "$EXT_DIR/index.ts" << 'EOF'
// TODO: Implement extension
export default {};
EOF

echo "✅ Created extension scaffold at $EXT_DIR"
echo "   Files created:"
echo "     $EXT_DIR/package.json"
echo "     $EXT_DIR/openclaw.plugin.json"
echo "     $EXT_DIR/index.ts"
echo "   Run 'pnpm install' from repo root to link the workspace package."
