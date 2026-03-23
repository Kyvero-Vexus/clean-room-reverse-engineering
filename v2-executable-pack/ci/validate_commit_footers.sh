#!/usr/bin/env bash
set -euo pipefail

# Validate CRRE commit footer markers in recent commit messages.
# Usage:
#   ./validate_commit_footers.sh [base_ref]
# Example:
#   ./validate_commit_footers.sh origin/main

BASE_REF="${1:-origin/main}"

if ! git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
  echo "ERROR: base ref '$BASE_REF' not found"
  exit 1
fi

COMMITS=$(git rev-list --no-merges "${BASE_REF}..HEAD")
if [[ -z "$COMMITS" ]]; then
  echo "No commits to validate"
  exit 0
fi

FAIL=0
for c in $COMMITS; do
  MSG=$(git log -1 --pretty=%B "$c")
  if ! grep -q "Spec-Refs:" <<<"$MSG"; then
    echo "ERROR: $c missing Spec-Refs footer"
    FAIL=1
  fi
  if ! grep -q "Test-Refs:" <<<"$MSG"; then
    echo "ERROR: $c missing Test-Refs footer"
    FAIL=1
  fi
  if ! grep -q "Provenance:" <<<"$MSG"; then
    echo "ERROR: $c missing Provenance footer"
    FAIL=1
  fi
done

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi

echo "CRRE commit footer validation passed"
