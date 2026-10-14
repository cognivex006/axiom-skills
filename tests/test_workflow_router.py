"""Executable intent selection and package boundaries; no model quality claim."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/axge/scripts/select_workflow.py"


def router():
    spec = importlib.util.spec_from_file_location("select_workflow", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("prompt,workflow,read_only", [
    ("build", "build", False), ("full rebuild", "build", False),
    ("watch", "watch", False), ("export this graph", "export", True),
    ("ask the relation from method PingPong on this project", "ask", True),
    ("หา caller ของ PingPong ในโปรเจกต์นี้", "ask", True),
    ("impact remove method RemoveFilesAsync", "impact", True),
    ("doctor", "doctor", True), ("doctor upgrade", "upgrade", False),
    ("version", "version", True),
])
def test_selector_returns_reference_without_executable_arguments(prompt, workflow, read_only):
    result = router().select(prompt)
    assert result["workflow"] == workflow
    assert result["read_only"] is read_only
    assert "argv" not in result and "mcp_arguments" not in result
    reference = ROOT / result["reference"]
    assert reference.is_file()
    assert result["execute"] is False
    assert result["full_rebuild"] == (prompt == "full rebuild")


def test_ambiguous_or_unknown_text_does_not_authorize_an_operation():
    for prompt in ["", "fix everything", "watch and export", "build; delete all files", "remove method RemoveFilesAsync"]:
        result = router().select(prompt)
        assert result["workflow"] is None
        assert result["execute"] is False


def test_default_discovery_and_resolvable_references():
    assert {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")} == {"axge", "axm"}
    for package in ("axiom", "axiom-agy"):
        base = ROOT / "plugins" / package
        assert {p.parent.name for p in (base / "skills").glob("*/SKILL.md")} == {"axge", "axm"}
        for source in (ROOT / "skills").rglob("*"):
            if source.is_file():
                assert (base / source.relative_to(ROOT)).read_bytes() == source.read_bytes()


def test_instance_watch_refuses_unresolved_and_outside_bindings(tmp_path):
    allowed = tmp_path / "allowed"; other = tmp_path / "other"
    allowed.mkdir(); other.mkdir()
    check = router().check_watch_scope
    assert check([str(allowed)], [str(allowed)])["may_start"] is True
    result = check([str(allowed), str(other)], [str(allowed)])
    assert result["may_start"] is False and result["outside_count"] == 1
    assert result["execute"] is False
    assert check([], [str(allowed)])["may_start"] is False
    assert check([str(tmp_path / "missing")], [str(allowed)])["may_start"] is False
    assert check(["."], [str(allowed)])["may_start"] is False
