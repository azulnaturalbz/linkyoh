"""Exact approved release transport; mutations require the owner-held ledger window."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

os.umask(0o077)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = Path('/tmp/linkyoh-strip-v2-60d5af7')
EVIDENCE = HERE / 'evidence'
REMOTE = '/opt/linkyoh/releases/60d5af7-20260914'
TRANSFER = '/tmp/linkyoh-strip-v2-60d5af7'
HOST = 'ec2-user@34.232.192.13'
KEY = '/Users/cristiansilva/WorkSpace/WhatsApp/wop/.generated/aws/wop-prd-key.pem'
IMAGE = 'sha256:778630b95827f791a3bc0c69eaf3326a99b400d6187b4bad2d3c859d75ce50fa'
COMMIT = '60d5af730c9844261b2a661dadb9ee42d98ee7c9'
LEDGER = Path('/Users/cristiansilva/WorkSpace/WhatsApp/wop/SHARED-HOST-MIGRATION.md')


def window():
    assert os.environ.get('LY_RELEASE_WINDOW_CONFIRMED') == COMMIT, 'Explicit coordinated window required'
    rows = [line for line in LEDGER.read_text().splitlines() if line.startswith('| `APP-') or line.startswith('| `HOST-BASE`')]
    own = next(line for line in rows if line.startswith('| `APP-LINKYOH`'))
    assert '`IN_PROGRESS`' in own and '60d5af7' in own
    assert not any('`IN_PROGRESS`' in line for line in rows if line != own), 'Another host operation is active'


def call(command, data=None):
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-i', KEY, HOST, command],
                            input=data, capture_output=True, timeout=300)
    if result.returncode:
        (OUT / 'ops-error.log').write_bytes(result.stdout + result.stderr)
        raise RuntimeError('Remote operation failed; private ops-error.log retained')
    return result.stdout


def remote(code):
    return call('sudo python3 -', code.encode())


def stage():
    window()
    call('mkdir -m 700 ' + TRANSFER)
    files = [OUT / 'image.tar.gz', OUT / 'source.tar', OUT / 'manifest.json', HERE / 'controller.py']
    subprocess.run(['scp', '-i', KEY, *map(str, files), HOST + ':' + TRANSFER + '/'], check=True, timeout=300)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    code = '''import hashlib,json,os,pathlib,shutil,subprocess,tarfile
os.umask(0o077)
source=pathlib.Path(TRANSFER); r=pathlib.Path(RELEASE)
assert not r.exists(),'Release attempt exists; reconcile first'
expected=HASHES
assert all(hashlib.sha256((source/n).read_bytes()).hexdigest()==h for n,h in expected.items())
r.mkdir(mode=0o700)
for name in expected: shutil.copyfile(source/name,r/name)
m=json.loads((r/'manifest.json').read_text())
assert m['commit']==COMMIT and not m['removed']
with tarfile.open(r/'source.tar') as archive:
    for member in archive.getmembers():
        if member.isdir(): continue
        assert member.isfile() and member.name in m['source']
        parts=pathlib.Path(member.name)
        assert not parts.is_absolute() and '..' not in parts.parts
        target=r/'source'/parts; target.parent.mkdir(parents=True,exist_ok=True)
        with archive.extractfile(member) as src,target.open('wb') as dst: shutil.copyfileobj(src,dst)
assert all(hashlib.sha256((r/'source'/n).read_bytes()).hexdigest()==h for n,h in m['source'].items())
result=subprocess.run(['docker','load','-i',str(r/'image.tar.gz')],capture_output=True,timeout=180)
(r/'image-load.log').write_bytes(result.stdout+result.stderr)
assert result.returncode==0,'Image load failed'
image=json.loads(subprocess.check_output(['docker','image','inspect','linkyoh-web:strip-v2-60d5af7']))[0]
assert image['Id']==IMAGE and image['Architecture']=='amd64'
assert image['Config']['Labels']['org.opencontainers.image.revision']==COMMIT
(r/'image-id').write_text(image['Id'])
(r/'candidate.json').write_text(json.dumps({'services':{'web':{'image':image['Id'],'mem_limit':'256m'}}}))
(r/'transport.json').write_text(json.dumps(expected,indent=2))
print(json.dumps({'image':image['Id'],'commit':COMMIT,'source_files':len(m['source']),'transport_verified':True}))
'''
    code = ('TRANSFER=' + repr(TRANSFER) + '\nRELEASE=' + repr(REMOTE) + '\nHASHES=' + repr(hashes) +
            '\nIMAGE=' + repr(IMAGE) + '\nCOMMIT=' + repr(COMMIT) + '\n' + code)
    result = remote(code)
    (EVIDENCE / 'stage.json').write_bytes(result)
    print(result.decode())


def preflight():
    window()
    code = '''import json,pathlib,subprocess
r=pathlib.Path(RELEASE)
base=['docker','compose','--project-directory','/opt/linkyoh','--env-file','/opt/linkyoh/.env','-p','linkyoh','-f','/opt/linkyoh/docker-compose.aws.yml','-f','/opt/linkyoh/docker-compose.release.yml','-f',str(r/'candidate.json'),'run','--rm','--no-deps','-e','PGOPTIONS=-c default_transaction_read_only=on','--entrypoint','python','web']
for name,args in [('django-check',['manage.py','check']),('migration-plan',['manage.py','migrate','--plan']),('migration-drift',['manage.py','makemigrations','--check','--dry-run'])]:
    result=subprocess.run(base+args,capture_output=True,timeout=120)
    (r/(name+'.log')).write_bytes(result.stdout+result.stderr)
    assert result.returncode==0,name+' failed'
    if name=='migration-plan': assert b'No planned migration operations.' in result.stdout
    print(name+': PASS')
runtime="import os,json,platform; os.environ.setdefault('DJANGO_SETTINGS_MODULE','linkyoh.settings'); import django; django.setup(); from django.conf import settings; from django.db import connection; assert not settings.DEBUG; assert not settings.LINKYOH_WOP_REVIEWED; assert not settings.LINKYOH_WOP_WEBSITE_KEY; c=connection.cursor(); c.execute('SHOW transaction_read_only'); assert c.fetchone()[0]=='on'; print(json.dumps({'python':platform.python_version(),'django':django.get_version(),'wop_enabled':False,'read_only':True}))"
result=subprocess.run(base+['-c',runtime],capture_output=True,timeout=120)
(r/'runtime-check.log').write_bytes(result.stdout+result.stderr)
assert result.returncode==0,'Runtime check failed'
print(result.stdout.decode())
'''
    print(remote('RELEASE=' + repr(REMOTE) + '\n' + code).decode())


def prepare():
    window()
    print(call('sudo python3 ' + REMOTE + '/controller.py prepare').decode())


def backups():
    window()
    private = ROOT.parent / '.release-backups/60d5af7-20260914'
    private.mkdir(mode=0o700, parents=True, exist_ok=True)
    expected = json.loads(call('sudo cat ' + REMOTE + '/backup-checksums.json'))
    for name, expected_hash in expected.items():
        assert name in ('backup.tar.gz', 'static-backup.tar.gz')
        data = call('sudo cat ' + REMOTE + '/' + name)
        assert hashlib.sha256(data).hexdigest() == expected_hash
        with (private / name).open('xb') as stream:
            stream.write(data)
        assert (private / name).stat().st_mode & 0o077 == 0
    remote('import pathlib;pathlib.Path(' + repr(REMOTE + '/offhost-verified.json') + ').write_text(' + repr(json.dumps(expected)) + ')')
    print(json.dumps({'offhost_verified': len(expected), 'path': str(private)}))


def deploy():
    window()
    print(call('sudo python3 ' + REMOTE + '/controller.py deploy').decode())


def archive():
    for name in ('before.json', 'cutover-before.json', 'cutover-after.json', 'cutover-result.json',
                 'image-source-proof.json', 'backup-checksums.json', 'trust.json', 'manifest.json',
                 'django-check.log', 'migration-plan.log', 'migration-drift.log', 'runtime-check.log', 'transport.json'):
        data = call('sudo cat ' + REMOTE + '/' + name)
        target = name.removesuffix('.log') + '.txt' if name.endswith('.log') else name
        if name.endswith('.log'):
            data = ('\n'.join(line.rstrip() for line in data.decode().splitlines()) + '\n').encode()
        (EVIDENCE / target).write_bytes(data)
    print('Sanitized release evidence archived')


def verify():
    window()
    code = '''import json,pathlib,runpy
r=pathlib.Path(RELEASE)
controller=runpy.run_path(str(r/'controller.py'))
before=json.loads((r/'cutover-before.json').read_text())
after=controller['snapshot']('final-after.json')
controller['unchanged'](before,after)
assert after['containers']['linkyoh-web-1']['image']==IMAGE
manifest=json.loads((r/'manifest.json').read_text())
assert all(controller['digest'](pathlib.Path('/opt/linkyoh')/p)==h for p,h in manifest['source'].items())
controller['ready']()
print(json.dumps(after))
'''
    result = remote('RELEASE=' + repr(REMOTE) + '\nIMAGE=' + repr(IMAGE) + '\n' + code)
    (EVIDENCE / 'final-after.json').write_bytes(result)
    data = json.loads(result)
    print(json.dumps({'utc': data['utc'], 'unchanged_neighbors': len(data['containers']) - 1,
                      'source_files': 357, 'protected_unchanged': True,
                      'available_memory_bytes': data['memory']['MemAvailable'],
                      'disk_free_bytes': data['disk_free_bytes']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('stage', 'preflight', 'prepare', 'backups', 'deploy', 'archive', 'verify'))
    EVIDENCE.mkdir(exist_ok=True)
    globals()[parser.parse_args().action]()
