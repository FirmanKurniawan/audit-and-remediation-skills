# Phase 4 — Fix Design

**Goal:** decide what to change and write it down **before** touching an editor.

A plan written after the patch is a justification, not a plan. Recording the
expected diff shape first is what makes scope creep visible instead of gradual.

## 4.1 Consider more than one option

For anything above a trivial fix, write two or three approaches with their
trade-offs:

| Approach | Blast radius | Risk | Effort | Fixes root cause? |
|---|---|---|---|---|

Prefer the one that removes the root cause with the smallest radius. When a
larger change is genuinely correct — the state machine really does need a single
source of truth — say so, and then **stop**: that is a design change, and it goes
back to the user as a proposal, not into this pass as a patch.

## 4.2 Write the plan

Fix-record `fix_plan`:

- `approach` — one paragraph.
- `files_to_change` — exact list, matching the scope from phase 1.
- `expected_diff_shape` — roughly how many lines, and what kind of change
  (guard added, parameter bound, config value flipped, lifecycle hook moved).
- `interface_changes` — none, or exactly what and who is affected.
- `data_migration` — none, or the plan.
- `backward_compatibility` — what happens to old clients, old stored data, old
  config.
- `feature_flag` — whether the change should be gated, for anything risky.
- `tests_to_add` — the regression test that would have caught this, named.
- `rejected_alternatives` — with reasons. Useful to the reviewer, and to you in
  six months.

## 4.3 What the plan may not contain

- Reformatting, renaming, or reorganising anything the fix does not require.
- A dependency upgrade, unless the finding *is* the dependency — and then only
  the minimum version that resolves it, with the breaking changes named.
- "While I'm here" improvements. Those are candidate findings.
- Suppressions: `# noqa`, `@SuppressWarnings`, `eslint-disable`, a broadened
  `catch`, a widened type. Silencing the detector is not fixing the defect.

## 4.4 Show it before doing it

For anything above `XS` effort, show the plan to the user and wait. It is far
cheaper to disagree about the approach now than about the diff later.

## Exit gate

- [ ] Alternatives considered and the choice justified
- [ ] Plan recorded before any edit
- [ ] Interface, migration and compatibility impacts decided
- [ ] Regression test named
- [ ] User agreed, where the change is non-trivial
