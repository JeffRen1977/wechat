#!/usr/bin/env bash
# Backward-compatible shim. Prefer ./scripts/run-image-generation.sh.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/run-image-generation.sh" "$@"
