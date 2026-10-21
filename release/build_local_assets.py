"""Build the portable bundle and standalone host packages from one clean commit."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from release.build_github_release import build as build_portable, verify_source
from release.build_host_packages import build as build_hosts

ROOT = Path(__file__).resolve().parents[1]


def build(output: Path, source: str):
    output = output.resolve()
    if output.exists() or output == ROOT or ROOT in output.parents:
        raise ValueError("new output outside the source checkout required")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)
    if source != head or dirty.strip():
        raise ValueError("exact clean committed source required")
    verify_source(ROOT, source)
    manifest = json.loads((ROOT / "release/skills-manifest.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="axiom-local-skills-") as temporary:
        work = Path(temporary)
        portable, hosts = work / "portable", work / "hosts"
        build_portable(ROOT, portable, "v" + manifest["component_version"], source)
        build_hosts(ROOT, hosts, source)
        for folder, revision_file in ((portable, "SOURCE-REVISION.txt"), (hosts, "HOST-SOURCE-REVISION.txt")):
            if (folder / revision_file).read_text().strip() != source:
                raise ValueError("package source drift")
            for line in (folder / "SHA256SUMS").read_text().splitlines():
                digest, name = line.split("  ", 1)
                if Path(name).name != name or hashlib.sha256((folder / name).read_bytes()).hexdigest() != digest:
                    raise ValueError("package checksum drift")
        files = [p for folder in (portable, hosts) for p in folder.iterdir() if p.name != "SHA256SUMS"]
        if len({p.name for p in files}) != len(files):
            raise ValueError("duplicate package asset")
        output.mkdir(parents=True)
        for path in files:
            shutil.copyfile(path, output / path.name)
        (output / "SHA256SUMS").write_text(
            "".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n"
                    for p in sorted(output.iterdir())), encoding="utf-8", newline="\n"
        )
    print("OK complete portable and standalone host assets; publication not performed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-revision", required=True)
    args = parser.parse_args()
    build(args.out, args.source_revision)
