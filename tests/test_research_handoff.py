"""Handoff unit checks use disposable public toy code, never private evaluator files."""
from __future__ import annotations

import io
import json
import stat
import zipfile

import pytest

from research.handoff.bundle import HandoffError, _zipinfo, pack, verify


@pytest.fixture
def handoff(tmp_path):
    candidate = tmp_path / "candidate"
    (candidate / "src").mkdir(parents=True)
    (candidate / "web").mkdir()
    (candidate / "src" / "service.py").write_text("print('public toy only')\n")
    (candidate / "web" / "index.html").write_text("<title>Demo</title>")
    archive = tmp_path / "external_inbox" / "candidate.zip"
    inbox = tmp_path / "assessor" / "verified"
    return candidate, archive, inbox


def test_export_and_verify_without_executing_any_code(handoff):
    candidate, archive, inbox = handoff
    out = pack(candidate, archive, "SYNTH_RUN", "T2")
    checked = verify(archive, inbox, extract=True)
    assert out["archive_sha256"] == checked["archive_sha256"]
    assert checked["files_checked"] == 2
    assert checked["untrusted_code_executed"] is False
    assert checked["evaluator_private_oracles_accessed"] is False
    assert (inbox / "src" / "service.py").read_text() == "print('public toy only')\n"
    assert (inbox / "handoff-manifest.json").is_file()


def test_handoff_is_deterministic_for_same_source(handoff):
    source, archive, inbox = handoff
    r1 = pack(source, archive, "R1", "T0")
    archive2 = archive.parent / "second.zip"
    r2 = pack(source, archive2, "R1", "T0")
    assert r1["archive_sha256"] == r2["archive_sha256"]


def test_refuse_overwrite_older_submission(handoff):
    source, archive, _ = handoff
    pack(source, archive, "R1", "T1")
    with pytest.raises(HandoffError, match="Refuse to overwrite"):
        pack(source, archive, "R1", "T1")


def test_source_symlink_rejected(handoff):
    source, archive, _ = handoff
    (source / "src" / "linked.py").symlink_to(source / "src" / "service.py")
    with pytest.raises(HandoffError, match="Symlinks"):
        pack(source, archive, "R1", "T1")


@pytest.mark.parametrize("name", [
    "src/.env", "web/folder/.hidden.js", "src/forbidden.sh",
    "assets/password.txt", "src/__pycache__/x.py", "src/not_code.exe",
])
def test_bad_path_or_suffix_rejected(handoff, name):
    source, archive, _ = handoff
    path = source / name
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("toy")
    except FileNotFoundError:
        return
    with pytest.raises(HandoffError):
        pack(source, archive, "R1", "T1")


def test_oversized_content_rejected(handoff):
    source, archive, _ = handoff
    (source / "src" / "large.py").write_bytes(b"x" * (2 * 1024 * 1024 + 1))
    with pytest.raises(HandoffError, match="Oversized"):
        pack(source, archive, "R1", "T1")


def test_empty_candidate_rejected(handoff):
    source, archive, _ = handoff
    for file in (source / "src" / "service.py", source / "web" / "index.html"):
        file.unlink()
    with pytest.raises(HandoffError, match="source count"):
        pack(source, archive, "R1", "T0")


def test_malformed_treatment_rejected(handoff):
    source, archive, _ = handoff
    with pytest.raises(HandoffError, match="Invalid treatment"):
        pack(source, archive, "R1", "T7")


def _rewrite(archive, transform):
    with zipfile.ZipFile(archive) as source:
        items = [(i, source.read(i)) for i in source.infolist()]
    with zipfile.ZipFile(archive, "w") as target:
        for info, content in items:
            info, content = transform(info, content)
            target.writestr(info, content)


def test_corrupted_payload_digest_rejected(handoff):
    source, archive, inbox = handoff
    pack(source, archive, "R1", "T2")
    def change(info, content):
        if info.filename == "payload/src/service.py":
            content = b"x" + content[1:]
        return info, content
    _rewrite(archive, change)
    with pytest.raises(HandoffError, match="hash mismatch"):
        verify(archive, inbox)


def test_zip_entry_symlink_rejected(handoff):
    source, archive, inbox = handoff
    pack(source, archive, "R1", "T2")
    def change(info, content):
        if info.filename.startswith("payload/"):
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
        return info, content
    _rewrite(archive, change)
    with pytest.raises(HandoffError, match="Nonregular"):
        verify(archive, inbox)


def test_zip_traversal_member_rejected(handoff):
    source, archive, inbox = handoff
    pack(source, archive, "R1", "T2")
    with zipfile.ZipFile(archive, "a") as target:
        target.writestr(_zipinfo("payload/../private.py"), b"bad")
    with pytest.raises(HandoffError, match="differ"):
        verify(archive, inbox)


def test_duplicate_zip_member_rejected(handoff):
    source, archive, inbox = handoff
    pack(source, archive, "R1", "T2")
    with zipfile.ZipFile(archive, "a") as target:
        with pytest.warns(UserWarning):
            target.writestr(_zipinfo("payload/src/service.py"), b"duplicate")
    with pytest.raises(HandoffError, match="Duplicate"):
        verify(archive, inbox)


def test_reject_extraction_to_existing_inbox(handoff):
    source, archive, inbox = handoff
    pack(source, archive, "R1", "T2")
    inbox.mkdir(parents=True)
    with pytest.raises(HandoffError, match="must not preexist"):
        verify(archive, inbox, extract=True)


def test_disallow_checkout_as_transfer_destination(handoff):
    source, archive, inbox = handoff
    from research.handoff.bundle import REPO
    with pytest.raises(HandoffError, match="outside public repository"):
        pack(source, REPO / "forbidden.zip", "R1", "T0")
