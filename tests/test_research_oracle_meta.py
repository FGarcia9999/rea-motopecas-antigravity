"""Positive/negative oracle quality controls use public synthetic metadata only."""
import copy

import pytest

from research.oracles.toy_meta_quality import summarize


def _report(result, is_mutant=False):
    return {
        "suite_sha256": "b" * 64,
        "suite_id": "PUBLIC_R2_SMOKE",
        "total_cases": 4,
        "scientific_status": "EVALUATOR_ENGINE_ONLY_NOT_T0_T3_CONFIRMATORY_EVIDENCE",
        "result": result,
        "cases": [
            {"case_id":"PUBLIC_RF03_VALID_CATEGORY",
             "failure_code":"LENGTH_MISMATCH" if is_mutant else None},
            *[{"case_id": f"OTHER_{i}", "failure_code": None} for i in range(3)],
        ],
    }


def test_oracle_controls_reject_mutant_and_accept_alternative():
    result = summarize(_report("PASS"), _report("FAIL", True), _report("PASS"))
    assert result["mutation_detection_rate"] == 1.0
    assert result["false_rejection_rate"] == 0.0
    assert result["status"] == "DESCRIPTIVE_ONLY_NO_SCIENTIFIC_APPROVAL"
    assert result["actual_hidden_test_count"] == 0
    assert result["independent_review"] is False


def test_different_suite_digest_rejected():
    other = _report("PASS")
    other["suite_sha256"] = "c" * 64
    with pytest.raises(ValueError, match="digest"):
        summarize(_report("PASS"), _report("FAIL", True), other)


def test_false_rejection_fails_control():
    with pytest.raises(ValueError, match="outcomes"):
        summarize(_report("PASS"), _report("FAIL", True), _report("FAIL", True))


def test_undetected_mutant_fails_control():
    with pytest.raises(ValueError, match="outcomes"):
        summarize(_report("PASS"), _report("PASS"), _report("PASS"))


def test_failed_but_not_category_mutant_rejected():
    mutant=_report("FAIL")
    with pytest.raises(ValueError, match="seeded category"):
        summarize(_report("PASS"), mutant, _report("PASS"))


def test_no_silent_empty_oracle_suite():
    base = _report("PASS")
    base["total_cases"] = 0
    with pytest.raises(ValueError, match="four-case"):
        summarize(base, _report("FAIL", True), _report("PASS"))
