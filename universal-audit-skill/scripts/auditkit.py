#!/usr/bin/env python3
"""
auditkit — deterministic validation library for universal-audit-skill.

Pure stdlib. No network. Read-only with respect to the audited repository:
the only path it ever writes is the --out file the caller names.

Every check has a stable rule id (Fnnn / Ennn / Dnnn / Rnnn / Snnn / Mnnn) so
results are comparable across runs and across agents.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Iterable

SCHEMA_VERSION = "2.0"

# --------------------------------------------------------------------------
# Controlled vocabularies. Anything not in these lists is a validation error,
# never a silent pass-through.
# --------------------------------------------------------------------------

SEVERITY = ["Critical", "High", "Medium", "Low", "Informational"]
PRIORITY = ["P0", "P1", "P2", "P3", "P4"]
CONFIDENCE = [
    "Confirmed",
    "Highly Likely",
    "Potential",
    "Needs Runtime Verification",
    "False Positive",
    "Not Applicable",
]
EPISTEMIC = ["Fact", "Inference", "Assumption"]

FINDING_CLASS = [
    "security",
    "privacy",
    "regulatory",
    "supply_chain",
    "functional",
    "reliability",
    "concurrency",
    "performance",
    "maintainability",
    "accessibility",
    "observability",
    "build_config",
    "test_gap",
]
SECURITY_CLASSES = {"security", "privacy", "supply_chain"}

STATUS = [
    "CANDIDATE",
    "VERIFIED_FINDING",
    "READY_FOR_FIX",
    "REPRODUCED",
    "FIX_IN_PROGRESS",
    "FIX_IMPLEMENTED",
    "VERIFICATION_PASSED",
    "REGRESSION_PASSED",
    "RE_AUDIT_PASSED",
    "VERIFIED_FIXED",
    "REGRESSED",
    "WONT_FIX",
    "SUPERSEDED",
    "DUPLICATE",
    "FALSE_POSITIVE",
]
# Statuses that mean "this is closed". Reaching one requires evidence.
CLOSED_STATUS = {"VERIFIED_FIXED", "WONT_FIX", "SUPERSEDED", "DUPLICATE", "FALSE_POSITIVE"}

REACHABILITY = ["Confirmed", "Unconfirmed", "Unreachable", "Not Applicable"]
REPRO_STATUS = ["Reproduced", "Not Reproduced", "Not Attempted", "Blocked", "Static Only"]
VERIFICATION_LEVEL = ["static", "unit", "integration", "runtime", "manual"]
EFFORT = ["XS", "S", "M", "L", "XL"]

EVIDENCE_TYPES = [
    "code",
    "command_output",
    "analyzer",
    "log",
    "config",
    "document",
    "reproduction",
    "absence",
    "runtime_record",
]

COMMAND_RESULT = [
    "Passed",
    "Passed with warnings",
    "Partial",
    "Failed",
    "Not Executed",
    "Blocked",
    "Not Applicable",
]
COMMAND_CLASS = ["SAFE_READ_ONLY", "CONTROLLED_EXECUTION", "REQUIRES_CONSENT", "PROHIBITED"]

RUNTIME_RESULT = ["PASS", "FAIL", "BLOCKED", "NOT_EXECUTED", "INCONCLUSIVE"]

REG_APPLICABILITY = [
    "Applicable",
    "Potentially Applicable",
    "Not Applicable",
    "Applicability Unconfirmed",
]
REG_FINDING_TYPE = [
    "Potential Compliance Gap",
    "Control Gap With Evidence",
    "Observation",
    "Not Applicable",
]
# Language a repository audit is not entitled to use about legal compliance.
FORBIDDEN_REG_PHRASES = [
    "non-compliant",
    "noncompliant",
    "violates gdpr",
    "violates the gdpr",
    "gdpr violation",
    "breaches gdpr",
    "certified compliant",
    "is compliant with",
    "fully compliant",
    "legally compliant",
]

CVSS_NOT_SCORED = "Not Scored — Insufficient Evidence"
CVSS_VECTOR_RE = re.compile(r"^CVSS:(3\.[01]|4\.0)/[A-Z]+:[A-Z]", re.I)
CVE_RE = re.compile(r"^CVE-\d{4}-\d{4,}$")
GHSA_RE = re.compile(r"^GHSA-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}$", re.I)
CWE_RE = re.compile(r"^CWE-\d+$")
FINDING_ID_RE = re.compile(r"^BUG-\d{3,}$")
FEATURE_ID_RE = re.compile(r"^FEAT-\d{3,}$")
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_]+\}\}")

SECRET_PATTERNS = [
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("stripe_key", re.compile(r"\b[sr]k_(?:live|test)_[0-9A-Za-z]{16,}\b")),
    ("assigned_secret", re.compile(
        r"\b(?:password|passwd|secret|api[_-]?key|token|client[_-]?secret)\b\s*[:=]\s*"
        r"[\"'][^\"'\s]{8,}[\"']", re.I)),
    ("conn_string_creds", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s:@]{4,}@")),
]
# Documentation legitimately shows redacted or illustrative forms.
SECRET_ALLOWLIST = re.compile(
    r"(redact|REDACTED|<[^>]*>|\.\.\.|xxx+|placeholder|example|EXAMPLE|dummy|"
    r"\$\{[^}]+\}|process\.env|os\.environ|value redacted)", re.I)


# --------------------------------------------------------------------------
# Result plumbing
# --------------------------------------------------------------------------

@dataclass
class Issue:
    rule: str
    severity: str  # "error" | "warning"
    finding_id: str | None
    message: str
    location: str | None = None

    def line(self) -> str:
        who = self.finding_id or self.location or "-"
        return f"[{self.severity.upper():7}] {self.rule} {who}: {self.message}"


@dataclass
class CheckResult:
    name: str
    executed: bool = True
    issues: list[Issue] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    blocked_reason: str | None = None

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def status(self) -> str:
        if not self.executed:
            return "BLOCKED" if self.blocked_reason else "NOT_EXECUTED"
        if self.errors:
            return "FAIL"
        if self.warnings:
            return "PASS_WITH_WARNINGS"
        return "PASS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "executed": self.executed,
            "blocked_reason": self.blocked_reason,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "stats": self.stats,
            "issues": [asdict(i) for i in self.issues],
        }


# --------------------------------------------------------------------------
# Fingerprinting (PART G)
# --------------------------------------------------------------------------

_STRING_LIT = re.compile(r"""(["'])(?:\\.|(?!\1).)*\1""")
_NUMBER = re.compile(r"\b\d+(?:\.\d+)?\b")
_WS = re.compile(r"\s+")
_COMMENT = re.compile(r"(//[^\n]*|#[^\n]*|/\*.*?\*/)", re.S)


def normalize_excerpt(text: str) -> str:
    """Collapse a code excerpt to something stable under formatting and
    literal churn, so a fingerprint survives a rename of a constant or a
    reflow by a formatter."""
    if not text:
        return ""
    t = _COMMENT.sub(" ", text)
    t = _STRING_LIT.sub('"S"', t)
    t = _NUMBER.sub("N", t)
    t = _WS.sub("", t)          # code excerpts are compared whitespace-free
    return t.lower()


def normalize_path(path: str) -> str:
    p = (path or "").replace("\\", "/").lstrip("./")
    return p.lower()


def weakness_key(finding: dict) -> str:
    """The defect class. For security findings the CWE is the stable key; for
    everything else the declared category is."""
    m = finding.get("mappings") or {}
    cwes = [c for c in (m.get("cwe") or []) if CWE_RE.match(str(c))]
    if cwes:
        return "+".join(sorted(cwes))
    return str(finding.get("category") or finding.get("finding_class") or "unspecified").lower()


def semantic_location(finding: dict) -> str:
    """File plus nearest named symbol. Deliberately excludes line numbers so a
    fingerprint survives insertions above the defect."""
    locs = finding.get("locations") or []
    if not locs:
        return normalize_path(finding.get("component", "")) + "::" + "no-location"
    parts = []
    for loc in sorted(locs, key=lambda l: (normalize_path(l.get("file", "")), l.get("symbol") or "")):
        sym = (loc.get("symbol") or "").strip().lower()
        parts.append(f"{normalize_path(loc.get('file',''))}::{sym or 'file-scope'}")
    return "|".join(parts)


def compute_fingerprint(finding: dict) -> str:
    material = "\u241f".join([
        str(finding.get("component") or "").strip().lower(),
        str(finding.get("finding_class") or "").strip().lower(),
        weakness_key(finding),
        semantic_location(finding),
        normalize_excerpt(_primary_excerpt(finding)),
    ])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def _primary_excerpt(finding: dict) -> str:
    for ev in finding.get("evidence") or []:
        if ev.get("type") == "code" and ev.get("excerpt"):
            return ev["excerpt"]
    for loc in finding.get("locations") or []:
        if loc.get("excerpt"):
            return loc["excerpt"]
    return ""


def _tokens(text: str) -> set[str]:
    """Tokens from the *raw* excerpt. Fingerprinting normalizes literals away;
    similarity scoring must not, or two statements that differ only in a
    variable name score far apart and the duplicate goes unnoticed."""
    t = _COMMENT.sub(" ", text or "")
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", t.lower()))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# --------------------------------------------------------------------------
# IO helpers
# --------------------------------------------------------------------------

def load_findings(path: str) -> tuple[list[dict], list[Issue]]:
    issues: list[Issue] = []
    findings: list[dict] = []
    if not os.path.exists(path):
        issues.append(Issue("F000", "error", None, f"findings file not found: {path}"))
        return findings, issues
    with open(path, encoding="utf-8") as fh:
        for n, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw or raw.startswith("//"):
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as exc:
                issues.append(Issue("F001", "error", None,
                                    f"line {n} is not valid JSON: {exc.msg}", path))
                continue
            if not isinstance(obj, dict):
                issues.append(Issue("F001", "error", None, f"line {n} is not a JSON object", path))
                continue
            obj["_line"] = n
            findings.append(obj)
    return findings, issues


def git(repo: str, *args: str) -> tuple[int, str]:
    try:
        p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=30)
        return p.returncode, (p.stdout or p.stderr).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, str(exc)


# --------------------------------------------------------------------------
# CHECK 1 — finding schema and semantic rules (PART D, F)
# --------------------------------------------------------------------------

def _req(finding: dict, key: str, issues: list[Issue], rule: str, fid: str) -> bool:
    val = finding.get(key)
    if val is None or (isinstance(val, (str, list, dict)) and len(val) == 0):
        issues.append(Issue(rule, "error", fid, f"required field '{key}' missing or empty"))
        return False
    return True


def _enum(finding: dict, key: str, allowed: list[str], issues: list[Issue],
         rule: str, fid: str, required: bool = True) -> None:
    val = finding.get(key)
    if val is None:
        if required:
            issues.append(Issue(rule, "error", fid, f"required field '{key}' missing"))
        return
    if val not in allowed:
        issues.append(Issue(rule, "error", fid,
                            f"'{key}' = {val!r} is not one of {allowed}"))


def validate_findings(findings: list[dict]) -> CheckResult:
    res = CheckResult("findings_schema")
    seen_ids: dict[str, int] = {}
    counts: dict[str, int] = {s: 0 for s in SEVERITY}

    for f in findings:
        fid = str(f.get("id") or f"<line {f.get('_line')}>")
        I = res.issues

        # -- identity ---------------------------------------------------
        if not FINDING_ID_RE.match(str(f.get("id", ""))):
            I.append(Issue("F002", "error", fid, "id must match BUG-NNN"))
        if f.get("id") in seen_ids:
            I.append(Issue("F003", "error", fid,
                           f"duplicate finding id (also on line {seen_ids[f['id']]})"))
        elif f.get("id"):
            seen_ids[f["id"]] = f.get("_line", 0)

        if f.get("schema_version") != SCHEMA_VERSION:
            I.append(Issue("F004", "error", fid,
                           f"schema_version must be {SCHEMA_VERSION!r}, got {f.get('schema_version')!r}"))

        # -- fingerprint (PART G) --------------------------------------
        if not f.get("fingerprint"):
            I.append(Issue("F005", "error", fid, "fingerprint missing"))
        else:
            expected = compute_fingerprint(f)
            if f["fingerprint"] != expected:
                I.append(Issue("F006", "error", fid,
                               f"fingerprint {f['fingerprint']} does not match recomputed "
                               f"{expected} — it must be derived, not authored"))

        # -- core scalars ----------------------------------------------
        for k, rule in (("component", "F007"), ("title", "F008"), ("audited_commit", "F009"),
                        ("impact", "F010"), ("root_cause", "F011"), ("category", "F012")):
            _req(f, k, I, rule, fid)

        _enum(f, "finding_class", FINDING_CLASS, I, "F013", fid)
        _enum(f, "severity", SEVERITY, I, "F014", fid)
        _enum(f, "priority", PRIORITY, I, "F015", fid)
        _enum(f, "confidence", CONFIDENCE, I, "F016", fid)
        _enum(f, "epistemic", EPISTEMIC, I, "F017", fid)
        _enum(f, "status", STATUS, I, "F018", fid)
        _enum(f, "effort", EFFORT, I, "F019", fid)
        if f.get("severity") in counts:
            counts[f["severity"]] += 1

        # -- evidence --------------------------------------------------
        ev = f.get("evidence") or []
        if not ev:
            I.append(Issue("F020", "error", fid, "no evidence entries — every finding needs at least one"))
        for e in ev:
            if e.get("type") not in EVIDENCE_TYPES:
                I.append(Issue("F021", "error", fid,
                               f"evidence type {e.get('type')!r} not in {EVIDENCE_TYPES}"))
            if not e.get("ref") and not e.get("excerpt"):
                I.append(Issue("F022", "error", fid, "evidence entry has neither ref nor excerpt"))

        # -- locations vs absence evidence -----------------------------
        locs = f.get("locations") or []
        has_absence = any(e.get("type") == "absence" for e in ev)
        if not locs and not has_absence:
            I.append(Issue("F023", "error", fid,
                           "no locations and no 'absence' evidence — a claim needs a place or a search"))
        for loc in locs:
            if not loc.get("file"):
                I.append(Issue("F024", "error", fid, "location without a file path"))
            ls, le = loc.get("line_start"), loc.get("line_end")
            if not isinstance(ls, int) or not isinstance(le, int):
                I.append(Issue("F025", "error", fid, "location line_start/line_end must be integers"))
            elif ls < 1 or le < ls:
                I.append(Issue("F026", "error", fid, f"impossible line range {ls}-{le}"))
            if not loc.get("verified_at"):
                I.append(Issue("F027", "error", fid,
                               "location missing verified_at — cite only lines re-read this session"))

        # -- reachability (PART F) -------------------------------------
        reach = f.get("reachability") or {}
        if reach.get("status") not in REACHABILITY:
            I.append(Issue("F028", "error", fid,
                           f"reachability.status must be one of {REACHABILITY}"))
        if f.get("severity") in ("Critical", "High", "Medium"):
            if reach.get("status") == "Unconfirmed" and f.get("confidence") == "Confirmed":
                I.append(Issue("F029", "error", fid,
                               "confidence 'Confirmed' with unconfirmed reachability at "
                               "Medium+ severity — downgrade confidence or prove the caller chain"))
            if reach.get("status") == "Confirmed" and not reach.get("entry_point"):
                I.append(Issue("F030", "error", fid,
                               "reachability Confirmed requires an entry_point"))
            if reach.get("status") == "Unreachable":
                I.append(Issue("F031", "warning", fid,
                               "unreachable code rated Medium+ — usually a maintainability issue"))

        # -- reproduction and verification -----------------------------
        rep = f.get("reproduction") or {}
        if rep.get("status") not in REPRO_STATUS:
            I.append(Issue("F032", "error", fid, f"reproduction.status must be one of {REPRO_STATUS}"))
        if not rep.get("expected") or not rep.get("observed"):
            I.append(Issue("F033", "error", fid,
                           "reproduction requires both 'expected' and 'observed'"))
        if rep.get("status") == "Reproduced" and not rep.get("procedure"):
            I.append(Issue("F034", "error", fid, "reproduction.status Reproduced requires a procedure"))

        ver = f.get("verification") or {}
        if not ver.get("procedure"):
            I.append(Issue("F035", "error", fid, "verification.procedure missing"))
        if not ver.get("expected_evidence"):
            I.append(Issue("F036", "error", fid, "verification.expected_evidence missing"))
        if ver.get("level") not in VERIFICATION_LEVEL:
            I.append(Issue("F037", "error", fid, f"verification.level must be one of {VERIFICATION_LEVEL}"))
        if f.get("confidence") == "Needs Runtime Verification" and ver.get("level") == "static":
            I.append(Issue("F038", "error", fid,
                           "confidence 'Needs Runtime Verification' cannot have a static "
                           "verification level"))

        # -- remediation -----------------------------------------------
        rem = f.get("remediation") or {}
        if not rem.get("strategy"):
            I.append(Issue("F039", "error", fid, "remediation.strategy missing"))

        # -- mappings, class-aware (PART D) ----------------------------
        m = f.get("mappings") or {}
        cls = f.get("finding_class")
        cwes = m.get("cwe") or []
        for c in cwes:
            if not CWE_RE.match(str(c)):
                I.append(Issue("F040", "error", fid, f"malformed CWE id {c!r}"))
        if cls in SECURITY_CLASSES and not cwes:
            I.append(Issue("F041", "error", fid,
                           "security-class finding requires at least one CWE"))
        if cls not in SECURITY_CLASSES and cwes:
            I.append(Issue("F042", "warning", fid,
                           f"CWE mapped onto a '{cls}' finding — only map a weakness taxonomy "
                           "where one genuinely applies"))

        cves = m.get("cve") or []
        for c in cves:
            if not (CVE_RE.match(str(c)) or GHSA_RE.match(str(c))):
                I.append(Issue("F043", "error", fid, f"malformed CVE/GHSA id {c!r}"))

        # EPSS and KEV are vulnerability-intelligence signals. They are
        # meaningless on a first-party source defect with no CVE.
        epss = m.get("epss")
        if epss not in (None, "Not Applicable"):
            if not any(CVE_RE.match(str(c)) for c in cves):
                I.append(Issue("F044", "error", fid,
                               "EPSS populated without an applicable CVE — use 'Not Applicable'"))
            elif not isinstance(epss, (int, float)) or not 0.0 <= float(epss) <= 1.0:
                I.append(Issue("F045", "error", fid, "EPSS must be a probability in [0,1]"))
        kev = m.get("kev")
        if kev not in (None, False, "Not Applicable"):
            if not any(CVE_RE.match(str(c)) for c in cves):
                I.append(Issue("F046", "error", fid,
                               "CISA KEV asserted without an applicable CVE — use 'Not Applicable'"))

        cvss = m.get("cvss")
        if cvss not in (None, CVSS_NOT_SCORED, "Not Applicable"):
            if not isinstance(cvss, dict):
                I.append(Issue("F047", "error", fid,
                               f"cvss must be an object, {CVSS_NOT_SCORED!r}, or 'Not Applicable'"))
            else:
                if not cvss.get("vector"):
                    I.append(Issue("F048", "error", fid,
                                   f"CVSS score without a vector — use {CVSS_NOT_SCORED!r}"))
                elif not CVSS_VECTOR_RE.match(str(cvss["vector"])):
                    I.append(Issue("F049", "error", fid, f"malformed CVSS vector {cvss['vector']!r}"))
                sc = cvss.get("score")
                if sc is not None and (not isinstance(sc, (int, float)) or not 0 <= float(sc) <= 10):
                    I.append(Issue("F050", "error", fid, "CVSS score out of range"))

        # -- regulatory safety (PART E) --------------------------------
        reg = f.get("regulatory")
        if cls == "regulatory" and not reg:
            I.append(Issue("F051", "error", fid,
                           "regulatory finding_class requires a 'regulatory' block"))
        if reg:
            if reg.get("applicability") not in REG_APPLICABILITY:
                I.append(Issue("F052", "error", fid,
                               f"regulatory.applicability must be one of {REG_APPLICABILITY}"))
            if not reg.get("rationale"):
                I.append(Issue("F053", "error", fid,
                               "regulatory finding must record the applicability rationale"))
            if reg.get("finding_type") not in REG_FINDING_TYPE:
                I.append(Issue("F054", "error", fid,
                               f"regulatory.finding_type must be one of {REG_FINDING_TYPE}"))
            if reg.get("applicability") in ("Not Applicable", "Applicability Unconfirmed") \
                    and reg.get("finding_type") == "Control Gap With Evidence":
                I.append(Issue("F055", "error", fid,
                               "cannot assert a control gap when applicability is not established"))
            if not reg.get("regime"):
                I.append(Issue("F056", "error", fid, "regulatory.regime missing"))
            blob = json.dumps(reg, ensure_ascii=False).lower() + " " + str(f.get("title", "")).lower()
            for phrase in FORBIDDEN_REG_PHRASES:
                if phrase in blob:
                    I.append(Issue("F057", "error", fid,
                                   f"forbidden compliance verdict language: {phrase!r} — a repository "
                                   "audit reports gaps, not legal conclusions"))
                    break

        # -- lifecycle -------------------------------------------------
        if f.get("status") in CLOSED_STATUS and f.get("status") == "VERIFIED_FIXED":
            if not f.get("fix_record"):
                I.append(Issue("F058", "error", fid,
                               "VERIFIED_FIXED requires a fix_record reference produced by the "
                               "remediation skill"))
        if f.get("status") == "SUPERSEDED" and not f.get("superseded_by"):
            I.append(Issue("F059", "error", fid, "SUPERSEDED requires superseded_by"))
        if f.get("status") == "DUPLICATE" and not f.get("duplicate_of"):
            I.append(Issue("F060", "error", fid, "DUPLICATE requires duplicate_of"))
        if f.get("confidence") == "False Positive" and f.get("status") not in (
                "FALSE_POSITIVE", "SUPERSEDED"):
            I.append(Issue("F061", "warning", fid,
                           "confidence 'False Positive' but status is not FALSE_POSITIVE"))

        # -- severity/priority coherence -------------------------------
        sev, pri = f.get("severity"), f.get("priority")
        if sev in SEVERITY and pri in PRIORITY:
            expected_pri = PRIORITY[SEVERITY.index(sev)]
            if pri != expected_pri and not f.get("priority_rationale"):
                I.append(Issue("F062", "error", fid,
                               f"priority {pri} diverges from severity {sev} "
                               f"(default {expected_pri}) without priority_rationale"))
        for blocked in f.get("blocks_features") or []:
            if not FEATURE_ID_RE.match(str(blocked)):
                I.append(Issue("F063", "error", fid, f"malformed feature id {blocked!r}"))

    res.stats = {"findings": len(findings), "by_severity": counts, "unique_ids": len(seen_ids)}
    return res


# --------------------------------------------------------------------------
# CHECK 2 — evidence and line references against the real repository
# --------------------------------------------------------------------------

def verify_evidence(findings: list[dict], repo: str, audit_dir: str | None = None) -> CheckResult:
    res = CheckResult("evidence_verification")
    if not os.path.isdir(repo):
        res.executed = False
        res.blocked_reason = f"repository path not found: {repo}"
        return res

    rc, head = git(repo, "rev-parse", "HEAD")
    head = head if rc == 0 else None
    checked_lines = 0
    checked_hashes = 0

    for f in findings:
        fid = str(f.get("id"))
        I = res.issues

        if head and f.get("audited_commit") and f["audited_commit"] not in (head, head[:len(f["audited_commit"])]):
            I.append(Issue("E001", "error", fid,
                           f"audited_commit {f['audited_commit']} != repository HEAD {head[:12]}"))

        for loc in f.get("locations") or []:
            rel = loc.get("file") or ""
            full = os.path.join(repo, rel)
            if not os.path.isfile(full):
                I.append(Issue("E002", "error", fid, f"cited file does not exist: {rel}"))
                continue
            try:
                with open(full, encoding="utf-8", errors="replace") as fh:
                    lines = fh.read().splitlines()
            except OSError as exc:
                I.append(Issue("E003", "error", fid, f"cannot read {rel}: {exc}"))
                continue
            ls, le = loc.get("line_start"), loc.get("line_end")
            if isinstance(ls, int) and isinstance(le, int):
                checked_lines += 1
                if le > len(lines):
                    I.append(Issue("E004", "error", fid,
                                   f"{rel}:{ls}-{le} exceeds file length ({len(lines)} lines)"))
                    continue
                actual = "\n".join(lines[ls - 1:le])
                want = loc.get("excerpt_sha256")
                if want:
                    checked_hashes += 1
                    got = hashlib.sha256(actual.encode("utf-8")).hexdigest()
                    if got != want:
                        I.append(Issue("E005", "error", fid,
                                       f"stale evidence: {rel}:{ls}-{le} content hash {got[:12]} "
                                       f"!= recorded {str(want)[:12]}"))
                if loc.get("symbol"):
                    window = "\n".join(lines[max(0, ls - 30):min(len(lines), le + 5)])
                    if loc["symbol"] not in window:
                        I.append(Issue("E006", "warning", fid,
                                       f"symbol {loc['symbol']!r} not found near {rel}:{ls}"))

        for e in f.get("evidence") or []:
            ref = e.get("ref")
            if not ref or e.get("type") == "document":
                continue
            if re.match(r"^https?://", str(ref)):
                continue
            base = audit_dir if str(ref).startswith(".audit") else repo
            cand = os.path.join(base if base else repo, str(ref).split(":")[0])
            if str(ref).startswith(".audit") and audit_dir:
                cand = os.path.join(os.path.dirname(audit_dir.rstrip("/")), str(ref).split(":")[0])
            if not os.path.exists(cand) and not os.path.exists(os.path.join(repo, str(ref).split(":")[0])):
                I.append(Issue("E007", "warning", fid, f"evidence artifact not found: {ref}"))

        if f.get("finding_class") in SECURITY_CLASSES and f.get("severity") in ("Critical", "High"):
            chain = (f.get("reachability") or {}).get("caller_chain") or []
            if (f.get("reachability") or {}).get("status") == "Confirmed" and not chain:
                I.append(Issue("E008", "error", fid,
                               "Critical/High security finding claims confirmed reachability "
                               "but records no caller chain"))

    res.stats = {"line_ranges_checked": checked_lines, "content_hashes_checked": checked_hashes,
                 "repo_head": head}
    return res


# --------------------------------------------------------------------------
# CHECK 3 — duplicate detection (PART G)
# --------------------------------------------------------------------------

def _symbols(finding: dict) -> set[str]:
    return {str(l.get("symbol") or "").strip().lower()
            for l in finding.get("locations") or [] if l.get("symbol")}


def detect_duplicates(findings: list[dict], threshold: float = 0.70) -> CheckResult:
    res = CheckResult("duplicate_detection")
    by_fp: dict[str, list[str]] = {}
    for f in findings:
        fp = f.get("fingerprint") or compute_fingerprint(f)
        by_fp.setdefault(fp, []).append(str(f.get("id")))
    exact = 0
    for fp, ids in by_fp.items():
        live = [i for i in ids]
        if len(live) > 1:
            exact += 1
            res.issues.append(Issue("D001", "error", ", ".join(live),
                                    f"identical fingerprint {fp} — these are the same finding; "
                                    f"keep the lowest id and mark the rest DUPLICATE"))

    near = 0
    for i, a in enumerate(findings):
        for b in findings[i + 1:]:
            if a.get("fingerprint") == b.get("fingerprint"):
                continue
            if a.get("component") != b.get("component"):
                continue
            if weakness_key(a) != weakness_key(b):
                continue
            sa, sb = _tokens(_primary_excerpt(a)), _tokens(_primary_excerpt(b))
            sim = jaccard(sa, sb)
            same_file = {normalize_path(l.get("file", "")) for l in a.get("locations") or []} & \
                        {normalize_path(l.get("file", "")) for l in b.get("locations") or []}
            declared = {str(a.get("duplicate_of")), str(b.get("duplicate_of"))}
            if str(a.get("id")) in declared or str(b.get("id")) in declared:
                continue
            same_symbol = bool(_symbols(a) & _symbols(b))
            if same_file and (sim >= threshold or same_symbol):
                near += 1
                res.issues.append(Issue(
                    "D002", "warning", f"{a.get('id')} / {b.get('id')}",
                    f"probable same root issue: same component, same weakness key, "
                    f"overlapping file, excerpt similarity {sim:.2f}"
                    + (", same symbol" if same_symbol else "")))
    res.stats = {"exact_duplicate_groups": exact, "near_duplicate_pairs": near,
                 "distinct_fingerprints": len(by_fp)}
    return res


# --------------------------------------------------------------------------
# CHECK 4 — report ↔ ledger reconciliation (PART I)
# --------------------------------------------------------------------------

BUG_HEADING_RE = re.compile(r"^#{2,4}\s*(BUG-\d{3,})\b", re.M)
FEAT_HEADING_RE = re.compile(r"^#{2,4}\s*(FEAT-\d{3,})\b", re.M)


def validate_report(findings: list[dict], report_path: str,
                    product_report_path: str | None = None) -> CheckResult:
    res = CheckResult("report_reconciliation")
    if not os.path.exists(report_path):
        res.executed = False
        res.blocked_reason = f"report not found: {report_path}"
        return res
    text = open(report_path, encoding="utf-8").read()
    in_report = set(BUG_HEADING_RE.findall(text))
    in_ledger = {str(f.get("id")) for f in findings
                 if f.get("status") not in ("DUPLICATE", "FALSE_POSITIVE")}

    for missing in sorted(in_ledger - in_report):
        res.issues.append(Issue("R001", "error", missing,
                                "present in findings.jsonl but absent from the report"))
    for extra in sorted(in_report - in_ledger):
        res.issues.append(Issue("R002", "error", extra,
                                "documented in the report but absent from findings.jsonl"))

    for ph in sorted(set(PLACEHOLDER_RE.findall(text))):
        res.issues.append(Issue("R003", "error", None,
                                f"unresolved template placeholder {ph}", report_path))

    if "DRAFT — VALIDATION FAILED" in text:
        res.issues.append(Issue("R004", "warning", None,
                                "report still carries the DRAFT banner", report_path))

    # Severity counts stated in the report must match the ledger.
    ledger_counts = {s: 0 for s in SEVERITY}
    for f in findings:
        if f.get("severity") in ledger_counts and f.get("status") not in ("DUPLICATE", "FALSE_POSITIVE"):
            ledger_counts[f["severity"]] += 1
    for sev in SEVERITY:
        m = re.search(rf"^\|\s*{sev}[^|]*\|\s*(\d+)\s*\|", text, re.M)
        if m and int(m.group(1)) != ledger_counts[sev]:
            res.issues.append(Issue("R005", "error", None,
                                    f"report states {m.group(1)} {sev} findings; ledger has "
                                    f"{ledger_counts[sev]}", report_path))

    feats_referenced = set()
    for f in findings:
        feats_referenced.update(str(x) for x in (f.get("blocks_features") or []))
    if product_report_path and os.path.exists(product_report_path):
        ptext = open(product_report_path, encoding="utf-8").read()
        pfeats = set(FEAT_HEADING_RE.findall(ptext))
        for ph in sorted(set(PLACEHOLDER_RE.findall(ptext))):
            res.issues.append(Issue("R003", "error", None,
                                    f"unresolved template placeholder {ph}", product_report_path))
        for miss in sorted(feats_referenced - pfeats):
            res.issues.append(Issue("R006", "warning", miss,
                                    "referenced as blocked by a finding but not defined in the "
                                    "product document"))
    res.stats = {"report_findings": len(in_report), "ledger_findings": len(in_ledger)}
    return res


# --------------------------------------------------------------------------
# CHECK 5 — secret leakage in generated artifacts (PART I)
# --------------------------------------------------------------------------

def scan_secrets(paths: Iterable[str]) -> CheckResult:
    res = CheckResult("secret_leakage")
    scanned = 0
    for path in paths:
        if not os.path.exists(path):
            continue
        scanned += 1
        with open(path, encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                if SECRET_ALLOWLIST.search(line):
                    continue
                for name, pat in SECRET_PATTERNS:
                    if pat.search(line):
                        res.issues.append(Issue(
                            "S001", "error", None,
                            f"possible {name} literal in generated artifact — reports must "
                            f"carry location and class, never the value",
                            f"{path}:{n}"))
                        break
    res.stats = {"files_scanned": scanned}
    if scanned == 0:
        res.executed = False
        res.blocked_reason = "no artifacts to scan"
    return res


# --------------------------------------------------------------------------
# CHECK 6 — audit manifest (PART H, K)
# --------------------------------------------------------------------------

def validate_manifest(path: str) -> CheckResult:
    res = CheckResult("manifest")
    if not os.path.exists(path):
        res.executed = False
        res.blocked_reason = f"manifest not found: {path}"
        return res
    try:
        m = json.load(open(path, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        res.issues.append(Issue("M001", "error", None, f"manifest is not valid JSON: {exc}", path))
        return res

    for key in ("schema_version", "project_name", "audit_date", "git", "tier",
                "components", "standards_selected", "threat_model", "executed_commands"):
        if key not in m:
            res.issues.append(Issue("M002", "error", None, f"manifest missing '{key}'", path))

    if m.get("schema_version") != SCHEMA_VERSION:
        res.issues.append(Issue("M003", "error", None,
                                f"manifest schema_version must be {SCHEMA_VERSION}", path))

    for c in m.get("components") or []:
        if not c.get("primary_marker"):
            res.issues.append(Issue("M004", "error", None,
                                    f"component {c.get('name')!r} has no primary_marker evidence", path))
        if c.get("confidence") not in ("Confirmed", "Likely", "Uncertain"):
            res.issues.append(Issue("M005", "error", None,
                                    f"component {c.get('name')!r} confidence invalid", path))

    for s in m.get("standards_selected") or []:
        for k in ("name", "version", "verification_status", "accessed"):
            if not s.get(k):
                res.issues.append(Issue("M006", "error", None,
                                        f"standard {s.get('name')!r} missing '{k}'", path))
        if s.get("verification_status") not in ("Verified", "Unverified", "Unreachable"):
            res.issues.append(Issue("M007", "error", None,
                                    f"standard {s.get('name')!r} verification_status invalid", path))

    for cmd in m.get("executed_commands") or []:
        if cmd.get("result") not in COMMAND_RESULT:
            res.issues.append(Issue("M008", "error", None,
                                    f"command result {cmd.get('result')!r} not in {COMMAND_RESULT}", path))
        if cmd.get("command_class") not in COMMAND_CLASS:
            res.issues.append(Issue("M009", "error", None,
                                    f"command {cmd.get('command')!r} missing/invalid command_class", path))
        if cmd.get("command_class") == "PROHIBITED":
            res.issues.append(Issue("M010", "error", None,
                                    f"a PROHIBITED command was recorded as executed: "
                                    f"{cmd.get('command')!r}", path))
        if cmd.get("result") not in ("Not Executed", "Blocked", "Not Applicable"):
            if not cmd.get("evidence"):
                res.issues.append(Issue("M011", "error", None,
                                        f"command {cmd.get('command')!r} reports {cmd.get('result')!r} "
                                        "with no captured evidence", path))
            if cmd.get("command_class") == "CONTROLLED_EXECUTION":
                st = cmd.get("repo_state") or {}
                if not st.get("before") or not st.get("after"):
                    res.issues.append(Issue("M012", "error", None,
                                            f"controlled execution {cmd.get('command')!r} must record "
                                            "repo_state.before and repo_state.after", path))
                elif st.get("source_modified") is True and not cmd.get("source_change_rationale"):
                    res.issues.append(Issue("M013", "error", None,
                                            f"{cmd.get('command')!r} modified source files during an "
                                            "analysis-only audit", path))

    for r in m.get("runtime_verifications") or []:
        if r.get("result") not in RUNTIME_RESULT:
            res.issues.append(Issue("M014", "error", None,
                                    f"runtime result {r.get('result')!r} not in {RUNTIME_RESULT}", path))
        if r.get("result") in ("PASS", "FAIL") and not r.get("artifact_path"):
            res.issues.append(Issue("M015", "error", None,
                                    f"runtime verification for {r.get('finding_id')} claims "
                                    f"{r.get('result')} without an artifact", path))
        if r.get("result") == "NOT_EXECUTED" and r.get("observed"):
            res.issues.append(Issue("M016", "error", None,
                                    f"runtime verification for {r.get('finding_id')} is NOT_EXECUTED "
                                    "but records an observation", path))

    tm = m.get("threat_model") or {}
    if not tm.get("worst_credible_outcome"):
        res.issues.append(Issue("M017", "error", None,
                                "threat_model.worst_credible_outcome missing — severity is "
                                "uncalibrated without it", path))
    return res


# --------------------------------------------------------------------------
# Quality gate (PART J)
# --------------------------------------------------------------------------

def run_gate(repo: str, audit_dir: str, report: str, product_report: str | None,
             out: str | None) -> tuple[dict, int]:
    findings_path = os.path.join(audit_dir, "findings.jsonl")
    manifest_path = os.path.join(audit_dir, "manifest.json")

    findings, load_issues = load_findings(findings_path)
    load = CheckResult("findings_load", issues=load_issues,
                       stats={"records": len(findings)})

    checks = [load]
    if not load.errors or findings:
        checks.append(validate_findings(findings))
        checks.append(verify_evidence(findings, repo, audit_dir))
        checks.append(detect_duplicates(findings))
        checks.append(validate_report(findings, report, product_report))
    checks.append(validate_manifest(manifest_path))
    checks.append(scan_secrets([p for p in (report, product_report, findings_path) if p]))

    errors = sum(len(c.errors) for c in checks)
    warnings = sum(len(c.warnings) for c in checks)
    blocked = [c.name for c in checks if not c.executed]

    if errors:
        verdict = "FAIL_VALIDATION"
    elif blocked and len(blocked) >= 3:
        verdict = "BLOCKED"
    elif warnings or blocked:
        verdict = "PASS_WITH_LIMITATIONS"
    else:
        verdict = "PASS"

    result = {
        "schema_version": SCHEMA_VERSION,
        "verdict": verdict,
        "repository": os.path.abspath(repo),
        "audited_commit": git(repo, "rev-parse", "HEAD")[1] if os.path.isdir(repo) else None,
        "error_count": errors,
        "warning_count": warnings,
        "blocked_checks": blocked,
        "checks": [c.to_dict() for c in checks],
        "report_banner_required": verdict == "FAIL_VALIDATION",
    }
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
    return result, (1 if verdict == "FAIL_VALIDATION" else 0)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

USAGE = """usage: auditkit.py <command> [options]

commands:
  findings     --findings F                      schema and semantic rules
  evidence     --findings F --repo R [--audit D] files, line ranges, hashes, commit
  lines        --findings F --repo R             line-reference check only
  duplicates   --findings F                      fingerprint and near-duplicate detection
  report       --findings F --report B [--product P]
  secrets      --paths A B C
  manifest     --manifest M
  fingerprint  --findings F                      print recomputed fingerprints
  gate         --repo R --audit D --report B [--product P] [--out O]
"""


def _arg(name: str, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def _args(name: str) -> list[str]:
    if name not in sys.argv:
        return []
    out = []
    for a in sys.argv[sys.argv.index(name) + 1:]:
        if a.startswith("--"):
            break
        out.append(a)
    return out


def _emit(res: CheckResult) -> int:
    for i in res.issues:
        print(i.line())
    print(f"{res.name}: {res.status}  errors={len(res.errors)} warnings={len(res.warnings)} "
          f"stats={json.dumps(res.stats, default=str)}")
    return 1 if res.errors else 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(USAGE)
        return 0
    cmd = argv[1]
    fpath = _arg("--findings", ".audit/findings.jsonl")
    repo = _arg("--repo", ".")
    audit = _arg("--audit", ".audit")

    if cmd == "gate":
        result, code = run_gate(repo, audit, _arg("--report", "BUG_ANALYSIS.md"),
                                _arg("--product"), _arg("--out"))
        for c in result["checks"]:
            print(f"  {c['name']:26} {c['status']:20} "
                  f"errors={c['error_count']} warnings={c['warning_count']}"
                  + (f"  ({c['blocked_reason']})" if c.get("blocked_reason") else ""))
        print(f"\nGATE VERDICT: {result['verdict']}  "
              f"errors={result['error_count']} warnings={result['warning_count']}")
        return code

    if cmd == "secrets":
        return _emit(scan_secrets(_args("--paths")))
    if cmd == "manifest":
        return _emit(validate_manifest(_arg("--manifest", ".audit/manifest.json")))

    findings, issues = load_findings(fpath)
    if issues:
        for i in issues:
            print(i.line())
        if not findings:
            return 1

    if cmd == "findings":
        return _emit(validate_findings(findings))
    if cmd in ("evidence", "lines"):
        return _emit(verify_evidence(findings, repo, audit))
    if cmd == "duplicates":
        return _emit(detect_duplicates(findings))
    if cmd == "report":
        return _emit(validate_report(findings, _arg("--report", "BUG_ANALYSIS.md"), _arg("--product")))
    if cmd == "fingerprint":
        for f in findings:
            print(f"{f.get('id')}\t{compute_fingerprint(f)}\t{f.get('fingerprint','-')}")
        return 0

    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
