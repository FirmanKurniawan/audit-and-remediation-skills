# Changelog

Semantic versioning. The version that matters here is the **contract** between
the skill and anything that consumes its output — the findings ledger, the
manifest, and the status vocabulary.

## 2.0.0 — 2026-09-10

**MAJOR.** Chosen deliberately over MINOR: the finding record changed shape
incompatibly, `.audit/findings.jsonl` gained required fields with no defaults, a
pipeline stage was added and another renamed, and an audit that previously
"completed" by writing two documents now completes only when a validator passes.
A v1 ledger will not validate under v2, and v1 prose claiming a nine-phase
pipeline is now wrong. Anything that consumed v1 output must be updated. See
`MIGRATION.md`.

### Fixed — contradictions confirmed in the v1 tree

- `SKILL.md` described a "nine-phase" workflow while defining eleven phases
  (0–10). The pipeline is now defined exactly once, in `references/pipeline.md`,
  and a test parses it and fails the build when any document, phase heading, or
  prose phase count disagrees.
- Threat modeling was attributed to Phase 3 in the `SKILL.md` pipeline table but
  actually lived in Phase 2. Phase 2 now owns it, and is renamed
  `02-standards-and-threat-model.md` to say so.
- Mode definitions were unachievable: "Security-only" skipped the phase that owns
  the findings ledger, and "Product-only" skipped the phase its own
  foundation-first rule depends on. Modes now declare a mandatory core and record
  their omissions.
- `phases/05-deep-analysis.md` referenced `templates/FINDING.schema.md`, which
  described a finding shape no tool enforced. Removed in favour of
  `references/evidence-contract.md` plus a generated JSON Schema.
- Prose used "Phase 0.5" and "Phase 5.4" for what were section numbers, reading
  as phases that did not exist. Now written as `§`.

### Added

- **Deterministic validation.** `scripts/auditkit.py` plus seven CLI wrappers.
  ~60 rules over findings (F), evidence (E), duplicates (D), report
  reconciliation (R), secrets (S) and the manifest (M).
- **Quality gate** (`phases/11-validation-gate.md`, `scripts/quality-gate.py`)
  writing `.audit/validation-result.json` with `PASS`,
  `PASS_WITH_LIMITATIONS`, `FAIL_VALIDATION` or `BLOCKED`. Reports that fail
  carry a DRAFT banner.
- **Finding fingerprints** derived from component, weakness class, file/symbol
  and normalized excerpt — never line numbers — with exact and near-duplicate
  detection (`references/fingerprinting.md`).
- **Command safety model** with four classes, pre/post repository-state
  snapshots on controlled execution, and detection of source modification during
  an analysis-only run (`references/command-safety-model.md`).
- **Regulatory applicability model**: four applicability values, mandatory
  rationale, `Potential Compliance Gap` instead of compliance verdicts, and a
  validator that rejects verdict language (`references/regulatory-applicability.md`).
- **Runtime verification contract** with a five-value result vocabulary and the
  rule that `NOT_EXECUTED` never becomes `PASS`
  (`references/runtime-verification.md`).
- **Generated JSON Schemas** (`schemas/`) produced from the validator's own
  vocabularies, with a `--check` mode so they cannot drift.
- **Self-test suite** (`tests/`): six fixture repositories including a mandatory
  clean negative control, seeded defects with verified line numbers, seeded
  negatives, and 85 deterministic tests covering the validator, fingerprints,
  evidence checks, the gate, the secret scanner, platform detection and
  documentation consistency.
- **`tests/AGENT_BENCHMARK.md`** — the detection-rate benchmark that this suite
  deliberately does *not* fake, reported as `NOT_EXECUTED`.
- **`references/cross-skill-boundary.md`** and the sibling
  `universal-remediation-skill`.

### Changed

- Severity is now one of four axes — severity, confidence, exploitability,
  priority — recorded separately. `Critical` + `Potential` is a valid combination.
- CWE is required for security, privacy and supply-chain findings and warned
  against elsewhere. EPSS and KEV require a real CVE. CVSS requires a vector or
  the literal `Not Scored — Insufficient Evidence`.
- Status lifecycle replaced with the fifteen-state vocabulary shared with the
  remediation skill. `VERIFIED_FIXED` requires a fix record.
- The findings ledger is the source of truth; reports are a rendering, reconciled
  in both directions including severity counts.
- Standards registry entries carry a verification status (`[V <date>]` / `[U]`).
  Verified this pass: SLSA v1.2, CycloneDX 1.7 / SPDX 3.0.1, OWASP MASWE 1.0.0
  and MASTG 2.0.0, ASVS 5.0.0, Top 10:2025, CWE Top 25 (2025), ISO/IEC
  25010:2023 / 25002:2024 / 25019:2023, EU CRA dates.
- `checklists/final-quality-bar.md` split into machine-checked and
  human-judgement halves; the human list no longer duplicates what a script does.
- `PROMPT_TUNING_NOTES.md` → `DESIGN_RATIONALE.md`.

### Known limitations

- The validator checks structure, resolvability and consistency. It cannot tell
  you whether a finding is *true*.
- Model detection quality against the fixtures is unmeasured.
- Standards versions go stale; the registry is a starting point, not an authority.

## 1.0.0 — 2026-09-09

Initial release: platform detection, standards selection matrix, threat-model-led
phases, per-platform playbooks, report templates, audit tiers, delta re-audit
mode.
