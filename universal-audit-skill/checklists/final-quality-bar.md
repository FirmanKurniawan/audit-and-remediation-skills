# Final Quality Bar

Split deliberately: the mechanical half is a script, the judgement half is you.
Anything a script can check is not on your list, because a human re-reading a
long document catches those inconsistently and feels productive anyway.

## Machine-checked (do not repeat by hand)

```bash
python3 scripts/quality-gate.py --repo . --audit .audit \
  --report BUG_ANALYSIS.md --product PRODUCT_FEATURE_ANALYSIS.md \
  --out .audit/validation-result.json
```

Covers: schema and vocabulary conformance · fingerprint correctness · duplicate
ids and duplicate root issues · cited files existing · line ranges within the file ·
content hashes still matching · commit match · report ↔ ledger reconciliation in
both directions · severity counts · unresolved placeholders · manifest and command
safety records · runtime record honesty · secret patterns in generated artifacts.

The verdict goes in the report. `FAIL_VALIDATION` means the documents carry the
DRAFT banner.

## Human judgement (only you can do these)

### Is the finding real?
- [ ] For each Critical and High: could you defend it to the engineer who wrote
      the code, with what is written in the record?
- [ ] Reachability claims trace to an entry point you actually followed, not one
      that plausibly exists
- [ ] Compensating controls were looked for, not assumed absent
- [ ] Disproven suspicions moved to rejected hypotheses with the reason, not
      quietly deleted

### Is the severity right?
- [ ] Each severity justified against consequence, with modifiers named
- [ ] Confidence not used to soften severity, or vice versa
- [ ] Priority divergence from severity explained where it occurs
- [ ] Nothing rated Critical because it was interesting to find

### Is the scope honest?
- [ ] Every detected platform audited or explicitly listed as out of scope
- [ ] Sampling rule stated for T2/T3, with what was skipped
- [ ] Blocked checks and unavailable environments named in Known Limitations
- [ ] The reader can tell what this audit did *not* look at

### Is the language honest?
- [ ] Fact / Inference / Assumption labeled throughout
- [ ] No compliance verdict anywhere; applicability recorded with a rationale
- [ ] `Needs Runtime Verification` findings carry a procedure someone else could
      execute without asking you a question
- [ ] Nothing claimed as fixed — this skill only analyses

### Is it useful?
- [ ] Each recommended fix is specific enough to start on Monday
- [ ] Each feature proposal traces to a problem statement with evidence
- [ ] Foundation-first rule applied to features blocked by open findings
- [ ] Roadmap uses relative timing, not invented dates
- [ ] An engineer and a product manager can both read it

### Repository safety
- [ ] `git status` shows only the two reports and `.audit/`
- [ ] No source, build, manifest, lockfile, or CI file touched
- [ ] No dependency installed or upgraded, no formatter or fixer run
- [ ] Any `source_modified: true` command record explained to the user

## The rule that outranks the rest

If a check fails, fix the finding — never the evidence. Editing a hash, widening
a line range, or dropping an inconvenient record to turn the gate green destroys
the only property that makes this audit worth reading.
