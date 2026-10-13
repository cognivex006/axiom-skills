"""Archive installation layouts, byte binding and failure boundaries for each host."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

import pytest

from release.build_host_packages import ROOT, HOSTS, build

SOURCE = 'a' * 40


def test_every_archive_is_standalone_and_exact(tmp_path):
    first = build(ROOT, tmp_path/'a', SOURCE)
    second = build(ROOT, tmp_path/'b', SOURCE)
    assert set(first['hosts']) == set(HOSTS)
    markers = {'codex':'.agents/plugins/marketplace.json', 'claude':'.claude-plugin/marketplace.json',
               'copilot':'.github/plugin/marketplace.json','gemini':'gemini-extension.json', 'antigravity':'plugin.json'}
    for host, row in first['hosts'].items():
        archive = tmp_path/'a'/row['archive']
        assert archive.read_bytes() == (tmp_path/'b'/row['archive']).read_bytes()
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == row['sha256']
        with zipfile.ZipFile(archive) as z:
            z.extractall(tmp_path/host)
            assert markers[host] in z.namelist()
            assert len([n for n in z.namelist() if n.endswith('/SKILL.md')]) == 10
            for name, digest in row['files'].items():
                assert hashlib.sha256((tmp_path/host/name).read_bytes()).hexdigest() == digest
            for skill in (ROOT/'skills').glob('*/SKILL.md'):
                assert (tmp_path/host/'skills'/skill.parent.name/'SKILL.md').read_bytes() == skill.read_bytes()
            if host in ('codex','claude','copilot'):
                market=json.loads(z.read(markers[host])); source=market['plugins'][0]['source']
                assert source == ({'source':'local','path':'./'} if host=='codex' else './')
            assert row['native_runtime'] == 'not_run'


def test_existing_output_and_moving_revision_are_refused(tmp_path):
    out=tmp_path/'existing';out.mkdir();sentinel=out/'human.txt';sentinel.write_text('keep')
    with pytest.raises(ValueError,match='new directory'):build(ROOT,out,SOURCE)
    assert sentinel.read_text()=='keep'
    with pytest.raises(ValueError,match='immutable'):build(ROOT,tmp_path/'new','main')
    assert not (tmp_path/'new').exists()


@pytest.mark.parametrize('mutation',['payload','catalog','version','market-version','entrypoint'])
def test_broken_sources_never_produce_an_archive(tmp_path,mutation):
    root=tmp_path/'source'
    shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache','evidence','.delivery'))
    if mutation=='payload':
        p=root/'plugins/axiom-agy/skills/graph-context/SKILL.md';p.write_bytes(p.read_bytes()+b'changed')
    elif mutation=='catalog':
        p=root/'marketplace-plugins/catalog.json';d=json.loads(p.read_text());d['packages']['gemini']='../escape';p.write_text(json.dumps(d))
    elif mutation=='version':
        p=root/'plugins/axiom/plugin.json';d=json.loads(p.read_text());d['version']='999.0.0';p.write_text(json.dumps(d))
    elif mutation=='market-version':
        p=root/'.github/plugin/marketplace.json';d=json.loads(p.read_text());d['plugins'][0]['version']='999.0.0';p.write_text(json.dumps(d))
    else:(root/'gemini-extension.json').write_text('{}')
    # Rebind the fixture manifest so structural/parity rejection is tested beyond the hash gate.
    manifest_path=root/'release/skills-manifest.json'
    manifest=json.loads(manifest_path.read_text())
    for entry in manifest['files']:
        raw=(root/entry['path']).read_bytes()
        entry['sha256']=hashlib.sha256(raw).hexdigest();entry['bytes']=len(raw)
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):build(root,tmp_path/'out',SOURCE)
    assert not (tmp_path/'out').exists()
