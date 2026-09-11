# Evidence Contract

The machine-readable contract lives in `schemas/finding.schema.json`, which is
generated from the vocabularies in `scripts/auditkit.py`. That script is the
enforcing implementation; this file explains the intent behind the rules and is
not a second definition of them.

## Why a contract

Prose instructions like "cite the line number" are not enforceable. A finding
record either has a resolvable citation or it does not, and a script can tell the
difference in milliseconds. Everything below exists so that a second, independent
agent can replay the reasoning chain without trusting the first one.

## Required on every actionable finding

| Field | Why |
|---|---|
| `id` | Stable across passes. Never reused, never renumbered. |
| `fingerprint` | Derived, not authored. See `references/fingerprinting.md`. |
| `audited_commit` | A finding without a commit is unverifiable a week later. |
| `component`, `platform` | Multi-surface products need per-surface attribution. |
| `finding_class`, `category` | Drives which mappings are required (see below). |
| `title`, `severity`, `priority`, `confidence`, `epistemic`, `status`, `effort` | Closed vocabularies, validated. |
| `locations[]` | `file`, `line_start`, `line_end`, `verified_at`, optional `symbol` and `excerpt_sha256`. |
| `evidence[]` | At least one entry. |
| `reachability` | `status` plus `entry_point` and `caller_chain` where claimed. |
| `reproduction` | `status`, `expected`, `observed`, and a `procedure` when reproduced. |
| `impact`, `root_cause` | Root cause is the mechanism, not a restatement of the symptom. |
| `remediation.strategy` | What to change, without pre-empting the remediation skill's design phase. |
| `verification` | `procedure`, `expected_evidence`, `level`. This is what closes the finding later. |

## Findings without a line number

Some real findings have no location — no CI pipeline, no SBOM, no test for a
critical path. Those require an `absence` evidence entry carrying the search that
would have found the thing:

```json
{"type": "absence",
 "search_command": "find . -name '*.yml' -path '*workflows*' -o -name '.gitlab-ci.yml'",
 "ref": ".audit/evidence/ci-search.txt",
 "excerpt": "0 results"}
```

Without it, "X is missing" is unfalsifiable. The validator rejects a finding that
has neither a location nor absence evidence (rule F023).

## Class-aware mappings (this is the part most audit templates get wrong)

A single oversized schema invites invented values. The mappings block is
**conditional**:

- `finding_class` in `security`, `privacy`, `supply_chain` → at least one CWE is
  required (F041), because a weakness taxonomy genuinely applies.
- Any other class → a CWE is *not* required, and mapping one anyway raises a
  warning (F042). A wrong default value is worse than an empty field. Use
  `Not Applicable`.
- `epss` may only carry a number when `cve` contains a CVE (F044). EPSS is the
  probability that a *published vulnerability* is exploited in the wild; it means
  nothing about a first-party defect that has no CVE.
- `kev` may only be true when `cve` contains a CVE (F046). CISA KEV is a catalog
  of known-exploited CVEs, not a property of your source code.
- `cvss` is either a full object with a `vector` (F048, F049), the literal
  `"Not Scored — Insufficient Evidence"`, or `"Not Applicable"`. A score without
  a vector is a number someone made up. When metrics had to be assumed, list them
  in `assumed_metrics` so a reader can disagree with the assumption instead of
  with the number.

## Regulatory findings

See `references/regulatory-applicability.md`. In short: applicability is a
separate, explicitly recorded judgement, the rationale is mandatory, and
compliance verdict language is rejected outright (F057).

## Severity, confidence, exploitability, priority

Four axes, never collapsed:

- **Severity** — consequence if it happens.
- **Confidence** — how sure we are it exists as described.
- **Exploitability** — how hard it is to trigger. Where a CVE exists this can be
  informed by EPSS/KEV; where it does not, it is a reasoned statement, not a score.
- **Priority** — what to do first, which also weighs business context and effort.

`Potential` confidence on a `Critical` severity finding is a legitimate and
common combination. Collapsing it either way — reporting it as Critical/Confirmed
or downgrading it to Medium because you are unsure — is a reporting failure.
Priority may diverge from severity, but only with a `priority_rationale` (F062).

## Verification and closure

`verification.procedure` is written at discovery time, before anyone is invested
in the fix. It is what the remediation skill later executes to prove closure.
A finding reaches `VERIFIED_FIXED` only with a `fix_record` reference (F058) —
source code changing is not evidence that a defect is gone.
