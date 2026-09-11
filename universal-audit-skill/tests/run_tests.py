#!/usr/bin/env python3
"""
Test suite for universal-audit-skill.

Scope, stated plainly: this exercises the *deterministic* parts of the skill —
the validator, the fingerprint function, the schemas, the fixture line
references, the documentation's internal consistency, and the platform-detection
heuristics. It does not and cannot measure how well a language model finds
defects; that requires an agent run against the fixtures and is reported
separately as NOT_EXECUTED unless someone actually runs it.

Exit code 0 only when every executed test passes.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import auditkit as A  # noqa: E402

CASES_DIR = os.path.join(HERE, "cases")
FIXTURES = os.path.join(HERE, "fixtures")

RESULTS: list[tuple[str, str, str]] = []  # (suite, name, status)
DETAIL: list[str] = []


def record(suite: str, name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((suite, name, "PASS" if ok else "FAIL"))
    if not ok and detail:
        DETAIL.append(f"  {suite}/{name}: {detail}")


def skip(suite: str, name: str, why: str) -> None:
    RESULTS.append((suite, name, "NOT_EXECUTED"))
    DETAIL.append(f"  {suite}/{name}: NOT_EXECUTED — {why}")


# --------------------------------------------------------------------------
# Finding builders
# --------------------------------------------------------------------------

def base_finding(**over) -> dict:
    f = {
        "schema_version": A.SCHEMA_VERSION,
        "id": "BUG-001",
        "audited_commit": "0" * 40,
        "component": "backend-api",
        "platform": "backend-api",
        "finding_class": "functional",
        "category": "error-handling",
        "title": "Retry loop swallows the cancellation exception",
        "severity": "Medium",
        "priority": "P2",
        "confidence": "Highly Likely",
        "epistemic": "Inference",
        "status": "VERIFIED_FINDING",
        "effort": "S",
        "locations": [{
            "file": "src/server.js", "line_start": 8, "line_end": 8,
            "symbol": "search", "verified_at": "2026-09-10",
            "excerpt": "db.all(\"SELECT ... LIKE '%\" + term + \"%'\")",
        }],
        "evidence": [{"type": "code", "ref": "src/server.js:8",
                      "excerpt": "db.all(\"SELECT ... LIKE '%\" + term + \"%'\")"}],
        "reachability": {"status": "Confirmed", "entry_point": "GET /search",
                         "caller_chain": ["GET /search", "handler", "db.all"]},
        "reproduction": {"status": "Static Only", "procedure": ["call GET /search?q=x"],
                         "expected": "parameterised query", "observed": "string concatenation"},
        "verification": {"procedure": "add an integration test asserting a bound parameter",
                         "expected_evidence": "query log shows a placeholder", "level": "integration"},
        "remediation": {"strategy": "use a bound parameter for the LIKE term"},
        "impact": "A crafted term alters the query shape.",
        "root_cause": "Query assembled by concatenation instead of binding.",
        "mappings": {},
    }
    f.update(over)
    f["fingerprint"] = A.compute_fingerprint(f)
    return f


def sec_finding(**over) -> dict:
    f = base_finding(finding_class="security", category="injection")
    f["mappings"] = {"cwe": ["CWE-89"]}
    f.update(over)
    f["fingerprint"] = A.compute_fingerprint(f)
    return f


# --------------------------------------------------------------------------
# Suite 1 — validator rule coverage
# --------------------------------------------------------------------------

def suite_validator() -> None:
    os.makedirs(CASES_DIR, exist_ok=True)

    def broken(f: dict, **over) -> dict:
        """Apply a mutation *after* fingerprinting where the mutation is not
        supposed to invalidate the fingerprint."""
        f = dict(f)
        f.update(over)
        return f

    cases: list[tuple[str, list[dict], list[str], list[str]]] = []
    # (name, findings, must_fire, must_not_fire)

    cases.append(("valid-functional", [base_finding()], [], ["F"]))
    cases.append(("valid-security", [sec_finding(
        mappings={"cwe": ["CWE-89"], "cve": [], "epss": "Not Applicable",
                  "kev": "Not Applicable", "cvss": A.CVSS_NOT_SCORED},
        severity="High", priority="P1")], [], ["F"]))
    cases.append(("valid-dependency-cve", [sec_finding(
        id="BUG-002", finding_class="supply_chain", category="vulnerable-dependency",
        mappings={"cwe": ["CWE-1395"], "cve": ["CVE-2024-12345"], "epss": 0.42, "kev": True,
                  "cvss": {"version": "4.0", "vector": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N",
                           "score": 9.3}},
        severity="High", priority="P1")], [], ["F"]))

    cases.append(("epss-without-cve", [sec_finding(
        mappings={"cwe": ["CWE-89"], "cve": [], "epss": 0.7})], ["F044"], []))
    cases.append(("kev-without-cve", [sec_finding(
        mappings={"cwe": ["CWE-89"], "cve": [], "kev": True})], ["F046"], []))
    cases.append(("cvss-without-vector", [sec_finding(
        mappings={"cwe": ["CWE-89"], "cvss": {"score": 7.5}})], ["F048"], []))
    cases.append(("cwe-on-functional-defect", [base_finding(
        mappings={"cwe": ["CWE-20"]})], ["F042"], []))
    cases.append(("security-without-cwe", [sec_finding(mappings={})], ["F041"], []))
    cases.append(("fabricated-fingerprint", [broken(base_finding(), fingerprint="deadbeefdeadbeef")],
                  ["F006"], []))
    cases.append(("missing-evidence", [broken(base_finding(), evidence=[])], ["F020"], []))
    cases.append(("impossible-line-range", [broken(base_finding(), locations=[{
        "file": "src/server.js", "line_start": 40, "line_end": 2,
        "verified_at": "2026-09-10"}])], ["F026"], []))
    cases.append(("unverified-line-citation", [broken(base_finding(), locations=[{
        "file": "src/server.js", "line_start": 8, "line_end": 8}])], ["F027"], []))
    cases.append(("duplicate-id", [base_finding(), base_finding(
        category="other", title="A different problem entirely here")], ["F003"], []))
    cases.append(("no-location-no-absence", [broken(base_finding(), locations=[],
                  evidence=[{"type": "code", "excerpt": "x"}])], ["F023"], []))
    cases.append(("confirmed-but-unreachable-proof", [broken(base_finding(
        confidence="Confirmed", severity="High", priority="P1"),
        reachability={"status": "Unconfirmed"})], ["F029"], []))
    cases.append(("runtime-confidence-static-verification", [broken(base_finding(
        confidence="Needs Runtime Verification"),
        verification={"procedure": "p", "expected_evidence": "e", "level": "static"})],
        ["F038"], []))
    cases.append(("priority-divergence-unexplained", [broken(base_finding(), priority="P0")],
                  ["F062"], []))
    cases.append(("verified-fixed-without-record", [broken(base_finding(),
                  status="VERIFIED_FIXED")], ["F058"], []))
    cases.append(("bad-severity-value", [broken(base_finding(), severity="Catastrophic")],
                  ["F014"], []))
    cases.append(("bad-status-value", [broken(base_finding(), status="closed")], ["F018"], []))

    reg_ok = base_finding(
        id="BUG-010", finding_class="regulatory", category="data-protection",
        title="Retention period is not defined for stored contact records",
        regulatory={"regime": "UU PDP No. 27/2022", "applicability": "Potentially Applicable",
                    "rationale": "App stores contact records; data-subject jurisdiction not "
                                 "confirmed with the product owner.",
                    "finding_type": "Potential Compliance Gap"})
    reg_ok["fingerprint"] = A.compute_fingerprint(reg_ok)
    cases.append(("valid-regulatory", [reg_ok], [], ["F"]))

    reg_bad = dict(reg_ok)
    reg_bad = broken(reg_ok, regulatory={
        "regime": "GDPR", "applicability": "Applicability Unconfirmed",
        "rationale": "no retention policy found",
        "finding_type": "Control Gap With Evidence"})
    cases.append(("regulatory-gap-without-applicability", [reg_bad], ["F055"], []))

    reg_verdict = broken(reg_ok, regulatory={
        "regime": "GDPR", "applicability": "Applicable",
        "rationale": "The application is NON-COMPLIANT with Article 5(1)(e).",
        "finding_type": "Control Gap With Evidence"})
    cases.append(("regulatory-compliance-verdict", [reg_verdict], ["F057"], []))

    for name, findings, must_fire, must_not in cases:
        path = os.path.join(CASES_DIR, f"{name}.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            for f in findings:
                fh.write(json.dumps({k: v for k, v in f.items() if k != "_line"},
                                    ensure_ascii=False) + "\n")
        loaded, _ = A.load_findings(path)
        res = A.validate_findings(loaded)
        res.issues += A.detect_duplicates(loaded).issues
        fired = {i.rule for i in res.issues}
        ok = True
        detail = []
        for rule in must_fire:
            if rule not in fired:
                ok = False
                detail.append(f"expected rule {rule} to fire; fired={sorted(fired)}")
        for prefix in must_not:
            offenders = [r for r in fired if r.startswith(prefix)]
            if offenders:
                ok = False
                detail.append(f"unexpected {prefix}* rules fired: {sorted(offenders)}")
        record("validator", name, ok, "; ".join(detail))

    # Duplicate detection: the BUG-014 / BUG-037 scenario from the brief.
    a = sec_finding(id="BUG-014")
    b = sec_finding(id="BUG-037")
    dup = A.detect_duplicates([a, b])
    record("validator", "exact-duplicate-detected",
           any(i.rule == "D001" for i in dup.issues),
           f"rules fired: {[i.rule for i in dup.issues]}")

    c = sec_finding(id="BUG-050")
    c["evidence"][0]["excerpt"] = (
        "db.all( \"SELECT id, title FROM notes WHERE title LIKE '%\" + searchTerm + \"%'\" )")
    c["locations"][0]["line_start"] = 8
    c["fingerprint"] = A.compute_fingerprint(c)
    d = sec_finding(id="BUG-051")
    d["evidence"][0]["excerpt"] = (
        "db.all(\"SELECT id, title FROM notes WHERE title LIKE '%\" + term + \"%'\");  // legacy")
    d["locations"][0]["line_start"] = 61
    d["fingerprint"] = A.compute_fingerprint(d)
    near = A.detect_duplicates([c, d])
    record("validator", "near-duplicate-detected",
           any(i.rule in ("D001", "D002") for i in near.issues),
           f"rules fired: {[i.rule for i in near.issues]}")


# --------------------------------------------------------------------------
# Suite 2 — fingerprint behaviour (PART G)
# --------------------------------------------------------------------------

def suite_fingerprint() -> None:
    f1 = sec_finding()
    f2 = dict(f1)
    f2["locations"] = [dict(f1["locations"][0], line_start=412, line_end=412)]
    record("fingerprint", "survives-line-movement",
           A.compute_fingerprint(f1) == A.compute_fingerprint(f2))

    f3 = dict(f1)
    f3["evidence"] = [dict(f1["evidence"][0],
                           excerpt="db.all(  \"SELECT ... LIKE '%\"  +  term  +  \"%'\"  )   ")]
    record("fingerprint", "survives-reformatting",
           A.compute_fingerprint(f1) == A.compute_fingerprint(f3))

    f4 = dict(f1)
    f4["evidence"] = [dict(f1["evidence"][0],
                           excerpt="db.all(\"SELECT ... LIKE '%\" + userQuery + \"%'\")")]
    # Contract: an identifier rename DOES move the fingerprint (the fingerprint
    # must stay discriminative), but the duplicate detector must still link the
    # two so a re-audit does not open a second ticket for the same defect.
    renamed_differs = A.compute_fingerprint(f1) != A.compute_fingerprint(f4)
    linked = any(i.rule in ("D001", "D002")
                 for i in A.detect_duplicates([dict(f1, id="BUG-014",
                                                    fingerprint=A.compute_fingerprint(f1)),
                                               dict(f4, id="BUG-037",
                                                    fingerprint=A.compute_fingerprint(f4))]).issues)
    record("fingerprint", "identifier-rename-differs-but-is-linked",
           renamed_differs and linked,
           f"differs={renamed_differs} linked={linked}")

    f4b = dict(f1)
    f4b["evidence"] = [dict(f1["evidence"][0],
                            excerpt="db.all(\"SELECT ... LIKE :prefix\" + term + \"%'\")")]
    record("fingerprint", "survives-string-literal-edit",
           A.compute_fingerprint(f1) == A.compute_fingerprint(f4b),
           "string literals are normalized before hashing")

    f5 = sec_finding()
    f5["mappings"] = {"cwe": ["CWE-79"]}
    record("fingerprint", "distinguishes-weakness-class",
           A.compute_fingerprint(f1) != A.compute_fingerprint(f5))

    f6 = sec_finding()
    f6["locations"] = [dict(f1["locations"][0], file="src/other.js")]
    record("fingerprint", "distinguishes-location",
           A.compute_fingerprint(f1) != A.compute_fingerprint(f6))

    record("fingerprint", "deterministic-across-runs",
           A.compute_fingerprint(f1) == A.compute_fingerprint(sec_finding()))
    record("fingerprint", "excludes-line-numbers",
           "line_start" not in A.semantic_location(f1) and
           str(f1["locations"][0]["line_start"]) not in A.semantic_location(f1))


# --------------------------------------------------------------------------
# Suite 3 — evidence verification against a real repository
# --------------------------------------------------------------------------

def suite_evidence() -> None:
    import hashlib
    tmp = tempfile.mkdtemp(prefix="auditkit-evidence-")
    repo = os.path.join(tmp, "repo")
    shutil.copytree(os.path.join(FIXTURES, "backend-api"), repo)
    rc, _ = A.git(repo, "init", "-q")
    have_git = rc == 0
    if have_git:
        A.git(repo, "add", "-A")
        A.git(repo, "-c", "user.email=t@example.invalid", "-c", "user.name=t",
              "commit", "-qm", "fixture")
    head = A.git(repo, "rev-parse", "HEAD")[1] if have_git else "0" * 40

    src = open(os.path.join(repo, "src/server.js"), encoding="utf-8").read().splitlines()
    good_line = 8
    excerpt = src[good_line - 1]
    good = sec_finding(audited_commit=head)
    good["locations"] = [{"file": "src/server.js", "line_start": good_line,
                          "line_end": good_line, "verified_at": "2026-09-10",
                          "excerpt_sha256": hashlib.sha256(excerpt.encode()).hexdigest(),
                          "symbol": "app.get"}]
    good["reachability"]["caller_chain"] = ["GET /search", "db.all"]
    good["fingerprint"] = A.compute_fingerprint(good)
    res = A.verify_evidence([good], repo)
    record("evidence", "valid-citation-passes", not res.errors,
           "; ".join(i.message for i in res.errors))

    missing = dict(good)
    missing["locations"] = [{"file": "src/does-not-exist.js", "line_start": 1, "line_end": 1,
                             "verified_at": "2026-09-10"}]
    record("evidence", "nonexistent-file-caught",
           any(i.rule == "E002" for i in A.verify_evidence([missing], repo).issues))

    beyond = dict(good)
    beyond["locations"] = [{"file": "src/server.js", "line_start": 9000, "line_end": 9001,
                            "verified_at": "2026-09-10"}]
    record("evidence", "line-beyond-eof-caught",
           any(i.rule == "E004" for i in A.verify_evidence([beyond], repo).issues))

    stale = dict(good)
    stale["locations"] = [dict(good["locations"][0], excerpt_sha256="a" * 64)]
    record("evidence", "stale-content-hash-caught",
           any(i.rule == "E005" for i in A.verify_evidence([stale], repo).issues))

    if have_git:
        wrong = dict(good)
        wrong["audited_commit"] = "1" * 40
        record("evidence", "wrong-commit-caught",
               any(i.rule == "E001" for i in A.verify_evidence([wrong], repo).issues))
    else:
        skip("evidence", "wrong-commit-caught", "git not available in this environment")

    nochain = dict(good)
    nochain["severity"] = "Critical"
    nochain["priority"] = "P0"
    nochain["reachability"] = {"status": "Confirmed", "entry_point": "GET /search",
                               "caller_chain": []}
    record("evidence", "missing-caller-chain-caught",
           any(i.rule == "E008" for i in A.verify_evidence([nochain], repo).issues))

    shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# Suite 4 — end-to-end quality gate (PART J)
# --------------------------------------------------------------------------

MIN_MANIFEST = {
    "schema_version": A.SCHEMA_VERSION,
    "project_name": "fixture", "audit_date": "2026-09-10",
    "pipeline_version": "2.0.0",
    "git": {"commit": "0" * 40, "branch": "main", "working_tree": "clean", "uncommitted_files": 0},
    "tier": {"level": "T1", "justification": "small fixture"},
    "components": [{"name": "api", "path": ".", "platform": "backend-api",
                    "primary_marker": "package.json", "confidence": "Confirmed", "in_scope": True}],
    "standards_selected": [{"name": "OWASP ASVS", "version": "5.0.0", "accessed": "2026-09-09",
                            "verification_status": "Verified", "applicability": "Applicable"}],
    "threat_model": {"worst_credible_outcome": "Unauthenticated read of other users' notes."},
    "executed_commands": [{"step": "build", "command": "npm run build",
                           "command_class": "CONTROLLED_EXECUTION", "result": "Not Executed"}],
}


def write_audit(tmp: str, findings: list[dict], manifest: dict, report_extra: str = "") -> tuple:
    audit = os.path.join(tmp, ".audit")
    os.makedirs(audit, exist_ok=True)
    with open(os.path.join(audit, "findings.jsonl"), "w", encoding="utf-8") as fh:
        for f in findings:
            fh.write(json.dumps(f) + "\n")
    with open(os.path.join(audit, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    counts = {s: 0 for s in A.SEVERITY}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    body = ["# BUG ANALYSIS — fixture", "", "| Severity | Count | Of which Confirmed |", "|---|---|---|"]
    for s in A.SEVERITY:
        body.append(f"| {s} | {counts[s]} | 0 |")
    body.append("")
    for f in findings:
        body.append(f"### {f['id']} — {f['title']}")
        body.append("")
    body.append(report_extra)
    report = os.path.join(tmp, "BUG_ANALYSIS.md")
    open(report, "w", encoding="utf-8").write("\n".join(body))
    return audit, report


def suite_gate() -> None:
    tmp = tempfile.mkdtemp(prefix="auditkit-gate-")
    repo = os.path.join(tmp, "repo")
    shutil.copytree(os.path.join(FIXTURES, "backend-api"), repo)
    A.git(repo, "init", "-q")
    A.git(repo, "add", "-A")
    A.git(repo, "-c", "user.email=t@example.invalid", "-c", "user.name=t", "commit", "-qm", "f")
    head = A.git(repo, "rev-parse", "HEAD")[1]

    import hashlib
    src = open(os.path.join(repo, "src/server.js"), encoding="utf-8").read().splitlines()
    f = sec_finding(audited_commit=head, severity="High", priority="P1")
    f["locations"] = [{"file": "src/server.js", "line_start": 8, "line_end": 8,
                       "verified_at": "2026-09-10", "symbol": "app.get",
                       "excerpt_sha256": hashlib.sha256(src[7].encode()).hexdigest()}]
    f["fingerprint"] = A.compute_fingerprint(f)
    man = json.loads(json.dumps(MIN_MANIFEST))
    man["git"]["commit"] = head

    audit, report = write_audit(repo, [f], man)
    result, code = A.run_gate(repo, audit, report, None, os.path.join(audit, "validation-result.json"))
    record("gate", "clean-audit-passes", result["verdict"] in ("PASS", "PASS_WITH_LIMITATIONS"),
           f"verdict={result['verdict']} errors={result['error_count']} "
           f"{[i['message'] for c in result['checks'] for i in c['issues'] if i['severity']=='error'][:3]}")
    record("gate", "writes-machine-readable-result",
           os.path.exists(os.path.join(audit, "validation-result.json")))

    # A finding in the ledger that never made it into the report.
    f2 = sec_finding(id="BUG-002", audited_commit=head, title="Second issue not written up anywhere")
    f2["locations"] = f["locations"]
    f2["fingerprint"] = A.compute_fingerprint(f2)
    with open(os.path.join(audit, "findings.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(f2) + "\n")
    result, code = A.run_gate(repo, audit, report, None, None)
    ledger_rule = any(i["rule"] == "R001" for c in result["checks"] for i in c["issues"])
    record("gate", "ledger-report-mismatch-fails",
           result["verdict"] == "FAIL_VALIDATION" and ledger_rule and code == 1,
           f"verdict={result['verdict']} R001={ledger_rule}")

    # Unresolved template placeholder.
    audit, report = write_audit(repo, [f], man, report_extra="Audited on {{AUDIT_DATE}}.")
    result, _ = A.run_gate(repo, audit, report, None, None)
    record("gate", "unresolved-placeholder-fails",
           any(i["rule"] == "R003" for c in result["checks"] for i in c["issues"]))

    # Manifest recording a prohibited command as executed.
    man2 = json.loads(json.dumps(man))
    man2["executed_commands"] = [{"step": "fix", "command": "npm audit fix",
                                  "command_class": "PROHIBITED", "result": "Passed",
                                  "evidence": ".audit/evidence/x.txt"}]
    audit, report = write_audit(repo, [f], man2)
    result, _ = A.run_gate(repo, audit, report, None, None)
    record("gate", "prohibited-command-fails",
           any(i["rule"] == "M010" for c in result["checks"] for i in c["issues"]))

    # Controlled execution without before/after repository state.
    man3 = json.loads(json.dumps(man))
    man3["executed_commands"] = [{"step": "build", "command": "npm run build",
                                  "command_class": "CONTROLLED_EXECUTION", "result": "Passed",
                                  "evidence": ".audit/evidence/build.txt"}]
    audit, report = write_audit(repo, [f], man3)
    result, _ = A.run_gate(repo, audit, report, None, None)
    record("gate", "controlled-execution-needs-state-record",
           any(i["rule"] == "M012" for c in result["checks"] for i in c["issues"]))

    # Runtime record claiming PASS with no artifact, and NOT_EXECUTED with an observation.
    man4 = json.loads(json.dumps(man))
    man4["runtime_verifications"] = [
        {"finding_id": "BUG-001", "environment": "staging", "timestamp": "2026-09-10T10:00:00Z",
         "command": "pytest -k repro", "result": "PASS"},
        {"finding_id": "BUG-002", "environment": "staging", "timestamp": "2026-09-10T10:05:00Z",
         "command": "pytest -k repro2", "result": "NOT_EXECUTED", "observed": "looked fine"},
    ]
    audit, report = write_audit(repo, [f], man4)
    result, _ = A.run_gate(repo, audit, report, None, None)
    fired = {i["rule"] for c in result["checks"] for i in c["issues"]}
    record("gate", "runtime-claims-need-artifacts", "M015" in fired and "M016" in fired,
           f"fired={sorted(r for r in fired if r.startswith('M'))}")

    shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# Suite 5 — secret leakage scanner, including the negative control
# --------------------------------------------------------------------------

def suite_secrets() -> None:
    tmp = tempfile.mkdtemp(prefix="auditkit-secrets-")
    leaky = os.path.join(tmp, "BUG_ANALYSIS.md")
    open(leaky, "w", encoding="utf-8").write(
        "### BUG-001\n"
        "Evidence:\n\n"
        "    aws_key = AKIAIOSFODNN7EXAMPLE\n"  # allowlisted by 'EXAMPLE'
        "    github_token = ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n"
        "    db = postgres://svcuser:hunter2hunter2@db.internal:5432/app\n")
    res = A.scan_secrets([leaky])
    rules = [i.location for i in res.issues]
    record("secrets", "detects-planted-token", len(res.errors) >= 2, f"hits={rules}")

    safe = os.path.join(tmp, "SAFE.md")
    open(safe, "w", encoding="utf-8").write(
        "`config/production.env:14` — hardcoded database password (Confirmed, value redacted)\n"
        "Set it via ${DB_PASSWORD} or process.env.DB_PASSWORD instead.\n"
        "Example only: password = \"<redacted>\"\n")
    record("secrets", "no-false-positive-on-redacted-report",
           not A.scan_secrets([safe]).errors,
           "; ".join(i.message for i in A.scan_secrets([safe]).errors))

    # Negative control: the skill's own documentation must be clean.
    docs = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "fixtures", "cases", "__pycache__")]
        docs += [os.path.join(dirpath, fn) for fn in filenames if fn.endswith((".md", ".json"))]
    res = A.scan_secrets(docs)
    record("secrets", "skill-docs-clean", not res.errors,
           "; ".join(f"{i.location}" for i in res.errors[:5]))

    # Negative control: the clean fixture must not trigger the scanner.
    clean_files = []
    for dirpath, _, filenames in os.walk(os.path.join(FIXTURES, "clean-lib")):
        clean_files += [os.path.join(dirpath, fn) for fn in filenames]
    record("secrets", "clean-fixture-no-secrets", not A.scan_secrets(clean_files).errors)

    shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# Suite 6 — fixtures: line accuracy and platform detection
# --------------------------------------------------------------------------

def suite_fixtures() -> None:
    if not os.path.isdir(FIXTURES):
        skip("fixtures", "all", "fixtures not materialized; run tests/make_fixtures.py")
        return

    total_seeded = 0
    for fx in sorted(os.listdir(FIXTURES)):
        path = os.path.join(FIXTURES, fx)
        exp_path = os.path.join(path, ".expected", "expectations.json")
        if not os.path.exists(exp_path):
            continue
        exp = json.load(open(exp_path, encoding="utf-8"))

        ok, detail = True, []
        for d in exp["seeded_defects"]:
            total_seeded += 1
            fpath = os.path.join(path, d["file"])
            if not os.path.isfile(fpath):
                ok = False
                detail.append(f"{d['id']}: missing file {d['file']}")
                continue
            lines = open(fpath, encoding="utf-8").read().splitlines()
            ln = d["line"]
            if not (1 <= ln <= len(lines)) or d.get("marker", "") not in lines[ln - 1]:
                ok = False
                detail.append(f"{d['id']}: line {ln} does not contain {d.get('marker')!r}")
        record("fixtures", f"{fx}-seeded-lines-accurate", ok, "; ".join(detail))

        # detect-stack.sh must find the declared primary markers and must not
        # hallucinate a platform the fixture does not have.
        script = os.path.join(ROOT, "scripts", "detect-stack.sh")
        try:
            out = subprocess.run(["bash", script, path], capture_output=True, text=True,
                                 timeout=60).stdout
        except (OSError, subprocess.SubprocessError) as exc:
            skip("fixtures", f"{fx}-platform-detection", f"detect-stack.sh failed: {exc}")
            continue
        missing = [m for m in exp["expected_markers"] if os.path.basename(m) not in out]
        missing += [t for t in exp.get("expected_output_tokens", []) if t not in out]
        record("fixtures", f"{fx}-markers-detected", not missing, f"not found in output: {missing}")

        section = {}
        cur = None
        for line in out.splitlines():
            if line.startswith("-- "):
                cur = line.strip("- ").strip()
                section[cur] = []
            elif cur and line.strip():
                section[cur].append(line)
        forbidden_hits = []
        mapping = {"mobile-android": "mobile", "mobile-ios": "mobile", "desktop": "desktop",
                   "embedded-iot": "embedded / iot", "web-frontend": "web frontend",
                   "backend-api": None}
        for plat in exp["forbidden_platforms"]:
            sec = mapping.get(plat)
            if sec and section.get(sec):
                forbidden_hits.append((plat, section[sec][:2]))
        record("fixtures", f"{fx}-no-phantom-platforms", not forbidden_hits, str(forbidden_hits))

    clean_exp = json.load(open(os.path.join(FIXTURES, "clean-lib", ".expected",
                                            "expectations.json"), encoding="utf-8"))
    record("fixtures", "clean-control-has-no-seeded-defects",
           clean_exp["seeded_defects"] == [],
           "the negative control must stay empty")
    record("fixtures", "seeded-defect-corpus-nonempty", total_seeded >= 8,
           f"only {total_seeded} seeded defects")

    # Agent detection rate against these fixtures cannot be measured here.
    skip("fixtures", "agent-detection-rate",
         "requires an agent run against the fixtures; see tests/AGENT_BENCHMARK.md")


# --------------------------------------------------------------------------
# Suite 7 — documentation consistency (PART B, R)
# --------------------------------------------------------------------------

# CHANGELOG.md and MIGRATION.md document *history*: removed files and superseded
# claims. A link checker asserting that historical references still resolve, or a
# lint asserting that no document mentions the old phase count, would be wrong
# about those two files specifically. The exclusion is narrow and deliberate —
# every other document is checked.
HISTORICAL_DOCS = {"CHANGELOG.md", "MIGRATION.md"}

PIPELINE_ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*`(phases/[0-9]{2}-[a-z-]+\.md)`\s*\|\s*([^|]+)\|", re.M)


def suite_docs() -> None:
    canon_path = os.path.join(ROOT, "references", "pipeline.md")
    if not os.path.exists(canon_path):
        record("docs", "canonical-pipeline-exists", False, "references/pipeline.md missing")
        return
    record("docs", "canonical-pipeline-exists", True)
    canon = open(canon_path, encoding="utf-8").read()
    rows = PIPELINE_ROW.findall(canon)
    record("docs", "canonical-pipeline-parses", len(rows) >= 10, f"{len(rows)} rows parsed")

    declared = {int(n): f for n, f, _ in rows}
    on_disk = sorted(f for f in os.listdir(os.path.join(ROOT, "phases")) if f.endswith(".md"))
    record("docs", "phase-files-match-canonical",
           sorted(os.path.basename(v) for v in declared.values()) == on_disk,
           f"declared={sorted(os.path.basename(v) for v in declared.values())} on_disk={on_disk}")
    record("docs", "phase-numbers-contiguous",
           sorted(declared) == list(range(min(declared), max(declared) + 1)),
           f"numbers={sorted(declared)}")

    # Each phase file's H1 must agree with its canonical number.
    bad = []
    for num, rel in declared.items():
        head = open(os.path.join(ROOT, rel), encoding="utf-8").readline().strip()
        if not re.match(rf"^#\s*Phase {num}\b", head):
            bad.append(f"{rel} starts with {head!r}, expected 'Phase {num}'")
    record("docs", "phase-headings-match-numbers", not bad, "; ".join(bad))

    # No document may restate a different phase count in prose.
    n = len(declared)
    words = {9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen"}
    wrong_counts = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "fixtures", "cases", "__pycache__")]
        for fn in filenames:
            if not fn.endswith(".md") or fn in HISTORICAL_DOCS:
                continue
            p = os.path.join(dirpath, fn)
            text = open(p, encoding="utf-8", errors="replace").read().lower()
            for cnt, word in words.items():
                if cnt == n:
                    continue
                if re.search(rf"\b{word}[- ]phase\b", text) or re.search(rf"\b{word} phases\b", text):
                    wrong_counts.append(f"{os.path.relpath(p, ROOT)} says '{word} phase(s)'")
    record("docs", "no-contradictory-phase-count", not wrong_counts, "; ".join(wrong_counts))

    # Every relative path referenced from a markdown file must exist.
    ref = re.compile(r"`((?:phases|playbooks|references|templates|checklists|scripts|schemas|prompts|tests)"
                     r"/[A-Za-z0-9._/-]+)`")
    broken = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "fixtures", "cases", "__pycache__")]
        for fn in filenames:
            if not fn.endswith(".md") or fn in HISTORICAL_DOCS:
                continue
            p = os.path.join(dirpath, fn)
            for m in ref.findall(open(p, encoding="utf-8", errors="replace").read()):
                if m.endswith("/") or "*" in m:
                    continue
                if not os.path.exists(os.path.join(ROOT, m)):
                    broken.append(f"{os.path.relpath(p, ROOT)} -> {m}")
    record("docs", "no-broken-internal-references", not broken, "; ".join(sorted(set(broken))[:6]))

    # Prohibited commands must never appear as an instruction to run.
    prohibited = ["git reset --hard", "git clean -fd", "rm -rf /", "npm audit fix",
                  "--fix", "--write", "-u --latest"]
    offenders = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "fixtures", "cases", "__pycache__")]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dirpath, fn)
            for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                stripped = line.strip()
                if not stripped.startswith(("$", "> $")) and not re.match(r"^(git|npm|npx|yarn|pnpm) ", stripped):
                    continue
                for cmd in prohibited:
                    if cmd in stripped:
                        offenders.append(f"{os.path.relpath(p, ROOT)}:{i} {stripped[:60]}")
    record("docs", "no-prohibited-command-in-runnable-position", not offenders, "; ".join(offenders))

    # Schemas must be in sync with the validator vocabularies.
    rc = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "generate-schemas.py"),
                         "--check"], capture_output=True, text=True)
    record("docs", "schemas-in-sync-with-validator", rc.returncode == 0, rc.stdout.strip())

    # SKILL.md must not duplicate the pipeline table (single source of truth).
    skill = open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8").read()
    dup_rows = PIPELINE_ROW.findall(skill)
    record("docs", "skill-does-not-duplicate-pipeline-table", len(dup_rows) == 0,
           f"SKILL.md restates {len(dup_rows)} pipeline rows; it should link to references/pipeline.md")


# --------------------------------------------------------------------------
# Suite 8 — remediation skill contract
# --------------------------------------------------------------------------

def suite_remediation() -> None:
    rem = os.path.join(os.path.dirname(ROOT), "universal-remediation-skill")
    if not os.path.isdir(rem):
        skip("remediation", "all", "universal-remediation-skill not present next to this skill")
        return
    required = ["SKILL.md", "README.md", "references/remediation-rules.md",
                "references/verification-rules.md", "references/rollback-rules.md",
                "templates/FIX_RECORD.template.json", "templates/FIX_LOG.template.md",
                "scripts/validate-fix.py", "schemas/fix-record.schema.json"]
    missing = [r for r in required if not os.path.exists(os.path.join(rem, r))]
    record("remediation", "required-files-present", not missing, f"missing={missing}")

    phases = sorted(f for f in os.listdir(os.path.join(rem, "phases")) if f.endswith(".md")) \
        if os.path.isdir(os.path.join(rem, "phases")) else []
    record("remediation", "phase-files-present", len(phases) >= 10, f"{len(phases)} phase files")

    # The fix validator must reject a fix record that claims VERIFIED_FIXED
    # while the original reproduction still fails.
    vf = os.path.join(rem, "scripts", "validate-fix.py")
    if not os.path.exists(vf):
        skip("remediation", "validate-fix-behaviour", "validate-fix.py missing")
        return
    tmp = tempfile.mkdtemp(prefix="fixrec-")
    good = {
        "schema_version": "2.0", "finding_id": "BUG-001",
        "original_fingerprint": "0123456789abcdef", "baseline_commit": "a" * 40,
        "changed_files": ["src/server.js"], "patch_summary": "bind the LIKE parameter",
        "root_cause": "query built by concatenation",
        "reproduction_before": {"result": "FAIL", "artifact_path": ".audit/evidence/before.txt"},
        "verification_after": {"result": "PASS", "artifact_path": ".audit/evidence/after.txt"},
        "build_result": "Passed", "targeted_tests": {"result": "PASS", "names": ["test_search_binding"]},
        "regression_result": "PASS", "runtime_result": "NOT_EXECUTED",
        "remaining_risks": "none identified", "rollback_procedure": "git revert <commit>",
        "resulting_commit": "b" * 40, "status": "VERIFIED_FIXED",
    }
    bad = dict(good, verification_after={"result": "FAIL", "artifact_path": ".audit/evidence/after.txt"})
    unrelated = dict(good, changed_files=["src/server.js", "README.md", "src/unrelated/theme.css"])
    for name, rec, expect_fail in (("good", good, False), ("still-reproduces", bad, True),
                                   ("scope-creep", unrelated, True)):
        p = os.path.join(tmp, f"{name}.json")
        json.dump(rec, open(p, "w", encoding="utf-8"), indent=2)
        rc = subprocess.run([sys.executable, vf, "--fix-record", p],
                            capture_output=True, text=True)
        failed = rc.returncode != 0
        record("remediation", f"validate-fix-{name}", failed == expect_fail,
               f"exit={rc.returncode} out={rc.stdout.strip()[:160]}")
    shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------

def main() -> int:
    suites = [suite_validator, suite_fingerprint, suite_evidence, suite_gate,
              suite_secrets, suite_fixtures, suite_docs, suite_remediation]
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    for s in suites:
        if only and only not in s.__name__:
            continue
        try:
            s()
        except Exception as exc:  # a crashing test is a failing test, never a silent pass
            record(s.__name__, "suite-crashed", False, f"{type(exc).__name__}: {exc}")

    width = max(len(f"{a}/{b}") for a, b, _ in RESULTS) + 2
    print("\n=== universal-audit-skill self-test ===\n")
    cur = None
    for suite, name, status in RESULTS:
        if suite != cur:
            print(f"[{suite}]")
            cur = suite
        print(f"  {name:<{width}} {status}")
    passed = sum(1 for _, _, s in RESULTS if s == "PASS")
    failed = sum(1 for _, _, s in RESULTS if s == "FAIL")
    notrun = sum(1 for _, _, s in RESULTS if s == "NOT_EXECUTED")
    if DETAIL:
        print("\ndetail:")
        for d in DETAIL:
            print(d)
    print(f"\nPASS {passed}   FAIL {failed}   NOT_EXECUTED {notrun}")

    out = os.path.join(HERE, "last-run.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"passed": passed, "failed": failed, "not_executed": notrun,
                   "results": [{"suite": s, "test": n, "status": st} for s, n, st in RESULTS],
                   "detail": DETAIL}, fh, indent=2)
    print(f"machine-readable result: tests/last-run.json")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
