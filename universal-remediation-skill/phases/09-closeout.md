# Phase 9 — Closeout

**Goal:** produce the record, prove closure independently, and update the ledger.

## 9.1 Write the fix record

From `templates/FIX_RECORD.template.json` to `.audit/fixes/<BUG-ID>.json`, then:

```bash
python3 scripts/validate-fix.py --fix-record .audit/fixes/BUG-014.json
```

The validator enforces the gates that matter: a fix cannot claim
`VERIFIED_FIXED` while its verification result is anything but `PASS`; extra
changed files need justification; dependency and lockfile changes need a
rationale; the rollback procedure is mandatory.

## 9.2 Delta re-audit

Run the audit skill in delta mode against the new commit. Independent derivation
is the point — the fix is confirmed when the audit *no longer finds the finding*,
not when the person who wrote the patch says it is gone.

```bash
python3 <audit-skill>/scripts/quality-gate.py --repo . --audit .audit \
  --report BUG_ANALYSIS.md --out .audit/validation-result.json
```

If the re-audit still derives the finding — at the same fingerprint, or as a
D002 near-duplicate — the fix is incomplete regardless of what phase 7 said.
Reopen it.

## 9.3 Update the ledger

In `.audit/findings.jsonl`, set `status: VERIFIED_FIXED`, `fix_record:
.audit/fixes/BUG-014.json`, and `resulting_commit`. Keep the original `id` and
`first_seen_commit`. Never delete a finding to close it.

If any gate ended short of PASS, record the highest status actually reached and
say what is outstanding. `FIX_IMPLEMENTED` with an honest note is a better
outcome than `VERIFIED_FIXED` with an invented one.

## 9.4 Report

Append to `FIX_LOG.md` and tell the user, briefly: what changed and where, why
the root cause is gone, what proves it, what regression coverage ran, what
remains unverified, how to roll back, and any candidate findings discovered along
the way — **which you did not fix**.

## 9.5 Then stop

One finding per pass. Return to phase 0 for the next one, with a fresh baseline
and a fresh consent check.

## Exit gate

- [ ] Fix record written and passing `validate-fix.py`
- [ ] Delta re-audit run and no longer deriving the finding
- [ ] Ledger updated with the honest status and the fix record reference
- [ ] `FIX_LOG.md` updated
- [ ] Candidate findings recorded, not fixed
- [ ] Rollback procedure verified as still accurate
