#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${1:-0.0.0.0}"
PORT="${2:-8787}"
RESULTS="${3:-$ROOT_DIR/results/results.tsv}"

exec python3 "$ROOT_DIR/scripts/dashboard_server.py" \
  --host "$HOST" \
  --port "$PORT" \
  --results "$RESULTS"
