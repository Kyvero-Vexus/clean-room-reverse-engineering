# RIRE Groff-lite Rubric + Bounded Scope Draft

## Behavior-first rubric (v0)
1. **Parsing fidelity (30 pts)**
   - Request/control-line recognition parity
   - Escape sequence handling for selected subset
2. **Macro semantics (20 pts)**
   - Deterministic `.de/.am` expansion behavior on fixture corpus
3. **Register/string state (15 pts)**
   - `.nr/.ds` observable behavior parity
4. **Flow formatting (15 pts)**
   - Fill/no-fill + line-break behavior against fixture expected output
5. **Traceability and legality (20 pts)**
   - Every behavior spec linked to independent fixture + provenance note
   - Contamination checklist complete for cycle artifacts

## Bounded groff-lite scope (this bead)
### Include
- Tokenization and request-line parsing
- `.de`, `.am`, `.nr`, `.ds` subset
- conditionals/register use required by current fixture corpus
- plaintext/terminal output backend only

### Exclude (explicit)
- full troff device model
- binary output drivers (PS/PDF/device backends)
- non-deterministic extension macros and vendor-specific quirks outside corpus

## Acceptance gates for next bead
- Rubric serialized to JSON (`results/reports/groff-rubric.json`)
- Scope written to markdown (`results/reports/groff-bounded-scope.md`)
- Each included feature mapped to at least one fixture id
- Contamination-control checklist attached in same report directory
