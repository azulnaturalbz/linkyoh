"""Verify the immutable app image; mount only the external test-runner helper."""

import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'evidence'
IMAGE = 'linkyoh-web:strip-v2-60d5af7'
spec = importlib.util.spec_from_file_location('qa_helpers', HERE.parent / 'runtime_tests.py')
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
qa.PREFIX = 'linkyoh-strip-v2-image-'


def main():
    OUT.mkdir(exist_ok=True)
    manifest = json.loads(Path('/tmp/linkyoh-strip-v2-60d5af7/manifest.json').read_text())
    image = json.loads(qa.run('image', 'inspect', IMAGE).stdout)[0]
    assert image['Architecture'] == 'amd64'
    assert image['Config']['Labels']['org.opencontainers.image.revision'] == manifest['commit']
    code = ('import hashlib,json,pathlib,platform,django; m=' + repr(manifest['source']) +
            '; bad=[p for p,h in m.items() if hashlib.sha256((pathlib.Path("/linkyoh")/p).read_bytes()).hexdigest()!=h]; '
            'print(json.dumps({"files":len(m),"mismatches":bad,"python":platform.python_version(),"django":django.get_version()})); assert not bad')
    parity = json.loads(qa.run('run', '--rm', '--network', 'none', '--memory', '128m',
                               '--entrypoint', 'python', IMAGE, '-c', code).stdout)
    receipt = {'checked_at': datetime.now(timezone.utc).isoformat(), 'commit': manifest['commit'],
               'image': image['Id'], 'architecture': image['Architecture'], 'parity': parity,
               'production_access': False, 'application_source_mount': False}
    try:
        qa.start(qa.PREFIX + 'redis', '--network', 'none', '--memory', '64m',
                 'redis:7-alpine', 'redis-server', '--save', '', '--appendonly', 'no')
        qa.start(qa.PREFIX + 'db', '--network', 'container:' + qa.PREFIX + 'redis', '--memory', '192m',
                 '-e', 'POSTGRES_DB=linkyoh_local_qa', '-e', 'POSTGRES_PASSWORD=synthetic-local-qa-only', 'postgres:18-alpine')
        for _ in range(60):
            if qa.run('exec', qa.PREFIX + 'db', 'pg_isready', '-h', '127.0.0.1', '-U', 'postgres', check=False).returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError('Disposable database not ready')
        helper = '/linkyoh/specs/005-lab-discovery/postgres_check.py'
        result = qa.run('run', '--rm', '--network', 'container:' + qa.PREFIX + 'redis', '--memory', '384m',
                        '--mount', f'type=bind,source={ROOT}/specs/005-lab-discovery/postgres_check.py,target={helper},readonly',
                        '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'PYTHONPATH=/linkyoh',
                        '--entrypoint', 'python', IMAGE, helper, check=False)
        output = result.stdout + result.stderr
        (OUT / 'image-tests.txt').write_text('\n'.join(line.rstrip() for line in output.splitlines()) + '\n')
        receipt['exit_code'] = result.returncode
        receipt['passed'] = result.returncode == 0
        print(output[-1200:])
        return result.returncode
    finally:
        for name in reversed(qa.owned):
            qa.run('rm', '--force', '--volumes', name)
        receipt['disposable_containers_removed'] = list(qa.owned)
        (OUT / 'image.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    sys.exit(main())
