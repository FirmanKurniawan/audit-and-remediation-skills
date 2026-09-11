# Phase 11 — Validation and Quality Gate

**Goal:** decide whether this audit is complete, using a script rather than the
agent's own opinion of its own work.

An audit is not finished because the documents were written. It is finished when
the validator says the documents and the ledger are mutually consistent, the
citations resolve against the real repository, and no rule in
`references/evidence-contract.md` is violated.

## 11.1 Run the gate

```bash
python3 scripts/quality-gate.py \
  --repo . --audit .audit \
  --report BUG_ANALYSIS.md \
  --product PRODUCT_FEATURE_ANALYSIS.md \
  --out .audit/validation-result.json
```

The gate runs, in order: findings load → schema and semantic rules → evidence and
line-reference verification against the working tree → duplicate detection →
report/ledger reconciliation → manifest and command-safety rules → secret-leakage
scan of the generated artifacts.

Individual checks can be run alone while iterating:
`scripts/validate-findings.py`, `scripts/verify-evidence.py`,
`scripts/verify-line-references.py`, `scripts/detect-duplicate-findings.py`,
`scripts/validate-final-report.py`, `scripts/validate-manifest.py`.

## 11.2 Verdicts

| Verdict | Meaning | What to do |
|---|---|---|
| `PASS` | No errors, no warnings, no blocked checks | Publish the reports. |
| `PASS_WITH_LIMITATIONS` | No errors; warnings or blocked checks present | Publish, and copy every blocked check into Known Limitations. |
| `FAIL_VALIDATION` | At least one error | Reports get the banner below and are not presented as final. |
| `BLOCKED` | Three or more checks could not run | The audit could not be validated; say so instead of implying it passed. |

On `FAIL_VALIDATION`, prepend to both documents, as the first line:

```
> **DRAFT — VALIDATION FAILED.** N validation errors are unresolved. Do not act
> on this document until `.audit/validation-result.json` reports PASS.
```

## 11.3 The rule that matters most

**Fix the finding, never the evidence.** When the validator reports that a line
citation does not resolve, the correct response is to re-read the file and
correct or withdraw the finding. Editing `excerpt_sha256`, widening a line range,
or deleting the failing record to make the gate green destroys the only property
that makes this audit reproducible. A withdrawn finding goes to the
rejected-hypotheses section with the reason.

If a rule is genuinely wrong for a project, record an exception in
`.audit/manifest.json` under `validation_exceptions` with a rationale and the
rule id. Exceptions appear verbatim in the report. They are visible decisions,
not silent suppressions.

## 11.4 Report the verdict

The terminal summary from Phase 10 must state the verdict, the error and warning
counts, and every blocked check. Never describe an audit as complete while
`.audit/validation-result.json` says otherwise, and never state a verdict without
having run the gate — if it could not run, say `NOT EXECUTED` and why.

## Exit gate

- [ ] `scripts/quality-gate.py` actually executed this session
- [ ] `.audit/validation-result.json` written
- [ ] Verdict reported honestly, including blocked checks
- [ ] `FAIL_VALIDATION` ⇒ both documents carry the DRAFT banner
- [ ] No evidence field edited to satisfy a check
