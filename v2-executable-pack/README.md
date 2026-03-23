# Clean-Room Reverse Engineering — Executable Pack (v2)

This folder turns the v1 strategy writeup into a project-executable operating pack.

## What this pack contains

1. `SOP.md`  
   Project-specific standard operating procedure for clean-room reverse engineering.
2. `RUNBOOK-contamination-response.md`  
   Incident playbook for contamination allegations or exposure events.
3. `CI-TRACEABILITY-POLICY.md`  
   Enforceable traceability policy and CI gating rules.
4. `EVIDENCE-BUNDLE-SCHEMA.md`  
   Counsel-ready evidence package structure and retention model.
5. `templates/`  
   Fill-in forms and templates for intake, taint declarations, spec clauses, and incident reports.
6. `ci/`  
   Example CI scripts to enforce provenance metadata and spec/test traceability.

---

## Intended outcomes

- Make independent creation defensible.
- Reduce contamination risk and ambiguity.
- Preserve legal-purpose and necessity evidence.
- Make audits routine instead of emergency-only.

---

## Implementation order (recommended)

1. Adopt `SOP.md` and assign actual people to A/B/C roles.
2. Wire the CI controls from `CI-TRACEABILITY-POLICY.md`.
3. Put templates into your issue/PR workflow.
4. Run one tabletop contamination drill using `RUNBOOK-contamination-response.md`.
5. Build and test a release evidence bundle using `EVIDENCE-BUNDLE-SCHEMA.md`.

---

## Notes

- This is an engineering governance package, **not legal advice**.
- Jurisdiction-specific counsel should review your first real deployment.
