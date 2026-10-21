"""Build standalone, digest-bound host packages without changing user configuration."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
import zipfile

from release.build_github_release import verify_source
from release.verify_manifest import verify, portable_relative

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {'axsk'}
HOSTS = ('codex', 'claude', 'gemini', 'antigravity', 'copilot')
INSTALL = {
    'codex': ['codex plugin marketplace add <extracted-package>', 'codex plugin add axiom@axiom-skills'],
    'claude': ['/plugin marketplace add <extracted-package>', '/plugin install axiom@axiom-skills'],
    'copilot': ['copilot plugin marketplace add <extracted-package>', 'copilot plugin install axiom@axiom-skills'],
    'gemini': ['gemini extensions install <extracted-package>'],
    'antigravity': ['agy plugin install <extracted-package>'],
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def checked_packages(root: Path) -> tuple[str, dict[str, str]]:
    problems = verify(root / 'release/skills-manifest.json', root)
    if problems:
        raise ValueError('; '.join(problems))
    version = json.loads((root / 'release/skills-manifest.json').read_text())['component_version']
    if not isinstance(version, str) or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?(?:\+[A-Za-z0-9.-]+)?', version):
        raise ValueError('invalid package version')
    catalog = json.loads((root / 'marketplace-plugins/catalog.json').read_text())
    packages = catalog['packages']
    if set(packages) != set(HOSTS) or set(catalog['hosts']) != set(HOSTS):
        raise ValueError('catalog must declare all five hosts')
    expected = {p.relative_to(root): p.read_bytes() for folder in ('skills', 'policy')
                for p in (root / folder).rglob('*') if p.is_file()}
    skills = list((root / 'skills').glob('*/SKILL.md'))
    if {p.parent.name for p in skills} != EXPECTED_SKILLS:
        raise ValueError('canonical skill inventory is incomplete')
    for skill in skills:
        body = skill.read_text()
        if not body.startswith('---\n') or '\n---\n' not in body:
            raise ValueError('skill frontmatter is missing')
        fields = dict(line.split(':', 1) for line in body.split('---', 2)[1].strip().splitlines())
        if fields.get('name', '').strip() != skill.parent.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', skill.parent.name):
            raise ValueError('skill name is invalid')
        description = fields.get('description', '').strip()
        if not description or len(description) > 1024:
            raise ValueError('skill description is invalid')
    for package in set(packages.values()):
        if not portable_relative(package) or not package.startswith('plugins/'):
            raise ValueError('unsafe package path')
        base = root / package
        for relative, raw in expected.items():
            if (base / relative).read_bytes() != raw:
                raise ValueError('package differs from canonical bytes: ' + str(relative))
        for folder in ('skills', 'policy'):
            actual = {p.relative_to(base) for p in (base / folder).rglob('*') if p.is_file()}
            wanted = {p for p in expected if p.parts[0] == folder}
            if actual != wanted:
                raise ValueError('undeclared package payload')
        if any(p.is_symlink() for p in base.rglob('*')):
            raise ValueError('linked package files are not supported')
    base = root / packages['copilot']
    portable = json.loads((base / 'plugin.json').read_text())
    if portable.get('$schema') != 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json' or portable.get('name') != 'axiom' or portable.get('version') != version:
        raise ValueError('portable manifest identity/version mismatch')
    allowed = {'$schema', 'name', 'version', 'description', 'author', 'homepage', 'repository', 'license', 'keywords', 'extensions'}
    if set(portable) - allowed:
        raise ValueError('unsupported portable manifest fields')
    for name in ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json', 'gemini-extension.json'):
        d = json.loads((base / name).read_text())
        if d.get('name') != 'axiom' or d.get('version') != version:
            raise ValueError('host manifest identity/version mismatch')
    agy = json.loads((root / packages['antigravity'] / 'plugin.json').read_text())
    if agy.get('name') != 'axiom' or set(agy) - {'$schema', 'name', 'description'}:
        raise ValueError('Antigravity manifest must keep its native format')
    for host, entry in catalog['hosts'].items():
        if not portable_relative(entry):
            raise ValueError('unsafe marketplace path')
        if host in ('codex', 'claude', 'copilot'):
            market = json.loads((root / entry).read_text())
            declared_version = market['plugins'][0].get('version')
            if declared_version is not None and declared_version != version:
                raise ValueError('marketplace declared version mismatch')
            source = market['plugins'][0]['source']
            source = source['path'] if isinstance(source, dict) else source
            if source.removeprefix('./') != packages[host] or market['plugins'][0]['name'] != 'axiom':
                raise ValueError('marketplace source mismatch')
    if (root / 'gemini-extension.json').read_bytes() != (base / 'gemini-extension.json').read_bytes() or (root / 'GEMINI.md').read_bytes() != (base / 'GEMINI.md').read_bytes():
        raise ValueError('repository Gemini entrypoint differs from package')
    return version, packages


def build(root: Path, output: Path, source_revision: str, legacy: bool = False) -> dict:
    if not re.fullmatch(r'[a-f0-9]{40}', source_revision):
        raise ValueError('source revision must be an immutable Git commit')
    version, packages = checked_packages(root)
    if legacy and tuple(int(part) for part in version.split('.')[:2]) >= (0, 2):
        raise ValueError('legacy compatibility expired at 0.2.0')
    if output.exists() or output.is_symlink():
        raise ValueError('output must be a new directory')
    payloads = {}
    for host, package in packages.items():
        base = root / package
        files = {p.relative_to(base).as_posix(): p.read_bytes() for p in base.rglob('*') if p.is_file()}
        if legacy:
            manifest = json.loads((root / 'compatibility/legacy-manifest.json').read_text())
            if manifest.get('deprecated_until') != '0.2.0':
                raise ValueError('legacy compatibility expiry missing')
            for name, digest in manifest['files'].items():
                if not portable_relative(name) or not name.startswith('compatibility/legacy-skills/'):
                    raise ValueError('unsafe legacy payload')
                raw = (root / name).read_bytes()
                if sha(raw) != digest:
                    raise ValueError('legacy alias bytes changed')
                files['skills/' + name.removeprefix('compatibility/legacy-skills/')] = raw
            files['legacy-compatibility.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
            previous = json.loads((root / 'compatibility/workflow-v019-manifest.json').read_text())
            for name, digest in previous['files'].items():
                if not portable_relative(name) or not name.startswith('compatibility/workflow-v019/skills/'):
                    raise ValueError('unsafe previous workflow path')
                raw = (root / name).read_bytes()
                if sha(raw) != digest:
                    raise ValueError('previous workflow compatibility bytes changed')
                files[name.removeprefix('compatibility/workflow-v019/')] = raw
        if host in ('codex', 'claude', 'copilot'):
            entry = {'name':'axiom', 'source': {'source':'local','path':'./'} if host == 'codex' else './', 'version':version}
            if host == 'codex':
                entry['policy'] = {'installation':'AVAILABLE','authentication':'ON_INSTALL'}
            catalog = {'name':'axiom-skills','owner':{'name':'cognivex006'},'plugins':[entry]}
            name = {'codex':'.agents/plugins/marketplace.json','claude':'.claude-plugin/marketplace.json','copilot':'.github/plugin/marketplace.json'}[host]
            files[name] = (json.dumps(catalog, indent=2)+'\n').encode()
        files['INSTALL.md'] = (f"# Axiom skills for {host}\n\nExtract this archive into a new directory. Replace `<extracted-package>` with that directory in these commands:\n\n```text\n" + '\n'.join(INSTALL[host]) + "\n```\n\nStart a new host session. Graph queries require a separately configured Axiom runtime, solution and MCP connection. Package validation is separate from native host execution.\n").encode()
        payloads[host] = files
    output.mkdir(parents=True)
    index = {'schema_version':1,'component':'axiom-skills','version':version,'source_revision':source_revision,'legacy_compatibility':legacy,'publication':'not_published','hosts':{}}
    for host, files in payloads.items():
        archive = output / f'axiom-skills-{version}-{host}.zip'
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as zipped:
            for name, raw in sorted(files.items()):
                if not portable_relative(name):
                    raise ValueError('unsafe archive path')
                info = zipfile.ZipInfo(name, (1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
                info.create_system=3; info.external_attr=0o100644 << 16
                zipped.writestr(info,raw)
        with zipfile.ZipFile(archive) as zipped:
            if set(zipped.namelist()) != set(files) or any(zipped.read(n) != raw for n,raw in files.items()):
                raise ValueError('archive byte verification failed')
        index['hosts'][host] = {'archive':archive.name,'sha256':sha(archive.read_bytes()),'files':{n:sha(raw) for n,raw in sorted(files.items())},'package_verified':True,'install':INSTALL[host],'native_runtime':'not_run'}
    (output/'host-packages.json').write_text(json.dumps(index,indent=2)+'\n')
    (output/'HOST-SOURCE-REVISION.txt').write_text(source_revision+'\n')
    (output/'SHA256SUMS').write_text(''.join(f"{sha(p.read_bytes())}  {p.name}\n" for p in sorted(output.iterdir()) if p.is_file()))
    return index


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--source-revision',required=True)
    parser.add_argument('--legacy',action='store_true',help='include deprecated aliases explicitly, until 0.2.0')
    args=parser.parse_args()
    verify_source(ROOT,args.source_revision)
    if args.legacy:
        import subprocess
        legacy_manifest=json.loads((ROOT/'compatibility/legacy-manifest.json').read_text())
        previous = json.loads((ROOT/'compatibility/workflow-v019-manifest.json').read_text())
        for name in ['compatibility/legacy-manifest.json', *legacy_manifest['files'],
                     'compatibility/workflow-v019-manifest.json', *previous['files']]:
            if subprocess.check_output(['git','show',args.source_revision+':'+name],cwd=ROOT)!=(ROOT/name).read_bytes():
                raise ValueError('legacy payload is not bound to source revision')
    result=build(ROOT,args.out,args.source_revision,args.legacy)
    print(f"Verified {len(result['hosts'])} standalone host packages")
