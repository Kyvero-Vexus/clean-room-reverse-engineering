# Real Cycle 003 — Cleanroom Skill Accuracy (GPL→GPL)

Date: 2026-03-21
Task: `sort-subset`
Goal metric: practical compatibility accuracy (functional parity under clean-room process constraints)

## Cycle structure (current pass)

- Baseline run tag: `cycle003_oracle_baseline`
- Candidate command: `/usr/bin/sort`
- Run dir: `results/runs/20260321T234016-sort-subset-cycle003_oracle_baseline`
- Evaluation harness: `scripts/run-benchmark.sh` + weighted scoring model

## Results (current pass)

- Oracle baseline total score: **100.0**
- Status: **ok**

## Contamination controls / process notes

- This run is harness validation evidence only (oracle executable), not independent reimplementation evidence.
- No source-code ingestion from GNU sort internals was performed in this pass.
- Next pass must provide behavior-first spec artifacts and independent candidate implementation(s) before keep/discard mutation decisions.

## Next required actions to complete Cycle-003 bead

1. Produce A-team behavior-first spec for bounded `sort-subset` semantics.
2. Produce independent baseline candidate implementation.
3. Produce at least one mutation candidate.
4. Re-run differential scoring on independent candidates.
5. Record keep/discard decision with evidence delta and publish final cycle report.
