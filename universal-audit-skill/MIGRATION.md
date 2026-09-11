# Migration — v1 → v2

Read `CHANGELOG.md` for what changed. This is what to do about it.

## If you have never run the skill

Nothing to migrate. Start at `SKILL.md`.

## If you have v1 reports but no ledger

v1 produced `BUG_ANALYSIS.md` and `PRODUCT_FEATURE_ANALYSIS.md` with no
`.audit/findings.jsonl`. You have two options.

**Option A — carry the ids forward (recommended).** Run v2 in delta mode against
the same commit. It re-derives findings, and you map the new records onto the old
ids by hand, keeping the v1 numbering. Ids stay stable for your team; the
evidence becomes verifiable.

**Option B — start clean.** Run a full v2 audit, keep the v1 report as a
historical document, and note in the new report that ids do not correspond. Less
work, but you lose the history on every open finding.

Do not hand-write a v1-shaped ledger. It will fail validation on fingerprints
(F005/F006), which are computed, and on the fields v1 never captured —
reachability, reproduction, verification procedure.

## If you have a v1-era `.audit/findings.jsonl`

The v1 example record used `file`/`line`, a hand-written `mappings` block, and a
free-text `status`. Under v2 it fails validation. The differences:

| v1 | v2 |
|---|---|
| `file`, `line` | `locations[]` with `line_start`, `line_end`, `verified_at`, optional `symbol` and `excerpt_sha256` |
| — | `fingerprint` (computed — never authored) |
| — | `schema_version: "2.0"` |
| — | `finding_class` from a closed list |
| — | `epistemic`: Fact / Inference / Assumption |
| — | `reachability` with status and caller chain |
| — | `reproduction` with status, expected, observed |
| — | `verification` with procedure, expected evidence, level |
| `fix`, `regression_risk`, `tests` | `remediation.strategy`, `.regression_surface`, `.required_tests` |
| `status: "Open"` | the fifteen-state lifecycle (`VERIFIED_FINDING`, …) |
| `mappings.cwe` on everything | CWE required for security/privacy/supply-chain only |
| — | EPSS/KEV rejected without a CVE; CVSS rejected without a vector |

Practical path: re-run the audit rather than converting by hand. The fields v2
adds are ones a converter would have to invent, and inventing them is precisely
what the schema exists to prevent.

## Documents that changed name or ownership

- `phases/02-standards-selection.md` → `phases/02-standards-and-threat-model.md`
- `templates/FINDING.schema.md` → deleted; see `references/evidence-contract.md`
  and `schemas/finding.schema.json`
- `PROMPT_TUNING_NOTES.md` → `DESIGN_RATIONALE.md`
- New: `phases/11-validation-gate.md`, `references/pipeline.md`,
  `references/fingerprinting.md`, `references/command-safety-model.md`,
  `references/regulatory-applicability.md`,
  `references/runtime-verification.md`, `references/cross-skill-boundary.md`

If you forked v1 and edited any of these, reconcile before upgrading. In
particular, **delete any local copy of the pipeline table** — v2 fails its own
tests when the pipeline is defined in more than one place.

## New habits

1. Run the gate. An audit is not finished until
   `.audit/validation-result.json` says so.
   ```bash
   python3 scripts/quality-gate.py --repo . --audit .audit \
     --report BUG_ANALYSIS.md --out .audit/validation-result.json
   ```
2. Do not fix evidence to pass validation. Fix or withdraw the finding.
3. Stop putting CWE on functional defects, and stop putting EPSS or KEV on
   anything without a CVE.
4. Regulatory findings record applicability and a gap. Never a verdict.
5. Remediation is a different skill. The audit never edits code.

## Verifying the upgrade

```bash
python3 tests/make_fixtures.py --clean
python3 tests/run_tests.py
python3 scripts/generate-schemas.py --check
```

All tests should pass, with `agent-detection-rate` reported as `NOT_EXECUTED`.
If the remediation skill is not installed alongside, its contract tests report
`NOT_EXECUTED` too — that is expected, not a failure.
