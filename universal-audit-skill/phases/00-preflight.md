# Phase 0 — Preflight

**Goal:** establish safety, scope, and a realistic budget before reading code.

## 0.1 Repository safety check

Read-only Git commands only:

```bash
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --porcelain
git log -15 --pretty='%h %ad %an %s' --date=short
```

Record uncommitted changes. **Do not stash, reset, or clean them.** If the tree
is dirty, say so in Document Control — findings may not match `HEAD`.

If the repository is not a Git repo, note it, use directory mtime for recency,
and set commit fields to `N/A`.

## 0.2 Size and shape

```bash
find . -path ./node_modules -prune -o -path ./.git -prune -o -type f -print | wc -l
du -sh . 2>/dev/null
```

Also count files per language and locate the largest source directories. This
drives the tier choice.

## 0.3 Choose an audit tier

| Tier | Trigger | Depth |
|---|---|---|
| **T1 Deep** | < ~800 source files, single app | Read every critical-path file end to end; line-level findings everywhere |
| **T2 Targeted** | ~800–5,000 files, or 2–4 modules | Full read of security/critical-path files; sampled read elsewhere; declare the sampling rule |
| **T3 Survey** | > ~5,000 files, monorepo, or many services | Architecture + config + dependency + entry-point analysis; deep-dive at most 3 subsystems chosen by risk; everything else explicitly out of scope |

Write the chosen tier and its justification into the manifest. In T2/T3, the
report's *Known Limitations* section must list what was **not** read.

## 0.4 Secret-handling posture

Before reading config files, commit to the redaction rule: any value that looks
like a credential, key, token, certificate, private endpoint, personal
identifier, or operational callsign is referenced by
`path:line — <class of secret>` and **never** reproduced, not even partially,
not even in a code excerpt. Truncate excerpts to exclude the value.

## 0.5 Consent gates

Read `references/command-safety-model.md` first — consent is scoped by command
class, not granted wholesale. Ask once, and record the answers in the manifest
under `consent`:

- May I run CONTROLLED_EXECUTION commands (build, tests, linters in report mode)?
  These execute project and third-party code.
- May I run REQUIRES_CONSENT commands (network: dependency resolution, advisory
  lookup)? This is a separate question from the one above.
- Is a runtime, device, or staging environment available for verification?
- Any directories, vendored code, or generated code to exclude?

If the user is unavailable, assume **SAFE_READ_ONLY only**, mark every other row
`Not Executed` with the reason, and continue statically. Never silently skip this
and later imply a build was clean.

PROHIBITED commands are never run, whatever the answer.

## 0.6 Initialize state

Create `.audit/` and instantiate `manifest.json` from
`templates/AUDIT_MANIFEST.template.json` (schema 2.0). Validate it early:

```bash
python3 scripts/validate-manifest.py --manifest .audit/manifest.json
```

A manifest that fails now will fail the gate at the end; catching it here costs
nothing.

## Exit gate

- [ ] Git state recorded, nothing mutated
- [ ] Tier chosen and justified
- [ ] Redaction rule committed to
- [ ] Consent recorded per command class (granted, denied, or unavailable)
- [ ] `.audit/manifest.json` created and passing `validate-manifest.py`
