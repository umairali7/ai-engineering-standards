#!/usr/bin/env bash
# Portable launcher for the one-process comprehensive offline demo.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python "$SCRIPT_DIR/demo_full.py"
