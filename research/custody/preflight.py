"""M00 synthetic canary probe. Run only under the actual AGENT process identity.

No private source/oracles are read. This checks a dedicated, pre-authorized,
NONSECRET access canary and a synthetic local runtime. It can prove only that
this identity was denied this canary at this instant, not global isolation.
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
from pathlib import Path
import stat
from urllib.parse import urlsplit

CANARY_NAME = "rea_m00_synthetic_canary.txt"
REPO = Path(__file__).resolve().parents[2]
HOSTS = {"127.0.0.1", "m00-reference"}
PORT = 8000


class ScopeError(ValueError):
    pass


def validate_runtime_url(value: str) -> tuple[str, int]:
    parts = urlsplit(value)
    try:
        port = parts.port
    except ValueError as exc:
        raise ScopeError("INVALID_PORT") from exc
    if (parts.scheme != "http" or parts.hostname not in HOSTS
            or port != PORT or parts.path not in {"", "/"} or parts.query
            or parts.fragment or parts.username or parts.password):
        raise ScopeError("RUNTIME_NOT_SYNTHETIC_ALLOWLIST")
    return parts.hostname, port


def _read_one_byte(path: Path) -> None:
    with path.open("rb") as handle:
        handle.read(1)


def inspect_canary(path: Path) -> str:
    if not path.is_absolute() or path.name != CANARY_NAME:
        return "REJECTED_SCOPE"
    if path.resolve(strict=False).is_relative_to(REPO):
        return "REJECTED_REPO_PATH"
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return "NOT_FOUND"
    except PermissionError:
        return "METADATA_DENIED_NOT_READ_PROOF"
    except OSError:
        return "ERROR"
    if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        return "UNSAFE_FILE_TYPE"
    try:
        _read_one_byte(path)
    except PermissionError:
        return "DENIED"
    except FileNotFoundError:
        return "NOT_FOUND"
    except OSError:
        return "ERROR"
    return "ACCESSIBLE"


def _http_status(host: str, port: int) -> int | None:
    conn = http.client.HTTPConnection(host, port, timeout=3)
    try:
        conn.request("GET", "/", headers={"Accept": "text/html"})
        response = conn.getresponse()
        response.read(0)
        return response.status
    finally:
        conn.close()


def _current_uid_matches(expected_uid: int) -> bool:
    # Linux isolated-runner case. Windows requires separate identity evidence;
    # no username supplied on the command line is accepted as attestation.
    if not hasattr(os, "geteuid"):
        return False
    return expected_uid > 0 and os.geteuid() == expected_uid


def assess(canary_path: Path, runtime_url: str, expected_uid: int) -> dict:
    host, port = validate_runtime_url(runtime_url)
    probe = inspect_canary(canary_path)
    try:
        reachable = _http_status(host, port) == 200
    except (OSError, http.client.HTTPException):
        reachable = False
    uid_verified = _current_uid_matches(expected_uid)
    technical_pass = probe == "DENIED" and reachable and uid_verified
    return {
        "schema_version": "1.0",
        "classification": "PUBLIC_SYNTHETIC_CANARY_ACCESS_TEST",
        "technical_result": "PASS_ONE_SCOPE" if technical_pass else "INCOMPLETE_OR_UNSAFE",
        "canary_read_result": probe,
        "authorized_synthetic_runtime_reachable": reachable,
        "uid_matches_predeclared_unprivileged_identity": uid_verified,
        "sensitive_file_contents_in_output": False,
        "canary_absolute_path_in_output": False,
        "real_llm_or_antigravity_identity_attested": False,
        "all_network_mcp_and_connector_scopes_checked": False,
        "scientific_P3": "HOLD",
        "pilot_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scoped canary only; never point this at a real private source or oracle"
    )
    parser.add_argument("--canary-file", type=Path, required=True)
    parser.add_argument("--runtime-url", required=True)
    parser.add_argument("--expected-uid", type=int, required=True)
    args = parser.parse_args()
    try:
        report = assess(args.canary_file, args.runtime_url, args.expected_uid)
    except (ScopeError, ValueError) as exc:
        print(json.dumps({"technical_result": "REJECTED",
                          "reason": str(exc), "scientific_P3": "HOLD",
                          "pilot_authorized": False}))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report["technical_result"] == "PASS_ONE_SCOPE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
