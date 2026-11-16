"""All tests use disposable folders and SYNTHETIC metadata only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from research.antigravity.session import ARTIFACTS, EvidenceError, audit, init, REPO


@pytest.fixture
def session(tmp_path):
    root = tmp_path / "private_operator_session"
    created = init(root)
    assert created["pilot_authorized"] is False
    return root


def _make_evidence(root, *, complete=True):
    for role, names in ARTIFACTS.items():
        if not complete and role == "decision_record":
            continue
        (root / "evidence" / names[0]).write_text("PUBLIC_SYNTHETIC_TEST_FIXTURE_" + role)


def _record(root, **changes):
    path = root / "session.DRAFT.json"
    obj = json.loads(path.read_text())
    obj.update(changes)
    path.write_text(json.dumps(obj))


def test_init_creates_private_template_with_no_false_claims(session):
    data = json.loads((session / "session.DRAFT.json").read_text())
    assert data["client_product"] == "UNSET"
    assert data["operator_confirms_two_actual_tools_calls"] is False
    assert data["independent_reviewer_signed_in_private_record"] is False
    assert data["rea_release"] == "6.9.0"
    assert (session / "PRIVATE_README.txt").is_file()


def test_empty_audit_remains_hold(session):
    result = audit(session)
    assert result["roles_present"] == 0
    assert result["result"] == "INCOMPLETE_PRIVATE_RECORD"
    assert result["pilot_authorized"] is False
    redacted = json.loads((session / "audit-redacted-candidate.json").read_text())
    assert redacted["publication_requires_independent_human_review"] is True


def test_all_files_and_operator_claims_still_not_proof(session):
    _make_evidence(session)
    _record(session, client_product="ANTIGRAVITY_IDE",
            client_version="SYNTHETIC_0.0.1",
            operator_confirms_authorization=True,
            operator_confirms_antigravity_origin=True,
            operator_confirms_two_actual_tools_calls=True,
            operator_confirms_evidence_to_decision_link=True,
            independent_reviewer_signed_in_private_record=True,
            tool_catalog_hash_frozen=True)
    result = audit(session)
    assert result["result"] == "FILES_PRESENT_AWAIT_INDEPENDENT_AUTHENTICATION"
    private = json.loads((session / "audit-private.json").read_text())
    public = json.loads((session / "audit-redacted-candidate.json").read_text())
    assert len(private["evidence"]) == 4
    assert public["antigravity_client_real_tool_use_independently_verified"] is False
    assert public["external_reviewer_attestation_examined"] is False
    assert public["scientific_P2"] == "HOLD"
    assert "PUBLIC_SYNTHETIC_TEST_FIXTURE_" not in json.dumps(public)
    assert str(session) not in json.dumps(public)


def test_missing_decision_record_cannot_fake_complete(session):
    _make_evidence(session, complete=False)
    _record(session, client_product="ANTIGRAVITY_CLI",
            operator_confirms_authorization=True,
            operator_confirms_antigravity_origin=True,
            operator_confirms_two_actual_tools_calls=True,
            operator_confirms_evidence_to_decision_link=True)
    assert audit(session)["result"] == "INCOMPLETE_PRIVATE_RECORD"


def test_invalid_release_and_target_rejected(session):
    _record(session, rea_release="latest")
    with pytest.raises(EvidenceError, match="UNFROZEN"):
        audit(session)


def test_mismatched_target_rejected(session):
    _record(session, authorized_target="https://example.org")
    with pytest.raises(EvidenceError, match="UNAUTHORIZED"):
        audit(session)


def test_duplicate_role_txt_png_rejected(session):
    (session / "evidence/tool-catalog.txt").write_text("SYNTHETIC")
    (session / "evidence/tool-catalog.png").write_bytes(b"\x89PNG_fake")
    with pytest.raises(EvidenceError, match="DUPLICATE"):
        audit(session)


def test_symlinked_evidence_rejected(session):
    source = session / "source.txt"
    source.write_text("SYNTHETIC")
    (session / "evidence/targets-call.txt").symlink_to(source)
    with pytest.raises(EvidenceError, match="REGULAR_FILE"):
        audit(session)


def test_extra_evidence_file_rejected(session):
    (session / "evidence/unreviewed.json").write_text("SYNTHETIC")
    with pytest.raises(EvidenceError, match="UNREVIEWED"):
        audit(session)


def test_oversized_file_rejected(session):
    (session / "evidence/tool-catalog.txt").write_bytes(b"a" * (2 * 1024 * 1024 + 1))
    with pytest.raises(EvidenceError, match="BOUNDED"):
        audit(session)


def test_public_repo_location_rejected():
    with pytest.raises(EvidenceError, match="OUTSIDE_PUBLIC_GIT_REPO"):
        init(REPO / "research/antigravity/private_test")


def test_cannot_overwrite_private_audit(session):
    audit(session)
    with pytest.raises(EvidenceError, match="REFUSE_OVERWRITE"):
        audit(session)


def test_approved_labels_are_not_authentication(session):
    _record(session, independent_reviewer_signed_in_private_record=True,
            operator_confirms_antigravity_origin=True,
            operator_confirms_two_actual_tools_calls=True)
    audit(session)
    public = json.loads((session / "audit-redacted-candidate.json").read_text())
    assert public["external_reviewer_attestation_examined"] is False
    assert public["antigravity_client_real_tool_use_independently_verified"] is False
