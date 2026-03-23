# Runbook: Contamination Response

Version: 1.0  
Trigger: suspected or confirmed exposure of clean implementation path to restricted source/expression

---

## 1) Activation criteria

Activate this runbook immediately if any of the following occur:

- Contributor discloses exposure to prohibited material for an in-scope module.
- Third-party allegation of copied expression in implementation.
- Forensic indicators (structural/line-level similarity beyond plausibly independent expression).
- Policy violation: A-Team artifact found in B-Team environment.

---

## 2) Initial response (0–4 hours)

1. **Freeze** affected modules/branches and block merges.
2. **Preserve evidence** (repos, logs, chat, artifacts) in immutable snapshot.
3. **Open incident record** using `templates/contamination-incident-report.md`.
4. **Assign Incident Commander (IC)** and Compliance Owner.
5. **Enforce comms protocol**: no speculative public statements.

Output: incident severity classification + immediate containment report.

---

## 3) Containment (same day)

- Identify potentially exposed contributors and modules.
- Revoke or adjust access where needed.
- Quarantine suspect artifacts in read-only location.
- Generate “blast radius” map:
  - modules touched,
  - commits implicated,
  - tests potentially tainted,
  - downstream dependencies.

Output: containment summary approved by Compliance Owner.

---

## 4) Forensic assessment (24–72 hours)

### 4.1 Technical analysis

- Diff and structural comparison between suspect code and known prohibited references (performed under approved legal/process controls).
- Timeline reconstruction from commit and communication metadata.
- Review provenance statements in PR history.

### 4.2 Process analysis

- Which controls failed?
- Were ACL boundaries bypassed?
- Was onboarding/training incomplete?

Output: preliminary findings report with confidence levels.

---

## 5) Remediation decision tree

## Case A: No meaningful contamination found

- Document rationale.
- Lift freeze with explicit sign-off.
- Add preventive controls for identified near-misses.

## Case B: Localized contamination likely

- Revert/purge affected code paths.
- Re-spec from clean evidence inputs.
- Reimplement with unexposed B-Team contributors.
- Re-run full clause/test traceability and verification.

## Case C: Broad contamination likely

- Pause release line.
- Re-baseline module/program from last uncontaminated point.
- Consider external audit for credibility restoration.

---

## 6) Recovery criteria

Recovery requires all of:

1. Clean reimplementation completed and reviewed.
2. Full conformance suite passes.
3. Updated compliance report indicates no critical unresolved risk.
4. Incident postmortem approved by Program + Compliance leads.

---

## 7) Communications plan

Internal status updates should include:
- what is known,
- what is unknown,
- what actions are taken,
- next checkpoint time.

External communication (if needed) should be factual and minimal:
- acknowledge investigation,
- avoid legal conclusions before review,
- commit to process transparency where appropriate.

---

## 8) Post-incident hardening

Within 7 days of closure:

- Add at least one control improvement (technical gate or process update).
- Run focused training on incident root causes.
- Update SOP and templates where needed.
- Schedule targeted re-audit in 30 days.

---

## 9) Incident severity rubric

- **SEV-1:** likely broad contamination, active release impact.
- **SEV-2:** localized contamination risk, manageable scope.
- **SEV-3:** policy/process near-miss, no strong contamination evidence.

Severity determines escalation chain and response SLAs.

---

## 10) Mandatory artifacts for closure

- Final incident report
- Corrective action list + owners
- Updated taint register
- Remediation commit/test evidence
- Compliance sign-off
