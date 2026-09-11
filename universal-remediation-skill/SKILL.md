---
name: universal-remediation-skill
description: |
  Safely fixes findings produced by the sibling `universal-audit-skill` skill,
  one finding at a time, under reproduction, minimal-patch, build, test,
  runtime and regression gates. Consumes `.audit/findings.jsonl` (preferred)
  or `BUG_ANALYSIS.md`, and writes a machine-readable fix record per finding.

  Use this skill when the user explicitly says "fix this finding", "patch
  BUG-014", "remediate", "resolve this audit finding", or hands over a
  validated audit and asks for the next fix.

  This skill MODIFIES SOURCE CODE — it never runs implicitly and requires an
  explicit request plus explicit consent. Do NOT use it for general refactors,
  feature work, or anything not bound to a specific validated finding.
descriptions:
  id-ID: |
    Memperbaiki temuan yang dihasilkan oleh skill saudara `universal-audit-skill`,
    satu temuan pada satu waktu, di bawah gerbang reproduksi, patch minimal,
    build, test, runtime, dan regresi. Mengkonsumsi `.audit/findings.jsonl`
    (pilihan utama) atau `BUG_ANALYSIS.md`, dan menulis fix record yang
    dapat dibaca mesin untuk setiap temuan.

    Gunakan skill ini ketika user secara eksplisit mengatakan "perbaiki
    temuan ini", "patch BUG-014", "remediate", "atasi temuan audit ini", atau
    menyerahkan audit yang sudah tervalidasi dan meminta perbaikan berikutnya.

    Skill ini MENGUBAH KODE SUMBER — tidak pernah berjalan secara implisit
    dan membutuhkan permintaan eksplisit plus persetujuan eksplisit. Jangan
    gunakan untuk refactor umum, pengerjaan fitur, atau apapun yang tidak
    terikat pada temuan tervalidasi tertentu.
  zh-Hans: |
    安全地修复由同级 skill `universal-audit-skill` 产出的发现，每次处理一个发现，
    历经复现、最小补丁、构建、测试、运行时与回归等关卡。读取 `.audit/findings.jsonl`
    （首选）或 `BUG_ANALYSIS.md`，并为每个发现写入机器可读的修复记录。

    当用户明确说"修复此发现"、"修补 BUG-014"、"补救"、"解决此审计发现"，或交
    付一份已验证的审计并要求进行下一项修复时，使用本 skill。

    本 skill 会修改源代码 — 绝不隐式运行，需要明确请求与明确授权。请勿用于
    一般性重构、特性开发或任何与已验证发现无关的工作。
displayNames:
  id-ID: Remediasi Universal
  zh-Hans: 通用修复
version: 1.0.0
audit_skill:
  name: universal-audit-skill
  min_version: 2.0.0
---

# Universal Remediation Skill

The companion to `universal-audit-skill`. That skill finds and reports; this one
fixes. They are separate on purpose — an agent that does both has an incentive to
decide an inconvenient finding was never real.

Read this file, then `references/remediation-rules.md`, then work the phases in
order for **one finding at a time**.

## Preconditions

Do not start until all of these hold:

1. The user explicitly asked for remediation. Being handed an audit is not a
   request to fix it.
2. A findings ledger exists. Prefer `.audit/findings.jsonl` over
   `BUG_ANALYSIS.md` when both are present — the ledger is structured, the report
   is a rendering of it.
3. The target finding's status is `VERIFIED_FINDING` or later. A `CANDIDATE`
   goes back to the audit for verification first.
4. The finding validates: `python3 <audit-skill>/scripts/validate-findings.py
   --findings .audit/findings.jsonl` reports no errors for it.
5. The working tree is clean, or the user has explicitly accepted that their
   uncommitted changes are in scope. Never stash or discard their work.
6. You know how to undo what you are about to do (`references/rollback-rules.md`).

## Hard rules

1. **One finding at a time.** No batching, no "while I was in there". Each fix
   is its own branch, its own patch, its own record, its own verification.
2. **No reproduction, no fix.** If the defect cannot be reproduced or otherwise
   demonstrated, the fix cannot be verified. Record `reproduction_waiver` with a
   reason and get explicit approval, or stop.
3. **Minimal patch.** Change the smallest thing that removes the root cause.
   No opportunistic refactoring, no reformatting, no dependency upgrades unless
   the finding *is* the dependency, no rewriting a working module because a
   different design would be cleaner.
4. **Source changes only where the finding lives.** Every file touched beyond
   the first needs a written justification in the fix record.
5. **A code change is not a fix.** `VERIFIED_FIXED` requires: the original
   reproduction no longer reproduces, targeted tests pass, regression tests pass,
   and a delta re-audit no longer derives the finding.
6. **Failed verification leaves the finding open.** It never closes by default,
   by timeout, or by argument.
7. **New defects are candidates, not side quests.** Append to the ledger with
   `status: CANDIDATE` and hand back to the audit. Do not fix them here.
8. **Never fabricate a result.** `NOT_EXECUTED` never becomes `PASS`. If the
   build could not run, say so and stop at that gate.
9. **Destructive commands stay prohibited**, exactly as in the audit skill —
   with the single, scoped exception that this skill may edit the specific source
   files a finding names, and only after its fix plan is recorded.

## Pipeline

Defined once in **`references/pipeline.md`**. Ten stages, 0 through 9, one
finding per pass.

## Lifecycle

```
CANDIDATE → VERIFIED_FINDING → READY_FOR_FIX → REPRODUCED → FIX_IN_PROGRESS
→ FIX_IMPLEMENTED → VERIFICATION_PASSED → REGRESSION_PASSED → RE_AUDIT_PASSED
→ VERIFIED_FIXED
```

Each arrow is a gate with evidence behind it. Statuses only advance on evidence;
they fall back on failure. The vocabulary comes from the audit skill's
`scripts/auditkit.py`, imported rather than redefined so the two cannot drift.

## Outputs

```
.audit/fixes/<BUG-ID>.json     the fix record (schemas/fix-record.schema.json)
.audit/fixes/<BUG-ID>.patch    the diff actually applied
.audit/evidence/<BUG-ID>-*.log before/after/build/test artifacts
FIX_LOG.md                     human-readable running log
```

Validate every record before closing:

```bash
python3 scripts/validate-fix.py --fix-record .audit/fixes/BUG-014.json
```

## Layout

- `references/pipeline.md` — the canonical stage list
- `references/remediation-rules.md` — minimal patch, scope, what never to touch
- `references/verification-rules.md` — what each gate requires
- `references/rollback-rules.md` — undo, before you need it
- `phases/` — the ten stages
- `templates/` — fix record and fix log
- `schemas/fix-record.schema.json` — the machine-readable contract
- `scripts/validate-fix.py` — the gate
- `prompts/` — master fix, single finding, verify-only

## Windows (win32) platform notes

The scripts are Python 3 stdlib only and run on Windows, macOS, and Linux.
The only adaptation is the launcher for `python3`:

| Platform | Command |
|---|---|
| Windows / PowerShell | `py <audit-skill>\scripts\validate-findings.py --findings .audit\findings.jsonl` |
| macOS / Linux / WSL | `python3 <audit-skill>/scripts/validate-findings.py --findings .audit/findings.jsonl` |
| Claude Code (any OS) | same as the platform above; `~/.claude/skills/` mirrors the Mavis user-global layout |

`<audit-skill>` resolves to the sibling skill directory. Under Mavis
user-global install that is `C:\Users\<you>\.minimax\skills\universal-audit-skill`
on Windows or `~/.mavis/skills/universal-audit-skill` on macOS/Linux. From
inside this skill the relative path is `..\universal-audit-skill\scripts\validate-findings.py`
(Windows) or `../universal-audit-skill/scripts/validate-findings.py` (POSIX).

CI on `.github/workflows/validate.yml` runs the self-test on `ubuntu-latest`
with `python3`; that path is unchanged.

## Cross-skill contract

This skill depends on `universal-audit-skill` v2.0.0 or later. The dependency
is real, not cosmetic:

- The lifecycle vocabulary (`CANDIDATE` → `VERIFIED_FIXED`) is imported from
  the audit skill's `scripts/auditkit.py` rather than redefined here, so the
  two cannot drift.
- The `findings.jsonl` schema, status enums, and validator contract come from
  the same source.
- Install layout must keep the two skills as siblings on disk
  (Mavis user-global install does this by default; see top-level README).

If the audit skill is upgraded, run its self-test first; if the contract
changed, this skill's gate (`scripts/validate-fix.py`) will reject records
that no longer match.
