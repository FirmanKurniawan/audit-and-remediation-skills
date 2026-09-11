# Remediation Rules

## The minimal patch principle

Change the smallest thing that removes the root cause. Everything below follows
from that.

**Why it is not just tidiness.** A minimal patch is reviewable, its regression
surface is knowable, and when something breaks next week the diff either explains
it or exonerates it. A patch that fixes a bug *and* renames three functions *and*
reformats a file cannot do any of those things. The refactor is not free; it is
paid for in review time and in attribution ambiguity, and it is paid by someone
else.

## What a fix may contain

- The change that closes the mechanism identified in phase 3.
- The regression test that would have caught the defect.
- A comment where the *reason* for the change is non-obvious.
- Whatever is strictly required to keep the build and existing tests green.

## What a fix may not contain

| Not allowed | Instead |
|---|---|
| Opportunistic refactoring | Record it as a candidate finding |
| Reformatting, reindentation, import reordering | Match the surrounding style; leave the rest |
| Renaming anything the fix does not require | Separate change, separate review |
| Dependency upgrades | Only when the finding *is* the dependency, at the minimum resolving version, with breaking changes named |
| Fixing the second bug you noticed | Candidate finding, back to the audit |
| Broadening a `catch`, widening a type, adding `# noqa` / `eslint-disable` / `@SuppressWarnings` | Fix the defect; silencing the detector is not remediation |
| Deleting or skipping a failing test | Understand why it fails first |
| Changing CI, containers, or infrastructure | Justify it explicitly or take it out |
| "Improving" a working module because a different design is cleaner | Propose it; do not smuggle it |

## Scope declaration

Phase 1 declares the primary file, any allowed additional files with a reason
each, and everything out of scope. Phase 5 is measured against that declaration.
Declaring scope *before* reading the surrounding code is the whole point — it is
easy to be disciplined about a file you have not yet been tempted by.

`scripts/validate-fix.py` rejects a record where files beyond the first carry no
justification (MP001), where documentation, styling, asset, CI or container files
appear without a reason (MP002, MP004), and where a dependency manifest or
lockfile changed without a rationale (MP003).

## Interfaces and compatibility

Before changing any signature, schema, route, event shape, or stored format, ask
who else depends on the current shape — including older clients still in the
field and data written by the old code. If the answer is "someone", the fix is a
compatibility event and needs a plan, not a patch. Say so and get a decision.

Code that relies on the *wrong* behaviour is the trap here. Fixing a lenient
parser can break every caller that has quietly been feeding it malformed input
for two years. That is often still the right fix — but it is a decision for the
user, made in the open.

## Security fixes specifically

- Fix the class, not the instance, when the same sink appears in several places
  in the same component — but list each occurrence in the scope declaration, and
  do not wander into other components.
- Do not add a blocklist where a safe API exists. Escaping a known bad character
  is not equivalent to binding a parameter.
- Do not fix an authorization gap in the UI. Fix it where the decision is
  enforced.
- Assume the vulnerability is known. If a secret was exposed, the fix includes
  rotation, and rotation is the user's action — say so explicitly rather than
  quietly removing the value from the file and calling it done.

## Dependency findings

When the finding *is* a vulnerable dependency:

- Move to the minimum version that resolves the advisory, not the newest.
- Name the breaking changes between the current and target version. If you cannot
  determine them, say so and stop; an unexamined major upgrade is a larger risk
  than the advisory in many cases.
- Record the transitive effect: one bump can move a dozen other packages.
- `dependency_change_rationale` is mandatory in the fix record.

## When the right fix is too big

Some findings need a redesign — a state machine with no single source of truth, a
missing abstraction, an authorization model that does not exist. Do not attempt
it inside a remediation pass. Write the finding up as a foundation item, propose
the design, and let the user schedule it. A half-done redesign shipped as a bug
fix is worse than the bug.

## Commit hygiene

One finding per commit. The message states the finding id, the mechanism, and
what proves it is gone:

```
fix(api): bind LIKE parameter in note search (BUG-014)

Query was assembled by concatenation, so a metacharacter in `q` changed the
parse. Bound the term instead.

Verified: repro in .audit/evidence/BUG-014-before.log no longer reproduces
(after.log). Added test_search_binding, which fails on the baseline commit.
```
