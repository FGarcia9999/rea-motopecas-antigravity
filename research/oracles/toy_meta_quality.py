"""Summarize PUBLIC positive/negative controls without scientific overclaim."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from research.contracts import summarize_oracle_quality


def summarize(reference: dict, mutant: dict, alternative: dict) -> dict:
    reports = (reference, mutant, alternative)
    if len({r.get("suite_sha256") for r in reports}) != 1:
        raise ValueError("Inconsistent evaluation suite digest")
    if len({r.get("suite_id") for r in reports}) != 1 or any(
        r.get("total_cases") != 4 or len(r.get("cases", [])) != 4
        or r.get("scientific_status") != "EVALUATOR_ENGINE_ONLY_NOT_T0_T3_CONFIRMATORY_EVIDENCE"
        for r in reports
    ):
        raise ValueError("Only the four-case public toy demo is supported")
    if reference.get("result") != "PASS" or alternative.get("result") != "PASS" or mutant.get("result") != "FAIL":
        raise ValueError("Required baseline/mutant/alternative outcomes absent")
    by_id = {c["case_id"]: c for c in mutant["cases"]}
    if not ("PUBLIC_RF03_VALID_CATEGORY" in by_id and
            by_id["PUBLIC_RF03_VALID_CATEGORY"]["failure_code"] == "LENGTH_MISMATCH"):
        raise ValueError("The intentionally seeded category defect was not detected")
    sample = {
        "application_id": "PUBLIC_ROTA2_TOY_ONLY",
        "reference_passed": True,
        "mutation_trials": [{"mutant_id": "PUBLIC_CATEGORY_MUTANT", "compiled": True,
                             "executed": True, "behavior_changed": True, "oracle_detected": True}],
        "correct_alternatives": [{"implementation_id": "PUBLIC_ALT_API", "verified_correct": True,
                                  "oracle_rejected": False}],
        "adjudication": {"double_reviewed": 0, "disagreements": 0, "resolved": 0},
        "status": "DRAFT",
    }
    result = summarize_oracle_quality(sample)
    result.update({
        "classification": "PUBLIC_TOY_CONTROLS_ONLY_NON_GENERALIZABLE",
        "actual_hidden_test_count": 0,
        "independent_review": False,
        "no_go_approved": False,
        "treatment_comparison": "NOT_EXECUTED",
        "reference_report_sha256": reference["suite_sha256"],
    })
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--mutant", type=Path, required=True)
    p.add_argument("--alternative", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    reports = [json.loads(x.read_text()) for x in
               (args.reference, args.mutant, args.alternative)]
    output = summarize(*reports)
    args.report.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: output[k] for k in ("classification","valid_mutants",
          "mutation_detection_rate","verified_correct_alternatives",
          "false_rejection_rate","actual_hidden_test_count")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
