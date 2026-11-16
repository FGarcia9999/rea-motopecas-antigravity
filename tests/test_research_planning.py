"""Public PRE-PILOT plan consistency tests; no hidden source/oracle material."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "research/planning/milestones.DRAFT.json"


def _load():
    return json.loads(PLAN.read_text(encoding="utf-8"))


def test_plan_is_draft_and_cannot_authorize_pilot():
    p = _load()
    assert p["status"] == "DRAFT_HOLD"
    assert p["classification"] == "PUBLIC_METHOD_INFRASTRUCTURE_ONLY"
    assert p["study_results_recorded"] == 0
    assert p["scientific_pilot_authorized"] is False
    assert p["independent_approvals_obtained"] is False
    assert p["actual_hidden_suite_in_public_repo"] is False
    assert all(m["status"] == "PENDING" and m["owner_assigned"] is False
               and m["private_evidence_required"] is True for m in p["milestones"])


def test_factorial_map_matches_protocol_and_exploratory_counts():
    p = _load()
    matrix = [(x["id"], x["workflow"], x["instrumentation"]) for x in p["treatment_mapping"]]
    assert matrix == [("T0", False, False), ("T1", True, False),
                      ("T2", False, True), ("T3", True, True)]
    assert p["primary_estimand"] == "E[Y(T3)]-E[Y(T1)]"
    assert p["pilot_total_planned"] == 20
    assert p["pilot_repetitions_per_arm_planned"] == 5
    assert len(matrix) * p["pilot_repetitions_per_arm_planned"] == p["pilot_total_planned"]


def test_no_go_metric_ids_match_existing_contract():
    p = _load()
    official = json.loads((ROOT / "research/templates/go_no_go.DRAFT.json").read_text())
    actual = {c["criterion_id"] for c in official["criteria"]}
    assert len(actual) == 9
    assert set(p["no_go_metric_ids"]) == actual
    assert all(c["threshold"] is None and c["approved"] is False for c in official["criteria"])


def test_milestones_form_acyclic_dependency_graph_with_no_unjustified_completion():
    steps = _load()["milestones"]
    lookup = {m["id"]: m for m in steps}
    assert len(steps) == 8 and len(lookup) == 8
    assert list(lookup) == [f"M{i:02d}" for i in range(8)]
    visiting, visited = set(), set()

    def visit(node):
        assert node not in visiting, "Cycle in the planning graph"
        if node in visited:
            return
        visiting.add(node)
        for dep in lookup[node]["depends_on"]:
            assert dep in lookup and dep != node
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for milestone in steps:
        assert milestone["deliverables"] and milestone["exit_evidence"]
        assert milestone["owner_role"] and "@" not in milestone["owner_role"]
        visit(milestone["id"])
    assert len(visited) == 8
    assert "M05" in lookup["M06"]["depends_on"]
    assert "M06" in lookup["M07"]["depends_on"]


def test_public_plan_has_no_private_file_paths_or_urls():
    # Tests a narrow structural invariant; it is NOT a universal secret scanner.
    p = _load()
    for milestone in p["milestones"]:
        for item in milestone["deliverables"] + milestone["exit_evidence"]:
            assert isinstance(item, str) and item
            assert "://" not in item and "\\" not in item and not item.startswith("/")
    text = PLAN.read_text(encoding="utf-8")
    assert "PRIVATE KEY" not in text and "access_token" not in text
