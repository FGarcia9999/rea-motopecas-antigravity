"""M02: REAL rea-agents stdio MCP JSON-RPC calls on an OWNED local toy browser.

This script is NOT Antigravity and makes no scientific pilot claim. Launching
npx is allowed only from a pinned version, against one exact local CDP origin.
It neither automates another person's browser nor uses hidden test suites.
Output: minimal, redacted metadata only; no raw browser/network payload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REA_VERSION = "6.9.0"
CDP_ENDPOINT = "http://127.0.0.1:9222"
APP_ORIGIN = "http://127.0.0.1:8000"
FAMILY_SCOPE = "browser"
MAX_FRAME = 12 * 1024 * 1024


class RpcError(RuntimeError):
    pass


class JsonRpcStdio:
    """Minimal synchronous MCP client; no dependency on the client's tool APIs."""

    def __init__(self, command: list[str], *, env: dict[str, str], stderr_path: Path):
        self.proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=stderr_path.open("wb"), env=env, bufsize=0,
        )
        self.sequence = 0
        self.pending = bytearray()
        self.deadline = 0.0

    def _write(self, message: dict[str, Any]) -> None:
        if self.proc.stdin is None:
            raise RpcError("MCP_STDIN_MISSING")
        self.proc.stdin.write(
            (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")
        )
        self.proc.stdin.flush()

    def notify(self, method: str, params: dict | None = None) -> None:
        self._write({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def rpc(self, method: str, params: dict, *, timeout: int = 90) -> dict:
        self.sequence += 1
        expected = self.sequence
        self._write({"jsonrpc": "2.0", "id": expected, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while True:
            if b"\n" in self.pending:
                raw, rest = self.pending.split(b"\n", 1)
                self.pending = bytearray(rest)
                if not raw.strip():
                    continue
                try:
                    message = json.loads(raw)
                except (ValueError, UnicodeDecodeError) as exc:
                    raise RpcError("NON_JSON_STDOUT_FRAME") from exc
                if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                    raise RpcError("INVALID_JSON_RPC_FRAME")
                if "id" not in message:
                    # notifications e.g., logging; never echo raw payloads
                    continue
                if message["id"] != expected:
                    raise RpcError("UNEXPECTED_RESPONSE_ID")
                if "error" in message:
                    error = message["error"]
                    code = error.get("code", "UNKNOWN") if isinstance(error, dict) else "UNKNOWN"
                    raise RpcError("MCP_RPC_ERROR_" + str(code))
                if "result" not in message:
                    raise RpcError("RPC_RESULT_MISSING")
                return message["result"]
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RpcError("MCP_RPC_TIMEOUT_" + method.replace("/", "_"))
            if self.proc.poll() is not None:
                raise RpcError("MCP_PROCESS_EXITED_" + str(self.proc.returncode))
            if self.proc.stdout is None:
                raise RpcError("MCP_STDOUT_MISSING")
            ready, _, _ = select.select([self.proc.stdout], [], [], min(remaining, 1.0))
            if not ready:
                continue
            raw = os.read(self.proc.stdout.fileno(), 65536)
            if not raw:
                raise RpcError("MCP_STDOUT_CLOSED")
            self.pending.extend(raw)
            if len(self.pending) > MAX_FRAME:
                raise RpcError("MCP_OUTPUT_FRAME_TOO_LARGE")

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        for stream in (self.proc.stdin, self.proc.stdout):
            if stream:
                stream.close()


def _hash_json(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _tool_response(result: dict) -> dict:
    if not isinstance(result, dict) or result.get("isError", False):
        raise RpcError("REA_MCP_TOOL_FAILED")
    struct = result.get("structuredContent")
    if isinstance(struct, dict):
        return struct
    # Text-only servers: only parse complete JSON, never log raw content.
    for item in result.get("content", []):
        if item.get("type") == "text":
            try:
                parsed = json.loads(item.get("text", ""))
            except (ValueError, TypeError):
                continue
            if isinstance(parsed, dict):
                return parsed
    raise RpcError("REA_MCP_MISSING_STRUCTURED_EVIDENCE")


def summarize_tools(tools: list[dict]) -> dict:
    names = [t.get("name") for t in tools]
    if len(names) != len(set(names)) or any(not isinstance(n, str) for n in names):
        raise RpcError("INVALID_TOOL_CATALOG")
    required = {"list_browser_targets", "inspect_web_page"}
    if not required.issubset(names):
        raise RpcError("MISSING_REQUIRED_BROWSER_TOOLS")
    for tool in tools:
        if tool["name"] in required:
            schema = tool.get("inputSchema", {})
            if not isinstance(schema, dict) or "cdp_endpoint" not in schema.get("properties", {}):
                raise RpcError("REA_MCP_BROWSER_INPUT_SCHEMA_MISMATCH")
            if tool["name"] == "inspect_web_page" and "target_id" not in schema.get("properties", {}):
                raise RpcError("REA_MCP_INSPECT_SCHEMA_MISMATCH")
    return {
        "tool_count": len(tools),
        "names_sha256": _hash_json(sorted(names)),
        "selected_input_schema_sha256": _hash_json({
            t["name"]: t.get("inputSchema") for t in tools if t["name"] in required
        }),
        "required_tools_visible": True,
    }


def _local_target(evidence: dict) -> str:
    normalized = evidence.get("normalized_result")
    if not isinstance(normalized, dict):
        raise RpcError("REA_MCP_BROWSER_NORMALIZED_RESULT_MISSING")
    options = normalized.get("targets", [])
    if not isinstance(options, list):
        raise RpcError("REA_MCP_TARGETS_NOT_LIST")
    candidates = [
        target for target in options
        if isinstance(target, dict) and target.get("type") == "page"
        and target.get("origin") == APP_ORIGIN
        and isinstance(target.get("target_id"), str)
        and 0 < len(target["target_id"]) <= 128
        and target["target_id"].isalnum()
    ]
    if len(candidates) != 1:
        raise RpcError("REA_MCP_EXPECTED_SINGLE_LOCAL_TARGET")
    return candidates[0]["target_id"]


def _evidence_identity(data: dict, operation: str) -> dict:
    if data.get("operation") != operation:
        raise RpcError("REA_MCP_OPERATION_MISMATCH")
    if data.get("provider", {}).get("id") != "rea-cdp-browser":
        raise RpcError("REA_MCP_PROVIDER_MISMATCH")
    if not isinstance(data.get("evidence_id"), str) or not data["evidence_id"].startswith("ev_"):
        raise RpcError("REA_MCP_EVIDENCE_ID_MISSING")
    normalized = data.get("normalized_result")
    if not isinstance(normalized, dict):
        raise RpcError("REA_MCP_NORMALIZED_RESULT_MISSING")
    return {
        "evidence_id_sha256": hashlib.sha256(data["evidence_id"].encode("utf-8")).hexdigest(),
        "operation": operation,
        "provider": "rea-cdp-browser",
        "normalized_result_present": True,
    }


def live_smoke(stderr_path: Path) -> dict:
    environment = os.environ.copy()
    environment.update({
        "REA_BROWSER_OBSERVE_ENABLED": "true",
        "REA_BROWSER_CDP_ENDPOINTS_JSON": json.dumps([CDP_ENDPOINT]),
        "REA_BROWSER_ALLOWED_ORIGINS_JSON": json.dumps([APP_ORIGIN]),
        "REA_MCP_TOOL_FAMILIES": FAMILY_SCOPE,
        "REA_MCP_OUTPUT_SCHEMA_PROFILE": "off",
    })
    # No setup writes to Antigravity; this is a separate stdio MCP client.
    client = JsonRpcStdio(
        ["npx", "-y", f"rea-agents@{REA_VERSION}", "mcp"],
        env=environment, stderr_path=stderr_path,
    )
    started = time.monotonic()
    try:
        server = client.rpc(
            "initialize",
            {"protocolVersion": "2025-03-26", "capabilities": {},
             "clientInfo": {"name": "rea-wp2-research-mcp-smoke",
                            "version": "0.1.0"}},
            timeout=125,
        )
        if not isinstance(server, dict) or "serverInfo" not in server:
            raise RpcError("MCP_INITIALIZATION_NOT_CONFIRMED")
        negotiated = server.get("protocolVersion")
        if not isinstance(negotiated, str):
            raise RpcError("MCP_PROTOCOL_NOT_NEGOTIATED")
        client.notify("notifications/initialized")
        catalog = client.rpc("tools/list", {}, timeout=120)
        if not isinstance(catalog, dict) or not isinstance(catalog.get("tools"), list):
            raise RpcError("MCP_TOOL_CATALOG_MISSING")
        summary = summarize_tools(catalog["tools"])
        target_response = client.rpc("tools/call", {
            "name": "list_browser_targets", "arguments": {"cdp_endpoint": CDP_ENDPOINT}
        }, timeout=90)
        target_evidence = _tool_response(target_response)
        target_identity = _evidence_identity(target_evidence, "list_browser_targets")
        selected_target = _local_target(target_evidence)

        inspect_response = client.rpc("tools/call", {
            "name": "inspect_web_page",
            "arguments": {"cdp_endpoint": CDP_ENDPOINT,
                          "target_id": selected_target,
                          "observation_ms": 1500},
        }, timeout=100)
        inspected = _tool_response(inspect_response)
        inspect_identity = _evidence_identity(inspected, "inspect_web_page")
        return {
            "schema_version": "1.0",
            "classification": "REAL_REA_MCP_STDIO_TOOL_CALL_ON_PUBLIC_LOCAL_DEMONSTRATOR",
            "rea_release_pin": REA_VERSION,
            "negotiated_mcp_protocol": negotiated,
            "server_name": str(server["serverInfo"].get("name", ""))[:80],
            "server_version": str(server["serverInfo"].get("version", ""))[:32],
            "mcp_transport": "stdio_JSON_RPC",
            "tool_family_scope": FAMILY_SCOPE,
            "output_schema_profile": "off",
            "catalog": summary,
            "list_targets": target_identity,
            "inspect_page": inspect_identity,
            "two_real_mcp_tools_executed": True,
            "authorized_target": APP_ORIGIN,
            "duration_milliseconds": round((time.monotonic() - started) * 1000),
            "raw_browser_data_in_public_report": False,
            "private_reference_or_hidden_oracles_used": False,
            "antigravity_client_used": False,
            "windows_client_homologated": False,
            "independent_scientific_review": False,
            "scientific_P2": "HOLD_PENDING_ANTIGRAVITY_AND_REVIEW",
            "pilot_t0_t3_executed": False,
        }
    finally:
        client.close()


def main() -> int:
    p = argparse.ArgumentParser(description="Local-owned real REA MCP client, not Antigravity")
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--stderr-file", required=True, type=Path)
    args = p.parse_args()
    if args.report.exists() or args.stderr_file.exists():
        raise SystemExit("REFUSE_OVERWRITE")
    if args.report.absolute().resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise SystemExit("REPORT_MUST_BE_OUTSIDE_PUBLIC_REPOSITORY")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.stderr_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = live_smoke(args.stderr_file)
    except (RpcError, OSError, ValueError, subprocess.SubprocessError) as exc:
        # No secret-bearing detail, no raw stderr/browser output.
        result = {"classification": "REAL_REA_MCP_STDIO_SMOKE",
                  "result": "FAIL",
                  "failure_class": type(exc).__name__,
                  "failure_code": str(exc)[:120] if isinstance(exc, RpcError) else "REDACTED",
                  "antigravity_client_used": False, "scientific_P2": "HOLD",
                  "pilot_t0_t3_executed": False}
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
        return 3
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in
        ("classification", "rea_release_pin", "two_real_mcp_tools_executed",
         "antigravity_client_used", "scientific_P2")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
