# Phase 0 — Preflight

**Goal:** a clean, reversible starting point, with consent that was actually given.

## 0.1 Confirm the request

Remediation modifies source code. Confirm explicitly:

- Which finding id (one, not a list).
- Which branch to work on. Default: a new branch `fix/<BUG-ID>` from the current
  HEAD. Never commit directly to a protected or shared branch.
- Whether the user wants a commit at the end, or just a working-tree change.
- Whether tests may run (CONTROLLED_EXECUTION consent, same model as the audit).

If the user asked to "fix everything", pick the highest-priority finding, do one
pass, show the result, and ask before continuing. A batch of unreviewed patches
is not a favour.

## 0.2 Capture the baseline

```bash
git rev-parse HEAD                  # baseline_commit — goes in the fix record
git branch --show-current
git status --porcelain | tee /tmp/fix-pre.txt | wc -l
```

If the tree is dirty, stop and ask. The user's uncommitted work may be in the
same file you are about to edit, and untangling that afterwards is not possible.
Never stash, reset, or clean on their behalf.

## 0.3 Write the rollback plan first

Before touching anything, write down how to undo it: the baseline commit, the
branch to delete, any generated artifact to remove, any migration to reverse.
See `references/rollback-rules.md`. Writing it afterwards means writing it under
pressure, which is when it gets written badly.

## 0.4 Record consent

Fix-record fields: `consent.requested_at`, `consent.granted_by`,
`consent.scope` (the finding id), `consent.may_commit`, `consent.may_run_tests`.

## Exit gate

- [ ] One finding id agreed
- [ ] Working tree clean, or dirty state explicitly accepted by the user
- [ ] Branch created from a recorded baseline commit
- [ ] Rollback plan written
- [ ] Consent recorded
