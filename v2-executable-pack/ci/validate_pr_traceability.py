#!/usr/bin/env python3
"""Validate CRRE traceability metadata in PR body.

Inputs (env):
  PR_BODY              full PR body text
  SPEC_INDEX_PATH      optional path to spec-index.yaml
  TEST_INDEX_PATH      optional path to test-index.yaml

Exit codes:
  0 -> pass
  1 -> fail
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

SPEC_RE = re.compile(r"CRRE-SPEC-[A-Z0-9-]+")
TEST_RE = re.compile(r"CRRE-TST-[A-Z0-9-]+")


def die(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)


def load_ids(path: str, key: str) -> set[str]:
    p = Path(path)
    if not p.exists():
        die(f"Missing index file: {path}")
    if yaml is None:
        die("PyYAML unavailable; cannot validate index IDs")
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or key not in data or not isinstance(data[key], list):
        die(f"Index format invalid for {path}; expected key '{key}' with list")
    ids = {str(x).strip() for x in data[key] if str(x).strip()}
    return ids


def main() -> int:
    body = os.environ.get("PR_BODY", "")
    if not body.strip():
        die("PR body is empty")

    # Required fields check
    required_markers = [
        "Spec-Refs:",
        "Test-Refs:",
        "Provenance-Statement:",
        "Exposure-Attestation:",
    ]
    for marker in required_markers:
        if marker not in body:
            die(f"Missing required PR metadata field: {marker}")

    spec_refs = set(SPEC_RE.findall(body))
    test_refs = set(TEST_RE.findall(body))

    if not spec_refs:
        die("No CRRE-SPEC-* IDs found in Spec-Refs")
    if not test_refs:
        die("No CRRE-TST-* IDs found in Test-Refs")

    spec_index = os.environ.get("SPEC_INDEX_PATH")
    test_index = os.environ.get("TEST_INDEX_PATH")

    if spec_index and test_index:
        valid_spec = load_ids(spec_index, "spec_ids")
        valid_test = load_ids(test_index, "test_ids")

        unknown_spec = sorted(spec_refs - valid_spec)
        unknown_test = sorted(test_refs - valid_test)
        if unknown_spec:
            die("Unknown spec IDs: " + ", ".join(unknown_spec))
        if unknown_test:
            die("Unknown test IDs: " + ", ".join(unknown_test))

    print("CRRE traceability check passed")
    print("Spec refs:", ", ".join(sorted(spec_refs)))
    print("Test refs:", ", ".join(sorted(test_refs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
