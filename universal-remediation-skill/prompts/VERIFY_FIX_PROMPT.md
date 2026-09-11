# Verify a Fix

For checking someone else's fix — a human's, another agent's, or your own from a
previous session. Verification only: **do not modify code in this mode.**

---

Verify the fix recorded at `.audit/fixes/{{FINDING_ID}}.json` against the
repository at its current commit.

## 1. Read the record, not the fix

Load the fix record and the original finding. Note the claimed status, the
baseline commit, the changed files, and both run results. Form your expectation
of what should be true *before* reading the diff — reading the patch first
anchors you to the author's reasoning.

## 2. Check the arithmetic of closure

- Did the defect reproduce before the change? (`reproduction_before.result == FAIL`)
- Is `verification_after.command` the *same* command? A changed procedure
  invalidates the comparison.
- Do both results have artifacts, and do the artifacts say what the record says?
  Read them; do not trust the summary field.
- Did the new regression test fail on the baseline commit? Re-run it there if the
  record does not show it.
- Are `build_result`, `targeted_tests.result` and `regression_result` consistent
  with the claimed status?
- Is there a delta re-audit, and does it still derive the finding?

```bash
python3 scripts/validate-fix.py --fix-record .audit/fixes/{{FINDING_ID}}.json --repo .
```

## 3. Check the patch itself

- Does it close the **mechanism**, or only the symptom that was visible?
- Does it introduce a new failure mode on the error path?
- Does it hold under concurrency, restart, and partial failure?
- Does it change any public interface, stored format, or behavioural contract
  without saying so?
- Is anything in the diff unrelated to the finding?
- Does it add a suppression instead of a fix?

## 4. Re-run what you can

Run the reproduction procedure yourself. An independent execution is worth more
than a re-read of someone else's log.

## 5. Verdict

One of:

- `CONFIRMED_FIXED` — every gate holds and you re-ran the verification yourself.
- `FIXED_UNVERIFIED` — the patch looks correct but a gate could not be
  independently re-run. Say which.
- `NOT_FIXED` — the defect still reproduces, or a gate fails. The finding
  reopens.
- `FIXED_WITH_CONCERNS` — the defect is gone but the patch introduces risk. Name
  it.

State what you executed and what you only read. Do not report a gate as verified
because the record says it passed — the record is the claim under examination.
