"""Hash tests use toy files, not real MCP traces."""
import hashlib
import pytest
from research.hash_artifact import hash_local_file

def test_hash_reports_integrity_not_execution(tmp_path):
    path = tmp_path / "toy.bin"
    path.write_bytes(b"abc")
    data = hash_local_file(path)
    assert data["sha256"] == hashlib.sha256(b"abc").hexdigest()
    assert data["bytes"] == 3
    assert data["status"] == "HASH_ONLY_NOT_EVIDENCE_OF_TOOL_EXECUTION"

def test_no_silent_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        hash_local_file(tmp_path / "not-exists")
