"""Workflow references and packaging are checked separately from runtime proof."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_internal_barriers_and_checkpoint_have_no_default_discovery():
    assert not list((ROOT / "skills").glob("graph-*/SKILL.md"))
    references = ROOT / "skills/axge/references"
    assert (references / "freshness.md").is_file()
    assert (references / "export.md").is_file()
    assert "staged" in (references / "export.md").read_text()
    assert "require_fresh" in (references / "mcp-routing.md").read_text()


def test_published_skills_do_not_carry_internal_tracking_ids():
    for p in (ROOT / "skills").rglob("*.md"):
        assert not re.search(r"\b(?:ADR-\d{4}|[A-Z]-\d{3}|V2-\d{3})\b", p.read_text()), p
