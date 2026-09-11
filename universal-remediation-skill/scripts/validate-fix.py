#!/usr/bin/env python3
"""
validate-fix.py — deterministic gate for a remediation fix record.

Answers one question a language model should never be trusted to answer about
its own work: is this finding actually closed, or does it just look closed?

Stdlib only. Read-only: it inspects a JSON record and, optionally, the repository
it refers to. It never edits anything.

Exit codes: 0 = record is coherent, 1 = validation errors, 2 = usage error.
"""
from __future__ import annotations

import json
import os
import re
import sys

SCHEMA_VERSION = "2.0"

# The vocabularies live in the audit skill so the two cannot drift. Import them
# when the sibling skill is present; fall back to a local copy when it is not,
# and say so, because a silent fallback is how drift starts.
_SHARED = None
for _cand in (
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "universal-audit-skill", "scripts"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "..", "universal-audit-skill", "scripts"),
):
    if os.path.isfile(os.path.join(_cand, "auditkit.py")):
        sys.path.insert(0, _cand)
        try:
            import auditkit as _SHARED  # type: ignore
        except Exception:
            _SHARED = None
        break

BUILD_RESULT = getattr(_SHARED, "COMMAND_RESULT", [
    "Passed", "Passed with warnings", "Partial", "Failed",
    "Not Executed", "Blocked", "Not Applicable"])
RUNTIME_RESULT = getattr(_SHARED, "RUNTIME_RESULT", [
    "PASS", "FAIL", "BLOCKED", "NOT_EXECUTED", "INCONCLUSIVE"])
STATUS = getattr(_SHARED, "STATUS", [
    "CANDIDATE", "VERIFIED_FINDING", "READY_FOR_FIX", "REPRODUCED",
    "FIX_IN_PROGRESS", "FIX_IMPLEMENTED", "VERIFICATION_PASSED",
    "REGRESSION_PASSED", "RE_AUDIT_PASSED", "VERIFIED_FIXED", "REGRESSED",
    "WONT_FIX", "SUPERSEDED", "DUPLICATE", "FALSE_POSITIVE"])

FINDING_ID_RE = re.compile(r"^BUG-\d{3,}$")
FINGERPRINT_RE = re.compile(r"^[0-9a-f]{16}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")

REQUIRED = [
    "schema_version", "finding_id", "original_fingerprint", "baseline_commit",
    "changed_files", "patch_summary", "root_cause", "reproduction_before",
    "verification_after", "build_result", "targeted_tests", "regression_result",
    "rollback_procedure", "status",
]

# Files whose modification during a single-finding fix is nearly always scope
# creep rather than remediation.
COSMETIC = re.compile(r"\.(md|rst|txt|css|scss|less|svg|png|jpe?g|ya?ml|toml|ini|cfg)$", re.I)
DEPENDENCY_FILES = re.compile(
    r"(^|/)(package(-lock)?\.json|yarn\.lock|pnpm-lock\.yaml|requirements[^/]*\.txt|"
    r"poetry\.lock|Pipfile(\.lock)?|pyproject\.toml|go\.(mod|sum)|Cargo\.(toml|lock)|"
    r"Gemfile(\.lock)?|composer\.(json|lock)|build\.gradle(\.kts)?|pom\.xml|"
    r"gradle/libs\.versions\.toml|Podfile(\.lock)?|pubspec\.(yaml|lock))$", re.I)
CONFIG_ESCALATION = re.compile(r"(^|/)(\.github/workflows/|\.gitlab-ci\.yml|Jenkinsfile|"
                               r"Dockerfile|docker-compose[^/]*\.ya?ml)", re.I)

SUPPRESSION_MARKERS = [
    "# noqa", "# type: ignore", "@SuppressWarnings", "eslint-disable",
    "// nolint", "#pragma warning disable", "// @ts-ignore", "// @ts-nocheck",
    "pylint: disable", "rubocop:disable", "checkstyle:off", "detekt:suppress",
]

ISSUES: list[tuple[str, str, str]] = []  # (rule, severity, message)


def err(rule: str, msg: str) -> None:
    ISSUES.append((rule, "error", msg))


def warn(rule: str, msg: str) -> None:
    ISSUES.append((rule, "warning", msg))


def _result_of(block, key: str = "result"):
    if isinstance(block, dict):
        return block.get(key)
    return block


def _artifact_of(block) -> str | None:
    return block.get("artifact_path") if isinstance(block, dict) else None


def validate(rec: dict, repo: str | None = None) -> None:
    # ---------------------------------------------------------------- shape
    for key in REQUIRED:
        v = rec.get(key)
        if v is None or (isinstance(v, (str, list, dict)) and len(v) == 0):
            err("FX000", f"required field '{key}' missing or empty")

    if rec.get("schema_version") != SCHEMA_VERSION:
        err("FX001", f"schema_version must be {SCHEMA_VERSION!r}, got {rec.get('schema_version')!r}")

    if not FINDING_ID_RE.match(str(rec.get("finding_id", ""))):
        err("FX002", "finding_id must match BUG-NNN")

    if not FINGERPRINT_RE.match(str(rec.get("original_fingerprint", ""))):
        err("FX003", "original_fingerprint must be the 16-hex fingerprint carried over "
                     "from the audit finding — it links the fix to what was found")

    if not COMMIT_RE.match(str(rec.get("baseline_commit", ""))):
        err("FX004", "baseline_commit must be a commit hash; without it the patch "
                     "cannot be reproduced or rolled back")

    status = rec.get("status")
    if status not in STATUS:
        err("FX005", f"status {status!r} is not in the shared lifecycle vocabulary")

    for key, allowed in (("build_result", BUILD_RESULT),
                         ("regression_result", RUNTIME_RESULT),
                         ("runtime_result", RUNTIME_RESULT)):
        val = rec.get(key)
        if val is not None and val not in allowed:
            err("FX006", f"{key} = {val!r} is not one of {allowed}")

    before = rec.get("reproduction_before") or {}
    after = rec.get("verification_after") or {}
    b_res, a_res = _result_of(before), _result_of(after)
    for label, res in (("reproduction_before", b_res), ("verification_after", a_res)):
        if res is not None and res not in RUNTIME_RESULT:
            err("FX007", f"{label}.result = {res!r} is not one of {RUNTIME_RESULT}")

    tests = rec.get("targeted_tests") or {}
    t_res = _result_of(tests)
    if t_res is not None and t_res not in RUNTIME_RESULT:
        err("FX008", f"targeted_tests.result = {t_res!r} is not one of {RUNTIME_RESULT}")

    # -------------------------------------------------- evidence for claims
    for label, block, res in (("reproduction_before", before, b_res),
                              ("verification_after", after, a_res)):
        if res in ("PASS", "FAIL") and not _artifact_of(block):
            err("FX009", f"{label} claims {res} without an artifact_path — a result "
                         "nobody can re-read is not evidence")
        if res == "NOT_EXECUTED" and (block.get("observed") if isinstance(block, dict) else None):
            err("FX010", f"{label} is NOT_EXECUTED but records an observation; "
                         "if you observed something, it executed")

    # ------------------------------------------------- the closure gate
    if status == "VERIFIED_FIXED":
        if a_res != "PASS":
            err("FX011", f"status VERIFIED_FIXED with verification_after.result = {a_res!r}. "
                         "The original failure still reproduces (or was never re-checked); "
                         "the finding stays open")
        if b_res != "FAIL" and not rec.get("reproduction_waiver"):
            err("FX012", f"status VERIFIED_FIXED but the defect was never reproduced "
                         f"(reproduction_before.result = {b_res!r}) and no "
                         "reproduction_waiver is recorded — there is nothing the fix proved")
        if rec.get("build_result") not in ("Passed", "Passed with warnings"):
            err("FX013", f"status VERIFIED_FIXED with build_result = "
                         f"{rec.get('build_result')!r}")
        if t_res != "PASS":
            err("FX014", f"status VERIFIED_FIXED with targeted_tests.result = {t_res!r}")
        if rec.get("regression_result") != "PASS":
            err("FX015", f"status VERIFIED_FIXED with regression_result = "
                         f"{rec.get('regression_result')!r}")
        if not rec.get("re_audit") or _result_of(rec.get("re_audit")) != "PASS":
            warn("FX016", "no passing delta re-audit recorded. Independent re-derivation is "
                          "what confirms closure; without it this is FIX_IMPLEMENTED at best")
        if rec.get("runtime_result") == "NOT_EXECUTED":
            warn("FX017", "runtime_result is NOT_EXECUTED. Acceptable when the defect has no "
                          "runtime dimension — state which case applies in remaining_risks")

    if rec.get("reproduction_waiver") and status == "VERIFIED_FIXED" and not rec.get("re_audit"):
        err("FX018", "a waived reproduction cannot reach VERIFIED_FIXED on its own; "
                     "a passing delta re-audit is required")

    if not rec.get("rollback_procedure"):
        err("FX019", "rollback_procedure missing")

    if b_res == "FAIL" and a_res == "FAIL":
        err("FX020", "the defect reproduced before and after the patch — this is not a fix")

    # --------------------------------------------- minimal patch enforcement
    changed = rec.get("changed_files") or []
    if not isinstance(changed, list) or not changed:
        err("MP000", "changed_files must list the files actually modified")
        changed = []

    justified = rec.get("scope_justification") or {}
    if isinstance(justified, list):
        justified = {j.get("file"): j.get("reason") for j in justified if isinstance(j, dict)}
    planned = set((rec.get("fix_plan") or {}).get("files_to_change") or [])

    if len(changed) > 1:
        extras = [f for f in changed[1:] if not justified.get(f) and f not in planned]
        if extras:
            err("MP001", f"{len(changed)} files changed for one finding; no justification for "
                         f"{extras}. Every file beyond the one holding the root cause needs a "
                         "written reason, or it is scope creep")

    for f in changed:
        if COSMETIC.search(f) and not justified.get(f) and not DEPENDENCY_FILES.search(f):
            err("MP002", f"{f} looks unrelated to a code fix (documentation, styling or asset) "
                         "and has no justification")
        if DEPENDENCY_FILES.search(f) and not rec.get("dependency_change_rationale"):
            err("MP003", f"{f} is a dependency manifest or lockfile; a fix may only touch one "
                         "when the finding is the dependency, and it needs "
                         "dependency_change_rationale naming the breaking changes")
        if CONFIG_ESCALATION.search(f) and not justified.get(f):
            err("MP004", f"{f} changes CI or container configuration; justify it or move it "
                         "out of this fix")

    if planned:
        unplanned = [f for f in changed if f not in planned and not justified.get(f)]
        if unplanned:
            err("MP005", f"files changed that were not in fix_plan.files_to_change: {unplanned}")

    lines = rec.get("patch_stats", {}).get("lines_changed")
    expected = (rec.get("fix_plan") or {}).get("expected_lines")
    if isinstance(lines, int) and isinstance(expected, int) and expected > 0:
        if lines > max(expected * 3, expected + 30):
            warn("MP006", f"patch is {lines} lines against a planned ~{expected}. A large "
                          "divergence from the plan is the earliest sign a fix is going wrong")

    # ------------------------------------------------------- suppressions
    diff = rec.get("patch_excerpt") or ""
    if repo and rec.get("patch_path"):
        p = os.path.join(repo, rec["patch_path"])
        if os.path.isfile(p):
            try:
                diff += open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                pass
    added = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    for marker in SUPPRESSION_MARKERS:
        if any(marker.lower() in l.lower() for l in added):
            err("MP007", f"the patch adds a suppression ({marker}). Silencing the detector is "
                         "not fixing the defect")
            break

    # ------------------------------------------------- repository coherence
    if repo:
        missing = [f for f in changed if not os.path.exists(os.path.join(repo, f))]
        if missing:
            warn("FX021", f"changed files not present in the repository: {missing} "
                          "(expected if the fix deleted them — say so in patch_summary)")

    if not rec.get("remaining_risks"):
        warn("FX022", "remaining_risks is empty. 'None' is a valid answer, but it should be a "
                      "decision someone made, not a field nobody filled in")

    if rec.get("new_candidate_findings"):
        for c in rec["new_candidate_findings"]:
            if isinstance(c, dict) and c.get("fixed_here"):
                err("FX023", f"candidate finding {c.get('id', '?')} was fixed inside this pass. "
                             "New defects are recorded and returned to the audit, not fixed "
                             "opportunistically")


def main(argv: list[str]) -> int:
    if "--fix-record" not in argv:
        print("usage: validate-fix.py --fix-record <path.json> [--repo <path>] [--json]")
        return 2
    path = argv[argv.index("--fix-record") + 1]
    repo = argv[argv.index("--repo") + 1] if "--repo" in argv else None

    if not os.path.isfile(path):
        print(f"[ERROR  ] FX000 fix record not found: {path}")
        return 1
    try:
        rec = json.load(open(path, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[ERROR  ] FX000 fix record is not valid JSON: {exc}")
        return 1

    validate(rec, repo)
    errors = [i for i in ISSUES if i[1] == "error"]
    warnings = [i for i in ISSUES if i[1] == "warning"]

    if "--json" in argv:
        print(json.dumps({
            "fix_record": path,
            "finding_id": rec.get("finding_id"),
            "status": rec.get("status"),
            "verdict": "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
            "errors": [{"rule": r, "message": m} for r, _, m in errors],
            "warnings": [{"rule": r, "message": m} for r, _, m in warnings],
        }, indent=2))
    else:
        for rule, sev, msg in ISSUES:
            print(f"[{sev.upper():7}] {rule} {rec.get('finding_id', '?')}: {msg}")
        verdict = "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS")
        print(f"\nfix-record validation: {verdict}  errors={len(errors)} "
              f"warnings={len(warnings)}")
        if _SHARED is None:
            print("note: universal-audit-skill/scripts/auditkit.py not found; used the local "
                  "vocabulary copy. Keep the two in sync.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
