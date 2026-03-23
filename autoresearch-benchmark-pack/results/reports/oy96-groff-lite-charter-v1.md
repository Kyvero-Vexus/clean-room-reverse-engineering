# OY96 Charter v1 — First Complex Clean-Room Target (groff-lite)

## Target Selection
- **Selected target:** `groff-lite` behavioral subset (GPL reference behavior only; no source-code derivation).
- **Reference executable:** `/usr/bin/groff` for black-box behavioral comparison.

## Bounded Scope (v1)
- In scope:
  - roff tokenizer/parser subset
  - macro expansion subset (`.de`, `.am`, `.ds`, `.nr`)
  - request interpreter subset + conditionals/register semantics
  - line-breaking/fill/diversion state machine
  - plaintext/terminal output backend path
- Out of scope:
  - full troff/nroff parity
  - device drivers beyond baseline terminal/plaintext
  - undocumented extensions lacking behavior-first spec coverage

## Compatibility Criteria
- Differential harness pass rate target: **>= 95%** on scoped corpus before escalation.
- No severity-1 regressions on held-out/adversarial fixtures.
- Deterministic replay required for all promoted cycle artifacts.

## Risk Notes
- Main risks: contamination, unstable spec boundaries, hidden parser edge-cases.
- Mitigations:
  - behavior-first specs and fixtures only
  - strict traceability logs per cycle
  - evidence bundles with contamination checklist
  - keep/discard decisions tied to measured compatibility deltas

## Go/No-Go Gates
- **Go** when:
  - traceability bundle complete
  - contamination controls pass
  - cycle score meets threshold and is reproducible
- **No-go** when:
  - missing evidence artifacts
  - unresolved contamination flags
  - non-deterministic benchmark outcomes

## Next Action
Run first charter-aligned cycle once dependency order permits:

```bash
scripts/run-benchmark.sh groff-lite-subset /usr/bin/groff cron-driver oy96_charter_cycle001
```
