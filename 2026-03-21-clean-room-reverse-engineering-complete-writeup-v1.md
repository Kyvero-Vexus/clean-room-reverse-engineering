# Clean-Room Reverse Engineering: Detailed Process Manual (v1)

**Date:** 2026-03-21  
**Prepared for:** strategic use in lawful interoperability-focused reverse engineering work  
**Scope:** process design, legal-risk controls, evidence architecture, historical and practitioner-informed lessons

> **Legal disclaimer:** This is an engineering-process research document, not legal advice. For real projects, counsel should review the exact jurisdiction, contracts, target technology, and anti-circumvention constraints before execution.

---

## 1) Executive Summary

Clean-room reverse engineering (CRRE) is not just “reverse engineering done carefully.” It is a **governance system** that produces a defensible claim of independent implementation.

At minimum, CRRE requires:

1. **Purpose limitation** (usually interoperability/compatibility),
2. **Separation of knowledge domains** (analysis/spec vs implementation),
3. **Artifact discipline** (traceable evidence for every step),
4. **Conformance validation** (black-box test proof), and
5. **Contamination response procedures** (for when boundaries fail).

If one of those pillars is weak, legal and reputational risk increases sharply.

---

## 2) What “clean-room” really means

### 2.1 Core pattern

A robust clean-room model uses two role partitions:

- **Analysis Team (potentially tainted):** lawfully observes target behavior and produces a functional specification.
- **Implementation Team (must remain clean):** writes new code from approved specs and public references only.

A practical third function is often essential:

- **Validation/Audit Team (independent):** verifies spec quality, implementation traceability, and contamination controls.

### 2.2 The legal intuition

In many jurisdictions, copyright protects expression, not raw functional ideas/interfaces as such. CRRE exists to create evidence that your implementation reproduces behavior, **not protected expression**.

---

## 3) Legal high-level constraints (US + EU)

## 3.1 United States (high-level)

### Copyright/fair use context

- **Sega v. Accolade (1992)** supports disassembly/intermediate copying as fair use where needed to access unprotected functional elements for compatibility.
- **Atari v. Nintendo (1992)** similarly supports reverse engineering in principle, but emphasizes that bad-faith acquisition/contamination can undercut defenses.
- **Sony v. Connectix (2000)** is a major compatibility/emulation precedent affirming fair-use room for intermediate copying during reverse engineering.

### DMCA anti-circumvention overlay

- 17 U.S.C. §1201 can create separate risk even where copyright arguments are favorable.
- §1201(f) includes an interoperability carveout, but it is narrow and purpose-bound.

**Operational implication:** Your process must prove necessity, narrow scope, and interoperability purpose at each technical step.

## 3.2 European Union (high-level)

### Software Directive (2009/24/EC)

- Interoperability decompilation is allowed only where indispensable and confined to what is necessary.
- Information gained is restricted from unrelated reuse.
- Contract clauses conflicting with Article 6 interoperability permissions are generally void.

### CJEU (SAS Institute v WPL, C-406/10)

- Functionality, programming language, and data file formats are generally not protected as expression in the same way as source/object code text.

**Operational implication:** Keep strict necessity logs and scope boundaries; capture why each reverse-engineering action was essential for interoperability.

---

## 4) End-to-end CRRE operating model

## Phase 0 — Project Charter and Gatekeeping

**Goal:** establish legal-technical scope before any analysis occurs.

**Required outputs:**
- CRRE Charter (purpose, target, interoperability objective)
- Jurisdiction assumptions memo
- Risk register (copyright, anti-circumvention, contract, trade secret)
- “No-go” criteria list

**Gate questions:**
- Is interoperability the explicit purpose?
- Are we lawful users of copies/hardware being analyzed?
- Are there contracts/NDAs that conflict with process openness?
- Is counsel sign-off needed before touching binaries/firmware?

---

## Phase 1 — Contamination Model and Team Topology

**Goal:** define who may see what, and enforce it technically.

### 4.1 Recommended roles

- **A-Team (Analysis):** reverse engineering, trace capture, protocol inference, behavior docs.
- **B-Team (Implementation):** no access to target internals/disassembly artifacts.
- **C-Team (Compliance/Audit):** enforces process and evidence quality.

### 4.2 Hard controls

- Separate repositories and ACLs.
- Separate chat channels and issue trackers.
- No direct copy/paste channel from A to B other than approved spec templates.
- Signed “taint declarations” per contributor.

### 4.3 Soft controls (still essential)

- Mandatory onboarding on contamination risk.
- Clear examples of forbidden artifacts (decompiled fragments, leaked code excerpts, line-structure mimicry examples).

**Deliverables:**
- Access matrix (person × repo × document class)
- Taint register
- Communication policy

---

## Phase 2 — Lawful Observation and Data Acquisition

**Goal:** obtain behavior evidence with minimal legal exposure.

### 5.1 Preferred data sources (lowest risk first)

1. Public vendor documentation/specs,
2. Public protocol traces/test corpora,
3. Black-box dynamic behavior experiments,
4. Static analysis/disassembly only when indispensable and allowed.

### 5.2 Evidence discipline

Every acquisition event should log:
- timestamp,
- actor,
- legal basis,
- purpose,
- expected interoperability output,
- resulting artifact hash/location.

**Deliverables:**
- Acquisition log
- Trace corpus
- Observation notebooks

---

## Phase 3 — Functional Specification Production (A-Team)

**Goal:** translate observations into an implementation-agnostic contract.

### 6.1 Spec structure

For each behavior/API/protocol unit:
- semantic description,
- inputs/outputs/types,
- state transitions,
- error conditions,
- timing/performance assumptions,
- compatibility edge cases,
- normative test vectors.

### 6.2 Expression hygiene rules

- No decompiled code snippets.
- No proprietary comments/identifiers unless independently necessary and justified.
- Prefer normalized pseudocode and state machines over language-specific imitation.

**Deliverables:**
- Versioned functional spec set
- “Expression scrub” review checklist

---

## Phase 4 — Conformance Suite Construction (A/C-Team)

**Goal:** turn spec into executable compatibility criteria.

### 7.1 Why this is critical

Conformance tests are the strongest practical proof that your team pursued behavior compatibility rather than textual copying.

### 7.2 Test taxonomy

- **Normative tests:** straight from spec requirements.
- **Differential tests:** compare target behavior vs implementation.
- **Negative tests:** malformed inputs and boundary misuse.
- **Regression tests:** preserve behavior over time.

**Deliverables:**
- Traceable test inventory (test ID ↔ spec clause)
- Baseline run logs against reference behavior

---

## Phase 5 — Clean Implementation (B-Team)

**Goal:** build independently from approved specs and tests.

### 8.1 Development constraints

- B-Team cannot access A-Team raw reverse-engineering artifacts.
- All major code decisions cite spec clauses, not target internals.
- Reviews include provenance checks (“show spec linkage”).

### 8.2 Commit protocol

Each non-trivial commit should include:
- spec section references,
- test IDs satisfied,
- implementation rationale.

**Deliverables:**
- Provenance-friendly commit history
- Implementation design notes

---

## Phase 6 — Independent Verification (C-Team)

**Goal:** validate compatibility and process integrity.

### 9.1 Verification dimensions

- functional pass/fail,
- edge-case parity,
- performance thresholds where relevant,
- process compliance (clean-room controls actually followed).

### 9.2 Audit outputs

- contamination risk findings,
- unresolved deviations,
- release recommendation.

**Deliverables:**
- Verification report
- Compliance report

---

## Phase 7 — Release Evidence Bundle

**Goal:** make defensibility portable and durable.

Create an immutable bundle containing:

- charter + legal-purpose memo,
- taint register snapshots,
- access-control exports,
- spec versions,
- test inventories + logs,
- build artifacts + hashes,
- audit reports,
- contamination incident records (if any) and remediation proof.

---

## 5) Contamination response playbook (when something goes wrong)

If contamination is suspected:

1. **Freeze** affected modules and branches.
2. **Isolate** contributors/artifacts potentially exposed.
3. **Forensic compare** with careful legal oversight where needed.
4. **Purge and re-spec** affected behavior from clean inputs.
5. **Re-implement** with unexposed contributors.
6. **Document remediation** end-to-end.

This step is expensive. Plan for it in advance.

---

## 6) Case studies and lessons

## 6.1 IBM PC BIOS clone era (Compaq/Phoenix pattern)

- Historical clean-room archetype: separated analysis/spec from implementation.
- Key lesson: organizational separation can unlock compatibility markets, but requires strong records to remain defensible over time.

## 6.2 Samba

- Practitioner reports describe shipping compatibility by wire-level observation + public information, while explicitly avoiding incompatible NDA channels.
- Key lesson: legal boundary choices are strategic architecture decisions, not admin afterthoughts.

## 6.3 Wine

- Contributor policy emphasizes clean-room constraints and strong conformance testing culture.
- Key lesson: long-lived compatibility projects survive through policy + tests + review discipline, not “heroic reverse engineering” alone.

## 6.4 ReactOS contamination controversy and audit response

- Public mailing-list disputes show how quickly trust can collapse when exposure boundaries are unclear.
- Later audit initiatives framed legal defensibility as a continuous engineering track.
- Key lesson: “clean-room” must be operationalized with ongoing governance and third-party scrutiny for sensitive components.

## 6.5 Emulation legal precedents

- Sega/Accolade and Sony/Connectix are foundational U.S. compatibility precedents.
- Key lesson: legal victories can validate approach but do not reduce process burden or litigation cost.

---

## 7) First-person practitioner takeaways (synthesized)

Recurring patterns from practitioner narratives and project docs:

1. **Refuse legal channels that poison implementation freedom** (e.g., NDA paths incompatible with open implementation).
2. **Prefer black-box and public-doc pathways first**; use higher-risk methods only when indispensable.
3. **Treat provenance as a deliverable** equal in importance to code.
4. **Assume future forensic scrutiny** of sensitive modules.
5. **Make audits routine**, not crisis-only.

---

## 8) Anti-patterns to avoid

- Single mixed team does analysis + coding with no barrier.
- Informal “trust me, I didn’t copy” documentation.
- Missing spec-to-test-to-commit traceability.
- Retroactive process justification after code already shipped.
- No incident response plan for contamination allegations.

---

## 9) Practical SOP templates

## 9.1 CRRE intake template (abridged)

- Project name:
- Interoperability objective:
- Target system/component:
- Jurisdictions in scope:
- Contractual constraints (EULA/NDA/license):
- Anti-circumvention risk notes:
- Go / No-go decision:

## 9.2 Taint declaration template (abridged)

- Contributor:
- Assigned role (A/B/C):
- Exposure disclosures (vendor source, leaks, prior NDA work):
- Acknowledgment of restrictions:
- Signature/date:

## 9.3 Spec clause template

- Clause ID:
- Behavior summary:
- Inputs:
- Outputs:
- Error handling:
- Determinism/timing notes:
- Test vectors:
- Evidence source references:

## 9.4 Commit provenance footer template

- Spec refs: CRRE-SPEC-xxx
- Test refs: CRRE-TST-yyy
- Rationale: <short statement>

---

## 10) Suggested tooling and infrastructure

- Repo segmentation: `analysis/`, `spec/`, `impl/`, `audit/` (separate ACLs where possible)
- Immutable logging: append-only logs with signing
- Artifact hashing: checksums for traces/spec snapshots/build outputs
- CI policy gates:
  - block merge without spec/test linkage
  - block merge if taint policy metadata missing
- Scheduled compliance reviews: monthly + release gates

---

## 11) 30/60/90 day rollout plan

## Day 0–30 (foundation)

- Draft charter and legal-risk map.
- Set team partitions and access controls.
- Publish contamination policy and declaration workflow.
- Pilot on one narrow interface.

## Day 31–60 (operationalize)

- Build spec template library and test taxonomy.
- Integrate traceability checks into CI.
- Run first internal compliance audit.
- Tabletop contamination-response drill.

## Day 61–90 (harden)

- Third-party review for highest-risk modules.
- Create release evidence bundle standard.
- Institutionalize recurring audits and incident playbook.
- Expand scope only after passing governance gates.

---

## 12) Source index (primary and project references)

### Legal / directive / case resources

- Sega v. Accolade (OpenJurist): https://openjurist.org/977/f2d/1510/sega-enterprises-ltd-v-accolade-inc
- Atari v. Nintendo (OpenJurist): https://openjurist.org/975/f2d/832/atari-games-corp-v-nintendo-of-america-inc
- Sony v. Connectix (opinion text mirror): https://law.resource.org/pub/us/case/reporter/F3/203/203.F3d.596.98-15840.99-15035.html
- 17 U.S.C. §1201 (Cornell LII): https://www.law.cornell.edu/uscode/text/17/1201
- EU Software Directive 2009/24/EC (EUR-Lex): https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32009L0024
- CJEU SAS Institute v WPL (C-406/10): https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62010CJ0406

### Project/process references

- Linux Journal Samba interview (Tridgell/Allison): https://www.linuxjournal.com/article/2900
- Samba history: https://www.samba.org/samba/history/
- Samba selftest README: https://github.com/samba-team/samba/blob/master/selftest/README
- Andrew Tridgell resources: https://www.samba.org/~tridge/
- Wine Developer FAQ: https://wiki.winehq.org/Developer_FAQ
- Wine README: https://raw.githubusercontent.com/wine-mirror/wine/master/README.md
- ReactOS dev mailing list (contamination discussion):
  - https://marc.info/?l=ros-dev&m=118775346131646&w=2
  - https://marc.info/?l=ros-dev&m=118775346131654&w=2
  - Audit thread: https://marc.info/?l=ros-dev&m=119018479822866&w=2

### Contextual historical references

- Clean-room design overview: https://en.wikipedia.org/wiki/Clean_room_design
- Phoenix Technologies overview: https://en.wikipedia.org/wiki/Phoenix_Technologies
- ReactOS overview: https://en.wikipedia.org/wiki/ReactOS
- Apache Harmony FAQ: https://harmony.apache.org/faq.html
- NIST SSDF (SP 800-218): https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf

---

## 13) What to do next (Session 2 recommendation)

To make this truly operational, next session should produce:

1. A **project-specific CRRE SOP** with exact role assignments and ACL map.
2. A **contamination-response runbook** tailored to your repos/tools.
3. A **traceability CI policy** (fail merges without spec/test/provenance metadata).
4. A **counsel-ready evidence bundle schema** (folder structure + required records).

That converts this writeup from strategy into execution.
