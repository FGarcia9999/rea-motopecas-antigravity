"""Fail-closed best-effort guard against publishing evaluator-private research assets.

Runs against Git-indexed paths, not only the working tree. This is a scoped
defense-in-depth detector, NOT a comprehensive secret scanner; a PASS does not
prove the checkout has never exposed confidential material. Never print any
matched contents or secret values to CI logs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DIRS = {
    "private_reference", "private-reference", "private_oracles",
    "private-oracles", "hidden_oracles", "hidden-oracles",
    "hidden_tests", "hidden-tests", "evaluator_private",
    "evaluator-private", "evaluator_only", "evaluator-only",
    "private_benchmark", "private-benchmark", "secrets",
    ".secrets", "ground_truth_private", "ground-truth-private",
}
FORBIDDEN_FILENAMES = {"id_rsa", "id_ed25519", ".env"}
FORBIDDEN_SUFFIXES = (
    ".har", ".pcap", ".pcapng", ".pem", ".p12", ".pfx", ".key",
    ".sqlite", ".sqlite3", ".db", ".private.json", ".hidden.json",
    ".secret.json", ".secret.yaml", ".secret.yml",
)
TEXT_EXT = {".py", ".md", ".txt", ".json", ".yml", ".yaml",
            ".toml", ".csv", ".env", ".ini", ".sh", ".ps1", ".sql"}
MAX_SCAN_BYTES = 2 * 1024 * 1024
# Do not spell a complete sample key in the source or test fixtures.
SENSITIVE = {
    "PEM_PRIVATE_KEY": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GITHUB_CLASSIC_TOKEN": re.compile(rb"ghp_[A-Za-z0-9]{36}"),
    "GITHUB_FINE_GRAINED_TOKEN": re.compile(rb"github_pat_[A-Za-z0-9_]{60,}"),
}
RESTRICTED_JSON_SETS = [
    {"suite_id", "application_id", "cases"},   # actual hidden-suite JSON
    {"reference_files", "oracle_sha256", "reference_dir_path"}, # private intake
    {"reference_owner_id", "evaluator_owner_id", "oracle_access", "candidate_applications"},
]


def path_rule(relative: str) -> str | None:
    if not relative or "\x00" in relative or "\\" in relative:
        return "INVALID_TRACKED_PATH"
    parts = relative.lower().split("/")
    if any(part in {".", "..", ""} for part in parts):
        return "INVALID_TRACKED_PATH"
    if any(part in FORBIDDEN_DIRS for part in parts[:-1]):
        return "PRIVATE_RESEARCH_DIRECTORY"
    filename = parts[-1]
    if filename in FORBIDDEN_FILENAMES and relative != ".env.example":
        return "CREDENTIAL_FILE"
    if any(filename.endswith(s) for s in FORBIDDEN_SUFFIXES):
        return "PRIVATE_OR_BINARY_ARTIFACT"
    if parts[0] == "research" and filename.endswith((".zip", ".tar", ".tgz", ".7z")):
        return "UNREVIEWED_RESEARCH_ARCHIVE"
    return None


def content_rule(relative: str, raw: bytes) -> str | None:
    ext = Path(relative).suffix.lower()
    if ext not in TEXT_EXT:
        return None
    if len(raw) > MAX_SCAN_BYTES:
        return "TEXT_FILE_TOO_LARGE_TO_SCAN"
    for label, pattern in SENSITIVE.items():
        if pattern.search(raw):
            return label
    # JSON tests, schemas and synthetic treatment packages are public, but a
    # materialized private suite or intake record must never be committed.
    if ext == ".json" and relative.startswith("research/") and not relative.startswith(
        ("research/schemas/", "research/templates/", "research/treatments/")
    ):
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError):
            return "INVALID_RESEARCH_JSON"
        if isinstance(data, dict):
            for fields in RESTRICTED_JSON_SETS:
                if fields.issubset(data):
                    return "EVALUATOR_PRIVATE_RECORD_OR_SUITE"
    return None


def scan_items(items: list[tuple[str, bytes]]) -> list[dict[str, str]]:
    """Pure helper; tests use synthetic names/content, not real hidden material."""
    errors = []
    for path, raw in items:
        rule = path_rule(path) or content_rule(path, raw)
        if rule:
            errors.append({
                "path_tag": hashlib.sha256(path.encode("utf-8")).hexdigest()[:16],
                "rule": rule,
            })
    return errors


def _tracked_files() -> list[tuple[str, bytes]]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    items = []
    for raw in output.split(b"\x00"):
        if not raw:
            continue
        rel = raw.decode("utf-8", "surrogateescape").replace("\\", "/")
        if (problem := path_rule(rel)):
            # Don't read protected paths even to scan their content.
            items.append((rel, b""))
            continue
        location = ROOT / rel
        if location.is_symlink() or not location.is_file():
            items.append((rel, b"-----BEGIN PRIVATE KEY-----"))
            continue
        if location.stat().st_size > MAX_SCAN_BYTES and location.suffix.lower() in TEXT_EXT:
            # Don't read giant logs/JSON; content_rule blocks these.
            items.append((rel, b"0" * (MAX_SCAN_BYTES + 1)))
        elif location.suffix.lower() in TEXT_EXT:
            items.append((rel, location.read_bytes()))
        else:
            items.append((rel, b""))
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description="Public repo guard; cannot certify absence of all secrets")
    parser.parse_args()
    try:
        items = _tracked_files()
        defects = scan_items(items)
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        print(json.dumps({"public_boundary": "ERROR", "reason": type(exc).__name__}))
        return 2
    result = {
        "public_boundary": "PASS_BEST_EFFORT" if not defects else "BLOCK",
        "tracked_files_examined": len(items),
        "violations": defects,
        "real_hidden_benchmark_attested": False,
        "full_secret_scan_guaranteed": False,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not defects else 3


if __name__ == "__main__":
    raise SystemExit(main())
