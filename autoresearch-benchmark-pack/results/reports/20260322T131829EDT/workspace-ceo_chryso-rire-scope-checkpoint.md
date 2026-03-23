# RIRE checkpoint: groff-lite rubric/scope progression

- Bead: `workspace-ceo_chryso-rire`
- Discipline: behavior-first specification, contamination controls, traceability evidence

## Concrete advancement this run

Validated and pinned the next executable boundary for `rire`:

```bash
python3 tools/define_groff_scope.py \
  --rubric results/reports/groff-rubric.json \
  --scope results/reports/groff-bounded-scope.md
```

## Deliverables expected from next executable step

1. `results/reports/groff-rubric.json` — bounded complexity rubric with acceptance thresholds.
2. `results/reports/groff-bounded-scope.md` — behavior-only scope/exclusions with legal-process gates.
3. Traceability section mapping each scope item to non-contaminating observed behavior sources.

## Clean-room guardrails re-asserted

- No source-code copying or line-level structural borrowing from upstream implementations.
- Keep all requirements phrased as externally-observable behavior.
- Preserve audit trail for each benchmark decision and keep/discard transition.
