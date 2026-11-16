"""Evaluator-only intake of private reference source, hidden oracles and policy.

This is a *metadata integrity* workflow, not an experimental run, independent
review, an isolation test, or a signature. It never copies source/tests into
public Git or includes private filenames in its public attestation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from research.oracles.blackbox import _validate_suite, OracleError

REPO = Path(__file__).resolve().parents[2]
MAX_REFERENCE_FILES = 200
MAX_REFERENCE_BYTES = 16 * 1024 * 1024
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_ORACLE_BYTES = 1_000_000
MAX_POLICY_BYTES = 64 * 1024
CODE_EXTENSIONS = {".py", ".js", ".html", ".css", ".json", ".sql", ".txt", ".svg", ".png", ".webp"}
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


class IntakeError(ValueError):
    pass


def _private(path: Path, *, file: bool = False, folder: bool = False) -> Path:
    if path.is_symlink():
        raise IntakeError("Private asset may not be symlink")
    candidate = path.absolute()
    if candidate.resolve().is_relative_to(REPO):
        raise IntakeError("Private assets and records must be stored outside public repository")
    if file and not candidate.is_file():
        raise IntakeError("Required evaluator-owned file missing")
    if folder and not candidate.is_dir():
        raise IntakeError("Required evaluator-owned directory missing")
    return candidate


def _read(path: Path, cap: int) -> bytes:
    try:
        info = path.lstat()
    except OSError as e:
        raise IntakeError("Missing evaluator-owned file") from e
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > cap:
        raise IntakeError("Evaluator-only input must be a unique regular bounded file")
    with path.open("rb") as f:
        value = f.read(cap + 1)
    if len(value) > cap:
        raise IntakeError("Evaluator-only asset exceeds byte cap")
    return value


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _files(root: Path) -> tuple[list[dict], str, int]:
    if not root.is_dir() or root.is_symlink():
        raise IntakeError("Reference must be a non-symlink directory")
    entries = []
    total = 0
    for base, dirs, names in os.walk(root, followlinks=False):
        p = Path(base)
        for d in dirs:
            node = p / d
            if node.is_symlink() or d.startswith(".") or d == "__pycache__":
                raise IntakeError("Unsafe reference directory")
        for n in names:
            path = p / n
            if path.is_symlink():
                raise IntakeError("Symlink source file")
            rel = path.relative_to(root).as_posix()
            if any(x.startswith(".") or x == "__pycache__" for x in path.relative_to(root).parts):
                raise IntakeError("Hidden paths forbidden")
            if path.suffix.lower() not in CODE_EXTENSIONS:
                raise IntakeError("Non-allowlisted reference file type")
            data = _read(path, MAX_FILE_BYTES)
            total += len(data)
            if total > MAX_REFERENCE_BYTES:
                raise IntakeError("Reference total too large")
            entries.append({"path": rel, "sha256": _hash(data), "bytes": len(data)})
            if len(entries) > MAX_REFERENCE_FILES:
                raise IntakeError("Too many reference files")
    if not entries:
        raise IntakeError("Empty reference")
    entries.sort(key=lambda x: x["path"])
    h = hashlib.sha256()
    for entry in entries:
        h.update((entry["path"] + "\0" + str(entry["bytes"]) + "\0" + entry["sha256"] + "\n").encode("utf-8"))
    return entries, h.hexdigest(), total


def _validate_policy(policy: dict) -> None:
    if type(policy) is not dict or set(policy) != {
        "schema_version", "benchmark_id", "reference_owner_id", "evaluator_owner_id",
        "authorization_id", "reference_access", "oracle_access", "observability",
        "candidate_applications", "approval_status",
    }:
        raise IntakeError("Policy keys missing or unexpected")
    if policy["schema_version"] != "1.0" or policy["approval_status"] != "DRAFT":
        raise IntakeError("Policy must be versioned, unapproved DRAFT")
    for key in ("benchmark_id", "reference_owner_id", "evaluator_owner_id", "authorization_id"):
        if not isinstance(policy[key], str) or not ID_PATTERN.fullmatch(policy[key]):
            raise IntakeError("Invalid identifier in evaluator policy")
    if policy["reference_owner_id"] == policy["evaluator_owner_id"]:
        raise IntakeError("Evaluator and reference owner roles must be independently designated")
    if policy["reference_access"] != "EVALUATOR_ONLY" or policy["oracle_access"] != "EVALUATOR_ONLY":
        raise IntakeError("Source and oracle must be declared evaluator-only")
    obs = policy["observability"]
    if not isinstance(obs, list) or sorted(obs) != [
        "DIRECT", "INDIRECT", "INSTRUMENT_ASSISTED", "UNAVAILABLE"
    ]:
        raise IntakeError("Explicit four observability classes required")
    apps = policy["candidate_applications"]
    if not isinstance(apps, list) or len(apps) < 1 or len(apps) > 12:
        raise IntakeError("At least one private benchmark candidate required")
    for item in apps:
        if not isinstance(item, dict) or set(item) != {"application_id", "domain", "agent_target_scope"}:
            raise IntakeError("Invalid candidate benchmark entry")
        if any(not isinstance(item[k], str) or not 1 <= len(item[k]) <= 120 for k in item):
            raise IntakeError("Invalid candidate field")
        if not ID_PATTERN.fullmatch(item["application_id"]):
            raise IntakeError("Invalid application ID")
        if item["agent_target_scope"] != "OWNED_AUTHORIZED_RUNTIME_ONLY":
            raise IntakeError("No external target authorization may be inferred")
    ids = [x["application_id"] for x in apps]
    if len(ids) != len(set(ids)):
        raise IntakeError("Duplicate application IDs")


def prepare(reference_dir: Path, oracle_file: Path, policy_file: Path,
            private_record: Path, public_attestation: Path) -> dict:
    """Fail closed; never attest a frozen pilot or leak contents of evaluator assets."""
    ref = _private(reference_dir, folder=True)
    oracle = _private(oracle_file, file=True)
    policy = _private(policy_file, file=True)
    private = _private(private_record)
    public = _private(public_attestation)
    if oracle.is_relative_to(ref) or policy.is_relative_to(ref):
        raise IntakeError("Oracle and policy must not reside in reference source root")
    if public == private or public.is_relative_to(ref) or private.is_relative_to(ref):
        raise IntakeError("Records must not overwrite or enter reference source")
    if private.exists() or public.exists():
        raise IntakeError("Refuse to overwrite prior attestation")
    oracle_raw = _read(oracle, MAX_ORACLE_BYTES)
    policy_raw = _read(policy, MAX_POLICY_BYTES)
    try:
        suite = json.loads(oracle_raw)
        metadata = json.loads(policy_raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise IntakeError("Invalid evaluator-owned JSON asset") from exc
    if not isinstance(suite, dict) or not isinstance(metadata, dict):
        raise IntakeError("Evaluator-owned inputs must be objects")
    try:
        _validate_suite(suite)
    except OracleError as exc:
        raise IntakeError("Hidden oracle suite fails public structural validation") from exc
    _validate_policy(metadata)
    if suite["application_id"] not in {x["application_id"] for x in metadata["candidate_applications"]}:
        raise IntakeError("Private suite application not declared in evaluator policy")
    entries, source_hash, source_bytes = _files(ref)
    timestamp = datetime.now(timezone.utc).isoformat()
    private_data = {
        "status": "CANDIDATE_INTAKE_ONLY_NOT_FROZEN",
        "created_utc": timestamp,
        "benchmark_id": metadata["benchmark_id"],
        "policy_sha256": _hash(policy_raw),
        "oracle_sha256": _hash(oracle_raw),
        "reference_tree_sha256": source_hash,
        "reference_files": entries,
        "reference_file_count": len(entries),
        "reference_total_bytes": source_bytes,
        "oracle_case_count": len(suite["cases"]),
        "application_id": suite["application_id"],
        "authorization_id": metadata["authorization_id"],
        "policy_file_path": str(policy),
        "oracle_file_path": str(oracle),
        "reference_dir_path": str(ref),
        "source_hidden_from_real_agent": False,
        "oracle_hidden_from_real_agent": False,
        "independent_reviewer_confirmed": False,
        "scientific_P1_P4_approved": False,
        "study_runs_executed": 0,
    }
    public_data = {
        "schema_version": "1.0",
        "classification": "REDACTED_BENCHMARK_CANDIDATE_METADATA_ONLY",
        "status": "PENDING_PRIVATE_EVALUATOR_ISOLATION_AND_APPROVAL",
        "created_utc": timestamp,
        "reference_tree_sha256": source_hash,
        "oracle_sha256": _hash(oracle_raw),
        "policy_sha256": _hash(policy_raw),
        "reference_file_count": len(entries),
        "reference_total_bytes": source_bytes,
        "oracle_case_count": len(suite["cases"]),
        "source_hidden_from_real_agent": False,
        "oracle_hidden_from_real_agent": False,
        "independent_reviewer_confirmed": False,
        "scientific_P1_P4_approved": False,
        "study_runs_executed": 0,
        "raw_source_or_oracle_contents_in_public_attestation": False,
        "reference_paths_in_public_attestation": False,
    }
    private.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    public.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        with private.open("x", encoding="utf-8") as f:
            os.chmod(private, 0o600)
            json.dump(private_data, f, indent=2)
            f.write("\n")
        with public.open("x", encoding="utf-8") as f:
            os.chmod(public, 0o600)
            json.dump(public_data, f, indent=2)
            f.write("\n")
    except Exception:
        private.unlink(missing_ok=True)
        public.unlink(missing_ok=True)
        raise
    return public_data


def main() -> int:
    p = argparse.ArgumentParser(description="Private evaluator asset intake; not a scientific freeze")
    p.add_argument("--reference-dir", required=True, type=Path)
    p.add_argument("--oracle-suite", required=True, type=Path)
    p.add_argument("--policy", required=True, type=Path)
    p.add_argument("--private-record", required=True, type=Path)
    p.add_argument("--public-attestation", required=True, type=Path)
    args = p.parse_args()
    try:
        result = prepare(args.reference_dir, args.oracle_suite, args.policy,
                         args.private_record, args.public_attestation)
        print(json.dumps({"status": result["status"], "source_hidden_from_real_agent": False,
                          "scientific_P1_P4_approved": False, "study_runs_executed": 0}))
        return 0
    except (IntakeError, OSError) as exc:
        print(json.dumps({"status": "REJECTED", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
