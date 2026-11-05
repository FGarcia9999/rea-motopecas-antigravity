"""Generate/check deterministic SHA-256 manifest of versioned REA project files.

Generated gate reports are runtime evidence and deliberately excluded: they are
mutable run artifacts, not reproducible source inputs. The manifest excludes itself.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"
EXCLUDE = {"MANIFEST.sha256", "gate-report.json", "docs/evidence/gate-report.json"}
START, END = "REV04_MANIFEST_START", "REV04_MANIFEST_END"


def render() -> str:
    result = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    paths = sorted({b.decode("utf-8", "surrogateescape").replace("\\", "/")
                    for b in result.split(b"\0") if b})
    lines = []
    for rel in paths:
        if rel in EXCLUDE:
            continue
        path = ROOT / rel
        if not path.is_file():
            raise RuntimeError(f"Tracked file missing: {rel}")
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate committed manifest")
    parser.add_argument("--print", action="store_true", dest="show", help="Show expected content")
    args = parser.parse_args()
    expected = render()
    if args.show:
        print(START)
        print(expected, end="")
        print(END)
        return 0
    if args.check:
        if not MANIFEST.is_file() or MANIFEST.read_text(encoding="utf-8") != expected:
            print("MANIFEST.sha256 differs from versioned source tree.", file=sys.stderr)
            print("Run: python scripts/refresh_manifest.py", file=sys.stderr)
            # Print the expected manifest on mismatch for audit/recovery from CI logs.
            print(START)
            print(expected, end="")
            print(END)
            return 1
        print("MANIFEST SHA-256: PASS", len(expected.splitlines()), "tracked inputs")
        return 0
    MANIFEST.write_text(expected, encoding="utf-8")
    print("Refreshed", MANIFEST, "with", len(expected.splitlines()), "tracked inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
