---
name: universal-remediation-skill
description: >-
  Safely fixes findings produced by universal-code-audit, one finding at a time,
  under reproduction, minimal-patch, build, test, runtime and regression gates.
  Consumes .audit/findings.jsonl (preferred) or BUG_ANALYSIS.md, and writes a
  machine-readable fix record per finding. Use when the user asks to fix, patch,
  remediate, or resolve findings from an audit. It MODIFIES SOURCE CODE, so it
  never runs implicitly — it requires an explicit request and explicit consent.
license: MIT
version: 1.0.0
requires: universal-code-audit >= 2.0.0
---

# Universal Remediation Skill

The companion to `universal-code-audit`. That skill finds and reports; this one
fixes. They are separate on purpose — an agent that does both has an incentive to
decide an inconvenient finding was never real.

Read this file, then `references/remediation-rules.md`, then work the phases in
order for **one finding at a time**.

## Preconditions

Do not start until all of these hold:

1. The user explicitly asked for remediation. Being handed an audit is not a
   request to fix it.
2. A findings ledger exists. Prefer `.audit/findings.jsonl` over
   `BUG_ANALYSIS.md` when both are present — the ledger is structured, the report
   is a rendering of it.
3. The target finding's status is `VERIFIED_FINDING` or later. A `CANDIDATE`
   goes back to the audit for verification first.
4. The finding validates: `python3 <audit-skill>/scripts/validate-findings.py
   --findings .audit/findings.jsonl` reports no errors for it.
5. The working tree is clean, or the user has explicitly accepted that their
   uncommitted changes are in scope. Never stash or discard their work.
6. You know how to undo what you are about to do (`references/rollback-rules.md`).

## Hard rules

1. **One finding at a time.** No batching, no "while I was in there". Each fix
   is its own branch, its own patch, its own record, its own verification.
2. **No reproduction, no fix.** If the defect cannot be reproduced or otherwise
   demonstrated, the fix cannot be verified. Record `reproduction_waiver` with a
   reason and get explicit approval, or stop.
3. **Minimal patch.** Change the smallest thing that removes the root cause.
   No opportunistic refactoring, no reformatting, no dependency upgrades unless
   the finding *is* the dependency, no rewriting a working module because a
   different design would be cleaner.
4. **Source changes only where the finding lives.** Every file touched beyond
   the first needs a written justification in the fix record.
5. **A code change is not a fix.** `VERIFIED_FIXED` requires: the original
   reproduction no longer reproduces, targeted tests pass, regression tests pass,
   and a delta re-audit no longer derives the finding.
6. **Failed verification leaves the finding open.** It never closes by default,
   by timeout, or by argument.
7. **New defects are candidates, not side quests.** Append to the ledger with
   `status: CANDIDATE` and hand back to the audit. Do not fix them here.
8. **Never fabricate a result.** `NOT_EXECUTED` never becomes `PASS`. If the
   build could not run, say so and stop at that gate.
9. **Destructive commands stay prohibited**, exactly as in the audit skill —
   with the single, scoped exception that this skill may edit the specific source
   files a finding names, and only after its fix plan is recorded.

## Pipeline

Defined once in **`references/pipeline.md`**. Ten stages, 0 through 9, one
finding per pass.

## Lifecycle

```
CANDIDATE → VERIFIED_FINDING → READY_FOR_FIX → REPRODUCED → FIX_IN_PROGRESS
→ FIX_IMPLEMENTED → VERIFICATION_PASSED → REGRESSION_PASSED → RE_AUDIT_PASSED
→ VERIFIED_FIXED
```

Each arrow is a gate with evidence behind it. Statuses only advance on evidence;
they fall back on failure. The vocabulary comes from the audit skill's
`scripts/auditkit.py`, imported rather than redefined so the two cannot drift.

## Outputs

```
.audit/fixes/<BUG-ID>.json     the fix record (schemas/fix-record.schema.json)
.audit/fixes/<BUG-ID>.patch    the diff actually applied
.audit/evidence/<BUG-ID>-*.log before/after/build/test artifacts
FIX_LOG.md                     human-readable running log
```

Validate every record before closing:

```bash
python3 scripts/validate-fix.py --fix-record .audit/fixes/BUG-014.json
```

## Layout

- `references/pipeline.md` — the canonical stage list
- `references/remediation-rules.md` — minimal patch, scope, what never to touch
- `references/verification-rules.md` — what each gate requires
- `references/rollback-rules.md` — undo, before you need it
- `phases/` — the ten stages
- `templates/` — fix record and fix log
- `schemas/fix-record.schema.json` — the machine-readable contract
- `scripts/validate-fix.py` — the gate
- `prompts/` — master fix, single finding, verify-only
