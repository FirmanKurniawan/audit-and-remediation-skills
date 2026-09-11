# Severity, Confidence, Exploitability, Priority

Four axes. They are recorded separately and never collapsed into one another.
Collapsing them is how an audit becomes either alarmist (everything Critical) or
negligent (uncertainty silently downgraded to Low).

| Axis | Question | Field |
|---|---|---|
| Severity | What happens if it is real and triggered? | `severity` |
| Confidence | How sure are we it exists as described? | `confidence` |
| Exploitability | How hard is it to trigger? | prose; `mappings.epss`/`kev` only with a CVE |
| Priority | What should be done first? | `priority` (+ `priority_rationale` when it diverges) |

A `Critical` severity finding with `Potential` confidence is a normal, correct
combination. Report it as exactly that.

## Severity

Severity is about **consequence**, not about how hard it was to find or how ugly
the code is.

### Critical / P0
- Remote code execution, authentication bypass, or unauthenticated access to
  other users' data
- Credential, key, or token exposure with real reach
- Unauthorized or persistent unintended action in the physical world
  (transmission, actuation, dispensing, movement)
- Irreversible data loss or corruption
- Complete unavailability of a life-, safety-, or revenue-critical function
- Regulatory breach with immediate legal exposure

### High / P1
- Crash or hang on a primary user flow, reproducible
- Privilege escalation between roles
- Sensitive data disclosure with limited scope or requiring some access
- Silent failure of a critical function — the user believes it worked
- Broken recovery: the system cannot return to a working state without reinstall
  or manual intervention
- Major concurrency defect with observable corruption
- Repeatable ANR/freeze, or a leak that exhausts resources within a normal session

### Medium / P2
- Functional failure with a workaround the user can discover
- Resource leak that matters only in long sessions
- Incorrect state that self-corrects or is recoverable by retry
- Weak security control that requires unusual preconditions to exploit
- Significant usability or accessibility barrier
- Missing validation with no proven exploitable path

### Low / P3
- Minor defect on a rare path
- Maintainability issues with a concrete cost
- Cosmetic inconsistency, low-impact edge case
- Deprecated API still functioning

### Informational / P4
- Hardening opportunity with no current exploit path
- Documentation gaps
- Optional optimization, style, or convention

## Priority vs severity

They are different axes. A Medium defect on the signup flow of a product about to
launch may be P1. A High-severity issue in a feature behind a flag nobody has
enabled may be P2. When they diverge, say why in one line.

## Modifiers

Raise a level when: the path is unauthenticated · exploitation is trivial ·
the affected data is regulated · the failure is silent · there is no recovery ·
it affects all users · a matching CVE is in CISA KEV · it involves physical
actuation or safety.

Lower a level when: it needs physical device access · it needs an already-
compromised account with equal privilege · it is behind a disabled flag ·
a compensating control is verified · the blast radius is a single local user's
own data.

Record which modifiers you applied. Unexplained severity is unusable to a triage
team.

## Exploitability signals: CVSS, EPSS, KEV

These three are vulnerability-intelligence instruments. They apply to *published
vulnerabilities*, and applying them to a first-party source defect produces
numbers that look rigorous and mean nothing.

**CVSS** — optional, and only where the vector is defensible. Use v4.0, record the
full vector string, and list every metric you had to assume in `assumed_metrics`
so a reader can disagree with the assumption rather than with the number. Where
the metrics cannot be justified, the value is the literal string
`Not Scored — Insufficient Evidence`. A score without a vector is rejected (F048).
For local-only client defects CVSS is a poor fit; use SSVC-style reasoning in
prose instead.

**EPSS** — the probability that a *known* vulnerability is exploited in the wild.
It requires a CVE. On a finding with no CVE the value is `Not Applicable`, and
populating it anyway is rejected (F044).

**KEV** — CISA's catalog of known-exploited CVEs. Same rule: no CVE, no KEV
(F046). A KEV hit escalates priority sharply and legitimately — which is exactly
why it must not be sprinkled onto findings that have no CVE to hit.

**CWE** — required for `security`, `privacy` and `supply_chain` findings (F041),
where a weakness taxonomy genuinely applies. Not required for ordinary functional
defects, and mapping one anyway raises a warning (F042). "Improper input
validation" is not a useful label for a rounding error.

## Confidence

| Status | Meaning | Required evidence |
|---|---|---|
| `Confirmed` | Proven to exist as described | Code + reachability, or reproduced failure, or captured output |
| `Highly Likely` | Strong static evidence, one small gap | Code + partial reachability; name the gap |
| `Potential` | Pattern present, impact unproven | Code citation + explicit statement of what is unproven |
| `Needs Runtime Verification` | Cannot be settled statically | Code citation + a concrete test procedure + expected evidence |
| `False Positive` | Investigated, does not hold | The mitigating evidence — goes in the rejected-hypotheses section |
| `Not Applicable` | The control or class does not apply here | Why |

Confidence never inflates severity. A `Potential` Critical is still reported as
Critical severity with `Potential` confidence — those are separate columns, and
collapsing them is how audits become either alarmist or negligent.

## Status lifecycle

Shared by the audit and remediation skills, enforced by `scripts/auditkit.py`:

```
CANDIDATE → VERIFIED_FINDING → READY_FOR_FIX → REPRODUCED → FIX_IN_PROGRESS
→ FIX_IMPLEMENTED → VERIFICATION_PASSED → REGRESSION_PASSED → RE_AUDIT_PASSED
→ VERIFIED_FIXED
```

Side states: `REGRESSED`, `WONT_FIX` (with the accepted-risk rationale and who
accepted it), `SUPERSEDED` (requires `superseded_by`), `DUPLICATE` (requires
`duplicate_of`), `FALSE_POSITIVE`.

`CANDIDATE` means found but not yet verified — it is not fixable and does not
appear in the report's finding list. `VERIFIED_FIXED` requires a `fix_record`
reference (F058): source code changing is not evidence that a defect is gone. A
failed verification returns the finding to its previous open state; it never
becomes closed by default.

## Effort

`XS` < 0.5 day · `S` 0.5–1 day · `M` 2–3 days · `L` 4–7 days · `XL` > 1 week or
needs redesign. Effort covers fix + tests + review, not just the edit.
