"""Test changed source on the deployed runtime in a disposable network-none DB."""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'evidence'
IMAGE = 'linkyoh-web:ui-34196aa'
PREFIX = 'linkyoh-strip-v2-qa-'
owned = []


def run(*args, check=True):
    return subprocess.run(['docker', *args], capture_output=True, text=True, check=check)


def start(name, *args):
    run('run', '--detach', '--pull=never', '--name', name, *args)
    owned.append(name)


def main():
    OUT.mkdir(exist_ok=True)
    receipt = {'checked_at': datetime.now(timezone.utc).isoformat(), 'image': IMAGE,
               'image_id': run('image', 'inspect', IMAGE, '--format', '{{.Id}}').stdout.strip(),
               'source': 'Read-only bind of current Linkyoh checkout', 'network': 'none', 'production_access': False}
    try:
        start(PREFIX + 'redis', '--network', 'none', '--memory', '64m',
              'redis:7-alpine', 'redis-server', '--save', '', '--appendonly', 'no')
        start(PREFIX + 'db', '--network', 'container:' + PREFIX + 'redis', '--memory', '192m',
              '-e', 'POSTGRES_DB=linkyoh_local_qa', '-e', 'POSTGRES_PASSWORD=synthetic-local-qa-only',
              'postgres:18-alpine')
        for _ in range(60):
            if run('exec', PREFIX + 'db', 'pg_isready', '-h', '127.0.0.1', '-U', 'postgres', check=False).returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError('Disposable PostgreSQL did not become ready')
        run('exec', PREFIX + 'redis', 'redis-cli', 'ping')
        result = run('run', '--rm', '--pull=never', '--platform', 'linux/amd64',
                     '--network', 'container:' + PREFIX + 'redis', '--memory', '384m',
                     '--mount', f'type=bind,source={ROOT},target=/linkyoh,readonly',
                     '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'PYTHONPATH=/linkyoh',
                     '--entrypoint', 'python', IMAGE,
                     '/linkyoh/specs/005-lab-discovery/postgres_check.py', check=False)
        output = result.stdout + result.stderr
        (OUT / 'runtime-tests.txt').write_text('\n'.join(line.rstrip() for line in output.splitlines()) + '\n')
        receipt['exit_code'] = result.returncode
        receipt['passed'] = result.returncode == 0
        print(output[-6000:])
        return result.returncode
    finally:
        for name in reversed(owned):
            run('rm', '--force', '--volumes', name)
        receipt['disposable_containers_removed'] = list(owned)
        (OUT / 'runtime.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    sys.exit(main())
