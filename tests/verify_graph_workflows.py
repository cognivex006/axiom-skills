"""Verify graph-build and graph-watch against a real engine in a disposable project."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import tempfile
import time


def verify(daemon: Path) -> dict:
    daemon = daemon.resolve()
    if not daemon.is_file():
        raise ValueError('installed graph engine required')
    calls = []
    with tempfile.TemporaryDirectory(prefix='axiom graph workflow ') as temporary:
        root = Path(temporary).resolve()
        repo, home = root/'repo', root/'home'
        source = repo/'src/GraphExample.cs'
        source.parent.mkdir(parents=True)
        source.write_text('namespace Example;\npublic class BeforeSave { public string Read() => "before"; }\n')
        (repo/'Example.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>\n')
        human = b'# Human instructions\nPreserve this file.\n'
        (repo/'AGENTS.md').write_bytes(human)
        config, bindings = root/'solution.json', root/'bindings.json'
        config.write_text(json.dumps({'id':'workflow-solution','profile':'default','catalog_host_repo':'repo-main','projects':[{'id':'app','repo_id':'repo-main','path':'src'}]}))
        bindings.write_text(json.dumps({'bindings':{'repo-main':str(repo)}}))
        env = dict(os.environ, AXIOM_HOME=str(home))
        def call(*words):
            result = subprocess.run([str(daemon),*map(str,words),'--json'],env=env,capture_output=True,text=True,timeout=45)
            calls.append({'argv':list(map(str,words)),'exit_code':result.returncode})
            if result.returncode:raise RuntimeError(result.stdout+result.stderr)
            return json.loads(result.stdout)
        version=call('version')
        call('solution','register','--config',config,'--bindings',bindings,'--dry-run')
        call('solution','register','--config',config,'--bindings',bindings,'--apply')
        call('reconcile','--solution','workflow-solution','--scope','full')
        before=call('query','context','--solution','workflow-solution','--symbol','Example.BeforeSave','--max-nodes','20','--max-bytes','8192')
        if 'BeforeSave' not in json.dumps(before):raise AssertionError('initial graph query missing source symbol')
        pointer=repo/'.axiom/graph/workflow-solution/_catalog/live/current.json'
        def generation():
            try:return json.loads(pointer.read_text())['generation_id']
            except (FileNotFoundError, json.JSONDecodeError):return None
        initial=generation()
        if not initial:raise AssertionError('initial publication missing')
        stderr=root/'daemon.log'; windows=os.name=='nt'
        with stderr.open('w') as errors:
            proc=subprocess.Popen([str(daemon),'serve','--json'],env=env,stdout=subprocess.DEVNULL,stderr=errors,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if windows else 0)
            try:
                # Allow startup baseline inventory before the observed save.
                time.sleep(1)
                if proc.poll() is not None:raise AssertionError('watch loop exited')
                baseline=generation();source.write_text(source.read_text()+'public sealed class AfterSave {}\n')
                started=time.monotonic();deadline=started+40;after=None
                while time.monotonic()<deadline:
                    if proc.poll() is not None:raise AssertionError('watch loop exited during refresh')
                    if generation()!=baseline:
                        result=call('query','context','--solution','workflow-solution','--symbol','Example.AfterSave','--max-nodes','20','--max-bytes','8192')
                        if 'AfterSave' in json.dumps(result):after=generation();break
                    time.sleep(.2)
                if not after:raise TimeoutError('saved source was not published automatically')
                elapsed=time.monotonic()-started
            finally:
                if proc.poll() is None:proc.send_signal(signal.CTRL_BREAK_EVENT if windows else signal.SIGINT)
                try:proc.wait(timeout=15)
                except subprocess.TimeoutExpired:proc.kill();proc.wait();raise RuntimeError('cooperative shutdown timed out')
            if proc.returncode!=0:raise AssertionError('daemon shutdown failed: '+stderr.read_text()[-500:])
        assert (repo/'AGENTS.md').read_bytes()==human
        return {'engine_sha256':hashlib.sha256(daemon.read_bytes()).hexdigest(),'engine_version':version,'platform':platform.system(),'machine':platform.machine(),'initial_generation':initial,'before_save_generation':baseline,'after_save_generation':after,'refresh_seconds':elapsed,'watcher_mode':'polling','manual_reconcile_after_save':False,'human_file_preserved':True,'cooperative_shutdown_exit':proc.returncode,'calls':[{'argv':[w if not str(w).startswith(str(root)) else '<temporary-input>' for w in row['argv']],'exit_code':row['exit_code']} for row in calls]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--daemon',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report=verify(args.daemon)
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: initial graph build and automatic saved-source publication')


if __name__=='__main__':main()
