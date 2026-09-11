# Phase 2 — Standards Selection and Threat Model

**Goal:** choose the smallest set of standards that actually applies, record their
versions *and how each version was verified*, build the threat model, and drop
the rest with a reason. This phase owns the threat model — nothing downstream
re-derives it. Applying mobile standards to a CLI tool
produces noise; skipping accessibility on a public web app produces negligence.

Load `references/standards-selection-matrix.md` and
`references/standards-registry.md`.

## 2.1 Selection procedure

1. Start from the platforms detected in Phase 1.
2. Add **context triggers** — these override platform defaults:
   - Handles payments → PCI DSS
   - Handles health data → HIPAA / local health regulation
   - Handles personal data of EU residents → GDPR
   - Handles personal data of Indonesian residents → UU PDP No. 27/2022
   - Sold or distributed in the EU as a product with digital elements → EU CRA
   - Public sector / education / large-market consumer web → WCAG 2.2 + EN 301 549
   - Industrial control, OT, or safety-relevant actuation → IEC 62443 (+ IEC 61508 / ISO 26262 if applicable)
   - Ships an LLM or ML model in the product → OWASP LLM Top 10, NIST AI RMF, ISO/IEC 42001
   - Published to an app store → Google Play / Apple App Store policy requirements
3. Always include the **universal core**: CWE + CWE Top 25, ISO/IEC 25010:2023,
   Sonar way / Clean as You Code, SSDF + SBOM basics, ISO/IEC/IEEE 29119 concepts.
4. For every standard you exclude, write one line explaining why.

## 2.2 Version discipline

For every standard used, record in `manifest.standards_selected`: **name,
version, publisher, url, accessed, verification_status, applicability, trigger,
limitations**.

`verification_status` is one of `Verified` (you checked the publisher this
session), `Unverified` (carried from prior knowledge — say so), or `Unreachable`
(you tried and could not). Never record `Verified` for a version you did not
check. `references/standards-registry.md` carries a starting point with its own
verification dates; it is a starting point, not an authority.

Never cite a superseded taxonomy as if it were current (for example ISO/IEC
25010:2011 subcharacteristics, or MASVS L1/L2/R verification levels, which were
replaced by MAS Testing Profiles).

## 2.3 Threat model first

Before applying any checklist, write a short threat model. This is what makes
the audit proportional instead of mechanical.

- **Assets** — what is worth attacking or losing (credentials, PII, funds, model
  weights, control over a physical actuator, availability of a critical channel).
- **Actors** — anonymous internet, authenticated user, malicious co-located app,
  network attacker (MITM/rogue AP), malicious insider, supply-chain attacker,
  someone with physical device access.
- **Entry points** — HTTP routes, IPC, deep links, exported components, sockets,
  file imports, USB/serial, message queues, third-party callbacks, model inputs.
- **Trust boundaries** — draw them explicitly; most real findings live on one.
- **STRIDE** per boundary for security; **LINDDUN** per data flow for privacy.
- **Worst credible outcome** — one sentence. This calibrates severity for the
  rest of the audit.

## 2.4 Output

| Standard | Version | Verification | Applies to | Applicability | Trigger / exclusion reason | Accessed |
|---|---|---|---|---|---|---|

`Applicability` uses the vocabulary in `references/regulatory-applicability.md`:
`Applicable`, `Potentially Applicable`, `Not Applicable`,
`Applicability Unconfirmed`. For regulatory regimes the honest default is one of
the latter two — most triggers are established outside the repository.

Plus the threat-model summary, which feeds Phase 3's critical-path list.

## Exit gate

- [ ] Standard set fixed, each with version, verification_status, applicability
- [ ] Exclusions justified in one line each
- [ ] Threat model written, trust boundaries named
- [ ] Worst credible outcome stated
