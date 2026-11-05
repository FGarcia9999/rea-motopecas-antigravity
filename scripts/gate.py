"""Gate executável: testes, checagem estática e evidência JSON independente."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'evidence'/'gate-report.json'


def run(command):
    p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=False)
    return {'command':' '.join(command),'exit_code':p.returncode,'stdout':p.stdout[-6000:],'stderr':p.stderr[-4000:]}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    checks=[run([sys.executable,'-m','compileall','-q','app']),run([sys.executable,'-m','pytest','-q','tests'])]
    sha_files={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.suffix in {'.py','.js','.css','.html','.mmd','.md','.svg','.png','.csv','.yml','.toml','.txt'} and '.venv' not in p.parts and 'evidence' not in p.parts}
    report={'kind':'REA gate report','date_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'file_sha256':sha_files,'status':'PASS' if all(c['exit_code']==0 for c in checks) else 'FAIL','independent_review':'NOT PERFORMED: independent agent review requires Antigravity execution'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print('GATE',report['status'],'-',OUT.relative_to(ROOT))
    for c in checks:
        print(c['command'],'=>',c['exit_code'])
        if c['exit_code'] != 0:
            print('--- FAIL STDOUT ---')
            print(c['stdout'][-6000:])
            print('--- FAIL STDERR ---')
            print(c['stderr'][-4000:])
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':sys.exit(main())
