# Phase 8 — Test Strategy and Coverage Gaps

**Goal:** say what testing exists, what is missing on the paths that matter, and
what to add first.

## 8.1 Inventory what exists

- Test frameworks and runners in use
- Test counts by level (unit / integration / e2e / performance / security)
- Where tests live and whether they run in CI
- Fixtures, factories, mocks, and test doubles — and whether they mock so much
  that the test proves nothing
- Flaky, skipped, and disabled tests (`skip`, `xit`, `@Ignore`, `#[ignore]`) —
  each one is a finding
- Coverage tooling and last measured numbers

## 8.2 Map coverage onto critical paths

Coverage percentage is a weak signal. Map instead:

| Critical flow | Existing test | Gap | Recommended test | Level | Priority |
|---|---|---|---|---|---|

A flow with 90% line coverage and no failure-path test is worse covered than one
with 40% and a test for every error branch.

## 8.3 Test types to consider, by evidence of need

Recommend a type only when a finding or a risk justifies it:

- **Unit** — pure logic, parsers, calculations, state reducers
- **Property-based / fuzz** — any parser, decoder, or protocol handler (Phase 5.2
  boundary list becomes the generator)
- **Contract** — between services or between client and API
- **Integration** — real database, real serialization, real HTTP client
- **End-to-end** — the two or three journeys that define the product
- **Concurrency / stress** — races found in Phase 5; run with race detectors
- **Failure injection** — timeouts, dropped connections, 500s, disk full,
  permission revoked mid-operation, process killed
- **Lifecycle** — restart, upgrade with existing data, process death and restore
- **Security** — authz matrix tests per role per resource, injection cases,
  regression tests for every security finding
- **Performance** — budgets on the paths users feel; not a generic benchmark suite
- **Accessibility** — automated axe-style checks plus a keyboard-only pass
- **Soak** — long-run for leaks, if the product runs for hours or days
- **Migration** — old data + new code, on real exported data shapes

## 8.4 Recommend a target shape

Give a concrete target: which levels, roughly what proportion, what runs on every
PR versus nightly, and what the CI quality gate should enforce for new code.
Include the cost: tests are maintenance, and a suggestion that doubles CI time
needs to say so.

## 8.5 Regression tests for findings

Every `Confirmed` finding from Phase 5–6 must have a named test in its
`Required Tests` field. A fix without a regression test is not done.

## Exit gate

- [ ] Existing tests inventoried with real counts
- [ ] Every critical path has a coverage verdict
- [ ] Every confirmed finding has a proposed regression test
- [ ] Skipped/flaky tests listed
