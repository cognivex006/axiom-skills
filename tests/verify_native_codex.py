"""Read-only native Codex plugin discovery check; does not start a model turn."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import selectors
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', type=Path, default=ROOT.parent)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    proc = subprocess.Popen(['codex','app-server','--stdio'],stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
    events = selectors.DefaultSelector();events.register(proc.stdout,selectors.EVENT_READ)

    def send(value):
        proc.stdin.write(json.dumps(value)+'\n');proc.stdin.flush()

    def receive(request):
        deadline=time.monotonic()+40
        while time.monotonic()<deadline:
            if events.select(timeout=1):
                line=proc.stdout.readline()
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
        found=[skill for row in result['data'] for skill in row.get('skills',[]) if skill['name'].startswith('axiom:')]
        expected={f'axiom:{p.parent.name}':p for p in (ROOT/'skills').glob('*/SKILL.md')}
        if len(found)!=len(expected) or {s['name'] for s in found}!=set(expected):
            raise RuntimeError('Codex did not discover all ten canonical Axiom skills')
        digests={}
        for skill in found:
            if not skill['enabled']:raise RuntimeError('an Axiom skill is disabled')
            raw=Path(skill['path']).read_bytes()
            if raw!=expected[skill['name']].read_bytes():raise RuntimeError('cached skill bytes differ')
            digests[skill['name']]=hashlib.sha256(raw).hexdigest()
        report={'codex_version':subprocess.check_output(['codex','--version'],text=True).strip(),
                'platform':platform.system(),'machine':platform.machine(),'method':'native skills/list',
                'skills':digests,'enabled':True,'model_turn_started':False,'desktop_ui':'not_run','graph_mcp_execution':'not_run'}
        args.out.write_text(json.dumps(report,indent=2)+'\n')
        print('PASS: native Codex discovers ten enabled canonical Axiom skills')
    finally:
        events.close();proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()


if __name__=='__main__':
    main()
