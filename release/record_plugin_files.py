#!/usr/bin/env python3
"""Record exact plugin and marketplace bytes in the skills install manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "skills-manifest.json"
SCOPES = ("plugins", ".agents/plugins", ".claude-plugin", "marketplace-plugins", ".github/plugin")


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = data["files"]
    reviewed = {entry["path"]: entry for entry in files}
    files[:] = [entry for entry in files if not any(
        entry["path"] == scope or entry["path"].startswith(scope + "/")
        for scope in SCOPES
    )]
    for scope in SCOPES:
        for path in sorted((ROOT / scope).rglob("*")):
            if not path.is_file():
                continue
            raw = path.read_bytes()
            relative = path.relative_to(ROOT).as_posix()
            digest = hashlib.sha256(raw).hexdigest()
            entry = {
                "path": relative,
                "role": "plugin-package" if scope == "plugins" else "plugin-marketplace",
                "sha256": digest,
                "bytes": len(raw),
            }
            # Retain an existing byte-bound review, or the exact canonical mirror's
            # review. Changed/unreviewed executable bytes still fail verification.
            canonical = "/".join(relative.split("/")[2:]) if scope == "plugins" else ""
            for review in (reviewed.get(relative), reviewed.get(canonical)):
                if review and review.get("sha256") == digest and review.get("capabilities"):
                    entry["capabilities"] = list(review["capabilities"])
                    break
            files.append(entry)
    scopes = data["install_policy"]["declared_scope"]
    for scope in SCOPES:
        if scope not in scopes:
            scopes.append(scope)
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Recorded {sum(any(entry['path'].startswith(scope + '/') for scope in SCOPES) for entry in files)} plugin files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
