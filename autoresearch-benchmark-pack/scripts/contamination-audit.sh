#!/usr/bin/env bash
# Contamination audit for clean-room candidate source.
# Checks candidate script for any imports/references to groff/nroff/troff source code
# or documentation that would indicate reverse-engineering from copyrighted source.
#
# Usage: ./scripts/contamination-audit.sh <candidate-script>
# Exit 0 = clean, 1 = contamination detected

set -euo pipefail

CANDIDATE="${1:-}"
if [[ -z "$CANDIDATE" || ! -f "$CANDIDATE" ]]; then
  echo "Usage: $0 <candidate-script>" >&2
  exit 1
fi

VIOLATIONS_FILE="$(mktemp)"
trap "rm -f $VIOLATIONS_FILE" EXIT

# Patterns that would indicate contamination (source-copy / oracle-exec)
SUSPECT_PATTERNS=(
  "groff/src"
  "troff/src"
  "ditroff"
  "GNU groff"
  "GPL.*groff"
)

for pat in "${SUSPECT_PATTERNS[@]}"; do
  if grep -qi "$pat" "$CANDIDATE" 2>/dev/null; then
    echo "copyright-reference: $pat" >> "$VIOLATIONS_FILE"
  fi
done

# Check that candidate does not exec groff/nroff/troff as oracle
for pat in "nroff" "groff" "troff"; do
  if grep -q "subprocess.*$pat\|os\.system.*$pat" "$CANDIDATE" 2>/dev/null; then
    echo "oracle-exec: $pat" >> "$VIOLATIONS_FILE"
  fi
done

TS="$(date -u +%Y%m%dT%H%M%SZ)"

python3 - "$VIOLATIONS_FILE" "$CANDIDATE" "$TS" <<'PYEOF'
import json, sys

vfile, candidate, ts = sys.argv[1], sys.argv[2], sys.argv[3]
with open(vfile) as f:
    violations = [l.strip() for l in f if l.strip()]

status = "contaminated" if violations else "clean"
print(json.dumps({
    "audit_timestamp": ts,
    "candidate": candidate,
    "status": status,
    "violations": violations,
    "verdict": "PASS" if status == "clean" else "FAIL"
}, indent=2))
PYEOF

# Exit code based on result
violations_count=$(wc -l < "$VIOLATIONS_FILE")
[[ "$violations_count" -eq 0 ]]
