# Evidence Rules

## Accepted evidence

1. **Code citation** — `path/to/file.ext:LINE` plus an excerpt short enough to be
   fair use and long enough to show the defect. Line number verified by re-reading
   the file in the same session.
2. **Command output** — the command, its exit status, and the captured output
   stored under `.audit/evidence/`.
3. **Analyzer output** — tool name and version, rule id, and the specific hit.
4. **Log or stack trace** — with the build/commit it came from.
5. **Configuration** — the file and setting, with the value redacted if sensitive.
6. **Official documentation** — title, publisher, version, URL, access date.
7. **Reproduction** — deterministic steps that a second person could follow.
8. **Absence evidence** — for "X is missing", show the search that would have found
   it: the command, the paths searched, and the empty result. "No test file matches
   `*Auth*` under `src/` or `tests/`" is evidence; "there are no auth tests" is not.

## Not evidence

- A function or variable name that sounds dangerous
- A pattern that "usually" indicates a bug, without checking this instance
- A dependency version that is old, without an advisory or a concrete impact
- An analyzer hit that was never validated against how the code runs
- "Best practice says…" with no link to a consequence in this codebase
- A line number you did not re-read
- Anything an LLM (including you) asserted earlier in the conversation without a source

## Epistemic labels

Attach one to every substantive statement in the reports:

- **Fact** — directly observed in the repository or in captured output.
- **Inference** — a conclusion drawn from facts; state the facts it rests on.
- **Assumption** — a belief needed to proceed; state how to validate it.

Never blend them in a single unmarked sentence. In tables, put the label in its
own column or bracket it inline: `Fact:`, `Inference:`, `Assumption:`.

## Reachability requirement

A finding on unreachable code is a maintainability issue, not a defect. Before
assigning Medium or above, establish a caller chain from a real entry point
(route, handler, exported symbol, lifecycle callback, scheduled job, IPC target).
If you cannot, cap confidence at `Potential` and note the missing link.

## Redaction

Report the location and class, never the value:

> `config/production.env:14` — hardcoded database password (`Confirmed`, value redacted)

Never include: passwords, API keys, tokens, private keys, certificates, seed
phrases, connection strings with credentials, internal hostnames or IPs that are
not public, personal data, customer names, or operational identifiers.

If a secret is found in Git history, say so and recommend rotation — the value is
compromised regardless of whether the current file is clean. Do not print the
value or the exact commit content.

## Citing the standards

Every standard reference carries a version and an access date. Bad:
"violates OWASP". Good: "OWASP ASVS v5.0.0-2.1.3 (accessed 2026-09-09)".

## When you cannot prove it

Say so, in the report, in the finding itself:

> `Needs Runtime Verification` — static analysis cannot determine whether the
> callback fires after teardown because the registration is dynamic
> (`src/net/session.ts:212`). Verify by: instrumenting the callback with a
> lifecycle assertion, then killing the connection during an active request.
> Expected evidence: no callback invocation after `dispose()` is logged.

A well-described unverified hypothesis is more useful than a confidently wrong
finding, and far more useful than silence.
