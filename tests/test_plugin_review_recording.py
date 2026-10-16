"""Regenerating plugin metadata retains only reviews bound to identical bytes."""
import hashlib
import json

from release import record_plugin_files


def test_reviewed_canonical_mirror_keeps_capabilities_but_changed_bytes_do_not(tmp_path, monkeypatch):
    raw = b"print('reviewed selector')\n"
    plugin = tmp_path / "plugins/axiom/skills/router.py"
    plugin.parent.mkdir(parents=True)
    plugin.write_bytes(raw)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(dict(files=[dict(path="skills/router.py", sha256=hashlib.sha256(raw).hexdigest(), capabilities=["read", "execute"])], install_policy=dict(declared_scope=[]))))
    monkeypatch.setattr(record_plugin_files, "ROOT", tmp_path)
    monkeypatch.setattr(record_plugin_files, "MANIFEST", manifest)
    record_plugin_files.main()
    entries = {r["path"]: r for r in json.loads(manifest.read_text())["files"]}
    assert entries["plugins/axiom/skills/router.py"]["capabilities"] == ["read", "execute"]
    record_plugin_files.main()
    assert json.loads(manifest.read_text())["files"] == list(entries.values())
    plugin.write_bytes(b"print('new unreviewed behavior')\n")
    record_plugin_files.main()
    entries = {r["path"]: r for r in json.loads(manifest.read_text())["files"]}
    assert "capabilities" not in entries["plugins/axiom/skills/router.py"]
