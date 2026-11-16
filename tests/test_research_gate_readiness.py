"""Synthetic and repository-draft gate tests. CI success must not authorize pilot."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

from research.gates.readiness import ROOT, assess


def _make_draft(tmp_path):
    for directory in ("research/templates", "research/treatments"):
        (tmp_path / directory).mkdir(parents=True)
    policy = ROOT / "research/templates/go_no_go.DRAFT.json"
    shutil.copyfile(policy, tmp_path / "research/templates/go_no_go.DRAFT.json")
    for n in range(4):
        shutil.copyfile(ROOT / f"research/treatments/T{n}.json",
                        tmp_path / f"research/treatments/T{n}.json")
    return tmp_path


def test_current_repository_not_automatically_authorized():
    report = assess(ROOT)
    assert report["scientific_status"] == "HOLD"
    assert report["pilot_authorized"] is False
    assert report["pilot_execution_permitted_by_this_tool"] is False
    assert report["observed_evidence"]["private_evaluator_assets_examined"] is False
    assert report["observed_evidence"]["external_scientific_approvals_verified"] is False
    assert report["observed_evidence"]["rea_mcp_stdio_two_tools_technical_smoke_available"] is True
    assert report["observed_evidence"]["criteria_defined"] == 9
    assert report["observed_evidence"]["criteria_without_approved_numeric_owner_threshold"] == 9
    assert {x["gate"] for x in report["blockers"]} >= {"P1", "P2", "P3", "P4"}


def test_missing_or_tampered_treatment_keeps_hold(tmp_path):
    root = _make_draft(tmp_path)
    path = root / "research/treatments/T1.json"
    obj = json.loads(path.read_text())
    obj["rea_instrumentation"] = True
    path.write_text(json.dumps(obj))
    r = assess(root)
    assert r["scientific_status"] == "HOLD"
    assert {"gate":"P1","code":"INVALID_TREATMENT_T1_CONTRACT"} in r["blockers"]


def test_missing_threshold_policy_blocks_pilot(tmp_path):
    root = _make_draft(tmp_path)
    (root / "research/templates/go_no_go.DRAFT.json").unlink()
    r = assess(root)
    assert {"gate":"P1","code":"INVALID_OR_MISSING_THRESHOLD_CONTRACT"} in r["blockers"]


def test_spoofed_approved_label_cannot_enable_pilot(tmp_path):
    root = _make_draft(tmp_path)
    path = root / "research/templates/go_no_go.DRAFT.json"
    policy = json.loads(path.read_text())
    policy["status"] = "APPROVED"
    policy["approved_by"] = "UNVERIFIED_NAME"
    policy["approved_at"] = "2026-11-16T17:30:00-03:00"
    for metric in policy["criteria"]:
        metric["threshold"] = 0.0
        metric["owner"] = "UNVERIFIED_OWNER"
        metric["approved"] = True
    path.write_text(json.dumps(policy))
    r = assess(root)
    assert r["pilot_authorized"] is False
    assert {"gate":"P1","code":"EXTERNAL_SIGNOFF_AND_RESEARCH_FREEZE_NOT_ATTESTED"} in r["blockers"]


def test_evidence_files_present_do_not_authorize(tmp_path):
    root = _make_draft(tmp_path)
    for path in (
        "research/WP2_CLI_SMOKE_EVIDENCE_2026-11-16.md",
        "research/oracles/blackbox.py",
        "research/isolation/agent_probe.py",
        "research/benchmark/intake.py",
    ):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("PUBLIC ENGINEERING EVIDENCE\n")
    result = assess(root)
    assert result["observed_evidence"]["rea_cli_technical_smoke_available"] is True
    assert result["pilot_authorized"] is False


def test_cli_requires_real_external_approval_to_start_pilot():
    r = subprocess.run(
        [sys.executable, "-m", "research.gates.readiness", "--require-ready"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert r.returncode == 3
    data = json.loads(r.stdout)
    assert data["scientific_status"] == "HOLD"
    assert data["pilot_authorized"] is False
