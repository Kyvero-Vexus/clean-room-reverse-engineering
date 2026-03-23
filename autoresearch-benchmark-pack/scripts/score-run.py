#!/usr/bin/env python3
"""Compute weighted score for a benchmark run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

WEIGHTS = {
    "functional_parity": 0.45,
    "cleanroom_compliance": 0.25,
    "reproducibility": 0.15,
    "simplicity": 0.10,
    "cost_efficiency": 0.05,
}


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-report", required=True)
    ap.add_argument("--checklist-report", required=True)
    ap.add_argument("--reproducibility", type=float, default=100.0)
    ap.add_argument("--simplicity", type=float, default=100.0)
    ap.add_argument("--cost", type=float, default=100.0)
    args = ap.parse_args()

    test = load_json(args.test_report)
    checklist = load_json(args.checklist_report)

    functional = float(test.get("pass_rate", 0.0)) * 100.0
    compliance = float(checklist.get("pass_rate", 0.0)) * 100.0
    reproducibility = max(0.0, min(100.0, args.reproducibility))
    simplicity = max(0.0, min(100.0, args.simplicity))
    cost = max(0.0, min(100.0, args.cost))

    hard_fail_reasons = []
    if test.get("status") != "ok":
        hard_fail_reasons.append("test_runner_error")
    if checklist.get("hard_fail"):
        hard_fail_reasons.append("critical_artifacts_missing")

    if hard_fail_reasons:
        out = {
            "status": "hard-fail",
            "hard_fail_reasons": hard_fail_reasons,
            "metrics": {
                "functional_parity": functional,
                "cleanroom_compliance": compliance,
                "reproducibility": reproducibility,
                "simplicity": simplicity,
                "cost_efficiency": cost,
            },
            "total_score": 0.0,
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0

    metrics = {
        "functional_parity": functional,
        "cleanroom_compliance": compliance,
        "reproducibility": reproducibility,
        "simplicity": simplicity,
        "cost_efficiency": cost,
    }

    total = sum(metrics[k] * WEIGHTS[k] for k in metrics)
    out = {
        "status": "ok",
        "weights": WEIGHTS,
        "metrics": metrics,
        "total_score": round(total, 4),
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
