# Phase 8 — Regression

**Goal:** confirm the fix did not break something else.

## 8.1 Scope the run

Minimum: every test covering the blast radius from phase 3. Preferred: the full
suite, if it runs in reasonable time. Record which you ran — "regression passed"
means nothing without its scope.

```bash
<test command> 2>&1 | tee .audit/evidence/BUG-014-regression.log
```

## 8.2 Compare against the baseline

A suite with pre-existing failures needs a baseline run, or you will attribute
someone else's broken test to your patch — or worse, dismiss a real regression as
pre-existing.

```bash
git worktree add /tmp/baseline <baseline_commit>
# run the suite there, record the failure set
git worktree remove /tmp/baseline
```

Record `regression.baseline_failures` and `regression.current_failures`. The
delta is what matters.

## 8.3 Beyond the test suite

The suite covers what someone thought to test. Also consider, where relevant:

- Old persisted data read by the new code, and new data read by an old client.
- Configuration written before the change.
- Performance on the changed path, if it is hot.
- Behaviour under restart, offline, and partial failure.
- The other platforms in a hybrid product — a fix in shared code lands everywhere.

## 8.4 If something regressed

Do not patch the regression on top. Revert the fix, return to phase 3 or 4, and
design an approach that does not cause it. Stacking a second fix onto a failing
first is how a two-line change becomes an incident.

## Exit gate

- [ ] Regression scope recorded
- [ ] Baseline failure set established
- [ ] No new failures, or each accepted in writing by the user
- [ ] Data, config and cross-platform compatibility considered
- [ ] Status advanced to `REGRESSION_PASSED`
