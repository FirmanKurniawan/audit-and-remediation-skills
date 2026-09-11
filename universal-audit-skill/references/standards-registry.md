# Standards Registry

A **starting point, not an authority.** Every entry carries a verification status;
the audit re-verifies what it relies on and records its own
`verification_status` in the manifest (`Verified` / `Unverified` / `Unreachable`).

| Status in this file | Meaning |
|---|---|
| **[V 2026-09-09]** | Checked against a primary or reliable secondary source on that date |
| **[U]** | Carried from prior knowledge; not checked this pass. Treat as a hypothesis |

Several of these move annually. Cite standards as
`Name Version (publisher, date; accessed <date>)`, and never record `Verified`
for something you did not check yourself.

## Application security

| Standard | Version / edition | Notes |
|---|---|---|
| OWASP Top 10 **[V 2026-09-09]** | **2025** (announced Nov 2025, final Jan 2026) | Supersedes 2021. Adds *Software Supply Chain Failures* and *Mishandling of Exceptional Conditions*; SSRF folded into Broken Access Control; misconfiguration rose. ~249 mapped CWEs. |
| OWASP ASVS **[V 2026-09-09]** | **5.0.0** (May 2025) | Web apps, APIs, web services. 17 chapters, ~350 requirements. Cite as `v5.0.0-<chapter>.<section>.<req>`. Level model revised — do not reuse 4.0 level numbering. |
| OWASP API Security Top 10 **[U]** | 2023 | BOLA, broken object property level authorization, unrestricted resource consumption, etc. |
| OWASP WSTG **[U]** | 4.x | Web test procedures. |
| OWASP MASVS **[V 2026-09-09]** | **2.x** (2.1.0 added MASVS-PRIVACY) | Eight groups: STORAGE, CRYPTO, AUTH, NETWORK, PLATFORM, CODE, RESILIENCE, PRIVACY. **No L1/L2/R levels since 2.0** — those became MAS Testing Profiles. |
| OWASP MASWE **[V 2026-09-09]** | **1.0.0** (17 Aug 2026) | First stable weakness enumeration, 78 weaknesses across the eight MASVS groups. Use MASWE ids in findings — they are actionable in a way MASVS control ids are not. |
| OWASP MASTG **[V 2026-09-09]** | **2.0.0** (June 2026) | Modular tests; every test links to a MASWE weakness. Chain: MASVS control → MASWE weakness → MASTG test → demo. |
| OWASP Desktop App Security Top 10 **[U]** | draft/1.x | Thick-client risks; supplement with platform-specific guidance (Electron security checklist, macOS hardened runtime, Windows AppContainer). |
| OWASP Top 10 CI/CD Security Risks **[U]** | 2022+ | Pipeline and runner risks. |
| OWASP Top 10 for LLM Applications **[U]** | 2025 | Only when the product ships an LLM feature. |
| OWASP SAMM **[U]** | 2.x | Programme maturity, not code — use for the maturity recommendations section. |
| OWASP Proactive Controls **[U]** | current | Developer-facing counterpart to the Top 10. |

## Weakness and risk taxonomy

| Standard | Version | Notes |
|---|---|---|
| CWE | current release | Cite specific CWE ids on every security finding. |
| CWE Top 25 **[V 2026-09-09]** | **2025** (published Dec 2025) | Built from 39,080 CVEs (Jun 2024–Jun 2025). XSS still #1; SQLi #2; CSRF #3; missing authorization up to #4; buffer overflow variants re-entered. |
| CAPEC | current | Attack patterns, for repro reasoning. |
| CVSS **[U]** | **v4.0** | Use only when the vector is defensible; record the full vector string. Never invent a score. |
| EPSS | current model | Exploitation likelihood — pairs with CVSS to avoid treating all Highs alike. |
| SSVC | current | Decision-tree triage; useful when CVSS overstates risk for a local app. |
| CISA KEV | live catalog | Known exploited — a KEV hit escalates priority regardless of CVSS. |

## Product and code quality

| Standard | Version | Notes |
|---|---|---|
| ISO/IEC 25010 **[V 2026-09-09]** | **2023** | Product quality model only. Nine characteristics; **Safety added**; Usability → Interaction Capability; Portability → Flexibility. Do not use the 2011 list. |
| ISO/IEC 25002 **[V 2026-09-09]** | **2024** | Quality model overview and usage; how the SQuaRE models fit together. |
| ISO/IEC 25019 **[V 2026-09-09]** | **2023** | Quality-in-use model (three characteristics) — split out of 25010:2011. |
| ISO/IEC 25012 | 2008 | Data quality model — use when the product is data-centric. |
| ISO/IEC 5055 | 2021 | CISQ automated source code measures for reliability, security, performance efficiency, maintainability. Good bridge between Sonar output and ISO language. |
| ISO/IEC 25040 / 2504n | current | Evaluation process, if a formal evaluation is requested. |
| Sonar way / Clean as You Code | current | Quality gate on new code; issue taxonomy (bug, vulnerability, security hotspot, code smell); cognitive complexity. |
| SEI CERT coding standards | per language | C, C++, Java, Perl, Android. Strong for native and memory-safety findings. |
| MISRA C/C++ | current | Only for safety-critical embedded. |

## Testing

| Standard | Version | Notes |
|---|---|---|
| ISO/IEC/IEEE 29119 | 2021–2022 parts | Test process, documentation, techniques. Use the vocabulary; do not impose the full documentation set on a small team. |
| ISO/IEC/IEEE 42010 | 2022 | Architecture description — for the system-map section. |

## Supply chain and secure development

| Standard | Version | Notes |
|---|---|---|
| NIST SSDF SP 800-218 | 1.1 (+ 800-218A for generative AI) | Practice groups PO/PS/PW/RV — map process gaps here. |
| NIST CSF | 2.0 (2024) | Organizational framing; includes the Govern function. |
| SLSA **[V 2026-09-09]** | **v1.2** current on slsa.dev; v1.1 was the prior approved version (v1.0 retired) | Build track stable; source and build-environment tracks still maturing. |
| OpenSSF Scorecard / Baseline | current | Repo hygiene checks that map directly to findings. |
| SBOM formats **[V 2026-09-09]** | **CycloneDX 1.7** (Oct 2025; ECMA-424 2nd ed. Dec 2025 — last of the 1.x line) · **SPDX 3.0.1** (3.0 line from Apr 2024; 3.1 RC in progress; SPDX 2.2.1 is the version standardised as ISO/IEC 5962:2021) | Either satisfies the CRA's machine-readable requirement. |
| in-toto / Sigstore | current | Attestation and signing. |
| NIST SP 800-63 | Rev. 4 (2024) | Digital identity / authentication assurance. |
| NIST SP 800-171 / 800-53 | current revisions | Only if the customer requires them. |

## Regulation (apply only when triggered — see the selection matrix)

| Regulation | Key dates / notes |
|---|---|
| **EU Cyber Resilience Act (CRA)** **[V 2026-09-09]** | In force 10 Dec 2024. Vulnerability/incident **reporting obligations from 11 Sep 2026**; remaining obligations incl. machine-readable SBOM, secure-by-design, CE marking **from 11 Dec 2027**. Applies to products with digital elements placed on the EU market, including non-EU manufacturers. |
| NIS2 | Sectoral operator obligations; may flow down to suppliers. |
| GDPR | EU personal data. |
| UU PDP No. 27/2022 (Indonesia) | Indonesian personal data protection; check current implementing regulations at audit time. |
| CCPA/CPRA | California. |
| PCI DSS | 4.x — card data. |
| HIPAA | US health data. |
| ISO/IEC 27001 / 27002 / 27701 | ISMS and privacy information management. |
| ISO/IEC 42001 | AI management system, when AI is in the product. |
| NIST AI RMF | 1.0 — AI risk framing. |

## Accessibility

| Standard | Version | Notes |
|---|---|---|
| WCAG | **2.2** (AA is the usual target) | Web and, by convention, desktop UIs. |
| EN 301 549 | current | EU public procurement; references WCAG. |
| Section 508 / ADA | current | US. |
| Platform a11y guidance | Android accessibility, Apple Accessibility (HIG) | Mobile specifics. |
| WAI-ARIA APG | current | Correct patterns for custom widgets. |

## Safety and industrial (conditional)

| Standard | Notes |
|---|---|
| IEC 62443 | Industrial automation and control system security. |
| IEC 61508 | Functional safety, general. |
| ISO 26262 | Automotive functional safety. |
| IEC 62304 | Medical device software. |
| DO-178C | Airborne software. |

## Performance and platform policy

| Reference | Notes |
|---|---|
| Core Web Vitals (LCP, INP, CLS) | Web user-experience budgets. |
| RAIL model | Web interaction budgets. |
| Android vitals (ANR rate, crash rate, wakeups) | Play Console thresholds. |
| Google Play policy: target API level, Data safety, permissions | Blocking for release. |
| Apple App Store Review Guidelines, privacy manifests, required-reason APIs | Blocking for release. |

## Engineering practice (soft references)

Twelve-Factor App · C4 model and arc42 for architecture documentation · DORA
metrics and SPACE for delivery health · Semantic Versioning · Conventional Commits.


## Using this registry

1. Take the entry as a hypothesis.
2. If the finding depends on the version — a control id, a deprecation, a
   deadline — verify it against the publisher and record `Verified` with today's
   date.
3. If you cannot reach the network, record `Unverified` and say so in the report's
   limitations. Do not upgrade an `[U]` to `Verified` because it sounds right.
4. Never cite a superseded taxonomy as current: ISO/IEC 25010:2011
   subcharacteristics, MASVS L1/L2/R verification levels (replaced by MAS Testing
   Profiles), and OWASP Top 10:2021 as "the" Top 10 are the three that recur.
