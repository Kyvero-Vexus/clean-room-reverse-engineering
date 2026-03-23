# Real Cycle 001 — Cleanroom Skill Accuracy (GPL→GPL)

Date: 2026-03-21
Task: `cut-subset`
Goal metric: practical compatibility accuracy (functional parity under clean-room process constraints)

## Cycle structure

- Baseline candidate: `candidates/cut_baseline.py`
- Mutation 1 candidate: `candidates/cut_mutation1.py`
- Evaluation harness: `scripts/run-benchmark.sh` + weighted scoring model

## Results

- Baseline total score: **88.75**
  - Functional parity: **75.0%** (3/4 cases)
  - Failure: `suppress-no-delim` (`-s` semantics not enforced)
- Mutation 1 total score: **100.0**
  - Functional parity: **100.0%** (4/4 cases)

## Keep/Discard decision

- **KEEP Mutation 1**
- Delta: **+11.25** total score
- Primary cause of improvement: explicit handling of `-s` behavior for lines lacking delimiter.

## Compatibility/legality interpretation

- This cycle demonstrates that clean-room artifacts can drive a compatible reimplementation for the tested subset.
- Legal confidence is process-based, not score-only:
  - A-Team spec was produced behavior-first,
  - implementation avoided source copying,
  - compliance artifacts were generated.
- This is still a bounded subset result, not full-command legal certification.

## Next cycle recommendation

1. Repeat same loop on `uniq-subset` with mutation pressure on `-d/-u/-c` interactions.
2. Promote edge-case matrix requirement into cleanroom skill instructions.
3. Run held-out task check after every 2 mutations to reduce overfitting.
