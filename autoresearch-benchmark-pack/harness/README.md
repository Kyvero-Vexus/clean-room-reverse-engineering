# Harness Contract (Skeleton)

## Inputs

- Task card (`tasks/<task>.yaml`)
- Candidate skill revision (branch/commit)
- Candidate implementation under evaluation
- Corpus for parity tests

## Required checks

1. Functional parity test run
2. Clean-room artifact checklist validation
3. Regression suite run
4. Optional rerun for reproducibility score

## Expected output bundle

- `checklist-report.json`
- `test-report.json`
- `score-report.json`
- `iteration-report.md`

(Current implementation stores these under `results/runs/<timestamp>-<task>-<tag>/`.)

## Execution order

1. validate task config
2. run parity tests
3. run compliance checklist
4. run regression set
5. compute weighted score
6. append row to `results/results.tsv`
