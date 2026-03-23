# oy96 complex target charter v2

- target: groff-lite subset
- bounded scope: parser/request subset + deterministic text output only
- exclusions: full macro package ecosystem, font/device backends
- compatibility criteria: fixture parity on bounded corpus, deterministic ordering, stable exit statuses
- risk controls: behavior-first specs, contamination audit log, traceability matrix
- go/no-go: proceed only if bundle automation + adversarial gate artifacts remain green
