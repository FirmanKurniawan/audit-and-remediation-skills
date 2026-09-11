# Phase 6 — Security, Supply Chain, and Privacy

**Goal:** a defensible security position with evidence, using the standard set
chosen in Phase 2.

## 6.1 Control review by domain

Adapt the depth to the platform. The domains below are universal; the
verification technique comes from the platform playbook and from ASVS (web/API),
MASVS+MASWE+MASTG (mobile), or the desktop checklist.

**Identity and access** — authentication mechanism and its weakest path, session
issuance/rotation/expiry/revocation, logout completeness, password and token
storage, MFA, account recovery, and authorization enforced server-side (or
trust-side) on *every* privileged operation rather than in the UI. Check for
horizontal (IDOR/BOLA) and vertical escalation on each resource-bearing endpoint.

**Data protection at rest** — what is stored, where, in what form, with what
lifetime. Hardcoded secrets. Keys in source or config. Platform keystore/keychain
usage. Backup and export inclusion. Cache, temp files, logs, clipboard,
screenshots, notifications. Deletion on logout and on uninstall.

**Cryptography** — algorithm and mode choice, key derivation, key lifecycle and
rotation, IV/nonce handling, randomness source, hashing with salt for
credentials, certificate and signature validation, and any hand-rolled crypto
(which is a finding by default). Note post-quantum exposure only if the product's
lifetime makes it relevant.

**Transport** — TLS enforcement and version, certificate and hostname validation,
any trust-all path (including debug-only code that ships), pinning and its
operational risk, cleartext fallbacks, sensitive data in URLs, redirect handling,
CORS, cookie flags, protocol downgrade, and unauthenticated or unencrypted
custom protocols.

**Platform surface** — whatever the OS exposes: HTTP routes and their auth, IPC,
exported components and intents, deep links, URL handlers, file handlers,
permissions requested versus needed, sandboxing, `postMessage`/webview bridges,
native bridges, and process privilege.

**Code and configuration** — injection sinks (SQL, command, template, path,
LDAP, XPath, deserialization), SSRF, unsafe reflection or dynamic loading,
debug artifacts in release, verbose errors, dangerous defaults, and
build-configuration drift between debug and production.

**Resilience** — only if the threat model justifies it. Obfuscation, integrity
checks, anti-tamper, and root/debugger detection are appropriate for
high-value or offline-licensed clients and inappropriate noise for an internal
tool. Say which case applies.

## 6.2 Supply chain

- Inventory direct and transitive dependencies with versions and licenses.
- Check lockfile presence and integrity pinning.
- Look for advisories against the actual versions in the lockfile, not the
  declared ranges. Score with CVSS v4.0 where a vector is defensible; use EPSS
  and the CISA KEV catalog to separate theoretical from exploited.
- Flag unmaintained packages, single-maintainer critical deps, install scripts,
  typosquat-prone names, vendored copies of upstream code, and binaries committed
  to the repo.
- Assess build integrity against SSDF and SLSA concepts: is the build
  reproducible, are artifacts signed, is provenance recorded, are CI secrets
  scoped, can a PR from a fork reach a privileged runner?
- SBOM: does one exist, is it machine-readable, is it regenerated per release?
  If the product is placed on the EU market, note the CRA timeline explicitly
  (vulnerability reporting obligations from 11 Sep 2026; remaining obligations
  including SBOM and CE marking from 11 Dec 2027) — verify current status at
  audit time.

Table format:

| Dependency | Version in lock | Latest verified | Risk | Advisory | Breaking-change risk | Recommendation |
|---|---|---|---|---|---|---|

Never recommend a major upgrade without naming the breaking changes.

## 6.3 Privacy

Apply LINDDUN to each data flow. Then check:

- **Minimization** — is each collected field necessary and used?
- **Purpose and consent** — is collection disclosed, is consent real and revocable?
- **Retention and deletion** — is there a defined lifetime and a working delete path?
- **Third parties** — SDKs, analytics, crash reporting: what leaves the device or
  server, to whom, and is it disclosed?
- **Identifiers** — device ids, advertising ids, fingerprinting, stable ids in logs.
- **Sensitive-signal indicators** — camera, microphone, location, screen capture:
  is the user aware while it is happening?
- **Logs** — the most common privacy leak. Check every log statement on the
  auth, payment, and personal-data paths.
- **Regulatory hooks** — GDPR (EU), UU PDP No. 27/2022 (Indonesia), CCPA/CPRA
  (California), plus sectoral rules. Report *gaps against requirements*, never a
  compliance verdict: you are not the auditor of record.

## 6.4 Security matrix

| Domain / control group | Applicable | Status | Evidence | Findings | Remaining tests |
|---|---|---|---|---|---|

Status: `Pass` · `Partial` · `Fail` · `Not Tested` · `Not Applicable`.
`Pass` requires positive evidence that the control exists and works — the absence
of a finding is not a pass.

## Exit gate

- [ ] Every applicable domain has a status with evidence
- [ ] Dependency risks tied to lockfile versions
- [ ] Privacy flows reviewed, log leakage checked
- [ ] No compliance verdict claimed without evidence
- [ ] No secret values reproduced anywhere
