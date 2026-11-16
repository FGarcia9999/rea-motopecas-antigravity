"""Generate a clearly PUBLIC toy benchmark recipe in private temporary storage.

Even with a runtime-random token this is NOT an independently designed hidden
benchmark: the generator itself is public. The output is only for intake testing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import secrets

from .intake import _private, IntakeError


def make_fixture(directory: Path) -> dict[str, Path]:
    root = _private(directory)
    if root.exists():
        raise IntakeError("Refuse to overwrite evaluator fixture directory")
    ref = root / "reference"
    evaluator = root / "evaluator"
    ref.mkdir(parents=True, mode=0o700)
    evaluator.mkdir(mode=0o700)
    token = secrets.token_hex(16)
    (ref / "runtime.py").write_text(
        "# GENERATED PUBLIC RECIPE; private token is test-only\n"
        "TOKEN = " + repr(token) + "\n"
        "def app_status(): return {'status': 'ok'}\n", encoding="utf-8"
    )
    suite = {
        "schema_version": "1.0",
        "suite_id": "PUBLIC_INTAKE_FIXTURE",
        "application_id": "SYNTHETIC_P0",
        "cases": [{"case_id": "PUBLIC_HEALTH",
                   "criticality": "MAJOR",
                   "steps": [{"method": "GET", "path": "/api/health",
                              "expected_status": 200,
                              "checks": [{"op": "equals", "pointer": "/status", "value": "ok"}]}]}],
    }
    policy = {
        "schema_version": "1.0",
        "benchmark_id": "PUBLIC_SYNTHETIC_INTAKE",
        "reference_owner_id": "PUBLIC_REF_OWNER",
        "evaluator_owner_id": "PUBLIC_EVAL_OWNER",
        "authorization_id": "LOCAL_SYNTHETIC_ONLY",
        "reference_access": "EVALUATOR_ONLY",
        "oracle_access": "EVALUATOR_ONLY",
        "observability": ["DIRECT", "INDIRECT", "INSTRUMENT_ASSISTED", "UNAVAILABLE"],
        "candidate_applications": [{"application_id": "SYNTHETIC_P0", "domain": "public-toy",
                                    "agent_target_scope": "OWNED_AUTHORIZED_RUNTIME_ONLY"}],
        "approval_status": "DRAFT",
    }
    (evaluator / "oracle.json").write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")
    (evaluator / "policy.json").write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    for path in [ref / "runtime.py", evaluator / "oracle.json", evaluator / "policy.json"]:
        path.chmod(0o600)
    return {"reference": ref, "oracle": evaluator / "oracle.json",
            "policy": evaluator / "policy.json", "root": root}


def main() -> int:
    ap = argparse.ArgumentParser(description="Public fixture recipe (not hidden benchmark)")
    ap.add_argument("--destination", type=Path, required=True)
    args = ap.parse_args()
    fixture = make_fixture(args.destination)
    print(json.dumps({"status": "PUBLIC_RECIPE_PRIVATE_RUNTIME_FIXTURE_CREATED",
                      "scientific_benchmark": False, "hidden_oracle_approved": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
