# Design Rationale (v1)

Why the skill departs from a conventional single-project audit prompt, and why
each standard was added. This documents the v1 design; `CHANGELOG.md` and
`MIGRATION.md` cover what v2 changed on top of it.

Phase numbers below refer to the canonical pipeline in `references/pipeline.md`;
section references use `§`.

## A. Structural changes

### 1. Platform detection replaces a hardcoded project
The original assumed one Android/Kotlin repository. Phase 1 now fingerprints the
stack from build manifests and entry points and supports nine platform classes
plus four product shapes (single-platform, hybrid, monorepo, shared-core,
full-stack). Every finding carries a component name, because "the app validates
input" is meaningless when a product has three clients and one of them does not.

### 2. Conditional standards instead of a fixed list
Applying mobile controls to a CLI tool produces noise; skipping accessibility on
a public web app is negligence. `references/standards-selection-matrix.md` maps
platform × context trigger to a required set, and every exclusion needs a written
reason. An exclusion without a reason is indistinguishable from an oversight.

### 3. A budget model
A 20,000-file monorepo and a 300-file service cannot get the same treatment, and
an audit that silently runs out of context mid-way is worse than one that declares
its limits up front. Three tiers (Deep / Targeted / Survey) with a mandatory
sampling statement in the report.

### 4. Threat model before checklists
The original was checklist-driven, which produces uniform depth regardless of
risk. The standards-and-threat-model stage now requires assets, actors, entry points,
trust boundaries, STRIDE/LINDDUN, and a one-sentence worst credible outcome. That sentence
calibrates every severity in the document.

### 5. Machine-readable state
`.audit/manifest.json` and `.audit/findings.jsonl` make the audit diffable,
which is what makes the delta re-audit mode possible. Reports that get rewritten
from scratch every pass lose institutional memory, and teams stop trusting the ids.

### 6. Delta re-audit mode
Real audits are repeated. `prompts/REAUDIT_DELTA_PROMPT.md` re-verifies open
findings against a new commit, preserves ids, and adds a changelog. Notably it
forbids marking something fixed just because a line number moved.

### 7. Explicit consent gates
Running a project's build scripts executes its code. The original assumed that was
fine. The preflight stage (§0.5) asks once, records the answer, and degrades to
SAFE_READ_ONLY-only analysis when consent is absent — instead of quietly skipping and later implying
the build was clean.

## B. Anti-hallucination hardening

The failure mode of a long audit prompt is a confident, well-formatted document
full of invented line numbers. Four mechanisms address this:

1. **Verification pass** (deep-analysis stage, §5.4) — re-open the file, confirm
   the line, confirm reachability from a real entry point, and check for a
   mitigating guard before the finding leaves the phase. In v2 the mechanical
   half of this became a script.
2. **Reachability requirement** — a finding on unreachable code is a
   maintainability issue, not a defect. Medium-and-above needs a caller chain.
3. **Absence evidence** — "X is missing" must show the search that would have
   found it. This is the single most common unfalsifiable audit claim.
4. **Sampling re-check at report time** — at least ten citations re-verified; if
   one is wrong, all of them get re-checked.

Plus: severity and confidence kept as independent axes (collapsing them is how
audits become either alarmist or negligent), a closed vocabulary for command
results, and a rejected-hypotheses section so disproven ideas are recorded rather
than deleted and re-litigated next quarter.

## C. Content additions

- **Failure-and-recovery journeys** given equal weight to happy paths in the
  product analysis, since that is where most operational pain actually lives.
- **Technical-debt ranking** by complexity × change frequency × criticality,
  using `git log` for churn. A complex file nobody touches is not the problem.
- **Foundation-first rule** — a feature whose subsystem has an open Critical or
  High finding cannot be `Build Now`, regardless of score.
- **Accessibility** promoted from a passing mention to a required section wherever
  a UI exists.
- **Supply chain** promoted from a dependency table to a full domain, matching its
  new position in the OWASP Top 10:2025.
- **Observability** treated as a defect class, not a nice-to-have: a failure
  nobody can see is a failure nobody can fix.
- **Redaction rules** made explicit and mandatory, including for Git history.

## D. Standards assessment

The original set — OWASP MASVS, ISO/IEC 25010, Sonar way — is a reasonable spine
for a mobile app, but it leaves large gaps for a general-purpose audit.

### What the original three cover
| Standard | Covers | Blind spot |
|---|---|---|
| OWASP MASVS | Mobile client security and privacy | Nothing server-side, nothing web, no supply chain, no accessibility |
| ISO/IEC 25010 | Product quality vocabulary | No security *controls*, no process, no regulation |
| Sonar way | Code-level maintainability and reliability | No architecture, no runtime behaviour, no threat context |

### What was added, and why each earns its place

| Added | Fills |
|---|---|
| **OWASP ASVS 5.0** | Requirement-level web/API security. MASVS has no equivalent for the server the mobile app talks to. |
| **OWASP Top 10:2025** | Current risk framing; adds Software Supply Chain Failures and Mishandling of Exceptional Conditions, and folds SSRF into Broken Access Control. |
| **OWASP API Security Top 10** | BOLA and object-property-level authorization, which the generic Top 10 under-weights and which is the most common real-world API breach. |
| **MASWE 1.0 + MASTG 2.0** | MASVS control ids are too abstract to hand a developer. MASWE gives a specific weakness, MASTG gives the test. |
| **OWASP Desktop App Top 10** | Thick-client risks (IPC, local privilege, update integrity, binary planting) that no other standard in the original set touches. |
| **CWE + CWE Top 25 (2025)** | A shared, tool-compatible taxonomy. Every serious finding should carry a CWE id. |
| **CVSS 4.0 + EPSS + CISA KEV** | Separating theoretically severe from actually exploited. Treating every High alike is how remediation queues stall. |
| **ISO/IEC 25002:2024, 25019:2023, 25012** | The 2023 revision split 25010 apart; citing 25010 alone for quality-in-use or data quality is now wrong. |
| **ISO/IEC 5055 (CISQ)** | Bridges Sonar-style automated measures into ISO language — useful when a customer asks for ISO-framed evidence. |
| **NIST SSDF 800-218, SLSA, OpenSSF Scorecard, SBOM** | Build and delivery integrity. None of the original three look at the pipeline at all, which is where several high-profile compromises have started. |
| **EU CRA** | Now a hard deadline rather than a nice-to-have: reporting obligations from 11 Sep 2026, remaining obligations including machine-readable SBOM and CE marking from 11 Dec 2027, for products with digital elements on the EU market — including non-EU manufacturers. |
| **GDPR / UU PDP No. 27/2022 / CCPA** | ISO 25010 has no privacy characteristic. Data-protection obligations need their own hook. |
| **WCAG 2.2 / EN 301 549** | Accessibility is legally required in many markets and entirely absent from all three original standards. |
| **ISO/IEC/IEEE 29119** | Vocabulary and structure for the test-strategy section, so "add more tests" becomes a specific recommendation. |
| **STRIDE + LINDDUN** | Makes the audit risk-driven rather than checklist-driven, and gives privacy a systematic method rather than a vibe check. |
| **SEI CERT / MISRA** | Native and safety-critical code, where memory-safety CWEs dominate. |
| **IEC 62443 / 61508 / 26262 / 62304** | Software that moves things in the physical world needs a safety frame, not just a security one. |
| **OWASP LLM Top 10 / NIST AI RMF / ISO 42001** | Prompt injection, tool permissions, and model-artifact integrity are ordinary application risks now. |
| **Core Web Vitals / Android vitals / store policies** | Concrete, externally enforced thresholds that can block a release regardless of code quality. |

### What was deliberately not added
SOC 2, ISO 27001 certification criteria, and CMMI are organizational, not
codebase, standards — they belong in a programme assessment, not a repository
audit. OWASP SAMM is included only as a reference for maturity recommendations,
not as an evaluation axis. Adding process frameworks to a code audit produces
findings nobody in the repository can act on.

## E. Known trade-offs

- **The prompt is long.** Progressive disclosure (SKILL.md → phase → playbook)
  keeps working context manageable, but a model with a small context window will
  still struggle. The tier system is the mitigation.
- **Depth versus speed.** A full T1 audit is genuinely slow. The quick-triage
  prompt exists for when that is the wrong trade.
- **Standards drift.** Versions in the registry were verified 9 September 2026 and
  will go stale; the registry requires re-verification at audit time rather than
  pretending to be permanent.
- **Static analysis has a ceiling.** Roughly a third of interesting findings in
  concurrent or lifecycle-heavy code cannot be settled without running it. The
  `Needs Runtime Verification` status is an honest answer, not a cop-out — but it
  does mean the audit is a starting point, not a certificate.
