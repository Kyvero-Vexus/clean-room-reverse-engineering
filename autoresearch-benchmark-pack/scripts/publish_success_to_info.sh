#!/usr/bin/env bash
set -euo pipefail

# Publish a successful clean-room cycle to ~/info/clean-room-successes.
#
# Usage:
#   ./scripts/publish_success_to_info.sh <cycle-id> <run-dir> <report-md> [spec-file]
#
# Example:
#   ./scripts/publish_success_to_info.sh \
#     real-cycle-003 \
#     results/runs/20260322T010000-sort-subset-realcycle003-mut1 \
#     results/real-cycle-003-report.md \
#     real-cycle-003/A-team/spec-sort-subset.md

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <cycle-id> <run-dir> <report-md> [spec-file]" >&2
  exit 1
fi

CYCLE_ID="$1"
RUN_DIR="$2"
REPORT_MD="$3"
SPEC_FILE="${4:-}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_BASE="/home/slime/info/clean-room-successes"
OUT_DIR="$OUT_BASE/$CYCLE_ID"

mkdir -p "$OUT_DIR"

cp "$ROOT_DIR/$REPORT_MD" "$OUT_DIR/" 
cp "$ROOT_DIR/$RUN_DIR/score-report.json" "$OUT_DIR/score-report.json"
cp "$ROOT_DIR/$RUN_DIR/test-report.json" "$OUT_DIR/test-report.json"

if [[ -n "$SPEC_FILE" && -f "$ROOT_DIR/$SPEC_FILE" ]]; then
  cp "$ROOT_DIR/$SPEC_FILE" "$OUT_DIR/"
fi

echo "Published success bundle to: $OUT_DIR"
