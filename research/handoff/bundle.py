"""Content-addressed, minimal-risk *handoff* of candidate implementation files.

NOT a cryptographic signature, a malware scanner, an isolation boundary or proof
of independent assessment. Never execute files merely because verification passed.
The evaluator controls the destination and retains the transfer outside Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import zipfile

REPO = Path(__file__).resolve().parents[2]
MAX_FILES = 120
MAX_TOTAL = 8 * 1024 * 1024
MAX_FILE = 2 * 1024 * 1024
MAX_MANIFEST = 128 * 1024
MAX_ARCHIVE = 10 * 1024 * 1024
ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
ROOTS = {"src", "web", "assets"}
EXT = {
    "src": {".py", ".txt"},
    "web": {".html", ".css", ".js", ".json"},
    "assets": {".svg", ".png", ".jpg", ".webp"},
}


class HandoffError(ValueError):
    pass


def _external(path: Path) -> Path:
    p = path.absolute()
    if p.resolve().is_relative_to(REPO):
        raise HandoffError("Candidate workspace and evaluator storage must not be inside public repository")
    return p


def _name(name: str) -> str:
    if not name or len(name) > 180 or "\\" in name or ":" in name or "\x00" in name:
        raise HandoffError("Unsafe file name")
    if not name.isascii() or any(ord(x) < 32 or ord(x) == 127 for x in name):
        raise HandoffError("Only simple ASCII paths permitted")
    p = PurePosixPath(name)
    if p.is_absolute() or len(p.parts) < 2 or any(x in (".", "..") or (x.startswith(".") or x == "__pycache__") for x in p.parts):
        raise HandoffError("Traversal/dot paths not permitted")
    if p.parts[0] not in ROOTS or p.suffix.lower() not in EXT[p.parts[0]]:
        raise HandoffError("Unexpected file type/path in candidate transfer")
    if name != p.as_posix() or "//" in name:
        raise HandoffError("Noncanonical filename")
    return name


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _manifest(man: dict) -> list[dict]:
    if type(man) is not dict or set(man) != {"schema_version", "run_id", "treatment_id", "files", "format_status"}:
        raise HandoffError("Unknown/missing manifest properties")
    if man["schema_version"] != "1.0" or man["format_status"] != "UNTRUSTED_AGENT_SUBMISSION":
        raise HandoffError("Unsupported handoff format/status")
    if not isinstance(man["run_id"], str) or not ID.fullmatch(man["run_id"]):
        raise HandoffError("Invalid run ID")
    if man["treatment_id"] not in {"T0", "T1", "T2", "T3"}:
        raise HandoffError("Invalid treatment")
    files = man["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
        raise HandoffError("Invalid source count")
    names = set()
    size_sum = 0
    for entry in files:
        if type(entry) is not dict or set(entry) != {"path", "sha256", "bytes"}:
            raise HandoffError("Invalid file entry")
        name = _name(entry["path"])
        if name in names:
            raise HandoffError("Duplicate file")
        names.add(name)
        size = entry["bytes"]
        if type(size) is not int or not 0 <= size <= MAX_FILE:
            raise HandoffError("Invalid file size")
        size_sum += size
        if not isinstance(entry["sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", entry["sha256"]):
            raise HandoffError("Invalid digest")
    if size_sum > MAX_TOTAL:
        raise HandoffError("Bundle over capacity")
    return files


def _read_source(path: Path) -> bytes:
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise HandoffError("Candidate source unavailable") from exc
    if not stat.S_ISREG(mode) or path.is_symlink():
        raise HandoffError("Symlinks and special files are forbidden")
    if path.stat().st_size > MAX_FILE:
        raise HandoffError("Oversized candidate file")
    try:
        with path.open("rb") as f:
            data = f.read(MAX_FILE + 1)
    except OSError as exc:
        raise HandoffError("Cannot read candidate source") from exc
    if len(data) > MAX_FILE:
        raise HandoffError("Oversized candidate file")
    return data


def _zipinfo(name: str) -> zipfile.ZipInfo:
    zi = zipfile.ZipInfo(name, date_time=(2024, 1, 1, 0, 0, 0))
    zi.compress_type = zipfile.ZIP_STORED
    zi.create_system = 3
    zi.external_attr = (stat.S_IFREG | 0o600) << 16
    return zi


def pack(workspace: Path, destination: Path, run_id: str, treatment_id: str) -> dict:
    folder = _external(workspace)
    output = _external(destination)
    if not folder.is_dir() or folder.is_symlink():
        raise HandoffError("Agent workspace must exist and not be a symlink")
    if output.exists():
        raise HandoffError("Refuse to overwrite existing submission")
    if output.parent.resolve().is_relative_to(folder.resolve()):
        raise HandoffError("Output cannot be inside the agent workspace")
    source = {}
    for f in sorted(folder.rglob("*")):
        rel = f.relative_to(folder).as_posix()
        if f.is_dir() and not f.is_symlink():
            continue
        name = _name(rel)
        source[name] = _read_source(f)
        if len(source) > MAX_FILES or sum(map(len, source.values())) > MAX_TOTAL:
            raise HandoffError("Candidate too large")
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "treatment_id": treatment_id,
        "files": [{"path": name, "sha256": _hash(data), "bytes": len(data)}
                  for name, data in sorted(source.items())],
        "format_status": "UNTRUSTED_AGENT_SUBMISSION",
    }
    _manifest(manifest)
    manifest_raw = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(manifest_raw) > MAX_MANIFEST:
        raise HandoffError("Metadata too large")
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Exclusive output avoids unintentionally overwriting a previous run.
    try:
        with output.open("xb") as file:
            with zipfile.ZipFile(file, "w") as archive:
                archive.writestr(_zipinfo("handoff-manifest.json"), manifest_raw)
                for name, data in sorted(source.items()):
                    archive.writestr(_zipinfo("payload/" + name), data)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    output.chmod(0o600)
    if output.stat().st_size > MAX_ARCHIVE:
        output.unlink()
        raise HandoffError("Archive too large")
    return {"run_id": run_id, "treatment_id": treatment_id,
            "file_count": len(source), "archive_sha256": _hash(output.read_bytes()),
            "status": "EXPORTED_NOT_SCIENTIFICALLY_ATTESTED"}


def verify(archive_path: Path, inbox: Path, *, extract: bool = False) -> dict:
    archive_file = _external(archive_path)
    target = _external(inbox)
    if not archive_file.is_file() or archive_file.is_symlink() or archive_file.stat().st_size > MAX_ARCHIVE:
        raise HandoffError("Invalid archive file")
    if target.exists():
        raise HandoffError("Evaluator inbox path must not preexist")
    with zipfile.ZipFile(archive_file, "r") as archive:
        infos = archive.infolist()
        if not infos or len(infos) > MAX_FILES + 1:
            raise HandoffError("Unexpected archive count")
        names = [i.filename for i in infos]
        if len(names) != len(set(names)) or names[0] != "handoff-manifest.json":
            raise HandoffError("Duplicate or missing manifest")
        for item in infos:
            if item.is_dir() or item.flag_bits & 1 or item.file_size > MAX_FILE or item.compress_type != zipfile.ZIP_STORED:
                raise HandoffError("Encrypted/compressed/directory/oversized archive members forbidden")
            if item.create_system == 3 and stat.S_IFMT(item.external_attr >> 16) != stat.S_IFREG:
                raise HandoffError("Nonregular archive members forbidden")
        if infos[0].file_size > MAX_MANIFEST:
            raise HandoffError("Manifest too large")
        try:
            manifest = json.loads(archive.read(infos[0]))
        except (UnicodeError, ValueError) as exc:
            raise HandoffError("Invalid manifest JSON") from exc
        entries = _manifest(manifest)
        if set(names[1:]) != {"payload/" + e["path"] for e in entries}:
            raise HandoffError("Archive files differ from manifest")
        total = 0
        files = {}
        for entry in entries:
            raw = archive.read("payload/" + entry["path"])
            total += len(raw)
            if len(raw) != entry["bytes"] or _hash(raw) != entry["sha256"] or total > MAX_TOTAL:
                raise HandoffError("File corruption or hash mismatch")
            files[entry["path"]] = raw

    if extract:
        if target.resolve().is_relative_to(archive_file.parent.resolve()) and target == archive_file.parent:
            raise HandoffError("Invalid inbox")
        target.mkdir(mode=0o700, parents=True, exist_ok=False)
        try:
            for name, data in files.items():
                file = target / name
                file.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                with file.open("xb") as output:
                    output.write(data)
                file.chmod(0o600)
            (target / "handoff-manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            (target / "handoff-manifest.json").chmod(0o600)
        except Exception:
            # Do not silently return a partial or verified inbox.
            raise
    return {"run_id": manifest["run_id"], "treatment_id": manifest["treatment_id"],
            "files_checked": len(files), "archive_sha256": _hash(archive_file.read_bytes()),
            "status": "FORMAT_AND_HASHES_VERIFIED_NO_EXECUTION_OR_AUTHORSHIP_ATTESTATION",
            "untrusted_code_executed": False,
            "evaluator_private_oracles_accessed": False}


def main() -> int:
    p = argparse.ArgumentParser(description="Safe candidate transfer; not a scientific evaluation")
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("pack")
    a.add_argument("--workspace", required=True, type=Path)
    a.add_argument("--archive", required=True, type=Path)
    a.add_argument("--run-id", required=True)
    a.add_argument("--treatment", required=True)
    b = sub.add_parser("verify")
    b.add_argument("--archive", required=True, type=Path)
    b.add_argument("--inbox", required=True, type=Path)
    b.add_argument("--extract", action="store_true")
    args = p.parse_args()
    try:
        if args.command == "pack":
            output = pack(args.workspace, args.archive, args.run_id, args.treatment)
        else:
            output = verify(args.archive, args.inbox, extract=args.extract)
        print(json.dumps(output, sort_keys=True))
        return 0
    except (HandoffError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "REJECTED", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
