"""M02 local MCP JSON-RPC client tests, synthetic outputs only."""
from __future__ import annotations

import json

import pytest

from research.mcp_stdio_smoke import (
    APP_ORIGIN, RpcError, _evidence_identity, _hash_json, _local_target,
    _tool_response, summarize_tools,
)


def _tool(name, required=()):
    schema = {"type": "object", "properties": {"cdp_endpoint": {"type": "string"}}}
    if "target_id" in required:
        schema["properties"]["target_id"] = {"type": "string"}
    return {"name": name, "inputSchema": schema}


def test_catalog_summary_contains_real_tool_contracts_only():
    res = summarize_tools([
        _tool("inspect_web_page", ("target_id",)), _tool("list_browser_targets")
    ])
    assert res["tool_count"] == 2
    assert len(res["names_sha256"]) == 64
    assert res["required_tools_visible"] is True
    assert "cdp_endpoint" not in json.dumps(res)


@pytest.mark.parametrize("names", [
    [_tool("inspect_web_page", ("target_id",))],
    [_tool("list_browser_targets")],
    [_tool("list_browser_targets"), _tool("list_browser_targets"), _tool("inspect_web_page", ("target_id",))],
])
def test_missing_or_duplicate_catalog_fails(names):
    with pytest.raises(RpcError):
        summarize_tools(names)


def test_unsupported_inspect_schema_rejected():
    with pytest.raises(RpcError, match="INSPECT_SCHEMA_MISMATCH"):
        summarize_tools([_tool("list_browser_targets"), _tool("inspect_web_page")])


def test_extract_only_one_exact_authorized_origin_and_page():
    data = {"normalized_result": {"targets": [
        {"origin": APP_ORIGIN, "type": "page", "target_id": "ABC123"},
        {"origin": "https://forbidden.invalid", "type": "page", "target_id": "NO"},
    ]}}
    assert _local_target(data) == "ABC123"


@pytest.mark.parametrize("bad", [
    {"origin": "https://forbidden.invalid", "type": "page", "target_id": "NO"},
    {"origin": APP_ORIGIN, "type": "worker", "target_id": "ABC123"},
    {"origin": APP_ORIGIN, "type": "page", "target_id": "../../"},
    {"origin": APP_ORIGIN, "type": "page", "target_id": "bad space"},
])
def test_reject_nonlocal_or_unsafe_targets(bad):
    with pytest.raises(RpcError):
        _local_target({"normalized_result": {"targets": [bad]}})


def test_ambiguous_multiple_local_targets_rejected():
    data = {"normalized_result": {"targets": [
        {"origin": APP_ORIGIN, "type": "page", "target_id": "A1"},
        {"origin": APP_ORIGIN, "type": "page", "target_id": "A2"},
    ]}}
    with pytest.raises(RpcError, match="EXPECTED_SINGLE"):
        _local_target(data)


def test_evidence_identity_keeps_only_digest_not_target_id():
    raw = {"operation": "inspect_web_page", "evidence_id": "ev_some_example_123",
           "provider": {"id": "rea-cdp-browser"},
           "normalized_result": {"secret_browser_value": "DO_NOT_EXPOSE"}}
    summary = _evidence_identity(raw, "inspect_web_page")
    assert len(summary["evidence_id_sha256"]) == 64
    assert "DO_NOT_EXPOSE" not in json.dumps(summary)
    assert "ev_some_example_123" not in json.dumps(summary)


def test_wrong_provider_and_missing_evidence_rejected():
    with pytest.raises(RpcError, match="PROVIDER"):
        _evidence_identity({"operation": "inspect_web_page",
                            "provider":{"id":"not-rea"},
                            "evidence_id":"ev_1","normalized_result":{}}, "inspect_web_page")
    with pytest.raises(RpcError, match="EVIDENCE_ID"):
        _evidence_identity({"operation":"inspect_web_page",
                            "provider":{"id":"rea-cdp-browser"},
                            "normalized_result":{}}, "inspect_web_page")


def test_structured_content_preferred_without_logging_payload():
    payload = {"structuredContent": {"evidence_id": "ev_123", "normalized_result": {}},
               "content": [{"type":"text", "text":"SECRET_DO_NOT_READ"}]}
    assert _tool_response(payload)["evidence_id"] == "ev_123"


def test_text_fallback_parses_exact_json_record_only():
    payload = {"content":[{"type":"text","text":json.dumps({"evidence_id":"ev_abc"})}]}
    assert _tool_response(payload)["evidence_id"] == "ev_abc"


def test_mcp_is_error_rejected_and_no_raw_echo():
    with pytest.raises(RpcError, match="TOOL_FAILED"):
        _tool_response({"isError": True, "content":[{"type":"text","text":"sensitive"}]})


def test_deterministic_catalog_digest():
    assert _hash_json({"b":2,"a":1}) == _hash_json({"a":1,"b":2})
