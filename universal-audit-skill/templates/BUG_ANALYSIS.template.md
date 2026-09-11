# BUG ANALYSIS — {{PROJECT_NAME}}

> Analysis document. No source code was modified as part of this audit.
> Last pass: {{AUDIT_DATE}} · commit `{{COMMIT}}` · changes this pass: <summary>
> Validation: <PASS | PASS_WITH_LIMITATIONS | FAIL_VALIDATION | BLOCKED> —
> see `.audit/validation-result.json`
>
> If validation failed, this line is replaced by:
> **DRAFT — VALIDATION FAILED.** N validation errors are unresolved. Do not act
> on this document until `.audit/validation-result.json` reports PASS.

## 1. Document Control

| Field | Value |
|---|---|
| Repository | {{PROJECT_NAME}} |
| Branch | {{BRANCH}} |
| Commit | {{COMMIT}} |
| Working tree | clean / dirty (N modified files) |
| Audit date | {{AUDIT_DATE}} |
| Audit tier | T1 Deep / T2 Targeted / T3 Survey — <justification> |
| Auditor roles | Senior engineer, QA, application security, architect, DevSecOps |
| Platforms | {{PLATFORMS}} |
| Scope | <what was covered> |
| Out of scope | <what was not, and why> |
| Build environment | <toolchain versions actually observed> |
| Standards used | {{STANDARDS_SET}} — versions and verification status in §19 |
| Findings ledger | `.audit/findings.jsonl` (schema 2.0) — the source of truth for this document |
| Validation result | `.audit/validation-result.json` |
| Known limitations | <no runtime environment, no build consent, sampling rule, etc.> |

## 2. Executive Summary

Three to six paragraphs, no bullet padding. Cover: overall health; whether the
build and tests ran and what happened; finding counts by severity; the single
largest risk and why; where technical debt concentrates; what could not be
verified; and the readiness verdict with its reasoning.

Do not describe the product as production-ready without evidence for that claim.

| Severity | Count | Of which Confirmed |
|---|---|---|
| Critical / P0 | | |
| High / P1 | | |
| Medium / P2 | | |
| Low / P3 | | |
| Informational / P4 | | |

## 3. Platform and Architecture Overview

Detected components table (from Phase 1), system map (Mermaid), data flows,
trust boundaries, critical paths, external dependencies, and the state machines
that matter.

## 4. Threat Model Summary

Assets, actors, entry points, trust boundaries, STRIDE/LINDDUN highlights, and
the worst credible outcome. This is what calibrates every severity below.

## 5. Audit Methodology

What was done: static inspection (which paths, how sampled), build and test
execution, linters and analyzers with versions, dependency analysis, security
review, runtime verification performed, runtime verification **not** performed,
and research sources.

## 6. Build and Test Results

| Check | Command | Result | Evidence | Notes |
|---|---|---|---|---|

Results are limited to: Passed · Passed with warnings · Partial · Failed ·
Not Executed · Blocked · Not Applicable.

## 7. Severity and Confidence Model

State the model in use (see `references/severity-and-confidence.md`) so a reader
can audit the audit.

## 8. Findings

Repeat this block per finding.

---

### BUG-001 — <specific, falsifiable title>

| | |
|---|---|
| Fingerprint | `<16 hex, computed — see references/fingerprinting.md>` |
| Severity | Critical / High / Medium / Low / Informational |
| Priority | P0–P4 (+ rationale if it diverges from severity) |
| Confidence | Confirmed / Highly Likely / Potential / Needs Runtime Verification |
| Exploitability | prose; EPSS/KEV only where a CVE applies |
| Epistemic | Fact / Inference / Assumption |
| Status | CANDIDATE … VERIFIED_FIXED (see references/severity-and-confidence.md) |
| Category | <functional, security, concurrency, lifecycle, resource, performance, UX, a11y, build, supply chain, …> |
| Component / platform | <from Phase 1> |
| Affected versions/environments | |
| Standard mappings | ASVS v5.0.0-x.y.z · MASWE-00xx · CWE-xxx · OWASP A0x:2025 — CWE required for security/privacy/supply-chain classes only |
| CVSS | vector + score, or `Not Scored — Insufficient Evidence`, or `Not Applicable` |
| EPSS / KEV | `Not Applicable` unless the finding maps to a real CVE |
| ISO/IEC 25010:2023 | <characteristic → subcharacteristic> |
| Sonar quality | Reliability / Security / Maintainability / Security hotspot |
| Location | `path/to/file.ext:LINE` (verified {{AUDIT_DATE}}) |
| Introduced by | commit `<hash>` if determinable, else Unknown |

**Description** — what is wrong, precisely.

**Evidence**

```lang
// path/to/file.ext:LINE
<minimal excerpt, secrets redacted>
```

Plus command output, log, or analyzer hit, with its location under `.audit/evidence/`.

**Reachability** — the caller chain from a real entry point, or a statement that
it could not be established.

**Preconditions** — what must be true for this to occur.

**Reproduction Steps** — numbered, deterministic. For `Needs Runtime Verification`
findings, this is the verification procedure and the expected evidence instead.

**Expected Result** / **Actual Result**

**Impact** — for the user, the operator, the business, and (where relevant)
safety. Be concrete about blast radius.

**Root Cause** — the design or implementation reason, not a restatement of the symptom.

**Recommended Fix** — specific and lifecycle-aware. Say what to change and what
to be careful about. Do not propose a fix that ignores the concurrency or
lifecycle constraints that caused the bug.

**Regression Risk** — what else touches this code and could break.

**Required Tests** — named tests that must exist before this is closed.

**Definition of Done** — measurable acceptance criteria.

**Effort** — XS / S / M / L / XL.

**Ledger record** — `.audit/findings.jsonl`, id `BUG-001`. If this section and the
ledger disagree, the ledger is right and the validator will say so.

---

## 9. Findings Requiring Runtime Verification

Same block format, plus: why it cannot be settled statically, the environment and
instrumentation needed, the test scenario, and the expected evidence.

## 10. Security Assessment Matrix

| Domain / control group | Standard ref | Applicable | Status | Evidence | Findings | Remaining tests |
|---|---|---|---|---|---|---|

`Pass` requires positive evidence.

## 11. Privacy Assessment

Data inventory, flows, LINDDUN highlights, log leakage, third-party transmission,
retention and deletion, and gaps against the applicable regulation. Gaps, not
verdicts.

## 12. ISO/IEC 25010:2023 Quality Matrix

| Characteristic | Current condition | Evidence | Main gaps | How to measure | Priority |
|---|---|---|---|---|---|

Use the 2023 taxonomy, including Safety where it applies.

## 13. Code Quality Summary (Sonar-style)

Reliability risks · security hotspots · maintainability · complexity hotspots ·
duplication · dead code · technical-debt hotspots ranked by
complexity × churn × criticality · test coverage (measured or `Not Measured`) ·
proposed quality gate for new code.

## 14. Dependency and Supply-chain Risks

| Dependency | Version in lock | Latest verified | Risk | Advisory (CVE/GHSA) | KEV/EPSS | Breaking-change risk | Recommendation |
|---|---|---|---|---|---|---|---|

Plus: lockfile and pinning status, SBOM status, build provenance, CI trust
issues, and any regulatory deadline that applies.

## 15. Test Coverage Gaps

| Critical flow | Existing test | Gap | Recommended test | Level | Priority |
|---|---|---|---|---|---|

## 16. Prioritized Remediation Plan

**Immediate (before the next build)** — Critical/High blockers.
**Short term (1–2 sprints)** — reliability, security, testability.
**Medium term (1–3 months)** — architecture, observability, automation.
**Long term** — redesign and structural change.

Per item: id, owner role, dependencies, effort, risk reduction, validation method.

## 17. Release Recommendation

One of: `DO NOT RELEASE` · `INTERNAL TESTING ONLY` · `CONTROLLED PILOT` ·
`CONDITIONALLY READY` · `READY FOR REVIEWED SCOPE`.

State the reasoning, the unresolved blockers, and the conditions that would change
the verdict.

## 18. False Positives and Rejected Hypotheses

What was suspected, what was checked, and why it did not hold. This prevents the
next audit from re-litigating the same ground.

## 19. References

| Source | Publisher | Version / date | URL | Accessed | Verification | Type |
|---|---|---|---|---|---|---|

`Verification` is `Verified` (checked against the publisher during this audit),
`Unverified` (carried from prior knowledge), or `Unreachable`.

## 20. Validation Record

| | |
|---|---|
| Gate command | `python3 scripts/quality-gate.py --repo . --audit .audit --report BUG_ANALYSIS.md` |
| Verdict | |
| Errors / warnings | |
| Blocked checks | |
| Validation exceptions | rule id, rationale, who approved |

An audit with no validation record has not been validated. Say `NOT EXECUTED`
rather than leaving this section empty.
