# Real Cycle 002 — Cleanroom Skill Accuracy (GPL→GPL)

Date: 2026-03-21
Task: `uniq-subset`
Goal metric: practical compatibility accuracy (functional parity under clean-room process constraints)

## Cycle structure

- Baseline candidate: `candidates/uniq_baseline.py`
- Mutation 1 candidate: `candidates/uniq_mutation1.py`
- Evaluation harness: `scripts/run-benchmark.sh` + weighted scoring model

## Results

- Baseline total score: **66.25**
  - Functional parity: **25.0%** (1/4 cases)
  - Failures: `default`, `count`, `duplicates-only`
  - Root cause: terminal adjacent group not emitted at end-of-stream.
- Mutation 1 total score: **100.0**
  - Functional parity: **100.0%** (4/4 cases)

## Keep/Discard decision

- **KEEP Mutation 1**
- Delta: **+33.75** total score
- Primary cause of improvement: explicit end-of-stream flush of final adjacent group.

## Compatibility/legality interpretation

- This cycle strengthens evidence that clean-room specs can drive highly compatible implementations for grouped stream semantics.
- Legal confidence remains process-based:
  - behavior-first A-Team spec,
  - independent B-Team implementation path,
  - C-Team artifact and score evidence.
- This is bounded subset evidence, not blanket legal certification of full command compatibility.

## Next cycle recommendation

1. Run `sort-subset` next with emphasis on key selection and stable-order edge cases.
2. Promote explicit **end-of-stream state flush** checks into spec/test templates for stateful tools.
3. Add held-out sample variant to `uniq-subset` to reduce overfitting to one corpus.
