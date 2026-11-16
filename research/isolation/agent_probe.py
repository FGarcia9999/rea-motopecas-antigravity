"""P3 synthetic probe executed as *unprivileged*, isolated agent identity.

A PASS means only that THIS container configuration blocked tested paths and
ports. It DOES NOT prove universal confidentiality or approve the actual P3 gate.
Never prints protected canary content or invokes untrusted targets.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
from pathlib import Path
import socket
import urllib.error
import urllib.request


def _get_json(url: str) -> dict:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=3) as response:
        if response.status != 200:
            raise RuntimeError("Non-200 target status")
        return json.loads(response.read(4096))


def _tcp_blocked(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return False
    except (socket.timeout, socket.gaierror, OSError):
        return True


def _has_default_route() -> bool:
    # Docker IPv4 routing: destination 00000000 denotes a default route.
    with open("/proc/net/route", encoding="utf-8") as f:
        return any(row.split()[1] == "00000000" for row in f.read().splitlines()[1:] if len(row.split()) > 1)


def run(evaluator_ip: str) -> dict:
    ip = ipaddress.ip_address(evaluator_ip)
    if ip.version != 4 or not ip.is_private:
        raise ValueError("Evaluator must be a private Docker IPv4 address")
    try:
        target_ok = _get_json("http://p3-reference:8000/api/health")["status"] == "ok"
    except Exception:
        target_ok = False

    canary = Path("/restricted/p3-canary")
    canary_denied = False
    try:
        with canary.open("rb") as f:
            f.read(1)
    except PermissionError:
        canary_denied = True
    except (FileNotFoundError, OSError):
        pass  # NOT_FOUND is not DENIED.

    checks = {
        "synthetic_reference_api_accessible": target_ok,
        "evaluator_dns_access_blocked": _tcp_blocked("p3-evaluator", 8001),
        "evaluator_direct_ip_access_blocked": _tcp_blocked(str(ip), 8001),
        "explicitly_mounted_canary_read_denied": canary_denied,
        "reference_source_not_mounted": not Path("/srv/reference/app/main.py").exists(),
        "evaluator_private_store_not_mounted": not Path("/evaluator-private").exists(),
        "docker_control_socket_not_mounted": not Path("/var/run/docker.sock").exists(),
        "non_root_agent_uid": os.geteuid() == 65534,
        "no_ipv4_default_route": not _has_default_route(),
    }
    passed = all(checks.values())
    return {
        "result": "PASS_LIMITED_SMOKE" if passed else "FAIL",
        "checks": checks,
        "scientific_P3": "NOT_APPROVED",
        "real_reference_isolation": "NOT_EVALUATED",
        "real_oracle_isolation": "NOT_EVALUATED",
        "agent_is_a_scripted_probe_not_a_LLM": True,
        "canary_content_in_report": False,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--evaluator-ip", required=True)
    args = ap.parse_args()
    result = run(args.evaluator_ip)
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["result"] == "PASS_LIMITED_SMOKE" else 3)
