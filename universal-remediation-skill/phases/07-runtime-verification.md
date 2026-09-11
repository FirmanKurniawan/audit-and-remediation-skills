# Phase 7 — Runtime Verification

**Goal:** re-run the original reproduction. This is the gate that decides whether
the defect is actually gone.

## 7.1 Re-run exactly what reproduced it

Same command, same environment, same preconditions, same iteration count as
phase 2. Changing the procedure between before and after invalidates the
comparison — and is the most common way a fix gets falsely closed.

```bash
<same repro command as phase 2> 2>&1 | tee .audit/evidence/BUG-014-after.log
echo "exit=$?" >> .audit/evidence/BUG-014-after.log
```

Record `verification_after`: `result`, `command`, `exit_code`, `expected`,
`observed`, `artifact_path`, `artifact_sha256`, `iterations`.

## 7.2 Interpreting the result

| `reproduction_before` | `verification_after` | Meaning |
|---|---|---|
| FAIL | PASS | The defect is gone by the same measurement that found it. Proceed. |
| FAIL | FAIL | **Not fixed.** The finding stays open. Return to phase 3. |
| FAIL | INCONCLUSIVE | Not fixed. Refine the procedure. |
| FAIL | BLOCKED / NOT_EXECUTED | Verification could not run. Status stops at `FIX_IMPLEMENTED`. |
| PASS (waived) | PASS | Weak evidence — say so in the record and rely on the re-audit. |

`NOT_EXECUTED` never becomes `PASS`. Not because the code obviously works now.

## 7.3 Timing-dependent defects

Run at least as many iterations as phase 2, under at least the same contention.
Record the number. "Did not reproduce in 500 iterations under the same load"
is a claim someone can check; "seems fine now" is not.

## 7.4 Verify the fix, not the test

Confirm the observation actually depends on the patch. If the reproduction
stopped failing because the environment changed, the log will usually show it —
different timings, a different code path, a missing precondition. Look before
concluding.

## Exit gate

- [ ] Same procedure re-run, artifact captured
- [ ] Result recorded honestly
- [ ] Iteration count matched or exceeded for timing defects
- [ ] `FAIL` ⇒ finding remains open and the pass returns to phase 3
- [ ] `PASS` ⇒ status advanced to `VERIFICATION_PASSED`
