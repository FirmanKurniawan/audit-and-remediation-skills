# Phase 2 — Reproduce

**Goal:** observe the defect before changing anything. This is the gate that
makes "fixed" mean something later.

## 2.1 Run the recorded procedure

Execute `reproduction.procedure` from the finding, or `verification.procedure`
where the finding was static-only. Capture everything:

```bash
<repro command> 2>&1 | tee .audit/evidence/BUG-014-before.log
echo "exit=$?" >> .audit/evidence/BUG-014-before.log
sha256sum .audit/evidence/BUG-014-before.log
```

Record `reproduction_before`: `result`, `command`, `exit_code`, `expected`,
`observed`, `artifact_path`, `artifact_sha256`, and for anything timing-dependent
the **iteration count and conditions**.

## 2.2 Result vocabulary

`FAIL` here is the good outcome: the defect reproduced, so the fix has something
to prove. Also valid: `PASS` (did not reproduce), `BLOCKED`, `NOT_EXECUTED`,
`INCONCLUSIVE`.

## 2.3 When it does not reproduce

Do not proceed to a fix on the assumption that the code is wrong anyway.

- **Race or timing defect** — increase iterations, add contention, slow the
  machine. Record how many attempts. Non-reproduction in 500 iterations is a
  data point; non-reproduction in 3 is noise.
- **Environment-dependent** — record what environment would be needed and mark
  the gate `BLOCKED`.
- **Genuinely not there** — this is a valuable result. Send it back to the audit
  as a `FALSE_POSITIVE` candidate with your evidence. Do not fix a defect that
  does not exist; the patch will be unverifiable and may cause a real one.

## 2.4 Static-only findings

Some real defects have no runtime reproduction — a missing security header, a
hardcoded secret, an absent authorization check. Their "reproduction" is a
deterministic observation:

```bash
grep -n "allowBackup" app/src/main/AndroidManifest.xml | tee .audit/evidence/BUG-014-before.log
```

That is a legitimate `reproduction_before` with `result: FAIL`, as long as the
same observation is repeated after the fix and flips.

## 2.5 Waivers

If no reproduction is possible at all, record `reproduction_waiver` with the
reason, get explicit user approval, and carry the reduced confidence through to
closeout. A waived reproduction can never produce `VERIFIED_FIXED` on its own —
the best available status is `FIX_IMPLEMENTED` plus a re-audit result.

## Exit gate

- [ ] Reproduction attempted and its artifact captured
- [ ] Result recorded with the real vocabulary, no rounding toward convenience
- [ ] Iteration count recorded for timing-dependent defects
- [ ] Status advanced to `REPRODUCED`, or the pass stopped with a waiver
