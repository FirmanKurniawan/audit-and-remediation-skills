# Fix a Single Finding

Short form, for when the pipeline is already understood and one specific finding
needs closing.

---

Fix **{{FINDING_ID}}** from `.audit/findings.jsonl`. One finding only.

Work these gates in order and stop at the first that fails:

1. **Preflight** — clean tree (ask if dirty), baseline commit recorded, branch
   `fix/{{FINDING_ID}}`, rollback plan written before any edit.
2. **Ingest** — load the record; refuse it if status is `CANDIDATE`, if it fails
   validation, or if it has no verification procedure. Declare scope: the primary
   file, allowed extras with reasons, everything else out.
3. **Reproduce** — run the recorded procedure, capture the artifact. If it does
   not reproduce, stop and report that instead of fixing on faith.
4. **Root cause** — the mechanism in one paragraph, plus callers and dependents.
5. **Plan** — files, expected diff shape, interface and compatibility impact,
   the regression test you will add. Written before the first edit.
6. **Patch** — minimal. No reformatting, renaming, suppressions, or dependency
   changes. Add the test.
7. **Build and test** — the new test must fail on the baseline commit and pass on
   the patch.
8. **Verify** — re-run the identical reproduction command. `FAIL` means not fixed.
9. **Regress** — suite run against a baseline failure set.
10. **Close** — fix record at `.audit/fixes/{{FINDING_ID}}.json`, validated;
    delta re-audit; ledger updated; rollback re-checked.

Report at the end: what changed and where, why the root cause is gone, what
proves it, what regression coverage ran, what is still unverified, how to roll
back, and any candidate findings you found and **did not** fix.

If any gate fails, say which one, record the highest status actually reached, and
stop. Do not proceed on the assumption that the next gate will make up for it.
