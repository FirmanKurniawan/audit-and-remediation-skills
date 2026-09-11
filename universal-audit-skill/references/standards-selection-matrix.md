# Standards Selection Matrix

Read down the platform column, then apply context triggers. Legend:
**R** required · **C** conditional (trigger below) · **–** not applicable.

| Standard | Web FE | Backend/API | Mobile | Desktop | CLI/Lib | Embedded/IoT | Data/ML | Infra/IaC |
|---|---|---|---|---|---|---|---|---|
| OWASP Top 10:2025 | R | R | C | C | – | C | C | C |
| OWASP ASVS 5.0 | R | R | C¹ | C¹ | – | – | C¹ | – |
| OWASP API Security Top 10 | C² | R | C² | C² | – | C² | C² | – |
| OWASP MASVS / MASWE / MASTG | – | – | R | – | – | C³ | – | – |
| OWASP Desktop App Top 10 | – | – | – | R | – | – | – | – |
| OWASP Top 10 CI/CD | C | C | C | C | C | C | C | R |
| OWASP LLM Top 10 | C⁴ | C⁴ | C⁴ | C⁴ | C⁴ | – | C⁴ | – |
| CWE + CWE Top 25 (2025) | R | R | R | R | R | R | R | R |
| CVSS 4.0 / EPSS / KEV | R | R | R | R | R | R | R | R |
| ISO/IEC 25010:2023 | R | R | R | R | R | R | R | R |
| ISO/IEC 25012 (data quality) | – | C | – | – | – | – | R | – |
| ISO/IEC 5055 (CISQ) | C | C | C | C | C | R | C | – |
| Sonar way / Clean as You Code | R | R | R | R | R | R | R | C |
| SEI CERT / MISRA | – | C⁵ | C⁵ | C⁵ | C⁵ | R | – | – |
| ISO/IEC/IEEE 29119 | R | R | R | R | R | R | R | C |
| NIST SSDF 800-218 | R | R | R | R | R | R | R | R |
| SLSA + SBOM + Scorecard | R | R | R | R | R | R | R | R |
| WCAG 2.2 / EN 301 549 | R | – | R⁶ | R | – | C⁶ | C⁶ | – |
| GDPR / UU PDP / CCPA | C⁷ | C⁷ | C⁷ | C⁷ | C⁷ | C⁷ | C⁷ | C⁷ |
| EU CRA | C⁸ | C⁸ | C⁸ | C⁸ | C⁸ | C⁸ | C⁸ | – |
| PCI DSS | C⁹ | C⁹ | C⁹ | C⁹ | – | C⁹ | – | C⁹ |
| IEC 62443 / 61508 / 26262 / 62304 | – | C¹⁰ | C¹⁰ | C¹⁰ | – | C¹⁰ | – | C¹⁰ |
| NIST AI RMF / ISO 42001 | C⁴ | C⁴ | C⁴ | C⁴ | C⁴ | C⁴ | R⁴ | – |
| Core Web Vitals | R | – | C¹¹ | – | – | – | – | – |
| Android vitals / Play policy | – | – | R¹² | – | – | C¹² | – | – |
| App Store Review + privacy manifest | – | – | R¹³ | C¹³ | – | – | – | – |
| STRIDE + LINDDUN | R | R | R | R | C | R | R | R |
| Twelve-Factor | C | R | – | – | – | – | C | R |

**Triggers**

1. ASVS applies to any HTTP/API surface the component exposes or consumes with
   its own auth logic; use it alongside MASVS for the client, not instead of it.
2. The component exposes or consumes a REST/GraphQL/gRPC API.
3. The device runs a mobile-class OS (Android Things, embedded Android, custom AOSP).
4. The product ships an ML model, LLM feature, agent, or RAG pipeline.
5. The component includes C, C++, Rust `unsafe`, or JNI/FFI code.
6. Any user-facing interface. For embedded/data, applies when there is an operator
   HMI or a reporting UI.
7. Personal data is collected, stored, or transmitted — pick by data-subject
   jurisdiction, not company location.
8. The product (or a component of it) is placed on the EU market as a product with
   digital elements.
9. Cardholder data is stored, processed, or transmitted — including via a redirect
   integration, which reduces but does not eliminate scope.
10. The software controls, monitors, or informs physical processes, vehicles, or
    medical devices. Pick the sector-specific one.
11. The mobile app embeds webviews serving web content to users.
12. Distributed via Google Play.
13. Distributed via the Apple App Store (iOS/macOS).

## Hybrid products

For a multi-platform product, take the **union** of the applicable sets and
evaluate each control **per surface**. A shared backend does not inherit a pass
because the mobile client got one. Record the matrix per component in Phase 2 and
keep the component name on every finding.

For shared-core architectures (KMP, Rust core + FFI, shared TS domain), audit the
core once against the strictest applicable set, then audit each shell for its
platform-specific surface (permissions, storage, IPC, packaging).

## Deliberate exclusions

Write one line per excluded standard, e.g.:

> PCI DSS — Not Applicable. No cardholder data path found; payments are handled
> by a hosted checkout redirect (`src/checkout/provider.ts:88`) and no PAN, CVV,
> or track data appears in the codebase or schema.

An exclusion without a reason is indistinguishable from an oversight.
