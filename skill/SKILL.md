---
name: cleanroom-reverse-engineering
description: "Run lawful clean-room reverse engineering programs with strict role separation, provenance controls, and audit-ready evidence bundles. Use for interoperability-focused reimplementation work."
metadata:
  openclaw:
    emoji: "🧼"
---

# Clean-Room Reverse Engineering Skill

This skill operationalizes clean-room reverse engineering (CRRE) as an enforceable process, not just a coding style.

## Mode Selection

- Use `cleanroom-reverse-engineering-quickstart` for low-risk/small-scope projects.
- Use `cleanroom-reverse-engineering-strict` for high-risk/high-scrutiny projects.
- If unsure, default to **strict**.

## Auto-Router (5 yes/no questions)

Answer these in order:

1. Is the target in a high-sensitivity domain (kernel, firmware, BIOS, crypto, security-critical runtime)?
2. Is there known or possible contamination history (prior exposure, leaked-source risk, past allegation)?
3. Is legal exposure medium/high (commercial deployment against a major vendor, cross-jurisdiction constraints, likely dispute surface)?
4. Is contributor surface broad (more than 3 contributors, external contributors, or high turnover)?
5. Is scope narrow with low risk (single component, short timeline, black-box/public-doc-heavy path)?

Routing rule:
- If **Q1/Q2/Q3/Q4 = yes** → use `cleanroom-reverse-engineering-strict`.
- Else if **Q5 = yes** → use `cleanroom-reverse-engineering-quickstart`.
- Else → use `cleanroom-reverse-engineering-strict`.

> **Not legal advice.** Use legal counsel for jurisdiction-specific approval.

---

## When to Use

✅ Use this skill when the task involves:
- Reimplementing behavior/protocols/APIs for compatibility/interoperability.
- Reverse engineering where contamination risk is non-trivial.
- Work that may require legal/process defensibility later.

❌ Do **not** use this as-is when:
- You already have a direct license/spec permission path that avoids RE.
- The request is generic debugging with no reverse engineering.
- The user asks for unlawful bypassing/exfiltration (decline).

---

## Non-Negotiable Rules

1. **Interoperability purpose must be explicit.**
2. **Team wall is mandatory:**
   - A-Team = analysis/spec
   - B-Team = clean implementation
   - C-Team = compliance/verification
3. **No A/B role overlap** for the same module.
4. **No raw reverse-engineering artifacts into implementation lanes.**
5. **Every implementation change must trace to spec + tests.**
6. **Contamination suspicion triggers immediate incident runbook.**

---

## Canonical Source Pack

Use the v2 pack produced from prior research as source-of-truth templates:

- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/SOP.md`
- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/RUNBOOK-contamination-response.md`
- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/CI-TRACEABILITY-POLICY.md`
- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/EVIDENCE-BUNDLE-SCHEMA.md`
- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/templates/`
- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/ci/`

If these are missing, recreate them before proceeding.

---

## Execution Workflow (Mandatory)

## Phase 0 — Intake and Go/No-Go

Create CRRE intake record with:
- objective (must be interoperability/compatibility),
- target component scope,
- jurisdictions,
- contract/NDA constraints,
- anti-circumvention risk notes,
- initial risk register.

**Gate:** Stop unless objective + legal/process scope is explicit.

## Phase 1 — Team Topology + Access Controls

Set up A/B/C separation:
- separate repos/folders/channels,
- explicit ACL boundaries,
- taint declarations signed.

**Gate:** No technical work before boundaries are enforceable.

## Phase 2 — Lawful Observation (A-Team)

Prioritize lowest-risk sources first:
1. public docs,
2. black-box behavior traces,
3. only then deeper RE where necessary and allowed.

Record legal necessity for each activity.

**Gate:** C-Team approves observation scope minimization.

### Optional accelerator: Supermodel structural extraction

When external upload is allowed for the target repo, A-Team may use:
- `supermodeltools-codegraph` skill
- dependency/call/domain/impact outputs

Use only as structural evidence inputs for specs/tests. Do not treat API output as a substitute for contamination controls.

## Phase 3 — Functional Specs (A-Team)

Produce clause-based behavior specs:
- inputs/outputs/state/error semantics,
- edge cases,
- version deltas,
- test vectors,
- option/flag behavior matrix (explicitly include suppression/pass-through semantics where applicable),
- stateful stream lifecycle semantics (especially terminal/end-of-input flush behavior).

Expression hygiene:
- no copied code fragments,
- no proprietary expression leakage.

**Gate:** C-Team signs off expression hygiene + completeness.

## Phase 4 — Conformance Suite (A + C)

Build test inventory linked to spec clauses.
- normative tests,
- differential tests,
- negative tests,
- regression tests.

**Gate:** every spec clause has at least one test.

## Phase 5 — Clean Implementation (B-Team)

Implement from approved spec+tests only.
Every PR/commit must include:
- `Spec-Refs: CRRE-SPEC-*`
- `Test-Refs: CRRE-TST-*`
- provenance statement
- exposure attestation

**Gate:** CI traceability policy must pass.

## Phase 6 — Compliance Verification (C-Team)

Run:
- conformance suite,
- provenance spot checks,
- role-boundary audit,
- exception review.

**Gate:** no unresolved critical compliance findings.

## Phase 7 — Evidence Bundle + Release

Generate counsel-ready bundle using schema:
- governance,
- role/access records,
- observation logs,
- specs,
- conformance outputs,
- implementation provenance,
- audits/incidents,
- checksums/signatures.

**Gate:** release blocked unless bundle is complete.

---

## Required Artifacts Checklist

- [ ] CRRE intake form
- [ ] A/B/C roster + taint register
- [ ] ACL export evidence
- [ ] legal necessity log
- [ ] spec index + spec clauses
- [ ] test index + traceability matrix
- [ ] PR/commit provenance metadata
- [ ] compliance report
- [ ] incident register (even if empty)
- [ ] signed evidence bundle manifest

---

## Contamination Response (Immediate)

If contamination is suspected:
1. freeze affected modules,
2. preserve evidence snapshots,
3. open incident report,
4. isolate blast radius,
5. re-spec + reimplement with clean contributors,
6. publish remediation evidence.

Use:
- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/RUNBOOK-contamination-response.md`

---

## CI Enforcement Baseline

Adopt these checks:
- PR metadata validator (`Spec-Refs`, `Test-Refs`, provenance, attestation),
- commit footer validator,
- ID integrity against spec/test indexes,
- branch protection requiring compliance review.

Reference implementations:
- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/ci/validate_pr_traceability.py`
- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/ci/validate_commit_footers.sh`
- `/home/slime/info/clean-room-reverse-engineering/v2-executable-pack/ci/github-action-crre-traceability.yml`

---

## Minimal Command Sequence (Bootstrap)

```bash
# In target repo root
mkdir -p crre/{templates,ci}

# Copy baseline templates
cp /home/slime/info/clean-room-reverse-engineering/v2-executable-pack/templates/* crre/templates/
cp /home/slime/info/clean-room-reverse-engineering/v2-executable-pack/ci/* crre/ci/

# Add canonical indexes (initial)
cat > crre/spec-index.yaml <<'YAML'
spec_ids: []
YAML

cat > crre/test-index.yaml <<'YAML'
test_ids: []
YAML

cat > crre/traceability-matrix.yaml <<'YAML'
links: []
YAML
```

---

## Deliverable Standard

When this skill is used successfully, output should include:
- explicit role assignment,
- gates passed/failed,
- artifact locations,
- unresolved risks,
- next gate owner.

No “done” claim without evidence bundle readiness.
