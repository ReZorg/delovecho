#!/bin/bash
# Check GSD installation status across all runtimes

echo "=== GSD Installation Check ==="
echo ""

# Check Claude Code
if [ -d "$HOME/.claude/commands/gsd" ]; then
    VERSION=$(node "$HOME/.claude/get-shit-done/bin/gsd-tools.js" --version 2>/dev/null || echo "unknown")
    CMD_COUNT=$(ls "$HOME/.claude/commands/gsd/"*.md 2>/dev/null | wc -l)
    echo "[✓] Claude Code (global): $CMD_COUNT commands installed"
else
    echo "[✗] Claude Code (global): not installed"
fi

if [ -d ".claude/commands/gsd" ]; then
    CMD_COUNT=$(ls ".claude/commands/gsd/"*.md 2>/dev/null | wc -l)
    echo "[✓] Claude Code (local): $CMD_COUNT commands installed"
else
    echo "[✗] Claude Code (local): not installed"
fi

# Check OpenCode
OPENCODE_DIR="${OPENCODE_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode}"
if [ -d "$OPENCODE_DIR/commands/gsd" ]; then
    CMD_COUNT=$(ls "$OPENCODE_DIR/commands/gsd/"*.md 2>/dev/null | wc -l)
    echo "[✓] OpenCode (global): $CMD_COUNT commands installed"
else
    echo "[✗] OpenCode (global): not installed"
fi

# Check Gemini
GEMINI_DIR="${GEMINI_CONFIG_DIR:-$HOME/.gemini}"
if [ -d "$GEMINI_DIR/commands/gsd" ]; then
    CMD_COUNT=$(ls "$GEMINI_DIR/commands/gsd/"*.md 2>/dev/null | wc -l)
    echo "[✓] Gemini (global): $CMD_COUNT commands installed"
else
    echo "[✗] Gemini (global): not installed"
fi

# Check project planning
echo ""
if [ -d ".planning" ]; then
    echo "[✓] Project initialized (.planning/ exists)"
    [ -f ".planning/PROJECT.md" ] && echo "    PROJECT.md: present"
    [ -f ".planning/ROADMAP.md" ] && echo "    ROADMAP.md: present"
    [ -f ".planning/STATE.md" ] && echo "    STATE.md: present"
    [ -f ".planning/config.json" ] && echo "    config.json: present"
else
    echo "[✗] No project initialized (no .planning/ directory)"
fi
