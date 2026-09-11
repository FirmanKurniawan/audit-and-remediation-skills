# Universal Remediation Skill

The fixing half of a two-skill pair. It consumes findings produced by
[`universal-audit-skill`](../universal-audit-skill) and repairs them **one at a
time**, under gates that make "fixed" mean something.

**v1.0.0** · requires `universal-audit-skill >= 2.0.0`

## Why it is a separate skill

An agent that both finds and fixes has an incentive problem: the cheapest way to
close a finding is to decide it was never real. Splitting the roles means the
thing that closes a finding is a verification procedure written *before* anyone
was invested in the fix, and closure is confirmed by a re-audit that re-derives
the finding independently.

It also keeps consent honest. Auditing is read-mostly; remediation rewrites the
user's code. Those deserve different conversations.

## Pipeline

Ten stages, defined once in `references/pipeline.md`, one finding per pass:

```
0 preflight → 1 ingest → 2 reproduce → 3 root cause → 4 fix design
→ 5 implement → 6 build & test → 7 runtime verification → 8 regression → 9 closeout
```

Each stage ends in a gate. A failed gate stops the pass — it does not degrade
into a warning.

## Lifecycle

```
CANDIDATE → VERIFIED_FINDING → READY_FOR_FIX → REPRODUCED → FIX_IN_PROGRESS
→ FIX_IMPLEMENTED → VERIFICATION_PASSED → REGRESSION_PASSED → RE_AUDIT_PASSED
→ VERIFIED_FIXED
```

A failed verification returns the finding to its previous open state. It never
closes by default, by timeout, or by argument.

## The gate

```bash
python3 scripts/validate-fix.py --fix-record .audit/fixes/BUG-014.json
```

Catches, deterministically:

- `VERIFIED_FIXED` while the original failure still reproduces
- a fix claimed without the defect ever having been reproduced
- `PASS`/`FAIL` results with no artifact, and `NOT_EXECUTED` carrying an observation
- more than one changed file with no written justification (scope creep)
- documentation, styling, CI or container files swept into a code fix
- dependency manifests or lockfiles touched without a rationale
- patches that add a suppression (`# noqa`, `eslint-disable`, `@SuppressWarnings`)
  instead of fixing the defect
- a missing rollback procedure
- a new defect fixed opportunistically inside the pass

It imports its vocabularies from the audit skill's `scripts/auditkit.py` when the
sibling directory is present, so the two cannot drift apart.

## Outputs

```
.audit/fixes/<BUG-ID>.json     the fix record (schemas/fix-record.schema.json)
.audit/fixes/<BUG-ID>.patch    the diff actually applied
.audit/evidence/<BUG-ID>-*.log before / after / build / test artifacts
FIX_LOG.md                     human-readable running log
```

## Non-negotiables

1. One finding at a time. No batching, no "while I was in there".
2. No reproduction, no fix.
3. Minimal patch: no refactoring, no reformatting, no dependency upgrades unless
   the finding *is* the dependency.
4. A code change is not a fix. Verification, regression, and re-audit are.
5. New defects are recorded as candidates and handed back to the audit.
6. `NOT_EXECUTED` never becomes `PASS`.

## Layout

```
SKILL.md                 entry point, preconditions, hard rules
references/pipeline.md   canonical stage list and gates
references/              remediation, verification and rollback rules
phases/                  the ten stages
schemas/                 fix-record contract
scripts/validate-fix.py  the deterministic gate
templates/               fix record and fix log
prompts/                 master fix, single finding, verify-only
```

## License

MIT.
