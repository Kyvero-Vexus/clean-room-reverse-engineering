# CI Traceability Policy for CRRE

Version: 1.0  
Applies to: all repositories participating in clean-room implementation

---

## 1) Policy objective

Block merges that lack defensible provenance metadata linking implementation changes to approved specs and conformance tests.

---

## 2) Required metadata model

## 2.1 PR-level required fields

Each PR must include:

- `Spec-Refs:` list of `CRRE-SPEC-*` IDs
- `Test-Refs:` list of `CRRE-TST-*` IDs
- `Provenance-Statement:` short independent-creation rationale
- `Exposure-Attestation:` checkbox confirming no prohibited exposure for scope

### Example

```
Spec-Refs: CRRE-SPEC-NET-012, CRRE-SPEC-NET-019
Test-Refs: CRRE-TST-NET-044, CRRE-TST-NET-052
Provenance-Statement: Implemented from approved spec clauses and black-box tests.
Exposure-Attestation: [x] I have not used prohibited source artifacts for this scope.
```

## 2.2 Commit-level required markers

For non-trivial commits in CRRE scope:

- `Spec-Refs:` footer
- `Test-Refs:` footer

---

## 3) CI gates (must fail closed)

1. **Metadata gate**
   - Fails if PR body lacks any required CRRE fields.
2. **Identifier integrity gate**
   - Fails if referenced IDs do not exist in canonical spec/test inventories.
3. **Coverage gate**
   - Fails if changed files in CRRE-scoped paths have no spec refs.
4. **Traceability gate**
   - Fails if referenced tests are not present or not executed in CI.
5. **Policy gate**
   - Fails if contributor taint status conflicts with role boundaries.

---

## 4) Repository conventions

Expected canonical files:

- `crre/spec-index.yaml` (master list of valid spec IDs)
- `crre/test-index.yaml` (master list of valid test IDs)
- `crre/traceability-matrix.yaml` (spec↔test mapping)
- `crre/taint-register.yaml` (role and exposure status)

---

## 5) Branch protection requirements

- Require passing status checks for all CRRE gates.
- Require at least one Compliance/C-Team reviewer on CRRE-labeled PRs.
- Disable direct pushes to protected branches.

---

## 6) Exception process

Exceptions must be rare and documented.

Required for exception approval:
- Written reason,
- Risk statement,
- Compensating controls,
- Expiration date,
- Compliance Lead approval.

No permanent exceptions for traceability fields.

---

## 7) Auditability requirements

- CI logs for CRRE gates retained minimum 24 months.
- Test artifacts and reports retained with hash references.
- Merge metadata must preserve PR body and approval history.

---

## 8) Suggested implementation

See `ci/` folder in this pack:
- `validate_pr_traceability.py`
- `validate_commit_footers.sh`
- `github-action-crre-traceability.yml`

---

## 9) Rollout plan

1. Week 1: warn-only mode for metadata gate.
2. Week 2: fail-close metadata + identifier gates.
3. Week 3: enable coverage + traceability gates.
4. Week 4: enforce branch protections and compliance reviewer rule.
