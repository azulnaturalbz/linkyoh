"""Test the immutable candidate using an existing isolated local QA network."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
helper = root / 'specs/005-lab-discovery/postgres_check.py'
target = '/linkyoh/specs/005-lab-discovery/postgres_check.py'
command = ['docker', 'run', '--rm', '--platform', 'linux/amd64',
           '--name', 'linkyoh-ui-release-tests', '--network', 'container:linkyoh-ui-qa-redis',
           '--memory', '384m', '--mount', f'type=bind,source={helper},target={target},readonly',
           '-e', 'PYTHONPATH=/linkyoh', '--entrypoint', 'python',
           'linkyoh-web:ui-34196aa', target]
result = subprocess.run(command, capture_output=True)
output = result.stdout + result.stderr
(Path(__file__).parent / 'evidence/runtime-tests.txt').write_bytes(output)
print(output.decode()[-5000:])
sys.exit(result.returncode)
