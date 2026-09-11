# Phase 4 — Build, Test, and Static Analysis

**Goal:** turn claims into observations, under the command safety model.

Read `references/command-safety-model.md` before running anything. Every command
is classified, consent is scoped by class, and CONTROLLED_EXECUTION is bracketed
by a repository-state snapshot. This phase owns command evidence: any later phase
that runs something records it here, through the same contract.

## 4.1 Environment inventory

Record actual versions, not documented ones:

```bash
# generic
git --version; node --version; npm --version; python3 --version; java -version
# per stack, as relevant
./gradlew --version; ./mvnw --version; go version; cargo --version
dotnet --info; swift --version; flutter --version; rustc --version
```

Also record: package manager and lockfile presence, required env vars and which
are missing, container/runtime versions, target platform versions (compileSdk /
targetSdk / minSdk, browserslist, `engines`, framework target, deployment target).

## 4.2 Discover tasks before running them

Never guess a command. Enumerate first:

```bash
cat package.json | head -60          # scripts block
./gradlew tasks --all | head -80
make help 2>/dev/null || cat Makefile | head -40
cat Taskfile.yml justfile 2>/dev/null
```

## 4.3 Run, in this order, stopping at the first that is not permitted

| Step | Typical commands |
|---|---|
| Install / restore | `npm ci`, `pip install -r requirements.txt`, `bundle install`, `go mod download` |
| Compile / build | `npm run build`, `./gradlew assembleDebug`, `cargo build`, `dotnet build`, `flutter build` |
| Type check | `tsc --noEmit`, `mypy`, `pyright` |
| Lint | `eslint`, `ruff`, `detekt`, `ktlint`, `clippy`, `./gradlew lint`, `swiftlint`, `golangci-lint` |
| Test | `npm test`, `pytest`, `./gradlew test`, `go test ./...`, `cargo test` |
| Coverage | `jest --coverage`, `pytest --cov`, JaCoCo/Kover, `cargo llvm-cov` |
| Dependency audit | `npm audit`, `pip-audit`, `osv-scanner`, `cargo audit`, `./gradlew dependencies` |
| SBOM | `syft`, `cyclonedx-*`, `npm sbom` |
| Secret scan | `gitleaks detect --no-git` (report locations only, never values) |

Rules:
- **Read-only flags only.** Never `--fix`, `--write`, `-u`, `--update`.
- Do not install new tooling or edit build files to make a tool run. If the tool
  is absent, that absence is itself a finding — recommend adopting it, with
  `absence` evidence showing the search.
- Capture raw output to `.audit/evidence/<step>.txt` and cite it.
- Time-box long steps; a truncated run is `Partial`, not `Passed`.

### Bracketing a controlled execution

```bash
git -C "$REPO" rev-parse HEAD; git -C "$REPO" branch --show-current
git -C "$REPO" status --porcelain | tee /tmp/pre.txt | wc -l
# ... run the command, capturing output ...
git -C "$REPO" status --porcelain | tee /tmp/post.txt | wc -l
diff /tmp/pre.txt /tmp/post.txt
```

Record both snapshots in the command record. New files under a known build output
directory are expected. **Any change to tracked source, a manifest, a lockfile, or
CI config sets `source_modified: true` — stop, tell the user which command did it,
and do not revert it yourself.** The validator rejects a controlled execution
record without both snapshots (M012).

## 4.4 Build failure classification

If something fails, classify the cause before blaming the code:

`Environment` · `Missing SDK/toolchain` · `Missing local config or secret` ·
`Unreachable dependency repository` · `Source compilation error` ·
`Resource/asset error` · `Manifest/config merge` · `Native/FFI compilation` ·
`Test failure` · `Version incompatibility` · `Flaky/nondeterministic`

Only `Source compilation error`, `Test failure`, and reproducible
`Version incompatibility` are application defects. Environment problems are
documented as audit limitations, not as bugs — unless the project claims a
reproducible build, in which case irreproducibility *is* the defect.

## 4.5 Evidence table (goes into the report verbatim)

| Check | Command | Class | Result | Evidence | Source modified | Notes |
|---|---|---|---|---|---|---|
| Build | `npm run build` | CONTROLLED_EXECUTION | Passed | `.audit/evidence/build.txt` | no | 42s, 3 warnings |
| Tests | `npm test` | CONTROLLED_EXECUTION | Failed (2/118) | `.audit/evidence/test.txt` | no | see BUG-007 |
| Lint | `eslint .` | CONTROLLED_EXECUTION | Not Executed | — | — | consent not granted |

Allowed results: `Passed`, `Passed with warnings`, `Partial`, `Failed`,
`Not Executed`, `Blocked`, `Not Applicable`. Nothing else.

## 4.6 Static analysis without running anything

Even with zero execution consent, these are always available:
grep/AST search for dangerous APIs, config review, dependency manifest review
against advisory knowledge, control-flow reading of critical paths, and
comparison of declared versus actual behaviour.

## Exit gate

- [ ] Environment versions recorded from real output
- [ ] Every command classified before it ran
- [ ] Every controlled execution has before/after repository state
- [ ] Every attempted command has captured output
- [ ] Failures classified by cause
- [ ] No `Passed` without evidence
- [ ] `validate-manifest.py` clean on the command records
