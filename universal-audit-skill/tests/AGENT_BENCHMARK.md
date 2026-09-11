# Agent Detection Benchmark

`tests/run_tests.py` verifies the deterministic machinery. It cannot verify the
part that actually finds bugs, because that is a language model, not a function.
This file describes the benchmark that closes the gap, and why its result is
reported as `NOT_EXECUTED` until someone runs it.

## What it measures

Run the skill, unmodified, against each fixture in `tests/fixtures/`, then compare
`.audit/findings.jsonl` with that fixture's `.expected/expectations.json`.

| Metric | Definition |
|---|---|
| True positives | Seeded defects reported at the right file with the right defect class |
| Missed | Seeded defects absent from the ledger |
| False positives | Medium-or-above findings that map to no seeded defect |
| Negative-control violations | Any Medium-or-above finding in `clean-lib` |
| Seeded-negative hits | Findings landing on a documented `seeded_negatives` entry — the expensive kind of false positive |
| Location accuracy | Reported line within ±3 of the seeded line |
| Duplicate rate | Findings sharing a fingerprint or flagged D002 |
| Standards accuracy | Selected standards against `expected_standards`; penalise both misses and irrelevant additions |
| Validation pass rate | Runs where the quality gate reports PASS or PASS_WITH_LIMITATIONS without hand-editing |

## Protocol

1. Fresh fixtures: `python3 tests/make_fixtures.py --clean`.
2. `git init` each fixture and commit, so citations have a real commit.
3. Run the skill on each fixture in a clean context, five runs per fixture — a
   single run measures luck, not capability.
4. Do not let the harness see `.expected/`; delete or move it during the run.
5. Score with the definitions above. Report mean and spread, not the best run.

## Thresholds worth holding to

- Negative-control violations: **zero**. An auditor that finds vulnerabilities in
  clean code is worse than no auditor, because its output cannot be triaged.
- Seeded-negative hits: zero for the documented ones.
- Recall on seeded defects: report it honestly rather than tuning until it looks
  good. Recall bought by lowering the evidence bar is not recall.
- Validation pass rate without hand-editing: this is the honest measure of
  whether the evidence contract is workable in practice. If the model cannot
  satisfy the contract, the contract is too strict or the phases explain it badly
  — fix that, do not relax the validator.

## Why it is not automated here

Running it requires an agent runtime, a model, an API budget, and a decision
about which model version is under test. Hard-coding any of that would make the
suite fail for everyone else. Wiring it up is left to whoever operates the skill;
until then the suite reports `NOT_EXECUTED`, which is the truthful status.

Do not report a detection rate that was not measured.
