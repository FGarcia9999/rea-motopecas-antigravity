"""Executable *syntax and consistency* contracts for WP1–WP3.

Validating a JSON document never proves that a REA/MCP tool was invoked, a model
ran, or that a reference/oracle is correct. Hidden evaluator data belongs OUTSIDE
the public repository and the implementing-agent workspace.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_ROOT = Path(__file__).resolve().parent / "schemas"
TREATMENTS = {"T0": (False, False), "T1": (True, False),
              "T2": (False, True), "T3": (True, True)}
REQUIRED_GATES = {
    "MCP_LIVE_CALL", "TRACE_COMPLETENESS", "SOURCE_ISOLATION",
    "AUTHORIZATION_EQUIVALENCE", "ORACLE_MUTATION_DETECTION",
    "ORACLE_FALSE_REJECTION", "MAX_COST", "MAX_ATTRITION",
    "HUMAN_INTERVENTIONS",
}
TERMINAL = {"SUCCEEDED", "FAILED", "TIMED_OUT", "BUDGET_EXHAUSTED", "BLOCKED"}


class ContractError(ValueError):
    """Structured data cannot enter the research evaluation pipeline."""


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContractError("Top-level JSON must be an object")
    return data


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _is_placeholder(value: Any) -> bool:
    return not isinstance(value, str) or not value.strip() or any(
        tag in value.upper() for tag in ("TO_SELECT", "TO_DEFINE", "TO_FREEZE",
                                         "TO_HOMOLOGATE", "UNDEFINED", "UNSPECIFIED",
                                         "PROVISIONAL", "DRAFT_")
    )


def validate_document(kind: str, document: dict[str, Any]) -> dict[str, Any]:
    """Schema-check + cross-field constraints; NOT empirical attestation."""
    path = SCHEMA_ROOT / f"{kind}.schema.json"
    if kind not in {"ground_truth", "evidence", "treatment", "run_manifest", "oracle_quality", "go_no_go"}:
        raise ContractError(f"Unknown contract kind: {kind}")
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda e: (list(map(str, e.path)), e.message))
    if errors:
        e = errors[0]
        location = "/".join(str(i) for i in e.path) or "$"
        raise ContractError(f"{kind} {location}: {e.message}")
    if kind == "treatment":
        expected = TREATMENTS[document["treatment_id"]]
        actual = (document["structured_workflow"], document["rea_instrumentation"])
        if actual != expected:
            raise ContractError(f"Factor mismatch in {document['treatment_id']}: expected W/I={expected}")
        tools = document["tools_allowed"]
        if not expected[1] and (any("REA_" in t or "MCP" in t for t in tools)
                                or document["version_manifest"]["rea_release"] is not None):
            raise ContractError("Non-instrumented arm cannot access REA/MCP")
        if expected[1] and not any("REA" in t or "MCP" in t for t in tools):
            raise ContractError("Instrumented arm must list its REA/MCP tool interface")
        if document["status"] == "FROZEN":
            fields = [
                document["baseline_agent"], document["model_id"], document["stop_rule"],
                document["permissions"]["authorized_target"],
                document["permissions"]["network_policy"],
                document.get("approved_by"),
                document.get("approved_at"),
            ]
            fields.extend(document["version_manifest"][k] for k in
                          ("agent", "browser", "runtime"))
            if any(_is_placeholder(x) for x in fields):
                raise ContractError("FROZEN treatment contains unapproved or placeholder configuration")
            if any(not _is_sha(document["version_manifest"][key]) for key in
                   ("prompts_sha256", "skills_sha256")):
                raise ContractError("FROZEN treatment requires prompt/skill SHA-256 digests")
            if expected[1] and (_is_placeholder(document["version_manifest"]["rea_release"]) or
                                not _is_sha(document["version_manifest"]["mcp_schema_sha256"])):
                raise ContractError("FROZEN instrumented arm needs real REA release and MCP schema hash")
            budget = document["budget"]
            if any(budget[x] is None for x in ("wall_seconds", "max_tool_calls", "token_cap")):
                raise ContractError("FROZEN treatment requires numeric resource budgets")
    elif kind == "evidence":
        if document["record_type"] == "TOOL_CALL" and document["epistemic_status"] == "OBSERVED":
            if document["tool_invocation"].get("status") != "SUCCESS":
                raise ContractError("Failed/timed-out tool call cannot be labeled OBSERVED success")
        if document.get("decision_link", {}).get("verification_status") == "VERIFIED" and \
                document["epistemic_status"] not in {"OBSERVED", "INFERRED"}:
            raise ContractError("Decision link cannot be VERIFIED from unavailable/unknown evidence")
    elif kind == "run_manifest":
        if document["status"] in TERMINAL:
            if not document.get("completed_at") or not document.get("started_at"):
                raise ContractError("Terminal run must preserve start/end timestamps")
            for k in ("model_id", "environment_sha256", "treatment_sha256"):
                if not document.get(k):
                    raise ContractError(f"Terminal run missing {k}")
        if document["status"] == "SUCCEEDED" and document["isolation_status"] != "VERIFIED":
            raise ContractError("Cannot certify a successful run without verified isolation")
    elif kind == "oracle_quality":
        trial_ids = [x["mutant_id"] for x in document["mutation_trials"]]
        if len(trial_ids) != len(set(trial_ids)):
            raise ContractError("Duplicate mutant_id biases sensitivity")
        alt_ids = [x["implementation_id"] for x in document["correct_alternatives"]]
        if len(alt_ids) != len(set(alt_ids)):
            raise ContractError("Duplicate alternatives bias false rejection")
        adjud = document["adjudication"]
        if adjud["resolved"] > adjud["disagreements"] or adjud["disagreements"] > adjud["double_reviewed"]:
            raise ContractError("Invalid adjudication counts")
        if document["status"] == "REVIEWED" and (not document["reference_passed"]
                or not document.get("reviewer_id") or adjud["double_reviewed"] == 0
                or adjud["resolved"] != adjud["disagreements"]):
            raise ContractError("REVIEWED oracle requires reference pass and completed adjudication")
    elif kind == "go_no_go":
        ids = [x["criterion_id"] for x in document["criteria"]]
        if len(ids) != len(set(ids)) or set(ids) != REQUIRED_GATES:
            raise ContractError("Exactly nine distinct prespecified gate criteria are required")
        if document["status"] == "APPROVED":
            if not document.get("approved_by") or not document.get("approved_at"):
                raise ContractError("APPROVED freeze requires named research-team sign-off")
            if any(x["threshold"] is None or x["owner"] is None or not x["approved"]
                   for x in document["criteria"]):
                raise ContractError("No-go thresholds and owners must be approved before pilot")
    return document


def summarize_oracle_quality(document: dict[str, Any]) -> dict[str, Any]:
    """Report non-invented rates; zero eligible items remain not-estimable, never 100%."""
    validate_document("oracle_quality", document)
    eligible = [m for m in document["mutation_trials"]
                if m["compiled"] and m["executed"] and m["behavior_changed"]]
    detected = sum(bool(m["oracle_detected"]) for m in eligible)
    correct = [x for x in document["correct_alternatives"] if x["verified_correct"]]
    false_rejected = sum(bool(x["oracle_rejected"]) for x in correct)
    return {
        "status": "DESCRIPTIVE_ONLY_NO_SCIENTIFIC_APPROVAL",
        "valid_mutants": len(eligible),
        "detected_valid_mutants": detected,
        "mutation_detection_rate": detected / len(eligible) if eligible else None,
        "verified_correct_alternatives": len(correct),
        "false_rejected_alternatives": false_rejected,
        "false_rejection_rate": false_rejected / len(correct) if correct else None,
        "reference_passed": document["reference_passed"],
        "double_reviewed": document["adjudication"]["double_reviewed"],
    }


def summarize_evidence(records: list[dict[str, Any]], eligible_behavior_ids: set[str]) -> dict[str, Any]:
    """Deduplicate by evidence_id and behavior_id; common eligibility denominator."""
    if not eligible_behavior_ids:
        raise ContractError("Eligible behavior set cannot be empty; evaluator must freeze denominator")
    ids: set[str] = set()
    covered: set[str] = set()
    used: set[str] = set()
    valid_ids: set[str] = set()
    for record in records:
        validate_document("evidence", record)
        evid = record["evidence_id"]
        if evid in ids:
            raise ContractError("Repeated evidence_id cannot be counted twice")
        ids.add(evid)
        if record["epistemic_status"] == "OBSERVED":
            valid_ids.add(evid)
            if record["behavior_id"] in eligible_behavior_ids:
                covered.add(record["behavior_id"])
            if record.get("decision_link", {}).get("verification_status") == "VERIFIED":
                used.add(evid)
    return {
        "status": "DESCRIPTIVE_ONLY_NOT_CAUSAL",
        "eligible_behaviors": len(eligible_behavior_ids),
        "covered_behavior_ids": sorted(covered),
        "observation_coverage": len(covered) / len(eligible_behavior_ids),
        "unique_valid_observations": len(valid_ids),
        "verified_decision_links": len(used),
        "evidence_utilization": len(used) / len(valid_ids) if valid_ids else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Schema and consistency checks; NOT proof of completed experiments")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate")
    v.add_argument("kind", choices=["ground_truth","evidence","treatment","run_manifest","oracle_quality","go_no_go"])
    v.add_argument("file", type=Path)
    o = sub.add_parser("oracle-summary")
    o.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        kind = args.kind if args.command == "validate" else "oracle_quality"
        doc = validate_document(kind, load_json(args.file))
        if args.command == "oracle-summary":
            result = summarize_oracle_quality(doc)
        else:
            result = {"contract": kind, "schema_valid": True, "data_attested": False,
                      "scientific_freeze_approved": False}
            if kind in {"treatment", "go_no_go"}:
                result["status"] = doc["status"]
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ContractError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema_valid": False, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
