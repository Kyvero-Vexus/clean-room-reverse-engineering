# SOP: Clean-Room Reverse Engineering (CRRE)

Version: 1.0  
Status: Operational baseline  
Owner: CRRE Program Lead

> This SOP is a process control document for lawful interoperability-focused work.

---

## 1) Purpose

Define a repeatable process to produce independently implemented compatibility behavior while minimizing legal and provenance risk.

## 2) Scope

Applies to projects where functionality/protocol/API behavior of a target system is being reproduced for interoperability.

## 3) Role model (mandatory)

- **A-Team (Analysis / potentially tainted)**
  - Acquires lawful observations, traces, and behavioral evidence.
  - Authors implementation-agnostic functional specs.
- **B-Team (Implementation / must remain clean)**
  - Implements only from approved specs, public docs, and test artifacts.
  - No access to disassembly artifacts or raw reverse-engineering notes.
- **C-Team (Compliance + Verification / independent)**
  - Enforces policy, audits provenance, and signs release readiness.

No contributor may serve in both A and B for the same module.

---

## 4) Entry criteria (before any technical work)

A CRRE effort may begin only if all are true:

1. Interoperability objective is explicitly documented.
2. Target/jurisdiction/contract constraints are documented.
3. A/B/C role roster and ACL map are approved.
4. Taint declarations are signed.
5. Artifact repository structure is provisioned and access-tested.

---

## 5) Workflow stages and gates

## Stage 0 — Intake and legal-purpose framing

Required artifacts:
- `CRRE-INTAKE` record (template)
- Risk assumptions memo
- Initial no-go list

Gate 0 approval:
- Program Lead + Compliance Lead

## Stage 1 — Observation and evidence capture (A-Team)

Allowed activities:
- Public documentation review
- Black-box behavior experiments
- Trace captures
- Decompilation/disassembly only when documented as necessary and allowed

Required logging per activity:
- Actor, timestamp, objective, legal-purpose note, artifact hash/location

Outputs:
- Observation log
- Trace corpus
- Draft behavior notes

Gate 1 approval:
- C-Team checks sufficiency + scope minimization

## Stage 2 — Functional spec creation (A-Team)

Rules:
- Specs must describe behavior and contracts, not source expression.
- No copied code fragments from target materials.

Outputs:
- Clause-based functional spec
- Clause IDs (e.g., `CRRE-SPEC-NET-012`)

Gate 2 approval:
- C-Team expression-hygiene review + traceability completeness

## Stage 3 — Conformance suite design (A + C)

Rules:
- Every spec clause must map to at least one test.
- Differential tests should include success and failure behaviors.

Outputs:
- Test inventory with IDs (e.g., `CRRE-TST-NET-044`)
- Clause→test traceability matrix

Gate 3 approval:
- C-Team test adequacy sign-off

## Stage 4 — Clean implementation (B-Team)

Rules:
- B-Team works from approved spec+test outputs only.
- Every PR/commit must cite spec and test IDs.

Outputs:
- Implementation code
- Design notes and rationale

Gate 4 approval:
- CI traceability checks pass
- C-Team provenance spot review pass

## Stage 5 — Verification and release readiness (C-Team)

Rules:
- Must run full conformance suite and retain logs.
- Must resolve or explicitly defer deviations with risk acceptance.

Outputs:
- Verification report
- Compliance report
- Release recommendation

Gate 5 approval:
- Compliance Lead + Program Lead

---

## 6) Artifact classes

- **Class A:** raw reverse-engineering artifacts (A-only)
- **Class S:** approved functional specs (A/C write, B read)
- **Class T:** test suites and logs (A/C write, B read)
- **Class I:** implementation artifacts (B write, C read)
- **Class R:** release evidence bundle (C custodian)

---

## 7) Access control baseline

- Separate repos or logical stores by artifact class.
- Enforce write/read boundaries via ACL, not policy text alone.
- Require SSO identity and immutable audit logs for privileged access changes.

---

## 8) Required metadata in development workflow

Each implementation PR must include:

- Spec references: one or more `CRRE-SPEC-*`
- Test references: one or more `CRRE-TST-*`
- Provenance statement: independent implementation rationale
- Exposure attestation checkbox

PRs missing this metadata must fail CI.

---

## 9) Contamination controls

Hard controls:
- No A↔B direct technical handoff outside approved templates.
- No B-Team access to A-Team raw artifacts.

Soft controls:
- Quarterly contamination training.
- Red-team review of borderline modules.

If exposure occurs, execute `RUNBOOK-contamination-response.md` immediately.

---

## 10) Review cadence

- Weekly: traceability and ACL drift review
- Monthly: contamination risk audit
- Per release: evidence bundle generation and checklist sign-off

---

## 11) Exit criteria for each release

A release is eligible only if:

1. All required clauses/tests are mapped.
2. CI traceability policy passes.
3. Compliance report has no unresolved critical findings.
4. Evidence bundle is complete and signed.

---

## 12) Minimal RACI

- Program Lead: accountable for scope and gates
- A-Team Lead: responsible for evidence + specs
- B-Team Lead: responsible for clean implementation
- Compliance Lead: accountable for process integrity
- Legal liaison (if assigned): consulted on high-risk steps

---

## 13) Practitioner-informed guardrails

- Decide NDA/contract posture before technical work (Samba lesson).
- Assume line-by-line scrutiny on sensitive low-level code (ReactOS lesson).
- Treat audits as a normal delivery track, not PR response theater.
