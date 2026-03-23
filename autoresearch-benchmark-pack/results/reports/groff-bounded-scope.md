# Groff-lite Bounded Scope (rire v1)

## Include
- Tokenization and request/control-line parsing
- Escape sequence handling required by scoped fixtures
- Macro subset: `.de`, `.am`
- Register/string subset: `.nr`, `.ds`
- Text flow behavior: fill/no-fill and line breaks for plaintext output backend

## Exclude
- Full troff device model
- PostScript/PDF/binary device backends
- Vendor-specific macro ecosystems outside scoped fixture corpus

## Feature → Fixture Mapping
- Tokenization + request lines → `groff-token-001`
- Escape handling → `groff-escape-001`
- `.de/.am` macro expansion → `groff-macro-001`
- `.nr/.ds` state behavior → `groff-state-001`
- Flow formatting → `groff-flow-001`

## Contamination-Control Checklist
- [x] Behavior-first scope defined without copying implementation code
- [x] Required outputs are artifacted under `results/reports/`
- [x] Acceptance gates stated explicitly
- [x] Scope limits recorded (include/exclude) to avoid hidden expansion
