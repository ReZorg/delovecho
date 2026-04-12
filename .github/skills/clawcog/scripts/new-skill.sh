#!/usr/bin/env bash
# new-skill.sh — Scaffold a new OpenCog skill in the repo or workspace
# Usage: bash {baseDir}/scripts/new-skill.sh <skill-name> [target-dir]
#
# target-dir defaults to ./skills/ (relative to current directory)

set -euo pipefail

SKILL_NAME="${1:?Usage: new-skill.sh <skill-name> [target-dir]}"
TARGET_DIR="${2:-./skills}"
SKILL_DIR="$TARGET_DIR/$SKILL_NAME"

if [ -d "$SKILL_DIR" ]; then
  echo "❌ Skill directory already exists: $SKILL_DIR"
  exit 1
fi

mkdir -p "$SKILL_DIR"

cat > "$SKILL_DIR/SKILL.md" << 'SKILLEOF'
---
name: SKILL_NAME_PLACEHOLDER
description: TODO — What the skill does and when to use it.
metadata: { "opencog": { "emoji": "🔧" } }
---

# SKILL_NAME_PLACEHOLDER

## Overview

TODO: Describe what this skill enables.

## Usage

TODO: Instructions for the agent.
SKILLEOF

# Replace placeholder with actual skill name
sed -i "s/SKILL_NAME_PLACEHOLDER/$SKILL_NAME/g" "$SKILL_DIR/SKILL.md"

echo "✅ Created skill scaffold at $SKILL_DIR"
echo "   Edit $SKILL_DIR/SKILL.md to complete the skill."
echo "   Refresh skills in OpenCog to load it."
