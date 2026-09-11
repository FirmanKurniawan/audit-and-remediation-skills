# Quick Triage Prompt

For when a full audit is too heavy: a time-boxed pass that finds the things that
would embarrass you in production, without the full document set.

---

Run a **time-boxed triage** of this repository. Target: under 30 minutes of tool
work. Produce `BUG_ANALYSIS.md` only — no product document.

Do not modify source code. Read-only Git commands. No dependency installs, no
auto-fix, no build-file edits.

**Steps**

1. **Identify the stack** from build manifests and entry points — not from folder
   names. State the platforms detected and the marker file that proves each.
2. **Skim for the highest-yield classes only:**
   - Secrets in the repo or in Git history (locations only, never values)
   - Missing or client-side-only authorization on privileged operations
   - Injection sinks reachable from user input
   - Disabled TLS/certificate validation, including "debug-only" paths that ship
   - Dependencies with known-exploited advisories at their lockfile versions
   - Crash-prone paths on the primary user flow
   - Swallowed exceptions on error paths that leave broken state
   - Unbounded retry, missing timeout, or resource leak on the hot path
   - Debug artifacts, verbose logging of sensitive data, and test endpoints in release
3. **Verify before reporting.** Re-read every cited line. Establish reachability
   from a real entry point. Drop anything you cannot substantiate.
4. **Report at most 20 findings**, ranked by severity, each with:
   verified `file:line` · evidence excerpt · impact in one sentence ·
   recommended fix in two sentences · confidence · effort.
5. **List explicitly what you did not check**, so nobody mistakes this for a
   complete audit.
6. Give a one-paragraph verdict: is there anything here that blocks a release?

**Rules**

- No invented line numbers. No `Passed` for commands you did not run.
- CWE only where a weakness taxonomy applies; EPSS and KEV only with a real CVE;
  CVSS only with a defensible vector, otherwise
  `Not Scored — Insufficient Evidence`.
- Regulatory observations record applicability and a gap, never a verdict.
- No secret values in the output.
- Severity and confidence stay independent.
- If you finish early, deepen the top three findings rather than adding weak ones.
