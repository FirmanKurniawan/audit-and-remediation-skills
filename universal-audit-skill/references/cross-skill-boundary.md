# Cross-Skill Boundary

Two skills, one contract between them.

```
universal-audit-skill            universal-remediation-skill
─────────────────────            ───────────────────────────
READ                             READ
CONTROLLED EXECUTION             CONTROLLED EXECUTION
REPORT                           MODIFY SOURCE
                                 TEST / VERIFY
                                 RECORD THE FIX
```

## Why they are separate

An agent that can both find and fix has an incentive problem: the cheapest way to
close a finding is to decide it was not real. Separating the roles means the
thing that closes a finding is the *verification procedure written before anyone
was invested in the fix*, and the thing that confirms closure is a re-audit that
re-derives the finding independently.

It also keeps blast radius honest. An audit that silently starts editing has
changed a user's repository without the consent conversation that remediation
requires.

## Handoff: audit → remediation

The remediation skill consumes `.audit/findings.jsonl`, preferring it over
`BUG_ANALYSIS.md` when both exist — the ledger is structured, the report is a
rendering. It ingests only findings whose status is `VERIFIED_FINDING` or later
and whose record passes `scripts/validate-findings.py`. A `CANDIDATE` finding is
not fixable; it goes back to the audit for verification first.

Carried across: `id`, `fingerprint`, `audited_commit`, `locations`,
`reproduction`, `verification`, `remediation.strategy`,
`remediation.regression_surface`, `blocks_features`.

## Handoff: remediation → audit

The remediation skill writes `.audit/fixes/<BUG-ID>.json`, shaped by that skill's
fix-record schema. A finding reaches
`VERIFIED_FIXED` only when a fix record exists, its verification result is
`PASS`, and a delta re-audit no longer derives the finding. Validator rule F058
enforces the first part; the re-audit enforces the rest.

## New defects found during remediation

Record as a **candidate finding** appended to `.audit/findings.jsonl` with
`status: CANDIDATE`, `epistemic: Inference`, and evidence — then stop. Do not fix
it. Opportunistic fixing is how a one-line patch becomes a 40-file diff nobody
can review, and how an unrelated regression gets attributed to the wrong change.
The candidate is verified on the next audit pass and becomes fixable then.

The reverse is equally binding: an audit that notices an obvious one-line fix
records it in `remediation.strategy` and moves on.

## Shared vocabulary

Both skills use the same status lifecycle, the same fingerprint function, and the
same result vocabularies, all defined in `scripts/auditkit.py` in this skill. The
remediation skill imports it rather than redefining it, so the two cannot drift.
