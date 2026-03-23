# oy96 handoff checkpoint v2 (2026-03-22 09:37 ET)

## Target
- Complex target: `groff-lite-subset`
- Candidate oracle binary: `/usr/bin/groff`

## Bounded scope (for jpph cycle001)
- Include: core text formatting behaviors covered by benchmark subset
- Exclude: macro packages, device-specific output backends, non-subset options

## Compatibility gate
- Command to execute on unblock:
  - `scripts/run-benchmark.sh groff-lite-subset /usr/bin/groff cron-driver jpph_cycle001`
- Required artifact:
  - `results/reports/jpph-cycle001-report.json` (or iteration report in run dir)

## Clean-room controls
- Behavior-first spec only; no source-derived implementation
- Traceability via run ledger + copied report artifacts
- Contamination controls maintained through benchmark harness isolation

## Close-ready checklist status
- Charter: drafted and refreshed ✅
- Handoff checkpoint: prepared for jpph ✅
- Awaiting dependency closure (`7van`) before `jpph` can run ⏳
