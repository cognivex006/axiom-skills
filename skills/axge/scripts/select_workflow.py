"""Select one reference for common explicit intents; never execute or build tool argv.

Agents interpret broader language themselves using SKILL.md. Unknown/combined text
requires semantic resolution, not a guessed mutation. Input is untrusted text.
"""
import argparse
import json
import re
from pathlib import Path


def check_watch_scope(registered_roots: list[str], authorized_roots: list[str]) -> dict:
    """Inspect actual bindings against explicit authorization; never start a process."""
    if any(not Path(root).is_absolute() for root in [*registered_roots, *authorized_roots]):
        return {"may_start": False, "reason": "binding_must_be_absolute", "execute": False}
    try:
        registered = [Path(root).resolve(strict=True) for root in registered_roots]
        authorized = [Path(root).resolve(strict=True) for root in authorized_roots]
    except (OSError, RuntimeError):
        return {"may_start": False, "reason": "binding_unavailable", "execute": False}
    if not registered or not authorized:
        return {"may_start": False, "reason": "scope_unresolved", "execute": False}
    outside = [root for root in registered if not any(root == bound or root.is_relative_to(bound) for bound in authorized)]
    return {"may_start": not outside, "reason": "outside_authorized_scope" if outside else "registered_scope_within_authorization",
            "outside_count": len(outside), "execute": False}


def select(prompt: str) -> dict:
    text = prompt.strip().casefold()
    result = {"workflow": None, "reference": None, "read_only": True,
              "full_rebuild": False, "execute": False,
              "reason": "Resolve unknown or combined intent in context"}
    if not text or any(token in text for token in (";", "&&", "|", "`", "$(`")):
        return result
    if re.search(r"\b(and|then)\b", text):
        return result
    workflow = None
    if text == "doctor upgrade":
        workflow = "upgrade"
    elif text in ("version", "รุ่น", "check version"):
        workflow = "version"
    elif text in ("doctor", "diagnose", "ตรวจสุขภาพ"):
        workflow = "doctor"
    elif text in ("build", "refresh graph", "initial graph", "full rebuild", "สร้างกราฟ"):
        workflow = "build"
    elif text in ("watch", "watch source changes", "ติดตามไฟล์"):
        workflow = "watch"
    elif text.startswith(("export", "ส่งออก")):
        workflow = "export"
    elif text.startswith(("impact ", "ผลกระทบ")):
        workflow = "impact"
    elif text.startswith(("ask ", "หา caller", "who calls ", "find callers ")):
        workflow = "ask"
    if workflow:
        owner = "axm" if workflow == "upgrade" else "axge"
        result.update(workflow=workflow, reference=f"skills/{owner}/references/{workflow}.md",
                      read_only=workflow not in ("build", "watch", "upgrade"),
                      full_rebuild=text == "full rebuild", reason="Selected reference only; host authorization governs tools")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent")
    print(json.dumps(select(parser.parse_args().intent), ensure_ascii=False))
