# Phase 1 — Ingest the Finding

**Goal:** load the finding from the machine-readable ledger and establish its
scope before forming any opinion about the fix.

## 1.1 Load it

Prefer `.audit/findings.jsonl`. Use `BUG_ANALYSIS.md` only when no ledger exists,
and say so in the fix record — a report-only source loses the fingerprint, the
verification procedure, and the regression surface, all of which this pipeline
depends on.

```bash
grep '"id": "BUG-014"' .audit/findings.jsonl | python3 -m json.tool
python3 <audit-skill>/scripts/validate-findings.py --findings .audit/findings.jsonl
```

## 1.2 Refuse the ones you should refuse

| Condition | Action |
|---|---|
| `status: CANDIDATE` | Return to the audit for verification. Not fixable yet. |
| Validation errors on the record | Return it. A malformed finding cannot be verified as fixed. |
| `confidence: Potential` with no reproduction procedure | Ask the audit to confirm it first, or treat phase 2 as the confirmation step and record the result honestly. |
| `status: FALSE_POSITIVE` or `WONT_FIX` | Do not fix. Ask what changed. |
| No `verification.procedure` | Stop. Without it there is no way to prove closure. |

## 1.3 Carry forward

From the record: `id`, `fingerprint`, `audited_commit`, `locations`,
`reproduction`, `verification`, `remediation.strategy`,
`remediation.regression_surface`, `blocks_features`.

Note whether `audited_commit` matches HEAD. If the code has moved since the
audit, re-locate the defect by fingerprint and symbol rather than by line number,
and record that the line moved.

## 1.4 Set the scope

Declare, before reading further:

- **Primary file** — where the root cause lives.
- **Allowed additional files** — with a reason each. Empty is the good default.
- **Out of scope** — everything else, explicitly.

This declaration is what phase 5 is measured against. Writing it now, before you
have seen how tempting the surrounding code is, is the entire point.

## Exit gate

- [ ] Finding loaded from the ledger and validating
- [ ] Status is `VERIFIED_FINDING` or later
- [ ] Verification procedure present and executable
- [ ] Scope declared in writing
- [ ] Status advanced to `READY_FOR_FIX`
