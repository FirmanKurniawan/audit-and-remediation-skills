# Canonical Pipeline

**This file is the single source of truth for the pipeline.** Every other
document links here instead of restating the table; `tests/run_tests.py` parses
this file and fails the suite when the phase files, their headings, or any prose
phase count disagrees with it.

Pipeline version: **2.0.0** — twelve stages, numbered 0 through 11.

| Phase | File | Owns (authoritative output) |
|---|---|---|
| 0 | `phases/00-preflight.md` | Repository safety snapshot, scope, audit tier, consent record, `.audit/manifest.json` |
| 1 | `phases/01-platform-detection.md` | Component inventory with primary-marker evidence and confidence |
| 2 | `phases/02-standards-and-threat-model.md` | Applicable standards set with versions **and the threat model** |
| 3 | `phases/03-discovery-systemmap.md` | System map, critical-path inventory, extracted state machines |
| 4 | `phases/04-build-and-static-analysis.md` | Command evidence records with pre/post repository state |
| 5 | `phases/05-deep-analysis.md` | The findings ledger (`.audit/findings.jsonl`) |
| 6 | `phases/06-security-assessment.md` | Security, supply-chain and privacy control matrices |
| 7 | `phases/07-quality-assessment.md` | ISO/IEC 25010:2023 matrix, code-quality and accessibility assessment |
| 8 | `phases/08-test-strategy.md` | Coverage gaps and required regression tests |
| 9 | `phases/09-product-analysis.md` | Product understanding, feature inventory, prioritized proposals |
| 10 | `phases/10-reporting.md` | `BUG_ANALYSIS.md` and `PRODUCT_FEATURE_ANALYSIS.md` |
| 11 | `phases/11-validation-gate.md` | `.audit/validation-result.json` and the completion verdict |

## Ownership rules

A phase **owns** an output: it is the only place that produces it. Other phases
consume it. This prevents the same artifact being defined twice with different
rules, which is how a pipeline drifts.

- The **threat model belongs to Phase 2**, not Phase 3. It has to exist before
  standards depth and severity can be calibrated, and Phase 3 consumes it to
  decide which paths are critical.
- The **findings ledger belongs to Phase 5**. Phases 6, 7, 8 and 9 append to it
  through the same schema; none of them keeps a private list.
- **Command evidence belongs to Phase 4.** Any later phase that runs something
  records it through Phase 4's contract.
- **Reports belong to Phase 10**, and **the completion verdict belongs to
  Phase 11**. Phase 10 may not declare an audit complete.

## Exit gates

Every phase has an explicit exit gate at the bottom of its file. A phase is not
finished until its gate is satisfied. Phase 11 is machine-enforced: the gate is a
script, not a judgement.

## Modes

Modes select a subset of phases. Phase 0, 1, 2, 5, 10 and 11 are **always
required** — 5 because it owns the ledger the validator reconciles against, and
11 because an unvalidated audit has no completion verdict.

| Mode | Phases | Notes |
|---|---|---|
| Full audit | 0–11 | Default. |
| Security-only | 0, 1, 2, 3, 4, 5, 6, 10, 11 | Writes `BUG_ANALYSIS.md`. Skipping 7–9 is recorded as a scope limitation. |
| Product-only | 0, 1, 2, 3, 5, 9, 10, 11 | Phase 5 runs in survey depth to establish a defect baseline; without it the foundation-first rule in Phase 9 cannot be applied and the product document must say so. |
| Quick triage | 0, 1, 2, 5, 10, 11 | Time-boxed. The report must carry the triage scope banner. |
| Delta re-audit | 0, 1, 5, 10, 11 (+ any phase touched by the diff) | See `prompts/REAUDIT_DELTA_PROMPT.md`. |

Any mode that omits a phase records the omission in the manifest under
`not_verified` and in the report's Known Limitations.

## Boundary

This pipeline is **analysis only**. It never modifies application source. Fixing
findings is a separate skill (`universal-remediation-skill`) with its own
pipeline. An audit run that starts editing code has violated its contract, and
Phase 4's repository-state comparison is what detects it.
