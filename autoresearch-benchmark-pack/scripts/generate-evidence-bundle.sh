#!/usr/bin/env bash
# Generate a counsel-ready evidence bundle for a completed benchmark run.
#
# Usage: ./scripts/generate-evidence-bundle.sh <run-dir> [bundle-out-dir]
#
# Produces: <bundle-out-dir>/<run-id>-evidence-bundle.tar.gz
#           <bundle-out-dir>/<run-id>-evidence-manifest.json

set -euo pipefail

RUN_DIR="${1:-}"
BUNDLE_DIR="${2:-$(dirname "$0")/../results/bundles}"

if [[ -z "$RUN_DIR" || ! -d "$RUN_DIR" ]]; then
  echo "Usage: $0 <run-dir> [bundle-out-dir]" >&2
  exit 1
fi

RUN_ID="$(basename "$RUN_DIR")"
mkdir -p "$BUNDLE_DIR"

MANIFEST="$BUNDLE_DIR/${RUN_ID}-evidence-manifest.json"
BUNDLE_TAR="$BUNDLE_DIR/${RUN_ID}-evidence-bundle.tar.gz"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TS="$(date -u +%Y%m%dT%H%M%SZ)"

# Collect artifact list with sha256
artifacts=()
manifest_entries=()

for f in "$RUN_DIR"/*; do
  [[ -f "$f" ]] || continue
  rel="${f#$ROOT/}"
  sha="$(sha256sum "$f" | awk '{print $1}')"
  artifacts+=("$f")
  manifest_entries+=("{\"path\":\"$rel\",\"sha256\":\"$sha\"}")
done

# Include fixture corpus traceability manifest
FIXTURE_MANIFEST="$ROOT/results/fixtures/groff-lite-v1/traceability-manifest.json"
if [[ -f "$FIXTURE_MANIFEST" ]]; then
  sha="$(sha256sum "$FIXTURE_MANIFEST" | awk '{print $1}')"
  rel="${FIXTURE_MANIFEST#$ROOT/}"
  manifest_entries+=("{\"path\":\"$rel\",\"sha256\":\"$sha\"}")
  artifacts+=("$FIXTURE_MANIFEST")
fi

# Write manifest
{
  printf '{"bundle_id":"%s","generated_at":"%s","run_dir":"%s","artifacts":[\n' \
    "$RUN_ID" "$TS" "$(basename "$RUN_DIR")"
  IFS=','
  printf '%s' "${manifest_entries[*]}"
  unset IFS
  printf '\n]}\n'
} > "$MANIFEST"

# Create tarball
tar -czf "$BUNDLE_TAR" -C "$ROOT" \
  "$(realpath --relative-to="$ROOT" "$RUN_DIR")" \
  "$(realpath --relative-to="$ROOT" "$FIXTURE_MANIFEST")" \
  2>/dev/null || true

echo "Bundle:   $BUNDLE_TAR"
echo "Manifest: $MANIFEST"
