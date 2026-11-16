"""Synthetic negative tests for the public/private publication boundary."""
import json

import pytest

from scripts.check_research_public_boundary import content_rule, path_rule, scan_items


@pytest.mark.parametrize("path", [
    "research/private_reference/ref.py",
    "research/hidden_oracles/oracle.json",
    "research/evaluator-private/policy.json",
    "research/secrets/tokens.txt",
    "research/benchmark/private-benchmark/runtime.py",
    "research/private/file.txt",
    "outputs/hidden-tests/suite.json",
    "config/id_ed25519",
    "anything/secret.p12",
    "research/benchmark/evaluator.private.json",
    "research/raw-run.har",
    "research/tmp.tar",
])
def test_reject_sensitive_research_paths(path):
    if path == "research/private/file.txt":
        # a generic 'private' folder is intentionally NOT blocked by this
        # narrow list; use the reserved evaluator-specific names instead.
        assert path_rule(path) is None
    else:
        assert path_rule(path) is not None


@pytest.mark.parametrize("path", [
    "research/benchmark/intake.py",
    "research/benchmark/public_fixture.py",
    "research/oracles/suite.schema.json",
    "research/templates/go_no_go.DRAFT.json",
    "docs/research/EXPERIMENTAL_PROTOCOL_v1.2.md",
    ".env.example",
    "static/img/freio.svg",
])
def test_accept_existing_public_templates(path):
    assert path_rule(path) is None


def test_private_oracle_json_is_rejected_without_printing_contents():
    raw = json.dumps({"suite_id": "UNSHARED_ID", "application_id": "A",
                      "cases": [{"secret":"DO_NOT_LOG"}]}).encode()
    result = scan_items([("research/new-suite.json", raw)])
    assert result[0]["rule"] == "EVALUATOR_PRIVATE_RECORD_OR_SUITE"
    assert "DO_NOT_LOG" not in json.dumps(result)
    assert "UNSHARED_ID" not in json.dumps(result)


def test_private_intake_manifest_rejected():
    obj = {"reference_files": [], "oracle_sha256": "a"*64,
           "reference_dir_path": "/private/secret-location"}
    assert content_rule("research/export.json", json.dumps(obj).encode()) == "EVALUATOR_PRIVATE_RECORD_OR_SUITE"


def test_private_authorization_policy_rejected():
    obj = {"reference_owner_id":"REF", "evaluator_owner_id":"EV",
           "oracle_access":"EVALUATOR_ONLY", "candidate_applications":[]}
    assert content_rule("research/policy.json", json.dumps(obj).encode()) == "EVALUATOR_PRIVATE_RECORD_OR_SUITE"


def test_synthetic_private_key_marker_is_blocked():
    payload = b"-----BEGIN " + b"PRIVATE KEY-----"
    assert content_rule("docs/key.md", payload) == "PEM_PRIVATE_KEY"


def test_synthetic_credential_pattern_is_blocked():
    raw = b"ghp_" + b"a" * 36
    assert content_rule("docs/fixture.md", raw) == "GITHUB_CLASSIC_TOKEN"


def test_text_scan_cap_fails_closed():
    raw = b"x" * (2*1024*1024 + 1)
    assert content_rule("docs/too-large.md", raw) == "TEXT_FILE_TOO_LARGE_TO_SCAN"


def test_allowed_public_example_readme():
    assert scan_items([("research/benchmark/README.md", b"# Explains hidden tests but contains no data")]) == []


def test_credential_exception_env_example():
    assert path_rule(".env.example") is None
    assert path_rule(".env") == "CREDENTIAL_FILE"
