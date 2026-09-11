# Phase 6 — Build and Targeted Tests

**Goal:** confirm the change compiles and that the test written for it fails
before and passes after.

## 6.1 Build

Same command safety model as the audit: read-only flags, no dependency
resolution changes, no build-file edits to make something work.

```bash
<build command> 2>&1 | tee .audit/evidence/BUG-014-build.log
```

Record `build_result` from the same vocabulary the audit uses: `Passed`,
`Passed with warnings`, `Partial`, `Failed`, `Not Executed`, `Blocked`,
`Not Applicable`. A build that could not run is `Not Executed`, and the pass
stops there — you cannot verify a fix you could not build.

## 6.2 Prove the new test is real

Run the new regression test **against the baseline commit** as well as the patch:

```bash
git stash push --keep-index -- <changed files>   # only with the user's agreement
```

Safer, and the default: check out the baseline into a temporary worktree.

```bash
git worktree add /tmp/baseline <baseline_commit>
# copy the new test in, run it there, expect FAIL
git worktree remove /tmp/baseline
```

A regression test that passes on the unfixed code tests nothing. Record both
results in `targeted_tests.baseline_result` and `targeted_tests.result`.

## 6.3 Run the targeted suite

The new test plus every existing test covering the blast radius from phase 3.
Record names, counts, and the artifact path — not just "tests pass".

## Exit gate

- [ ] Build result recorded with evidence
- [ ] New test fails on the baseline and passes on the patch
- [ ] Targeted tests pass, with names recorded
- [ ] No test disabled, skipped, or weakened to get here
