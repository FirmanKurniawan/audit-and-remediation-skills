# Universal Audit & Remediation Skills

Two AI agent skills that split a job most tools conflate: **finding** defects and
**fixing** them.

| Skill | Role | Touches source? |
|---|---|---|
| [`universal-audit-skill`](universal-audit-skill/) | Platform-agnostic, evidence-based repository audit. Produces a machine-validated findings ledger plus `BUG_ANALYSIS.md` and `PRODUCT_FEATURE_ANALYSIS.md`. | **No** |
| [`universal-remediation-skill`](universal-remediation-skill/) | Fixes validated findings, one at a time, under reproduction / minimal-patch / build / verification / regression / re-audit gates. | Yes, under explicit consent |

## Why they are separate, and why they live in one repository

Separate because an agent that both finds and fixes has an incentive to decide an
inconvenient finding was never real. Closure is decided by a verification
procedure written before anyone was invested in the fix, and confirmed by a
re-audit that re-derives the finding independently.

One repository because they share a contract: the remediation skill imports the
audit skill's vocabularies from `universal-audit-skill/scripts/auditkit.py`, the
audit skill's test suite validates the remediation skill's gate, and their
versions move together. Two repositories would mean two sources of truth for the
same vocabulary — exactly the drift this design exists to prevent.

## Install

Pick the agent platform you use.

### Claude Code / Claude Cowork

```bash
git clone <this-repo> ~/src/audit-skills

# expose both skills to your agent
mkdir -p ~/.claude/skills
ln -s ~/src/audit-skills/universal-audit-skill        ~/.claude/skills/universal-code-audit
ln -s ~/src/audit-skills/universal-remediation-skill  ~/.claude/skills/universal-remediation
```

Symlinks keep the two side by side on disk, which the sibling-path lookups
depend on. Then ask: *"Audit this repository."*

### MiniMax Code / Mavis

```powershell
git clone <this-repo> C:\Users\<you>\src\audit-skills

# user-global install — visible to every agent on this profile
$Skills = Join-Path $env:USERPROFILE '.minimax\skills'
New-Item -ItemType Junction -Path (Join-Path $Skills 'universal-audit-skill')      -Target 'C:\Users\<you>\src\audit-skills\universal-audit-skill'
New-Item -ItemType Junction -Path (Join-Path $Skills 'universal-remediation-skill') -Target 'C:\Users\<you>\src\audit-skills\universal-remediation-skill'
```

Junctions are the Windows equivalent of symlinks — they keep both skills
side by side without duplicating files, so the remediation skill's
sibling-path lookups still resolve. **Open a new chat after this** — Mavis
only picks up newly installed skills on the next session.

On macOS / Linux with Mavis, the same layout uses `~/.mavis/skills/` and
`ln -s` exactly like the Claude block above.

Prefer a plain prompt? `universal-audit-skill/prompts/MASTER_PROMPT.md`
(English) or `MASTER_PROMPT.id.md` (Bahasa Indonesia).

## Verify the install

### macOS / Linux / WSL

```bash
cd ~/src/audit-skills/universal-audit-skill
python3 tests/make_fixtures.py --clean
python3 tests/run_tests.py
```

### Windows / PowerShell

```powershell
cd C:\Users\<you>\src\audit-skills\universal-audit-skill
py tests\make_fixtures.py --clean
py tests\run_tests.py
```

Expect **85 PASS, 0 FAIL, 1 NOT_EXECUTED**. The one not executed is the agent
detection-rate benchmark, which needs a model run and is described in
`universal-audit-skill/tests/AGENT_BENCHMARK.md`. It is reported honestly rather
than faked.

## Design principles

1. Evidence or it does not exist — and a script checks, so it is not a matter of
   the model's diligence.
2. Severity, confidence, exploitability and priority are four axes, never collapsed.
3. Instruments only where they mean something: CWE on weaknesses, EPSS and KEV
   only with a real CVE, CVSS only with a defensible vector.
4. Applicability before compliance — gaps and rationales, never legal verdicts.
5. Finding identity survives refactoring: fingerprints derive from semantics, not
   line numbers.
6. Command safety by class; controlled execution is bracketed by repository-state
   snapshots.
7. An audit completes when the validator says so, not when the documents are written.
8. Fix the finding, never the evidence.

## License

MIT.
