# Phase 7 — Product Quality and Code Quality

## 7.1 ISO/IEC 25010:2023 mapping

Use the **2023** product quality model. Nine characteristics — do not reproduce
the 2011 list from memory. In 2023: *Functional Suitability, Performance
Efficiency, Compatibility, Interaction Capability* (was Usability), *Reliability,
Security, Maintainability, Flexibility* (was Portability), and **Safety** (new,
with subcharacteristics covering operational constraint, risk identification,
fail-safe, hazard warning, and safe integration). Quality-in-use now lives in
ISO/IEC 25019:2023; the model-overview guidance lives in ISO/IEC 25002:2024.
Verify subcharacteristic names against the current standard before citing them.

For each characteristic that matters for this product:

| Characteristic | Current condition | Evidence | Main gaps | How to measure | Priority |
|---|---|---|---|---|---|

Rules:
- Skip characteristics that genuinely do not apply, with a one-line reason.
- Every "current condition" needs a citation or a measurement, not a vibe.
- "How to measure" must be an actual metric someone could collect next sprint.
- Include Safety whenever the software controls, actuates, transmits, or informs
  something in the physical world, or where a wrong output could cause harm.

## 7.2 Sonar-style code quality

Assess against Sonar way concepts and Clean as You Code (quality gate applied to
*new* code first, so a legacy codebase can improve without a rewrite):

- **Reliability risks** — null safety, resource management, exception handling,
  thread safety, unreachable or dead code.
- **Security hotspots** — code that requires human review rather than an
  automatic verdict; list them separately from vulnerabilities.
- **Maintainability** — cognitive and cyclomatic complexity hotspots, long
  functions, god classes, deep nesting, duplicated blocks, tangled coupling,
  inconsistent error propagation, naming that misleads.
- **Technical debt hotspots** — name the top 5–10 files/modules by
  (complexity × change frequency × criticality). Use `git log` to get change
  frequency; a complex file nobody touches is lower priority than a moderately
  complex file everyone edits.
- **Test coverage** — actual numbers if measured, `Not Measured` otherwise;
  never estimate a percentage.
- **Quality gate** — does one exist in CI? If not, propose a concrete gate for
  new code (e.g. no new blocker issues, coverage on new code ≥ X%, no new
  duplication above Y%).

Do not paste analyzer output as findings. Every high-impact rule violation must
be validated against how the code actually runs. Style-only rule hits go in an
aggregate count, not in individual finding entries.

## 7.3 Architecture and flexibility

- Layering violations and dependency direction
- Testability blockers: static state, hidden construction, untestable side effects
- Configuration and environment portability
- Scalability constraints that are structural rather than tunable
- Upgrade and migration paths (schema, config, stored data)
- Documentation adequacy for a new engineer to be productive

## 7.4 Accessibility and interaction

If there is a user interface, this is not optional. Web and desktop: WCAG 2.2 AA
criteria (contrast, focus visibility and order, target size, keyboard operability,
error identification, labels, status messages). Mobile: platform accessibility
APIs, content labels, touch target size, dynamic type, screen-reader traversal.
Public-sector or EU market: EN 301 549 as well.

Report concrete failures with locations, not a generic "improve accessibility".

## Exit gate

- [ ] 25010:2023 matrix filled with the current taxonomy
- [ ] Debt hotspots ranked by evidence, not intuition
- [ ] Coverage reported honestly
- [ ] Accessibility assessed wherever a UI exists
