# Rollback Rules

Write the rollback before the change, not after. Afterwards means under pressure,
which is when it gets written badly or not at all.

## What a rollback plan contains

1. **Baseline commit** — recorded in phase 0, before anything moved.
2. **Exact commands** to restore it, for both the uncommitted and committed case.
3. **Artifacts to remove** — build output, generated files, migrations applied.
4. **Side effects to reverse** — schema changes, feature flags flipped, caches
   to invalidate, config written outside the repository.
5. **What cannot be rolled back** — anything already sent, published, or acted
   on downstream. Name it explicitly; that is what makes the change worth extra
   care in the first place.

## Standard cases

Uncommitted, still in the working tree:

```bash
git checkout <baseline_commit> -- <the files you changed>
git status --porcelain      # confirm nothing else moved
```

Committed on a fix branch:

```bash
git switch <original-branch>
git branch -D fix/BUG-014
```

Already merged:

```bash
git revert <fix_commit>     # a new commit, never a history rewrite
```

Never `git reset --hard`, never `git clean -fd`, never a force push. Those are
prohibited in both skills for the same reason: they destroy work you did not
create and cannot restore.

## Irreversible operations

Some things do not roll back. Before doing any of them, stop and ask:

- Database migrations that drop or transform data
- Rotated credentials (rotation is usually correct — it is just not reversible)
- Published packages, pushed tags, released artifacts
- Messages sent, webhooks fired, payments moved
- Deleted files not tracked by version control

If a fix requires one, it is not a remediation pass any more; it is a change with
an operational plan, and it needs the user's explicit decision and a maintenance
window.

## Verify the plan is still true

At closeout, re-read the rollback procedure against what actually happened. Plans
written in phase 0 go stale — the change touched a file the plan did not
anticipate, or a migration got added in phase 5. A rollback procedure that
describes a fix that no longer exists is worse than none, because someone will
trust it.

## Partial rollback

Do not partially revert a fix to keep "the good parts". Either the fix stands or
it comes out whole. Half a patch is an untested state that nobody designed, and
it will be attributed to the original finding when it breaks.
