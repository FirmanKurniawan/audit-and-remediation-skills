# Verification Rules

## What each gate requires

| Gate | Requires | Recorded in |
|---|---|---|
| Reproduction | The defect observed before any change, with an artifact | `reproduction_before` |
| Build | Build command run, result from the shared vocabulary | `build_result` |
| Targeted test | New test **fails on the baseline** and passes on the patch | `targeted_tests.baseline_result`, `targeted_tests.result` |
| Runtime verification | The *same* procedure as reproduction, re-run | `verification_after` |
| Regression | Suite run with a baseline failure set to compare against | `regression` |
| Re-audit | Delta audit no longer derives the finding | `re_audit` |

## The same-procedure rule

`verification_after.command` must be the command from
`reproduction_before.command`. Not a similar one, not an improved one. Changing
the procedure between before and after is the most common way a fix gets falsely
closed — the new procedure passes because it measures something else.

If the procedure genuinely needs to change (it was wrong, or the fix changed the
interface it used), then re-run the *new* procedure against the baseline too, so
before and after are still comparable. Record both.

## The baseline-failing test rule

A regression test that passes on the unfixed code tests nothing. Run it against
the baseline commit — a `git worktree` is the safe way — and record
`targeted_tests.baseline_result`. It must be `FAIL`.

This catches the two most common fake tests: one that asserts something already
true, and one that exercises a path the defect never touched.

## Result vocabulary

`PASS` · `FAIL` · `BLOCKED` · `NOT_EXECUTED` · `INCONCLUSIVE`

- `PASS`/`FAIL` require an artifact path. A result nobody can re-read is not
  evidence (FX009).
- `NOT_EXECUTED` may not carry an observation. If you observed something, it
  executed (FX010).
- **`NOT_EXECUTED` never becomes `PASS`.** Not after review, not because the code
  obviously works now, not because the environment was unavailable and the
  deadline was not.
- `INCONCLUSIVE` is a real answer. Say what would settle it.

## Timing-dependent defects

Non-reproduction is weak evidence for a race. Record the iteration count and the
conditions, and match or exceed the reproduction run:

> Did not reproduce in 500 iterations under the same 5% packet loss and 4-way
> contention that reproduced it 47/500 times before the patch.

That is a claim someone can check. "Seems fine now" is not.

## Static-only findings

A missing header, a hardcoded secret, an absent authorization check: the
"reproduction" is a deterministic observation, and verification is the same
observation flipping.

```bash
grep -n "usesCleartextTraffic" app/src/main/AndroidManifest.xml
```

Legitimate before-and-after evidence, provided both runs use the identical
command and both artifacts are kept.

## What closure actually requires

`VERIFIED_FIXED` needs all of:

1. `reproduction_before.result == FAIL` (or an approved waiver)
2. `verification_after.result == PASS`
3. `build_result` in `Passed` / `Passed with warnings`
4. `targeted_tests.result == PASS`, with a failing baseline
5. `regression_result == PASS`, or every new failure accepted in writing
6. A delta re-audit that no longer derives the finding

Short of that, record the highest status actually reached — `FIX_IMPLEMENTED`,
`VERIFICATION_PASSED`, `REGRESSION_PASSED` — and say what is outstanding. An
honest partial status is useful. A fabricated `VERIFIED_FIXED` poisons the ledger
for everyone who reads it later.

## Re-audit independence

The re-audit runs the audit skill's pipeline against the new commit; it does not
ask the remediation agent whether the fix worked. If it still derives the
finding, at the same fingerprint or as a near-duplicate, the fix is incomplete
regardless of what phase 7 reported. That disagreement is information: usually it
means the symptom was fixed and the mechanism was not.
