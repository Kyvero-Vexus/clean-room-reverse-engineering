# Counsel-Ready Evidence Bundle Schema (CRRE)

Version: 1.0  
Purpose: define a standard folder and manifest format for release-time legal/process defensibility

---

## 1) Bundle principles

- Complete: enough artifacts to reconstruct process decisions.
- Verifiable: include hashes and immutable references.
- Traceable: connect purpose → specs → tests → implementation.
- Minimal: include what is needed, avoid irrelevant private data.

---

## 2) Folder schema

Use this structure per release:

```
crre-evidence-bundle/
  manifest.yaml
  00-governance/
    charter.md
    scope-and-objective.md
    jurisdiction-assumptions.md
    approvals/
  01-roles-and-access/
    team-roster.csv
    taint-register.yaml
    acl-exports/
    policy-acknowledgements/
  02-observation-and-analysis/
    acquisition-log.csv
    legal-necessity-log.csv
    trace-index.yaml
    notes/
  03-functional-specs/
    spec-index.yaml
    specs/
    expression-hygiene-reviews/
  04-conformance/
    test-index.yaml
    traceability-matrix.yaml
    test-results/
  05-implementation/
    commit-range.txt
    design-notes/
    provenance-footers-export.csv
  06-compliance-and-audit/
    audit-reports/
    exceptions/
    release-readiness.md
  07-incidents/
    incident-register.csv
    remediation-records/
  08-cryptographic-attestation/
    checksums.sha256
    signatures/
```

---

## 3) Minimal required files

- `manifest.yaml`
- `00-governance/charter.md`
- `01-roles-and-access/taint-register.yaml`
- `03-functional-specs/spec-index.yaml`
- `04-conformance/test-index.yaml`
- `04-conformance/traceability-matrix.yaml`
- `05-implementation/commit-range.txt`
- `06-compliance-and-audit/release-readiness.md`
- `08-cryptographic-attestation/checksums.sha256`

Bundle generation should fail if any required file is missing.

---

## 4) `manifest.yaml` required fields

```yaml
bundle_id: CRRE-BUNDLE-2026-03-21-R1
project: <project-name>
release_version: <semantic-version-or-tag>
generated_at_utc: <ISO-8601>
scope:
  objective: interoperability
  components:
    - <component-a>
jurisdictions:
  - US
  - EU
roles:
  analysis_team: [<names>]
  implementation_team: [<names>]
  compliance_team: [<names>]
hash_alg: sha256
signing:
  enabled: true
  signer: <identity>
artifacts:
  spec_index: 03-functional-specs/spec-index.yaml
  test_index: 04-conformance/test-index.yaml
  traceability_matrix: 04-conformance/traceability-matrix.yaml
  commit_range: 05-implementation/commit-range.txt
  release_readiness: 06-compliance-and-audit/release-readiness.md
```

---

## 5) Chain-of-custody recommendations

- Produce bundle from CI on protected branch/tag only.
- Generate checksums in deterministic file-order.
- Store signed bundle in immutable object storage.
- Retain prior bundle revisions; do not overwrite.

---

## 6) Retention policy baseline

- Compliance and audit reports: 7 years
- CI logs and test artifacts: 2 years minimum
- Incident records and remediation evidence: 7 years

Adjust based on counsel guidance and regulatory requirements.

---

## 7) Verification checklist (release gate)

Before release, Compliance verifies:

1. Spec/test IDs are internally consistent.
2. Commit range is complete and provenance metadata present.
3. Any exceptions are approved and unexpired.
4. Incident register has no unresolved critical entries.
5. Checksums/signatures validate.

---

## 8) Redaction model

If bundle must be shared externally:

- Preserve hash continuity wherever possible.
- Redact only sensitive personal/internal identifiers.
- Never redact fields needed to prove traceability logic.
- Include a redaction note describing what/why.
