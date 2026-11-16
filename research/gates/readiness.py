"""Evidence-aware, fail-closed planning readout for REA pilot P1–P4.

A GREEN GitHub CI, a valid JSON schema or a label 'APPROVED' cannot establish
permission to run a controlled scientific experiment. This tool refuses to
issue scientific approvals: researchers must verify signed records outside
the public implementing-agent workspace.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.contracts import ContractError, load_json, validate_document

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ("T0", "T1", "T2", "T3")


def assess(root: Path = ROOT) -> dict:
    """Inspect only public draft artifacts. Never read the private evaluator store."""
    blockers: list[dict[str, str]] = []
    criterion_count = 0
    incomplete = 0
    completed_configs = 0
    try:
        policy = validate_document("go_no_go", load_json(root / "research/templates/go_no_go.DRAFT.json"))
        criterion_count = len(policy["criteria"])
        incomplete = sum(
            c["threshold"] is None or not c["approved"] or not c["owner"]
            for c in policy["criteria"]
        )
        if policy["status"] != "APPROVED" or incomplete:
            blockers.append({"gate": "P1", "code": "NUMERIC_THRESHOLDS_AND_OWNERS_NOT_APPROVED"})
        else:
            blockers.append({"gate": "P1", "code": "EXTERNAL_SIGNOFF_AND_RESEARCH_FREEZE_NOT_ATTESTED"})
    except (OSError, ValueError, ContractError, KeyError) as exc:
        blockers.append({"gate": "P1", "code": "INVALID_OR_MISSING_THRESHOLD_CONTRACT"})
    for treatment in REQUIRED:
        try:
            package = validate_document("treatment", load_json(root / f"research/treatments/{treatment}.json"))
            completed_configs += int(package["status"] == "FROZEN")
        except (OSError, ValueError, ContractError, KeyError):
            blockers.append({"gate": "P1", "code": f"INVALID_TREATMENT_{treatment}_CONTRACT"})
    if completed_configs < len(REQUIRED):
        blockers.append({"gate": "P1", "code": "TREATMENTS_NOT_VERSION_FROZEN"})
    # Engineering artifacts may exist and be useful, but are not substitutes
    # for independent scientific gate approval.
    blockers.extend([
        {"gate": "P2", "code": "ANTIGRAVITY_MCP_REAL_CLIENT_TRACE_AND_APPROVAL_MISSING"},
        {"gate": "P3", "code": "REAL_AGENT_PRIVATE_SOURCE_AND_ORACLE_ISOLATION_NOT_VERIFIED"},
        {"gate": "P4", "code": "INDEPENDENT_HIDDEN_ORACLE_META_EVALUATION_MISSING"},
        {"gate": "P1-P4", "code": "INDEPENDENT_HUMAN_APPROVAL_RECORD_MISSING"},
    ])
    return {
        "schema_version": "1.0",
        "classification": "PUBLIC_PREPILOT_READINESS_DRAFT",
        "scientific_status": "HOLD",
        "pilot_authorized": False,
        "pilot_execution_permitted_by_this_tool": False,
        "observed_evidence": {
            "public_treatment_packages_checked": len(REQUIRED),
            "configured_treatments_marked_frozen": completed_configs,
            "criteria_defined": criterion_count,
            "criteria_without_approved_numeric_owner_threshold": incomplete,
            "rea_cli_technical_smoke_available": (root / "research/WP2_CLI_SMOKE_EVIDENCE_2026-11-16.md").is_file(),
            "rea_mcp_stdio_two_tools_technical_smoke_available": (root / "docs/research/M02_REAL_MCP_STDIO_CHECKPOINT_2026-11-16.md").is_file(),
            "public_oracle_engine_available": (root / "research/oracles/blackbox.py").is_file(),
            "public_synthetic_isolation_smoke_available": (root / "research/isolation/agent_probe.py").is_file(),
            "benchmark_private_intake_contract_available": (root / "research/benchmark/intake.py").is_file(),
            "private_evaluator_assets_examined": False,
            "external_scientific_approvals_verified": False,
        },
        "blockers": blockers,
        "failure_policy": "Fail closed; do not begin randomized T0-T3 runs until P1-P4 independently verified",
        "manuscript_m1v04_results_from_this_check": "NONE",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Public research gate readout; cannot authorize experiments")
    p.add_argument("--require-ready", action="store_true",
                   help="Exit 3 until independent signed gates can be verified by a future tool")
    args = p.parse_args()
    result = assess()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 3 if args.require_ready else 0


if __name__ == "__main__":
    raise SystemExit(main())
