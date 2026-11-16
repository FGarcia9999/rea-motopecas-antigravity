"""WP3 external, black-box behavior oracle runner.

The evaluator loads its own suite from OUTSIDE the repository, observes only an
authorized local API, and writes a metadata-only report outside the checkout.
This runner cannot certify source-hidden isolation or scientific independence;
those are separate research gates.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
SCHEMA = HERE / "suite.schema.json"
MAX_RESPONSE = 512 * 1024
MAX_REQUEST = 16 * 1024
ALLOWED_METHODS = {"GET", "POST"}
ALLOWED_HEADERS = {"content-type", "idempotency-key"}
CASE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,90}$")


class OracleError(ValueError):
    pass


def _external_file(path: Path, *, must_exist: bool) -> Path:
    candidate = path.resolve()
    if candidate.is_relative_to(REPOSITORY):
        raise OracleError("Evaluator-owned suite and reports must stay outside repository/agent checkout")
    if must_exist and (not candidate.is_file() or candidate.is_symlink()):
        raise OracleError("Evaluator suite file unavailable")
    return candidate


def _target_port(target: str) -> int:
    p = urlsplit(target)
    try:
        port = p.port
    except ValueError as exc:
        raise OracleError("Invalid port") from exc
    if p.scheme != "http" or p.hostname != "127.0.0.1" or port is None or not 8000 <= port <= 8999:
        raise OracleError("Only http://127.0.0.1:8000-8999 is authorized")
    if p.username or p.password or p.query or p.fragment or p.path not in {"", "/"}:
        raise OracleError("No credentials, path, query or fragment in target")
    return port


def _safe_path(path: str) -> str:
    if not path.startswith("/api/") or path.startswith("//") or "\\" in path or "#" in path:
        raise OracleError("Only relative /api/... paths are allowed")
    p = urlsplit(path)
    if p.scheme or p.netloc or p.fragment or not p.path.startswith("/api/"):
        raise OracleError("Absolute URLs or fragments are prohibited")
    decoded = unquote(p.path)
    if "//" in decoded or "\\" in decoded or any(x in {"..", "."} for x in decoded.split("/")):
        raise OracleError("Traversal path is prohibited")
    if any(ord(c) < 32 or ord(c) == 127 for c in path) or len(path) > 1024:
        raise OracleError("Invalid URL path")
    return path


def _pointer(data: object, pointer: str) -> object:
    if pointer == "":
        return data
    if not pointer.startswith("/") or "~" in re.sub(r"~[01]", "", pointer):
        raise OracleError("Invalid JSON Pointer")
    current = data
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if token not in current:
                raise OracleError("JSON_POINTER_MISSING")
            current = current[token]
        elif isinstance(current, list):
            if not token.isascii() or not token.isdigit() or (len(token)>1 and token[0]=="0"):
                raise OracleError("JSON_POINTER_BAD_INDEX")
            index=int(token)
            if index >= len(current):
                raise OracleError("JSON_POINTER_MISSING")
            current=current[index]
        else:
            raise OracleError("JSON_POINTER_MISSING")
    return current


def _validate_suite(doc: dict) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(doc))
    if errors:
        e = sorted(errors, key=lambda x: "/".join(map(str,x.path)))[0]
        raise OracleError("Suite schema: " + "/".join(map(str, e.path)) + " " + e.message)
    ids = [c["case_id"] for c in doc["cases"]]
    if len(ids) != len(set(ids)):
        raise OracleError("Duplicate case IDs are prohibited")
    for case in doc["cases"]:
        for step in case["steps"]:
            _safe_path(step["path"])
            if step["method"] not in ALLOWED_METHODS:
                raise OracleError("Forbidden method")
            if step["method"] == "GET" and "json" in step:
                raise OracleError("GET must not include a body")
            for header, value in step.get("headers", {}).items():
                if header.lower() not in ALLOWED_HEADERS:
                    raise OracleError("Forbidden header: " + header)
                if "\n" in value or "\r" in value:
                    raise OracleError("Header injection")
            names = list(step.get("capture", {}))
            if any(not CASE_ID_RE.fullmatch(n) for n in names):
                raise OracleError("Invalid capture name")


def _send(port: int, step: dict, run_key: str) -> tuple[int, object]:
    method = step["method"]
    path = _safe_path(step["path"])
    headers = {}
    for key, value in step.get("headers", {}).items():
        headers[key] = run_key if value == "$RUN_KEY" else value
    body = None
    if "json" in step:
        body = json.dumps(step["json"], separators=(",", ":")).encode("utf-8")
        if len(body) > MAX_REQUEST:
            raise OracleError("Payload too large")
        headers["Content-Type"] = "application/json"
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        content = response.read(MAX_RESPONSE + 1)
        if len(content) > MAX_RESPONSE:
            raise OracleError("Response exceeds evaluator size cap")
        if not content:
            return response.status, None
        try:
            return response.status, json.loads(content)
        except (ValueError, UnicodeDecodeError) as exc:
            raise OracleError("Expected JSON response") from exc
    finally:
        conn.close()


def _check(data: object, check: dict, captures: dict) -> None:
    op = check["op"]
    if op == "equals":
        actual = _pointer(data, check["pointer"])
        if type(actual) is not type(check["value"]) or actual != check["value"]:
            raise OracleError("EQUALS_MISMATCH")
    elif op == "length":
        value = _pointer(data, check["pointer"])
        if not isinstance(value, (dict, list, str)) or len(value) != check["value"]:
            raise OracleError("LENGTH_MISMATCH")
    elif op == "min_length":
        value = _pointer(data, check["pointer"])
        if not isinstance(value, (dict, list, str)) or len(value) < check["value"]:
            raise OracleError("MIN_LENGTH_MISMATCH")
    elif op == "all_equal":
        arr = _pointer(data, check["pointer"])
        if not isinstance(arr, list) or not arr or any(
            type(_pointer(item, check["field_pointer"])) is not type(check["value"])
            or _pointer(item, check["field_pointer"]) != check["value"] for item in arr
        ):
            raise OracleError("ALL_EQUAL_MISMATCH")
    elif op == "equals_capture":
        if check["capture_name"] not in captures:
            raise OracleError("CAPTURE_NOT_DEFINED")
        actual = _pointer(data, check["pointer"])
        if type(actual) is not type(captures[check["capture_name"]]) or actual != captures[check["capture_name"]]:
            raise OracleError("CAPTURE_MISMATCH")
    else:
        raise OracleError("Unsupported oracle assertion")


def evaluate(suite: dict, target: str, *, suite_sha256: str, run_id: str) -> dict:
    """Return only metadata and check outcomes, never response-body values."""
    _validate_suite(suite)
    port = _target_port(target)
    if not CASE_ID_RE.fullmatch(run_id):
        raise OracleError("Invalid run ID")
    started = datetime.now(timezone.utc).isoformat()
    outcomes = []
    for case in suite["cases"]:
        captures = {}
        failure = None
        steps_executed = 0
        # Fresh key per case prevents collision with prior runs on the demo.
        run_key = "wp3_" + uuid.uuid4().hex
        start_ns = time.monotonic_ns()
        for step in case["steps"]:
            try:
                status, data = _send(port, step, run_key)
                steps_executed += 1
                if status != step["expected_status"]:
                    raise OracleError("HTTP_STATUS_MISMATCH")
                for check in step.get("checks", []):
                    _check(data, check, captures)
                for key, pointer in step.get("capture", {}).items():
                    captures[key] = _pointer(data, pointer)
            except (OracleError, OSError, TimeoutError, http.client.HTTPException) as exc:
                failure = str(exc) if isinstance(exc, OracleError) else "TRANSPORT_OR_TIMEOUT"
                break
        outcomes.append({
            "case_id": case["case_id"],
            "criticality": case["criticality"],
            "passed": failure is None,
            "steps_executed": steps_executed,
            "configured_steps": len(case["steps"]),
            "failure_code": failure,
            "elapsed_ms": round((time.monotonic_ns() - start_ns) / 1e6, 2),
        })
    passed = sum(x["passed"] for x in outcomes)
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "application_id": suite["application_id"],
        "suite_id": suite["suite_id"],
        "suite_sha256": suite_sha256,
        "target": target,
        "started_at": started,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "result": "PASS" if passed == len(outcomes) else "FAIL",
        "passed_cases": passed,
        "total_cases": len(outcomes),
        "critical_failures": sum(not x["passed"] and x["criticality"] == "CRITICAL" for x in outcomes),
        "cases": outcomes,
        "raw_response_bodies_in_report": False,
        "isolation_attested": False,
        "oracle_independent_review_attested": False,
        "scientific_status": "EVALUATOR_ENGINE_ONLY_NOT_T0_T3_CONFIRMATORY_EVIDENCE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="External local-only oracle; no hidden suite is versioned here")
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    try:
        suite_path = _external_file(args.suite, must_exist=True)
        report_path = _external_file(args.report, must_exist=False)
        if suite_path == report_path:
            raise OracleError("Report must not overwrite evaluator suite")
        raw = suite_path.read_bytes()
        if len(raw) > 1_000_000:
            raise OracleError("Suite too large")
        doc = json.loads(raw)
        if not isinstance(doc, dict):
            raise OracleError("Suite must be JSON object")
        result = evaluate(doc, args.target, suite_sha256=hashlib.sha256(raw).hexdigest(), run_id=args.run_id)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({k: result[k] for k in ("run_id", "result", "passed_cases", "total_cases", "critical_failures", "suite_sha256")}))
        return 0 if result["result"] == "PASS" else 3
    except (OracleError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"result": "INVALID_OR_NOT_RUN", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
