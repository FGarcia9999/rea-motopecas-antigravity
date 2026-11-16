"""Private intake checks using a PUBLIC toy recipe; no research-hidden data."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from research.benchmark import intake
from research.benchmark.public_fixture import make_fixture


@pytest.fixture
def candidate(tmp_path):
    return make_fixture(tmp_path / "outside_repo_fixture")


def _prepare(candidate, suffix="a"):
    base = candidate["root"] / "evaluator-records"
    return intake.prepare(
        candidate["reference"], candidate["oracle"], candidate["policy"],
        base / f"private-{suffix}.json", base / f"public-{suffix}.json",
    )


def test_private_intake_emits_only_nonsecret_public_fields(candidate):
    report = _prepare(candidate)
    assert report["reference_file_count"] == 1
    assert report["oracle_case_count"] == 1
    assert report["study_runs_executed"] == 0
    assert report["source_hidden_from_real_agent"] is False
    assert report["scientific_P1_P4_approved"] is False
    assert report["raw_source_or_oracle_contents_in_public_attestation"] is False
    raw = (candidate["root"] / "evaluator-records/public-a.json").read_text()
    ref = (candidate["reference"] / "runtime.py").read_text()
    token = ref.split("TOKEN = ")[1].splitlines()[0].strip(" '\"")
    assert token not in raw
    assert str(candidate["root"]) not in raw
    assert "oracle.json" not in raw
    assert "runtime.py" not in raw
    private = json.loads((candidate["root"] / "evaluator-records/private-a.json").read_text())
    assert private["reference_files"][0]["path"] == "runtime.py"
    assert private["status"] == "CANDIDATE_INTAKE_ONLY_NOT_FROZEN"


def test_source_mutation_changes_reference_digest_without_changing_oracle(candidate):
    original = _prepare(candidate, "one")
    with (candidate["reference"] / "runtime.py").open("a") as file:
        file.write("# deliberate public toy change\n")
    updated = _prepare(candidate, "two")
    assert original["reference_tree_sha256"] != updated["reference_tree_sha256"]
    assert original["oracle_sha256"] == updated["oracle_sha256"]


def test_repeated_output_does_not_overwrite(candidate):
    _prepare(candidate)
    with pytest.raises(intake.IntakeError, match="Refuse to overwrite"):
        _prepare(candidate)


def test_symlink_reference_file_rejected(candidate):
    file = candidate["reference"] / "runtime.py"
    (candidate["reference"] / "linked.py").symlink_to(file)
    with pytest.raises(intake.IntakeError, match="Symlink"):
        _prepare(candidate)


def test_nested_dotfile_forbidden(candidate):
    nested = candidate["reference"] / "nested"
    nested.mkdir()
    (nested / ".env").write_text("SECRETS=toy")
    with pytest.raises(intake.IntakeError, match="Hidden"):
        _prepare(candidate)


def test_oracle_inside_reference_forbidden(candidate):
    hidden = candidate["reference"] / "hidden.json"
    hidden.write_bytes(candidate["oracle"].read_bytes())
    with pytest.raises(intake.IntakeError, match="must not reside"):
        intake.prepare(candidate["reference"], hidden, candidate["policy"],
                       candidate["root"] / "a.json", candidate["root"] / "b.json")


def test_policy_reference_owner_cannot_equal_evaluator_owner(candidate):
    policy = json.loads(candidate["policy"].read_text())
    policy["evaluator_owner_id"] = policy["reference_owner_id"]
    candidate["policy"].write_text(json.dumps(policy))
    with pytest.raises(intake.IntakeError, match="independently"):
        _prepare(candidate)


def test_unknown_benchmark_application_rejected(candidate):
    policy = json.loads(candidate["policy"].read_text())
    policy["candidate_applications"][0]["application_id"] = "OTHER_APP"
    candidate["policy"].write_text(json.dumps(policy))
    with pytest.raises(intake.IntakeError, match="not declared"):
        _prepare(candidate)


def test_unapproved_authorization_scope_rejected(candidate):
    policy = json.loads(candidate["policy"].read_text())
    policy["candidate_applications"][0]["agent_target_scope"] = "PUBLIC_INTERNET"
    candidate["policy"].write_text(json.dumps(policy))
    with pytest.raises(intake.IntakeError, match="external target"):
        _prepare(candidate)


def test_forged_approval_label_rejected(candidate):
    policy = json.loads(candidate["policy"].read_text())
    policy["approval_status"] = "APPROVED"
    candidate["policy"].write_text(json.dumps(policy))
    with pytest.raises(intake.IntakeError, match="unapproved DRAFT"):
        _prepare(candidate)


def test_unallowlisted_binary_reference_rejected(candidate):
    (candidate["reference"] / "production.db").write_bytes(b"db credentials?")
    with pytest.raises(intake.IntakeError, match="Non-allowlisted"):
        _prepare(candidate)


def test_oversized_reference_file_rejected(candidate):
    (candidate["reference"] / "runtime.py").write_bytes(b"0" * (2 * 1024 * 1024 + 1))
    with pytest.raises(intake.IntakeError, match="bounded file"):
        _prepare(candidate)


def test_private_input_can_never_be_inside_checkout(candidate):
    from research.benchmark.intake import REPO
    with pytest.raises(intake.IntakeError, match="outside public repository"):
        intake.prepare(REPO / "research", candidate["oracle"], candidate["policy"],
                       candidate["root"] / "a", candidate["root"] / "b")


def test_missing_oracle_required_fields_rejected(candidate):
    suite = json.loads(candidate["oracle"].read_text())
    suite["cases"][0]["steps"][0].pop("expected_status")
    candidate["oracle"].write_text(json.dumps(suite))
    with pytest.raises(intake.IntakeError, match="structural validation"):
        _prepare(candidate)


def test_no_test_cases_rejected(candidate):
    suite = json.loads(candidate["oracle"].read_text())
    suite["cases"] = []
    candidate["oracle"].write_text(json.dumps(suite))
    with pytest.raises(intake.IntakeError, match="structural validation"):
        _prepare(candidate)
