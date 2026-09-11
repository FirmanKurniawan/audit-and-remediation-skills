# Phase 5 — Implement the Minimal Patch

**Goal:** make the smallest change that removes the root cause, and nothing else.

## 5.1 Rules while editing

- Touch only the files in the plan. Every additional file needs a written
  justification in the fix record, and the validator flags unjustified extras.
- Do not reformat. If the file's style is inconsistent, match the surrounding
  code — the fix's diff must show the fix, not a whitespace storm.
- Do not rename anything the fix does not require.
- Do not fix the second bug you notice. Record it as a candidate.
- Keep the change reviewable: a reviewer should see the mechanism from phase 3
  being closed, and nothing else.
- Add the regression test named in the plan. A fix without a test is a fix that
  comes back.

## 5.2 Comments

Add a comment only where the *reason* is non-obvious — a bound that looks
arbitrary, an ordering that matters, a compatibility shim. Do not annotate the
patch with "fixed BUG-014"; that belongs in the commit message and the fix
record, and it rots in the source.

## 5.3 Capture the diff

```bash
git diff > .audit/fixes/BUG-014.patch
git diff --stat
```

Record `changed_files` and `patch_summary`. Check the stat output against
`expected_diff_shape` from the plan. If it is materially larger, stop and explain
why before continuing — that divergence is the single best early signal that a
fix is going wrong.

## 5.4 Self-review before the build

- Does the change close the mechanism, or only the symptom you could see?
- Does it introduce a new failure mode on the error path?
- Does it handle the boundary cases the audit listed for this defect class?
- Would it still be correct under concurrency, restart, or partial failure?
- Is anything here unrelated to the finding? Remove it.

## Exit gate

- [ ] Patch confined to planned files, extras justified
- [ ] No reformatting, renaming, suppressions, or opportunistic changes
- [ ] Regression test added
- [ ] Diff captured and compared against the plan
- [ ] Status advanced to `FIX_IMPLEMENTED`
