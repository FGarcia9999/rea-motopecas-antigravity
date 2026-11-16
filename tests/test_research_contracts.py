"""Public contract fixtures only. No real application ground truth/hidden oracle material."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from research.contracts import (
    SCHEMA_ROOT, TREATMENTS, ContractError, load_json,
    summarize_evidence, summarize_oracle_quality, validate_document,
)
from research.isolation_probe import probe_denied

ROOT = Path(__file__).resolve().parents[1]


def test_all_schema_definitions_valid():
    for path in sorted(SCHEMA_ROOT.glob("*.schema.json")):
        Draft202012Validator.check_schema(load_json(path))
    assert len(list(SCHEMA_ROOT.glob("*.schema.json"))) == 6


@pytest.mark.parametrize("tid", sorted(TREATMENTS))
def test_all_treatment_packages_draft_only(tid):
    package = load_json(ROOT / "research" / "treatments" / f"{tid}.json")
    assert validate_document("treatment", package) is package
    assert package["status"] == "DRAFT"
    assert package["model_id"] == "TO_SELECT"


def test_swapped_treatment_factor_is_rejected():
    package = load_json(ROOT / "research/treatments/T1.json")
    package["rea_instrumentation"] = True
    with pytest.raises(ContractError, match="Factor mismatch"):
        validate_document("treatment", package)


def test_mcp_cannot_leak_into_t0_or_t1():
    package = load_json(ROOT / "research/treatments/T0.json")
    package["tools_allowed"].append("REA_UNAUTHORIZED")
    with pytest.raises(ContractError, match="cannot access"):
        validate_document("treatment", package)


def test_freeze_cannot_be_faked_with_placeholder_details():
    package = load_json(ROOT / "research/treatments/T3.json")
    package["status"] = "FROZEN"
    with pytest.raises(ContractError, match="unapproved or placeholder"):
        validate_document("treatment", package)


def test_no_go_template_is_not_approved():
    policy = load_json(ROOT / "research/templates/go_no_go.DRAFT.json")
    assert validate_document("go_no_go", policy) is policy
    assert policy["status"] == "DRAFT"
    policy["status"] = "APPROVED"
    with pytest.raises(ContractError, match="sign-off"):
        validate_document("go_no_go", policy)


def test_require_all_nine_unique_gate_ids():
    policy = load_json(ROOT / "research/templates/go_no_go.DRAFT.json")
    policy["criteria"][1]["criterion_id"] = policy["criteria"][0]["criterion_id"]
    with pytest.raises(ContractError, match="Exactly nine"):
        validate_document("go_no_go", policy)


def _evidence(record_type="TOOL_CALL", epistemic_status="OBSERVED"):
    digest = "a" * 64
    return {
        "evidence_id": "EV-DEMO-1",
        "record_type": record_type,
        "epistemic_status": epistemic_status,
        "source": "PUBLIC_TOY_CASE_ONLY",
        "captured_at": "2026-11-16T12:00:00-03:00",
        "behavior_id": "DEMO-RF-01",
        "artifact_sha256": digest,
        "tool_invocation": {
            "tool_name": "FAKE_TEST_TOOL_NOT_REA",
            "tool_version": "0.0-test",
            "arguments_sha256": digest,
            "result_sha256": digest,
            "target": "LOCAL_TOY",
            "duration_ms": 5,
            "status": "SUCCESS",
        },
    }


def test_live_tool_call_requires_invocation_and_hashes():
    item = _evidence()
    assert validate_document("evidence", item)
    del item["tool_invocation"]
    with pytest.raises(ContractError):
        validate_document("evidence", item)


def test_failed_tool_call_cannot_be_observed_success():
    item = _evidence()
    item["tool_invocation"]["status"] = "TIMEOUT"
    with pytest.raises(ContractError, match="cannot be labeled"):
        validate_document("evidence", item)


def test_unavailable_not_observed():
    item = _evidence("UNAVAILABLE", "OBSERVED")
    with pytest.raises(ContractError):
        validate_document("evidence", item)


def test_evidence_coverage_deduplicates_behaviors_and_checks_decision_links():
    first = _evidence()
    second = copy.deepcopy(first)
    second["evidence_id"] = "EV-DEMO-2"
    second["decision_link"] = {
        "requirement_id": "DEMO-RF-01", "decision_id": "DEC-DEMO-1",
        "verification_status": "VERIFIED",
    }
    summary = summarize_evidence([first, second], {"DEMO-RF-01", "DEMO-RF-02"})
    assert summary["observation_coverage"] == .5
    assert summary["evidence_utilization"] == .5
    assert summary["status"] == "DESCRIPTIVE_ONLY_NOT_CAUSAL"
    with pytest.raises(ContractError, match="Repeated"):
        summarize_evidence([first, first], {"DEMO-RF-01"})


def test_evidence_zero_denominator_is_not_a_success():
    with pytest.raises(ContractError, match="cannot be empty"):
        summarize_evidence([], set())


def _oracle():
    return {
        "application_id": "PUBLIC_TOY_ONLY",
        "reference_passed": True,
        "status": "DRAFT",
        "mutation_trials": [
            {"mutant_id": "m1", "compiled": True, "executed": True,
             "behavior_changed": True, "oracle_detected": True},
            {"mutant_id": "m2", "compiled": True, "executed": True,
             "behavior_changed": True, "oracle_detected": False},
            {"mutant_id": "m3", "compiled": False, "executed": False,
             "behavior_changed": False, "oracle_detected": False},
            {"mutant_id": "m4", "compiled": True, "executed": False,
             "behavior_changed": True, "oracle_detected": True},
        ],
        "correct_alternatives": [
            {"implementation_id": "a1", "verified_correct": True,
             "oracle_rejected": False},
            {"implementation_id": "a2", "verified_correct": True,
             "oracle_rejected": True},
        ],
        "adjudication": {"double_reviewed": 2, "disagreements": 1, "resolved": 1},
    }


def test_oracle_denominators_use_only_executed_valid_defects():
    metrics = summarize_oracle_quality(_oracle())
    assert metrics["valid_mutants"] == 2
    assert metrics["mutation_detection_rate"] == .5
    assert metrics["false_rejection_rate"] == .5
    assert metrics["status"] == "DESCRIPTIVE_ONLY_NO_SCIENTIFIC_APPROVAL"


def test_oracle_missing_denominators_not_assumed_perfect():
    d = _oracle()
    d["mutation_trials"] = []
    d["correct_alternatives"] = []
    metrics = summarize_oracle_quality(d)
    assert metrics["mutation_detection_rate"] is None
    assert metrics["false_rejection_rate"] is None


def test_oracle_duplicate_mutant_rejected():
    d = _oracle()
    d["mutation_trials"].append(d["mutation_trials"][0])
    with pytest.raises(ContractError, match="Duplicate"):
        validate_document("oracle_quality", d)


def test_oracle_review_requires_reference_and_adjudication():
    d = _oracle()
    d["status"] = "REVIEWED"
    with pytest.raises(ContractError, match="REVIEWED oracle"):
        validate_document("oracle_quality", d)


def test_toy_ground_truth_schema_only():
    gt = {
        "application_id": "PUBLIC_TOY_ONLY", "requirement_id": "TOY_001",
        "source_statement": "A demo counter increments after a button click",
        "precondition": "counter is 0", "action_sequence": ["click increment"],
        "expected_behavior": "counter displays 1", "category": "UI",
        "criticality": "MINOR", "observability": "DIRECT", "oracle_id": "TOY_ORACLE",
    }
    assert validate_document("ground_truth", gt)


def test_completed_run_requires_real_metadata_and_isolation():
    d = {
        "study_id": "TOY", "run_id": "TOY-01", "application_id": "TOY",
        "treatment_id": "T0", "status": "SUCCEEDED", "seed_label": "toy",
        "artifact_workspace": "/tmp/toy", "authorization_scope": "local",
        "isolation_status": "NOT_VERIFIED", "started_at": None,
    }
    with pytest.raises(ContractError, match="start/end"):
        validate_document("run_manifest", d)


def test_filesystem_probe_never_claims_global_isolation(tmp_path):
    accessible = tmp_path / "public.txt"
    accessible.write_text("toy only")
    assert probe_denied(accessible)["result"] == "ACCESSIBLE"
    assert probe_denied(tmp_path / "missing.txt")["attests"] == "NOT_PROVEN"
