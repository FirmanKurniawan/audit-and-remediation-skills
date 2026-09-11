# Phase 10 — Reporting

**Goal:** render the ledger into the two documents, cross-link them, and give a
short terminal summary. This phase does **not** declare the audit complete — that
is the validation gate that follows it.

## 10.1 Write the documents

Use `templates/BUG_ANALYSIS.template.md` and
`templates/PRODUCT_FEATURE_ANALYSIS.template.md`. Write to the repository root
unless the user asked for a different location.

If a document already exists:
- Preserve its finding IDs. Never renumber `BUG-`/`FEAT-` identifiers.
- Update status on existing findings (`Open`, `Fixed`, `Regressed`,
  `Won't Fix`, `Superseded`) with the commit that changed it.
- Add new findings with the next free number.
- Keep a changelog line at the top of each document noting what this pass changed.

## 10.2 Cross-linking

- `FEAT-XXX` lists blocking `BUG-XXX` ids in its Dependencies section.
- Security features reference the specific control gap from Phase 6.
- Reliability features reference the specific defects from Phase 5.
- Diagnostics features reference the observability gaps from Phase 5.1.
- Architecture work references the maintainability/testability gaps from Phase 7.
- Both documents cite the same commit hash and audit date.

## 10.3 Before saving

The reports are a rendering of `.audit/findings.jsonl`. Every finding in the
ledger appears in the report and vice versa — the validator reconciles both
directions (R001/R002), including the severity counts in the summary table (R005).

Run `checklists/final-quality-bar.md` for the judgement calls a script cannot
make. The mechanical checks belong to the gate; do not duplicate them by hand.

## 10.4 Terminal summary

Print only this, and only after the gate has run. Do not dump the report contents.

```
AUDIT COMPLETE — {{PROJECT_NAME}} @ {{COMMIT}} ({{BRANCH}}), {{AUDIT_DATE}}

Platforms detected : <list, with confidence>
Audit tier         : <T1|T2|T3> — <one-line justification>

Files written      : BUG_ANALYSIS.md (new|updated), PRODUCT_FEATURE_ANALYSIS.md (new|updated), .audit/
Executed OK        : <commands that ran and passed>
Failed / blocked   : <commands that failed or were not permitted, with reason>

Findings           : Critical <n> · High <n> · Medium <n> · Low <n> · Info <n>
                     (Confirmed <n> / Needs Runtime Verification <n> / Potential <n>)

Top 5 risks        : 1..5 with BUG ids
Top 5 opportunities: 1..5 with FEAT ids
Top 3 foundations  : the three enabling pieces of work

Not verified       : <areas, files, or platforms not covered and why>
Validation         : <PASS | PASS_WITH_LIMITATIONS | FAIL_VALIDATION | BLOCKED | NOT EXECUTED>
                     errors <n> warnings <n> blocked checks <list>
Release verdict    : <DO NOT RELEASE | INTERNAL TESTING ONLY | CONTROLLED PILOT |
                      CONDITIONALLY READY | READY FOR REVIEWED SCOPE>

Repository changes : 2 report files + .audit/ working directory. No source code modified.
```

## 10.5 Closing statement

State plainly that this was analysis only and that no defect has been fixed.
Offer to start remediation as a separate, explicitly scoped task — and if the
user accepts, start from the Immediate group in the remediation plan.

## Exit gate

- [ ] Both documents written and valid Markdown
- [ ] IDs unique and stable across runs
- [ ] Cross-links present in both directions
- [ ] Human quality-bar checklist worked through
- [ ] Summary printed, report body not dumped
- [ ] No claim that anything was fixed
- [ ] Handed to the validation gate — completion is not declared here
