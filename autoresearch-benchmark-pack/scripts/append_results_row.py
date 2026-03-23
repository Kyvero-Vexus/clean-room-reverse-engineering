#!/usr/bin/env python3
"""Append one row to benchmark results TSV (safe for cron telemetry)."""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path

HEADER = ["iter", "commit", "task_id", "skill_variant", "score", "delta", "status", "description"]


def current_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
        return out or "nocommit"
    except Exception:
        return "nocommit"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--skill-variant", default="cron-driver")
    ap.add_argument("--score", type=float, required=True)
    ap.add_argument("--delta", type=float, default=0.0)
    ap.add_argument("--status", required=True)
    ap.add_argument("--description", default="")
    ap.add_argument("--commit", default="")
    args = ap.parse_args()

    results = Path(args.results)
    results.parent.mkdir(parents=True, exist_ok=True)

    rows = 0
    if results.exists():
        with results.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            rows = sum(1 for _ in reader)

    if not results.exists() or rows == 0:
        with results.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t", lineterminator="\n")
            writer.writerow(HEADER)
        rows = 1

    iter_num = rows
    commit = args.commit or current_commit()
    desc = (args.description or "").replace("\n", " ").replace("\t", " ")[:500]

    with results.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                str(iter_num),
                commit,
                args.task_id,
                args.skill_variant,
                f"{args.score:.4f}",
                f"{args.delta:.4f}",
                args.status,
                desc,
            ]
        )

    print(f"appended iter={iter_num} task={args.task_id} score={args.score:.4f} status={args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
