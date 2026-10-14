"""Read-only native Codex plugin discovery check; does not start a model turn."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import queue
import threading
import tempfile
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', type=Path, default=ROOT.parent)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--isolated', action='store_true', help='discover current project skills in a temporary workspace without installing a plugin')
    args = parser.parse_args()
    temporary = tempfile.TemporaryDirectory(prefix='axiom codex discovery ') if args.isolated else None
    if temporary:
        args.cwd = Path(temporary.name)
        shutil.copytree(ROOT/'skills', args.cwd/'.agents/skills')
    proc = subprocess.Popen(['codex','app-server','--stdio'],stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
    events = queue.Queue()
    def read_lines():
        for line in proc.stdout: events.put(line)
    reader = threading.Thread(target=read_lines, daemon=True); reader.start()

    def send(value):
        proc.stdin.write(json.dumps(value)+'\n');proc.stdin.flush()

    def receive(request):
        deadline=time.monotonic()+40
        while time.monotonic()<deadline:
            try:
                line=events.get(timeout=1)
            except queue.Empty:
                continue
            if line:
                if not line:raise RuntimeError('Codex app server closed')
                value=json.loads(line)
                if value.get('id')==request:
                    if 'error' in value:raise RuntimeError(str(value['error']))
                    return value['result']
        raise TimeoutError('Codex discovery timeout')

    try:
        send({'id':1,'method':'initialize','params':{'clientInfo':{'name':'axiom-package-verification','version':'1.0.0'},'capabilities':{'experimentalApi':True}}});receive(1)
        send({'method':'initialized','params':{}})
        send({'id':2,'method':'skills/list','params':{'cwds':[str(args.cwd.resolve())],'forceReload':True}})
        result=receive(2)
        all_skills = [skill for row in result['data'] for skill in row.get('skills', [])]
        found = [skill for skill in all_skills if skill['name'] in {'axge','axm'} and Path(skill['path']).is_relative_to(args.cwd)] if args.isolated else [skill for skill in all_skills if skill['name'].startswith('axiom:')]
        expected={(p.parent.name if args.isolated else f'axiom:{p.parent.name}'):p for p in (ROOT/'skills').glob('*/SKILL.md')}
        if len(found)!=len(expected) or {s['name'] for s in found}!=set(expected):
            raise RuntimeError('Codex did not discover all current canonical Axiom entrypoints')
        digests={}
        for skill in found:
            if not skill['enabled']:raise RuntimeError('an Axiom skill is disabled')
            raw=Path(skill['path']).read_bytes()
            if raw!=expected[skill['name']].read_bytes():raise RuntimeError('cached skill bytes differ')
            digests[skill['name']]=hashlib.sha256(raw).hexdigest()
        report={'codex_version':subprocess.check_output(['codex','--version'],text=True).strip(),
                'platform':platform.system(),'machine':platform.machine(),'method':'native skills/list', 'discovery_scope':'isolated-project' if args.isolated else 'installed-plugin', 'plugin_namespace':'not_run' if args.isolated else 'verified',
                'skills':digests,'enabled':True,'model_turn_started':False,'desktop_ui':'not_run','graph_mcp_execution':'not_run'}
        args.out.write_text(json.dumps(report,indent=2)+'\n')
        print('PASS: native Codex discovers two enabled canonical Axiom entrypoints')
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
        if temporary: temporary.cleanup()


if __name__=='__main__':
    main()
