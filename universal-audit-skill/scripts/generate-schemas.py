#!/usr/bin/env python3
"""
Generate schemas/*.json from the vocabularies in auditkit.py.

The schemas are for external tooling (editors, CI, other agents). auditkit.py
remains the authoritative implementation — generating one from the other is what
stops the two from drifting apart, which is the usual failure mode when a spec
and its validator are maintained by hand.

Run with --check in CI to fail when the committed schemas are stale.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auditkit as A  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "schemas")
BASE = "https://github.com/universal-audit-skill/schemas"


def finding_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{BASE}/finding.schema.json",
        "title": "Audit finding",
        "description": (
            "One finding from universal-audit-skill. Security-specific fields live "
            "under mappings and are optional for non-security classes; do not "
            "populate a field with an invented value to satisfy the shape — use "
            "'Not Applicable' where the vocabulary allows it."),
        "type": "object",
        "additionalProperties": True,
        "required": [
            "schema_version", "id", "fingerprint", "audited_commit", "component",
            "finding_class", "category", "title", "severity", "priority", "confidence",
            "epistemic", "status", "evidence", "reachability", "reproduction",
            "impact", "root_cause", "remediation", "verification", "effort",
        ],
        "properties": {
            "schema_version": {"const": A.SCHEMA_VERSION},
            "id": {"type": "string", "pattern": r"^BUG-\d{3,}$"},
            "fingerprint": {
                "type": "string", "pattern": "^[0-9a-f]{16}$",
                "description": "Derived, never authored. See references/fingerprinting.md.",
            },
            "audited_commit": {"type": "string", "minLength": 7},
            "component": {"type": "string", "minLength": 1},
            "platform": {"type": "string"},
            "finding_class": {"enum": A.FINDING_CLASS},
            "category": {"type": "string", "minLength": 1},
            "title": {"type": "string", "minLength": 8},
            "severity": {"enum": A.SEVERITY},
            "priority": {"enum": A.PRIORITY},
            "priority_rationale": {"type": "string"},
            "confidence": {"enum": A.CONFIDENCE},
            "epistemic": {"enum": A.EPISTEMIC},
            "status": {"enum": A.STATUS},
            "effort": {"enum": A.EFFORT},
            "locations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["file", "line_start", "line_end", "verified_at"],
                    "properties": {
                        "file": {"type": "string"},
                        "line_start": {"type": "integer", "minimum": 1},
                        "line_end": {"type": "integer", "minimum": 1},
                        "symbol": {"type": "string"},
                        "excerpt": {"type": "string"},
                        "excerpt_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                        "verified_at": {"type": "string"},
                    },
                },
            },
            "evidence": {
                "type": "array", "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["type"],
                    "properties": {
                        "type": {"enum": A.EVIDENCE_TYPES},
                        "ref": {"type": "string"},
                        "excerpt": {"type": "string"},
                        "sha256": {"type": "string"},
                        "search_command": {
                            "type": "string",
                            "description": "Required in spirit for type=absence: the search that "
                                           "would have found the thing claimed missing.",
                        },
                    },
                },
            },
            "reachability": {
                "type": "object",
                "required": ["status"],
                "properties": {
                    "status": {"enum": A.REACHABILITY},
                    "entry_point": {"type": "string"},
                    "caller_chain": {"type": "array", "items": {"type": "string"}},
                    "notes": {"type": "string"},
                },
            },
            "reproduction": {
                "type": "object",
                "required": ["status", "expected", "observed"],
                "properties": {
                    "status": {"enum": A.REPRO_STATUS},
                    "procedure": {"type": "array", "items": {"type": "string"}},
                    "expected": {"type": "string"},
                    "observed": {"type": "string"},
                },
            },
            "verification": {
                "type": "object",
                "required": ["procedure", "expected_evidence", "level"],
                "properties": {
                    "procedure": {"type": "string"},
                    "expected_evidence": {"type": "string"},
                    "level": {"enum": A.VERIFICATION_LEVEL},
                },
            },
            "remediation": {
                "type": "object",
                "required": ["strategy"],
                "properties": {
                    "strategy": {"type": "string"},
                    "minimal_patch_hint": {"type": "string"},
                    "regression_surface": {"type": "array", "items": {"type": "string"}},
                    "required_tests": {"type": "array", "items": {"type": "string"}},
                },
            },
            "impact": {"type": "string", "minLength": 8},
            "root_cause": {"type": "string", "minLength": 8},
            "mappings": {
                "type": "object",
                "properties": {
                    "cwe": {"type": "array", "items": {"type": "string", "pattern": r"^CWE-\d+$"}},
                    "cve": {"type": "array", "items": {"type": "string"}},
                    "cvss": {
                        "oneOf": [
                            {"const": A.CVSS_NOT_SCORED},
                            {"const": "Not Applicable"},
                            {
                                "type": "object",
                                "required": ["vector"],
                                "properties": {
                                    "version": {"enum": ["3.1", "4.0"]},
                                    "vector": {"type": "string"},
                                    "score": {"type": "number", "minimum": 0, "maximum": 10},
                                    "assumed_metrics": {"type": "array", "items": {"type": "string"}},
                                },
                            },
                        ]
                    },
                    "epss": {
                        "oneOf": [{"const": "Not Applicable"},
                                  {"type": "number", "minimum": 0, "maximum": 1}],
                        "description": "Only meaningful when mappings.cve contains a CVE.",
                    },
                    "kev": {
                        "oneOf": [{"const": "Not Applicable"}, {"type": "boolean"}],
                        "description": "Only meaningful when mappings.cve contains a CVE.",
                    },
                    "owasp": {"type": "array", "items": {"type": "string"}},
                    "asvs": {"type": "array", "items": {"type": "string"}},
                    "maswe": {"type": "array", "items": {"type": "string"}},
                    "iso25010": {"type": "array", "items": {"type": "string"}},
                    "sonar": {"type": "string"},
                },
            },
            "regulatory": {
                "type": "object",
                "required": ["regime", "applicability", "rationale", "finding_type"],
                "properties": {
                    "regime": {"type": "string"},
                    "applicability": {"enum": A.REG_APPLICABILITY},
                    "rationale": {"type": "string"},
                    "finding_type": {"enum": A.REG_FINDING_TYPE},
                    "article_reference": {"type": "string"},
                },
            },
            "blocks_features": {"type": "array", "items": {"type": "string", "pattern": r"^FEAT-\d{3,}$"}},
            "duplicate_of": {"type": "string"},
            "superseded_by": {"type": "string"},
            "fix_record": {"type": "string"},
            "first_seen_commit": {"type": "string"},
        },
    }


def manifest_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{BASE}/audit-manifest.schema.json",
        "title": "Audit manifest",
        "type": "object",
        "required": ["schema_version", "project_name", "audit_date", "git", "tier",
                     "components", "standards_selected", "threat_model", "executed_commands"],
        "properties": {
            "schema_version": {"const": A.SCHEMA_VERSION},
            "project_name": {"type": "string"},
            "audit_date": {"type": "string"},
            "pipeline_version": {"type": "string"},
            "git": {
                "type": "object",
                "required": ["commit", "branch", "working_tree"],
                "properties": {
                    "commit": {"type": "string"},
                    "branch": {"type": "string"},
                    "working_tree": {"enum": ["clean", "dirty", "not-a-repo"]},
                    "uncommitted_files": {"type": "integer", "minimum": 0},
                },
            },
            "tier": {
                "type": "object",
                "required": ["level", "justification"],
                "properties": {
                    "level": {"enum": ["T1", "T2", "T3"]},
                    "justification": {"type": "string"},
                    "sampling_rule": {"type": "string"},
                    "excluded_paths": {"type": "array", "items": {"type": "string"}},
                },
            },
            "consent": {
                "type": "object",
                "properties": {
                    "controlled_execution": {"type": "boolean"},
                    "network_access": {"type": "boolean"},
                    "runtime_environment": {"type": "string"},
                    "recorded_at": {"type": "string"},
                    "granted_by": {"type": "string"},
                },
            },
            "components": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "path", "platform", "primary_marker", "confidence", "in_scope"],
                    "properties": {
                        "name": {"type": "string"},
                        "path": {"type": "string"},
                        "platform": {"type": "string"},
                        "primary_marker": {"type": "string"},
                        "confidence": {"enum": ["Confirmed", "Likely", "Uncertain"]},
                        "in_scope": {"type": "boolean"},
                    },
                },
            },
            "standards_selected": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "version", "verification_status", "accessed", "applicability"],
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                        "publisher": {"type": "string"},
                        "url": {"type": "string"},
                        "accessed": {"type": "string"},
                        "verification_status": {"enum": ["Verified", "Unverified", "Unreachable"]},
                        "applicability": {"enum": A.REG_APPLICABILITY},
                        "trigger": {"type": "string"},
                        "limitations": {"type": "string"},
                    },
                },
            },
            "standards_excluded": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "reason"],
                    "properties": {"name": {"type": "string"}, "reason": {"type": "string"}},
                },
            },
            "threat_model": {
                "type": "object",
                "required": ["worst_credible_outcome"],
                "properties": {
                    "assets": {"type": "array", "items": {"type": "string"}},
                    "actors": {"type": "array", "items": {"type": "string"}},
                    "entry_points": {"type": "array", "items": {"type": "string"}},
                    "trust_boundaries": {"type": "array", "items": {"type": "string"}},
                    "worst_credible_outcome": {"type": "string"},
                },
            },
            "executed_commands": {"$ref": f"{BASE}/command-evidence.schema.json#/$defs/commandList"},
            "runtime_verifications": {
                "type": "array",
                "items": {"$ref": f"{BASE}/command-evidence.schema.json#/$defs/runtimeRecord"},
            },
            "not_verified": {"type": "array", "items": {"type": "string"}},
            "release_recommendation": {
                "enum": ["DO NOT RELEASE", "INTERNAL TESTING ONLY", "CONTROLLED PILOT",
                         "CONDITIONALLY READY", "READY FOR REVIEWED SCOPE", "NOT ASSESSED"],
            },
        },
    }


def command_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{BASE}/command-evidence.schema.json",
        "title": "Command execution and runtime verification evidence",
        "$defs": {
            "repoState": {
                "type": "object",
                "required": ["commit", "branch", "dirty_files"],
                "properties": {
                    "commit": {"type": "string"},
                    "branch": {"type": "string"},
                    "dirty_files": {"type": "integer", "minimum": 0},
                    "tracked_hash": {"type": "string",
                                     "description": "Hash of `git status --porcelain` output."},
                },
            },
            "commandRecord": {
                "type": "object",
                "required": ["step", "command", "command_class", "result"],
                "properties": {
                    "step": {"type": "string"},
                    "command": {"type": "string"},
                    "command_class": {"enum": A.COMMAND_CLASS},
                    "working_directory": {"type": "string"},
                    "environment_assumptions": {"type": "array", "items": {"type": "string"}},
                    "result": {"enum": A.COMMAND_RESULT},
                    "exit_code": {"type": ["integer", "null"]},
                    "duration_seconds": {"type": "number"},
                    "evidence": {"type": "string"},
                    "repo_state": {
                        "type": "object",
                        "properties": {
                            "before": {"$ref": "#/$defs/repoState"},
                            "after": {"$ref": "#/$defs/repoState"},
                            "source_modified": {"type": "boolean"},
                            "modified_paths": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "source_change_rationale": {"type": "string"},
                    "notes": {"type": "string"},
                },
            },
            "commandList": {"type": "array", "items": {"$ref": "#/$defs/commandRecord"}},
            "runtimeRecord": {
                "type": "object",
                "required": ["finding_id", "environment", "timestamp", "command", "result"],
                "properties": {
                    "finding_id": {"type": "string", "pattern": r"^BUG-\d{3,}$"},
                    "environment": {"type": "string"},
                    "device_or_platform": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "prerequisites": {"type": "array", "items": {"type": "string"}},
                    "command": {"type": "string"},
                    "exit_code": {"type": ["integer", "null"]},
                    "expected": {"type": "string"},
                    "observed": {"type": "string"},
                    "result": {"enum": A.RUNTIME_RESULT},
                    "artifact_path": {"type": "string"},
                    "artifact_sha256": {"type": "string"},
                    "operator": {"type": "string"},
                },
            },
        },
        "type": "object",
        "properties": {
            "commands": {"$ref": "#/$defs/commandList"},
            "runtime_verifications": {"type": "array", "items": {"$ref": "#/$defs/runtimeRecord"}},
        },
    }


SCHEMAS = {
    "finding.schema.json": finding_schema,
    "audit-manifest.schema.json": manifest_schema,
    "command-evidence.schema.json": command_schema,
}


def main() -> int:
    check = "--check" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    stale = []
    for name, builder in SCHEMAS.items():
        path = os.path.join(OUT, name)
        text = json.dumps(builder(), indent=2, ensure_ascii=False) + "\n"
        if check:
            if not os.path.exists(path) or open(path, encoding="utf-8").read() != text:
                stale.append(name)
        else:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"wrote schemas/{name}")
    if check:
        if stale:
            print("STALE SCHEMAS (run scripts/generate-schemas.py): " + ", ".join(stale))
            return 1
        print("schemas in sync with auditkit vocabularies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
