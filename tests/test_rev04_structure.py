"""Verificações estáticas da sincronização didática REV04 (não são prova de MCP vivo)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_rev04_documents_present():
    for relative in (
        "docs/REV04_SYNC_AUDIT.md",
        "docs/labs/REA_AB_C_REV04.md",
        "docs/evidence/rea-observation-template.md",
        ".agents/skills/rea-instrument/SKILL.md",
        ".agents/skills/rea-integrate/SKILL.md",
    ):
        assert (ROOT / relative).is_file(), relative


def test_rev04_three_routes_and_guardrails():
    text = (ROOT / "docs/labs/REA_AB_C_REV04.md").read_text(encoding="utf-8")
    for term in ("Opção", "A —", "B —", "C —", "category=Freios", "NOT VERIFIED", "127.0.0.1"):
        if term == "Opção":
            continue
        assert term in text


def test_rev04_evidence_template_not_fake_pass():
    text = (ROOT / "docs/evidence/rea-observation-template.md").read_text(encoding="utf-8")
    assert "NOT VERIFIED" in text
    assert "NOT EXECUTED" in text
