"""Single filesystem read probe, to run INSIDE the implementing agent sandbox.

This is not a complete isolation audit; paths/network/credentials/tool scopes must
be tested by separate evaluator-side checks. Never include hidden file contents.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def probe_denied(path: Path) -> dict:
    if not path.is_absolute():
        raise ValueError("Use absolute path. Run from the actual agent identity/sandbox.")
    try:
        with path.open("rb") as file:
            file.read(1)
    except PermissionError:
        return {"probe": "filesystem_read", "result": "DENIED", "attests": "THIS_PATH_ONLY"}
    except FileNotFoundError:
        return {"probe": "filesystem_read", "result": "NOT_FOUND", "attests": "NOT_PROVEN"}
    except OSError:
        return {"probe": "filesystem_read", "result": "ERROR", "attests": "NOT_PROVEN"}
    return {"probe": "filesystem_read", "result": "ACCESSIBLE", "attests": "ISOLATION_FAILED"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--protected-file", type=Path, required=True)
    a = p.parse_args()
    result = probe_denied(a.protected_file)
    print(json.dumps(result))
    return 0 if result["result"] == "DENIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
