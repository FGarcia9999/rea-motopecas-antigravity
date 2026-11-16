"""Hash a local artifact WITHOUT publishing its content or proving tool execution."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def hash_local_file(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"No regular file: {path}")
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as src:
        for block in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(block)
            total += len(block)
    return {"sha256": digest.hexdigest(), "bytes": total,
            "status": "HASH_ONLY_NOT_EVIDENCE_OF_TOOL_EXECUTION"}

def main() -> int:
    p = argparse.ArgumentParser(description="Hash private artifact locally; never upload automatically")
    p.add_argument("file", type=Path)
    args = p.parse_args()
    print(json.dumps(hash_local_file(args.file), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
