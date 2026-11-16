"""M00 scoped-preflight and role-graph checks on PUBLIC synthetic fixtures."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from research.custody import preflight

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "research/custody/access_matrix.DRAFT.json"


def test_public_custody_matrix_is_complete_and_non_authorizing():
    cfg = json.loads(POLICY.read_text(encoding="utf-8"))
    assert cfg["status"] == "DRAFT_HOLD"
    assert cfg["roles_actual_identities_assigned"] is False
    assert cfg["human_approval_received"] is False
    assert cfg["pilot_authorized"] is False
    assert cfg["scientific_p3_approved"] is False
    resources = {r["id"] for r in cfg["resources"]}
    roles = cfg["principals"]
    assert len({r["role"] for r in roles}) == len(roles) == 5
    assert len(resources) == len(cfg["resources"]) == 9
    assert all(not r["actual_identity_assigned"] and
               set(r["allow"]).isdisjoint(r["deny"]) and
               set(r["allow"]) | set(r["deny"]) == resources for r in roles)
    for role in ("implementing_agent", "experiment_operator"):
        principal = next(r for r in roles if r["role"] == role)
        assert "private_reference_source" in principal["deny"]
        assert "private_hidden_oracles" in principal["deny"]
        assert "private_ground_truth" in principal["deny"]
        assert "external_signed_approvals" in principal["deny"]
        assert "authorized_runtime_ui" in principal["allow"]


@pytest.mark.parametrize("url", [
    "https://127.0.0.1:8000/", "http://localhost:8000/",
    "http://127.0.0.2:8000/", "http://127.0.0.1:8001/",
    "http://example.org:8000/", "http://127.0.0.1:8000/admin",
    "http://user:password@127.0.0.1:8000/",
    "http://m00-reference:8000/?token=x",
    "http://m00-reference:8000/#x",
])
def test_external_or_out_of_scope_target_rejected(url):
    with pytest.raises(preflight.ScopeError):
        preflight.validate_runtime_url(url)


def test_accept_only_two_fixed_synthetic_targets():
    assert preflight.validate_runtime_url("http://127.0.0.1:8000/") == ("127.0.0.1", 8000)
    assert preflight.validate_runtime_url("http://m00-reference:8000/") == ("m00-reference", 8000)


def test_valid_file_current_user_access_is_security_failure(tmp_path, monkeypatch):
    canary = tmp_path / preflight.CANARY_NAME
    canary.write_text("PUBLIC_TEST_ONLY")
    monkeypatch.setattr(preflight, "_http_status", lambda *args: 200)
    monkeypatch.setattr(preflight, "_current_uid_matches", lambda *args: True)
    r = preflight.assess(canary, "http://127.0.0.1:8000/", 65534)
    assert r["canary_read_result"] == "ACCESSIBLE"
    assert r["technical_result"] == "INCOMPLETE_OR_UNSAFE"
    assert r["pilot_authorized"] is False


def test_explicit_denial_in_current_agent_identity_passes_one_scope_only(tmp_path, monkeypatch):
    canary = tmp_path / preflight.CANARY_NAME
    canary.write_text("SYNTHETIC")
    def deny(_):
        raise PermissionError("A fabricated test denial, not an actual agent account")
    monkeypatch.setattr(preflight, "_read_one_byte", deny)
    monkeypatch.setattr(preflight, "_http_status", lambda *args: 200)
    monkeypatch.setattr(preflight, "_current_uid_matches", lambda *args: True)
    r = preflight.assess(canary, "http://127.0.0.1:8000/", 65534)
    assert r["technical_result"] == "PASS_ONE_SCOPE"
    assert r["canary_read_result"] == "DENIED"
    assert r["real_llm_or_antigravity_identity_attested"] is False
    assert r["all_network_mcp_and_connector_scopes_checked"] is False
    assert r["scientific_P3"] == "HOLD"
    assert str(tmp_path) not in json.dumps(r)
    assert "SYNTHETIC" not in json.dumps(r)


def test_not_found_is_not_denied(tmp_path, monkeypatch):
    missing = tmp_path / preflight.CANARY_NAME
    monkeypatch.setattr(preflight, "_http_status", lambda *args: 200)
    monkeypatch.setattr(preflight, "_current_uid_matches", lambda *args: True)
    r = preflight.assess(missing, "http://127.0.0.1:8000/", 65534)
    assert r["canary_read_result"] == "NOT_FOUND"
    assert r["technical_result"] == "INCOMPLETE_OR_UNSAFE"


def test_wrong_name_not_probed(tmp_path):
    target = tmp_path / "actual-hidden-oracle.json"
    target.write_text("NEVER_INSPECT_ME")
    assert preflight.inspect_canary(target) == "REJECTED_SCOPE"


def test_symlink_canary_rejected(tmp_path):
    target = tmp_path / "source.txt"
    target.write_text("PUBLIC_TEST_ONLY")
    (tmp_path / preflight.CANARY_NAME).symlink_to(target)
    assert preflight.inspect_canary(tmp_path / preflight.CANARY_NAME) == "UNSAFE_FILE_TYPE"


def test_identity_not_attested_is_incomplete_even_when_denied(tmp_path, monkeypatch):
    canary = tmp_path / preflight.CANARY_NAME
    canary.write_text("PUBLIC")
    monkeypatch.setattr(preflight, "_read_one_byte", lambda _: (_ for _ in ()).throw(PermissionError()))
    monkeypatch.setattr(preflight, "_http_status", lambda *args: 200)
    monkeypatch.setattr(preflight, "_current_uid_matches", lambda *args: False)
    r = preflight.assess(canary, "http://m00-reference:8000/", 65534)
    assert r["canary_read_result"] == "DENIED"
    assert r["technical_result"] == "INCOMPLETE_OR_UNSAFE"


def test_network_down_does_not_pass(tmp_path, monkeypatch):
    canary = tmp_path / preflight.CANARY_NAME
    canary.write_text("PUBLIC")
    monkeypatch.setattr(preflight, "_read_one_byte", lambda _: (_ for _ in ()).throw(PermissionError()))
    monkeypatch.setattr(preflight, "_http_status", lambda *args: None)
    monkeypatch.setattr(preflight, "_current_uid_matches", lambda *args: True)
    assert preflight.assess(canary,"http://m00-reference:8000/",65534)["technical_result"] == "INCOMPLETE_OR_UNSAFE"


def test_canary_inside_public_checkout_rejected():
    candidate = ROOT / preflight.CANARY_NAME
    assert preflight.inspect_canary(candidate) == "REJECTED_REPO_PATH"
