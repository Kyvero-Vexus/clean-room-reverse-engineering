#!/usr/bin/env python3
"""Check required clean-room artifacts for a run directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = [
    "intake-form.md",
    "taint-register.yaml",
    "spec-index.yaml",
    "test-index.yaml",
    "traceability-matrix.yaml",
    "compliance-report.md",
]

CRITICAL = [
    "intake-form.md",
    "taint-register.yaml",
    "spec-index.yaml",
    "test-index.yaml",
    "traceability-matrix.yaml",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    found = []
    missing = []

    for rel in REQUIRED:
        p = run_dir / rel
        if p.exists():
            found.append(rel)
        else:
            missing.append(rel)

    critical_missing = [x for x in missing if x in CRITICAL]
    rate = len(found) / len(REQUIRED) if REQUIRED else 0.0

    payload = {
        "status": "ok",
        "run_dir": str(run_dir),
        "required_total": len(REQUIRED),
        "found_total": len(found),
        "pass_rate": rate,
        "found": found,
        "missing": missing,
        "critical_missing": critical_missing,
        "hard_fail": bool(critical_missing),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
