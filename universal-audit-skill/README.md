# Universal Code Audit Skill

**v2.0.0** — machine-validated findings, command-safety model, deterministic
finding fingerprints, and a self-test suite. See `CHANGELOG.md` and
`MIGRATION.md` if you are coming from v1.

An AI agent skill that performs a deep, evidence-based audit of **any** software
repository and produces two deliverables:

- `BUG_ANALYSIS.md` — defects, security findings, quality matrices, remediation plan, release recommendation
- `PRODUCT_FEATURE_ANALYSIS.md` — product understanding, personas, feature gaps, prioritized roadmap

It auto-detects whether the project is **web, mobile, desktop, backend/API,
embedded, data/ML, or hybrid (multi-platform)** and selects the applicable
standards accordingly. It is **analysis-only** and never modifies application code.

---

## Why this exists

Most "audit my repo" prompts fail in three ways: they hardcode one project, they
assume one platform, and they let the model invent line numbers. This skill fixes
all three with a platform-detection phase, a standards-selection matrix, and an
evidence ledger with a mandatory verification pass.

## Quick start

### As an agent skill (Claude Code / Claude Cowork / agent frameworks)

```bash
# personal skills
git clone https://github.com/<you>/universal-audit-skill ~/.claude/skills/universal-code-audit

# or per-project
git clone https://github.com/<you>/universal-audit-skill .claude/skills/universal-code-audit
```

Then just ask: *"Audit this repository."* The skill triggers on audit, security
review, QA, bug analysis, technical debt, release readiness, and product gap requests.

### As a plain prompt

Copy `prompts/MASTER_PROMPT.md` (English) or `prompts/MASTER_PROMPT.id.md`
(Bahasa Indonesia) into any chat and point it at your repo.

## Pipeline

Defined once in **`references/pipeline.md`** — stage numbering, which stage owns
which output, and which stages each mode requires. The test suite parses that
file and fails if any document, phase heading, or prose phase count disagrees
with it.

Findings accumulate in `.audit/findings.jsonl`, are cross-linked
(`BUG-XXX` ↔ `FEAT-XXX`) in the reports, and the run ends with a machine verdict
in `.audit/validation-result.json`.

## Validation

The audit is complete when a script says so, not when the documents are written.

```bash
python3 scripts/quality-gate.py --repo . --audit .audit \
  --report BUG_ANALYSIS.md --product PRODUCT_FEATURE_ANALYSIS.md \
  --out .audit/validation-result.json
```

Verdicts: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL_VALIDATION`, `BLOCKED`. On
failure the reports carry a DRAFT banner. Findings get fixed; evidence never does.

## Testing the auditor

```bash
python3 tests/make_fixtures.py --clean
python3 tests/run_tests.py
```

Six fixture repositories (web, backend, Android, desktop, embedded, and a
mandatory clean negative control) with seeded defects *and* seeded negatives —
code that looks dangerous and is not. The suite verifies the validator, the
fingerprint contract, the schemas, the fixture line references, platform
detection, and documentation consistency. It does not measure model detection
rate; that benchmark is described in `tests/AGENT_BENCHMARK.md` and is reported
as NOT_EXECUTED until someone runs it.

## Standards covered

Selected per detected platform — see `references/standards-selection-matrix.md`.

| Domain | Standards |
|---|---|
| Web / API security | OWASP ASVS 5.0, OWASP Top 10:2025, API Security Top 10, WSTG |
| Mobile security | OWASP MASVS 2.x, MASWE 1.0, MASTG 2.0 |
| Desktop / thick client | OWASP Desktop App Security Top 10, Electron security checklist |
| Weakness taxonomy | CWE, CWE Top 25 (2025), CAPEC |
| Risk scoring | CVSS v4.0, EPSS, SSVC, CISA KEV |
| Product quality | ISO/IEC 25010:2023, 25002:2024, 25019:2023, 25012, ISO/IEC 5055 |
| Code quality | Sonar way / Clean as You Code, SEI CERT, language style guides |
| Supply chain | NIST SSDF SP 800-218, SLSA, OpenSSF Scorecard/Baseline, SBOM (CycloneDX/SPDX) |
| Regulation | EU CRA, NIS2, GDPR, UU PDP (ID), PCI DSS 4.x, HIPAA (conditional) |
| Accessibility | WCAG 2.2, EN 301 549, platform a11y guidelines |
| Testing | ISO/IEC/IEEE 29119, test pyramid, mutation & property-based testing |
| Threat modeling | STRIDE, LINDDUN, MITRE ATT&CK |
| Performance | Core Web Vitals/INP, Android vitals, RAIL |
| Safety / industrial | IEC 62443, IEC 61508 / ISO 26262 (conditional) |
| AI/ML | OWASP LLM Top 10, NIST AI RMF, ISO/IEC 42001 (conditional) |

Versions are pinned in `references/standards-registry.md` with an access date and
must be re-verified at audit time.

## Design principles

1. **Evidence or it does not exist** — and a script checks, so it is not a matter
   of the model's diligence.
2. **Four axes, never collapsed** — severity, confidence, exploitability, priority.
3. **Instruments applied only where they mean something** — CWE on weaknesses,
   EPSS/KEV only with a CVE, CVSS only with a defensible vector.
4. **Applicability before compliance** — gaps and rationales, never legal verdicts.
5. **Stable finding identity** — fingerprints derived from semantics, not line
   numbers, so history survives refactoring.
6. **Command safety by class** — consent is scoped, controlled execution is
   bracketed by repository-state snapshots, prohibited commands never run.
7. **Threat-model-driven, not checklist-driven.** Depth proportional to risk.
8. **Budget-aware.** Three tiers so large monorepos degrade gracefully.
9. **Analysis only.** Fixing lives in `universal-remediation-skill`.

## Repository layout

```
SKILL.md            entry point and hard rules
references/         canonical pipeline, evidence contract, fingerprinting,
                    severity model, command safety, regulatory applicability,
                    runtime verification, standards registry and selection matrix
phases/             the pipeline, one file per stage
playbooks/          per-platform deep-analysis checklists
schemas/            generated JSON Schemas (finding, manifest, command evidence)
scripts/            auditkit.py plus the validator CLIs and detect-stack.sh
templates/          report skeletons and the manifest template
checklists/         the human half of the quality bar
tests/              fixtures, negative control, and the self-test suite
prompts/            copy-paste prompts (EN / ID / quick / delta)
```

## Companion skill

`universal-remediation-skill` consumes this skill's validated findings and fixes
them one at a time under its own gates. The boundary is documented in
`references/cross-skill-boundary.md` and is deliberate: an agent that both finds
and fixes has an incentive to decide a finding was never real.

## Limitations

- Static analysis cannot confirm runtime behaviour. Anything unproven is marked
  `Needs Runtime Verification` with a concrete test procedure.
- The validator checks structure, resolvability and internal consistency. It
  cannot tell you whether a finding is *true* — that is what the human half of
  the quality bar is for.
- Detection quality against the fixtures has not been benchmarked; see
  `tests/AGENT_BENCHMARK.md`.
- It does not run untrusted build scripts on request; builds happen only in the
  user's own environment with their consent.
- Market research quality depends on available public sources; competitor claims
  are limited to publicly documented behaviour.

## License

MIT. See `LICENSE`.
