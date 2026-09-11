---
name: universal-audit-skill
description: |
  Platform-agnostic, evidence-based audit of any software repository (web,
  backend/API, mobile, desktop, embedded/IoT, data/ML, CLI, infrastructure, or
  hybrid monorepos). Auto-detects the stack, selects applicable standards
  (OWASP ASVS/MASVS/Top 10, CWE, ISO/IEC 25010:2023, Sonar way, SSDF/SLSA/SBOM,
  WCAG, privacy regimes), produces a machine-validated findings ledger, and
  writes BUG_ANALYSIS.md and PRODUCT_FEATURE_ANALYSIS.md.

  Use this skill whenever the user asks to "audit this repository",
  "security review", "QA assessment", "code audit", "bug analysis",
  "technical-debt review", "release-readiness check", or "product gap analysis".

  ANALYSIS ONLY — never modifies application source code. For fixing
  validated findings, use the sibling `universal-remediation-skill`.
  Do NOT use this skill for live debugging, hot-fixes, or one-off code tweaks.
descriptions:
  id-ID: |
    Audit repository software berbasis bukti dan agnostic terhadap platform
    (web, backend/API, mobile, desktop, embedded/IoT, data/ML, CLI,
    infrastructure, atau monorepo hybrid). Mendeteksi stack secara otomatis,
    memilih standar yang relevan (OWASP ASVS/MASVS/Top 10, CWE,
    ISO/IEC 25010:2023, Sonar way, SSDF/SLSA/SBOM, WCAG, rezim privasi),
    menghasilkan ledger temuan yang divalidasi oleh script, dan menulis
    BUG_ANALYSIS.md serta PRODUCT_FEATURE_ANALYSIS.md.

    Gunakan skill ini ketika user meminta "audit repository ini",
    "tinjauan keamanan", "asesmen QA", "analisis bug", "tinjauan technical
    debt", "cekap kesiapan rilis", atau "analisis kesenjangan produk".

    HANYA ANALISIS — tidak pernah mengubah kode sumber aplikasi. Untuk
    memperbaiki temuan yang sudah tervalidasi, gunakan skill saudara
    `universal-remediation-skill`. Jangan gunakan skill ini untuk debugging
    langsung, hot-fix, atau perubahan kode satu kali.
  zh-Hans: |
    平台无关、基于证据的软件仓库审计（web、后端/API、移动、桌面、嵌入式/IoT、
    数据/ML、CLI、基础设施或混合 monorepo）。自动识别技术栈、选择适用的标准
    （OWASP ASVS/MASVS/Top 10、CWE、ISO/IEC 25010:2023、Sonar way、SSDF/SLSA/
    SBOM、WCAG、隐私法规），生成由脚本验证的发现分类账，并写入 BUG_ANALYSIS.md
    与 PRODUCT_FEATURE_ANALYSIS.md。

    当用户要求"审计此仓库"、"安全审查"、"QA 评估"、"代码审计"、"缺陷分析"、
    "技术债审查"、"发布就绪检查"或"产品差距分析"时使用本 skill。

    仅做分析 — 永不修改应用程序源代码。修复已验证的发现请使用同级 skill
    `universal-remediation-skill`。不要用于在线调试、紧急修复或单次代码调整。
displayNames:
  id-ID: Audit Kode Universal
  zh-Hans: 通用代码审计
version: 2.0.0
pipeline_version: 2.0.0
---

# Universal Code Audit Skill

Read this file fully. Then load `references/pipeline.md` — the canonical pipeline
definition — and work through the stages, loading one phase file at a time. Do
not load every playbook and reference up front.

## Deliverables

- `BUG_ANALYSIS.md` — defects, security findings, quality matrices, remediation
  plan, release recommendation.
- `PRODUCT_FEATURE_ANALYSIS.md` — product understanding, personas, feature gaps,
  prioritized roadmap.
- `.audit/findings.jsonl` — the machine-readable findings ledger. The reports are
  a rendering of this; the ledger is the source of truth.
- `.audit/manifest.json` — scope, tier, consent, components, standards, threat
  model, command evidence, runtime records.
- `.audit/validation-result.json` — the gate verdict from the final stage.

## Hard rules

1. **Analysis only.** Never edit, refactor, reformat, upgrade, or fix
   application source, build files, manifests, lockfiles, or CI config. The only
   paths this skill writes are the two reports and `.audit/`. Remediation is a
   separate skill with its own consent and its own gates; see
   `references/cross-skill-boundary.md`. Discovering a fix mid-audit is not
   authorization to apply it.
2. **Command safety.** Every command is classified before it runs
   (`references/command-safety-model.md`). PROHIBITED commands never run.
   CONTROLLED_EXECUTION requires consent plus a before/after repository-state
   record, and any modification to tracked source stops the audit.
3. **Evidence or it does not exist.** Every finding carries a verified
   `file:line` range, captured command output, or explicit absence evidence
   showing the search that would have found the missing thing. The contract is
   `references/evidence-contract.md`; it is enforced by a script, not by
   self-review.
4. **Never invent a line number, a fingerprint, a CVSS score, a CWE, an EPSS
   value, or a KEV flag.** Fingerprints are computed. CVSS without a defensible
   vector is `Not Scored — Insufficient Evidence`. EPSS and KEV apply only to
   findings with a real CVE. CWE is required for security-class findings and is
   not forced onto ordinary functional defects.
5. **Never report a command as passing unless it ran and passed.** `Not
   Executed` and `Blocked` are honest results. `NOT_EXECUTED` never becomes
   `PASS`.
6. **Never claim compliance.** Regulatory findings record applicability, a
   rationale, and a gap — never a legal verdict
   (`references/regulatory-applicability.md`).
7. **Never reproduce a secret.** Report location and class only. This applies to
   code excerpts, logs, and runtime artifacts.
8. **Label epistemics.** Every claim is `Fact`, `Inference`, or `Assumption`.
   Severity, confidence, exploitability, and priority stay four separate axes.
9. **Scale to the budget.** Pick a tier in the preflight stage and state it. A
   tier that samples must say what it sampled and what it skipped.
10. **The audit is complete when the validator says so**, not when the documents
    are written. Fix findings, never evidence, to make the gate pass.

## Pipeline

Defined once, in **`references/pipeline.md`**. That file lists every stage, which
stage owns which output, and which stages each mode requires. It is parsed by the
test suite, so it cannot silently drift from the phase files. Do not restate it
here or anywhere else.

## Working state

```
.audit/
  manifest.json            scope, consent, components, standards, threat model,
                           command evidence, runtime verifications
  findings.jsonl           one finding per line, schema 2.0
  evidence/                captured command output, logs, runtime artifacts
  validation-result.json   gate verdict
```

`.audit/` is a repository change. Declare it in the summary and tell the user
they can delete it or gitignore it. If the repository must stay pristine, put it
in a temp directory and say where.

## Tooling

All stdlib Python 3, no network, read-only against the audited repository.

| Script | Purpose |
|---|---|
| `scripts/detect-stack.sh` | Read-only platform fingerprinting (hints only — the detection stage verifies) |
| `scripts/validate-findings.py` | Schema and semantic rules over the ledger |
| `scripts/verify-evidence.py` | Files, line ranges, content hashes, commit match |
| `scripts/verify-line-references.py` | Line-reference subset of the above |
| `scripts/detect-duplicate-findings.py` | Exact and near-duplicate findings |
| `scripts/validate-final-report.py` | Report ↔ ledger reconciliation, placeholders |
| `scripts/validate-manifest.py` | Manifest, command safety, runtime records |
| `scripts/quality-gate.py` | Runs everything, writes the verdict |
| `scripts/generate-schemas.py` | Regenerates `schemas/` from the validator vocabularies |
| `tests/run_tests.py` | Self-test of this skill against its fixtures |

`scripts/auditkit.py` is the implementation the wrappers call and the
authoritative definition of every vocabulary.

## Placeholders

`{{PROJECT_NAME}}`, `{{PLATFORMS}}`, `{{STANDARDS_SET}}`, `{{AUDIT_DATE}}`,
`{{COMMIT}}`, `{{BRANCH}}`. Any placeholder left unresolved in a report is a
validation error (R003).

## Layout

- `references/pipeline.md` — canonical pipeline (read this second)
- `references/evidence-contract.md` — what a finding must carry
- `references/fingerprinting.md` — stable finding identity
- `references/severity-and-confidence.md` — the four axes
- `references/command-safety-model.md` — command classes and state comparison
- `references/regulatory-applicability.md` — applicability, never verdicts
- `references/runtime-verification.md` — runtime record contract
- `references/standards-registry.md` — versions with verification status
- `references/standards-selection-matrix.md` — platform × trigger → standard set
- `references/product-frameworks.md` — RICE and risk-adjusted scoring
- `references/cross-skill-boundary.md` — audit / remediation separation
- `phases/` — the pipeline, one file per stage
- `playbooks/` — per-platform deep-analysis checklists, loaded on demand
- `schemas/` — generated JSON Schemas
- `templates/` — report skeletons and the manifest template
- `checklists/final-quality-bar.md` — human checks the validator cannot make
- `tests/` — fixtures and the self-test suite
- `prompts/` — copy-pasteable prompts (EN/ID, quick triage, delta re-audit)
