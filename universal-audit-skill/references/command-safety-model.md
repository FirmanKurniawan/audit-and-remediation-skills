# Command Safety Model

Consent is necessary and not sufficient. A user who says "yes, run the build" has
not agreed to have their working tree rewritten by a formatter that a build
script happens to invoke. This model classifies every command, records repository
state around anything that executes project code, and detects modification after
the fact.

## Classes

**SAFE_READ_ONLY** — cannot modify the repository or execute project code.
Run freely. `git status`, `git log`, `git diff`, `git rev-parse`, `cat`, `grep`,
`find`, `ls`, `wc`, reading a lockfile, `scripts/detect-stack.sh`.

**CONTROLLED_EXECUTION** — executes project or third-party code and may write
build output. Requires consent, a pre-state snapshot, and a post-state
comparison. Builds, test runs, type checks, linters in report mode, dependency
resolution against a lockfile, SBOM generation.

**REQUIRES_CONSENT** — read-only in the repository but has an external effect or
cost: network calls, advisory lookups, registry queries, container pulls. Consent
recorded separately from execution consent, since a user may allow one and not
the other.

**PROHIBITED** — never run during an audit, under any consent. Recording one as
executed is a validation error (M010).

| Never run | Why |
|---|---|
| `git reset --hard`, `git checkout -- .`, `git clean -fd` | Destroys the user's uncommitted work |
| `git rebase`, `git push`, history rewrites | Changes shared history from an analysis task |
| `rm -rf <path>` | No audit step needs to delete anything |
| `npm audit fix` and equivalents | Silently rewrites dependencies and lockfiles |
| `<pm> install --save`, `<pm> update`, `-u`, `pip install -U` | Dependency drift mid-audit invalidates every finding |
| formatter in write mode, linter in fix mode, codemods | Rewrites source the audit is supposed to describe |
| migrations, seeders, `terraform apply`, `kubectl apply` | Side effects outside the repository |
| anything writing outside the repo, `.audit/`, or the system temp dir | Out of scope by construction |


Two rules that catch most accidents: **read-only flags only** — never `--fix`,
`--write`, `-u`, `--latest`; and **never edit a build file to make a tool run**.
A missing tool is a finding, not an obstacle to route around.

## Pre-execution record

Before any CONTROLLED_EXECUTION command:

```bash
git -C "$REPO" rev-parse HEAD
git -C "$REPO" branch --show-current
git -C "$REPO" status --porcelain | tee /tmp/pre.txt | wc -l
sha256sum /tmp/pre.txt
```

Store as `repo_state.before` with `commit`, `branch`, `dirty_files`,
`tracked_hash`. Record the working directory and the environment assumptions
(which env vars, which toolchain versions, whether the network was reachable).

## Post-execution comparison

Repeat the snapshot into `repo_state.after` and diff:

- New files under a known build output directory (`dist/`, `build/`, `target/`,
  `node_modules/`, `.gradle/`, `__pycache__/`) → expected. Note them and move on.
- **Any modification to a tracked source, manifest, lockfile, or CI file** → set
  `source_modified: true`, list `modified_paths`, and stop. This is the failure
  the model exists to catch. Report it to the user immediately, explain which
  command did it, and do not continue until they decide. Never revert it
  yourself — reverting is a destructive operation on work you did not create, and
  the user's uncommitted changes may be in the same file.

The validator requires `repo_state.before` and `after` on every
CONTROLLED_EXECUTION record (M012) and requires a written rationale whenever
`source_modified` is true (M013).

## Result vocabulary

`Passed` · `Passed with warnings` · `Partial` · `Failed` · `Not Executed` ·
`Blocked` · `Not Applicable`. Nothing else, and nothing except
`Not Executed`, `Blocked`, and `Not Applicable` may be recorded without captured
evidence (M011).

`Not Executed` means it did not run. It never becomes `Passed` because the code
"looked fine".

## Timeouts and interruption

Time-box every controlled execution. A command killed by a timeout is `Partial`
with the partial output retained, never `Failed` — the distinction matters,
because `Failed` implies the project is broken and `Partial` implies the audit
ran out of budget.

## Untrusted repositories

When auditing code you did not write, prefer a container or a throwaway VM.
Install scripts, test fixtures, and build plugins all execute arbitrary code with
your credentials. If no isolation is available, say so in the report's
limitations and consider declining controlled execution entirely — a static-only
audit with an honest limitation beats a compromised workstation.
