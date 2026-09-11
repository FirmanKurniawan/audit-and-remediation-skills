# FIX LOG — {{PROJECT_NAME}}

Human-readable companion to `.audit/fixes/*.json`. The JSON records are the
source of truth; this file is what a reviewer reads first.

> Every entry below was produced by `universal-remediation-skill`, one finding
> per pass. A status of `VERIFIED_FIXED` means the original reproduction no
> longer reproduces, targeted and regression tests pass, and a delta re-audit no
> longer derives the finding. Anything short of that says so.

## Summary

| Finding | Title | Status | Files | Verification | Re-audit | Commit |
|---|---|---|---|---|---|---|
| BUG-000 | | | | | | |

---

## BUG-000 — <title>

**Status:** `<lifecycle status>` · **Baseline:** `<commit>` · **Branch:** `<branch>`
**Record:** `.audit/fixes/BUG-000.json` · **Patch:** `.audit/fixes/BUG-000.patch`

**Root cause**
<the mechanism, one paragraph>

**What changed**
<files and the shape of the change; no diff dump>

**Reproduction before**
`<command>` → `<result>` — `.audit/evidence/BUG-000-before.log`

**Verification after**
`<same command>` → `<result>` — `.audit/evidence/BUG-000-after.log`

**Tests**
- Added: `<test name>` — fails on baseline, passes on the patch
- Targeted: `<result, names>`
- Regression: `<scope, baseline failures vs current>`

**Delta re-audit**
`<result>` — finding still derived: `<yes/no>`

**Remaining risks**
<what is still unverified, and what would settle it>

**Rollback**
```bash
<exact commands>
```

**Candidate findings discovered (not fixed)**
- `<id or description>` — appended to `.audit/findings.jsonl` as `CANDIDATE`

---
