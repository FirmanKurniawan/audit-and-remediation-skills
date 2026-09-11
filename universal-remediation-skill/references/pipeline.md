# Canonical Remediation Pipeline

Single source of truth. Ten stages, numbered 0 through 9. **One finding per
pass.** Do not restate this table elsewhere.

| Phase | File | Owns |
|---|---|---|
| 0 | `phases/00-preflight.md` | Consent, clean baseline, branch, rollback plan |
| 1 | `phases/01-ingest-finding.md` | The validated finding record and its fix scope |
| 2 | `phases/02-reproduce.md` | `reproduction_before` evidence |
| 3 | `phases/03-root-cause.md` | The mechanism, and the blast-radius map |
| 4 | `phases/04-fix-design.md` | The fix plan, reviewed before any edit |
| 5 | `phases/05-implement.md` | The minimal patch |
| 6 | `phases/06-build-test.md` | Build result and targeted test result |
| 7 | `phases/07-runtime-verification.md` | `verification_after` evidence |
| 8 | `phases/08-regression.md` | Regression result across the blast radius |
| 9 | `phases/09-closeout.md` | Fix record, delta re-audit, final status |

## Gates

Each phase ends in a gate. A gate that fails stops the pass — it does not
downgrade into a warning.

| After | Cannot proceed unless |
|---|---|
| 0 | Consent recorded, baseline commit captured, rollback written |
| 1 | Finding validates and is `VERIFIED_FINDING` or later |
| 2 | Defect reproduced, or a signed-off `reproduction_waiver` exists |
| 3 | Root cause stated as a mechanism, callers and dependents enumerated |
| 4 | Fix plan recorded *before* the first edit, with the expected diff shape |
| 5 | Patch confined to the planned scope; extra files justified in writing |
| 6 | Build passes and targeted tests pass |
| 7 | The original reproduction no longer reproduces, with an artifact |
| 8 | Regression suite passes, or every failure is explained and accepted |
| 9 | Fix record validates and the delta re-audit no longer derives the finding |

## Loop

One finding per pass. When the pass closes, return to phase 0 for the next
finding with a fresh baseline. Batching is what turns a two-line fix into an
unreviewable diff and makes an unrelated regression impossible to attribute.
