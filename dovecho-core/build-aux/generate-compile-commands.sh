#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v bear >/dev/null 2>&1; then
  echo "error: bear is required to generate compile_commands.json"
  echo "install: sudo apt-get install bear  (or your platform equivalent)"
  exit 1
fi

if [[ ! -f configure ]]; then
  ./autogen.sh
fi

if [[ ! -f Makefile ]]; then
  ./configure --enable-devel-checks
fi

bear --output compile_commands.json -- make -j"$(nproc)"

echo "compile_commands.json generated at: $ROOT_DIR/compile_commands.json"
