"""Package the approved Git tree without local data or runtime credentials."""

import hashlib
import json
import os
import subprocess
import tarfile
from pathlib import Path

os.umask(0o077)
ROOT = Path(__file__).resolve().parents[3]
OUT = Path('/tmp/linkyoh-strip-v2-60d5af7')
COMMIT = '60d5af730c9844261b2a661dadb9ee42d98ee7c9'
BASE = '34196aad3d0a50ac02c2b75981fb411645bffef5'
BASE_IMAGE = 'sha256:ff3ce873f0c0546f0b3dee0d1338fd682c909e914020689eff90fb06eefdf66c'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def manifest(ref):
    names = git('ls-tree', '-r', '--name-only', ref).decode().splitlines()
    paths = [p for p in names if p.startswith(('linkyoh/', 'linkyohapp/', 'static/', 'locale/'))
             or p in ('manage.py', 'credentials.py', 'requirements.txt', 'notification_tasks.py',
                      'Dockerfile', '.dockerignore', 'docker-compose.aws.yml')]
    return {p: hashlib.sha256(git('show', ref + ':' + p)).hexdigest() for p in paths}


def main():
    if OUT.exists():
        raise RuntimeError('Candidate package already exists; reconcile instead of overwriting')
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', 'linkyoh-web:ui-34196aa']))[0]
    assert image['Id'] == BASE_IMAGE and image['Architecture'] == 'amd64'
    base, source = manifest(BASE), manifest(COMMIT)
    removed = sorted(set(base) - set(source))
    assert not removed, 'Overlay packaging cannot remove inherited files'
    assert source['requirements.txt'] == base['requirements.txt']
    assert source['docker-compose.aws.yml'] == base['docker-compose.aws.yml']
    data = {'base_commit': BASE, 'base_image': BASE_IMAGE, 'base': base, 'source': source,
            'commit': COMMIT, 'removed': removed}
    OUT.mkdir(mode=0o700)
    (OUT / 'manifest.json').write_text(json.dumps(data, indent=2) + '\n')
    archive_path = OUT / 'source.tar'
    subprocess.run(['git', 'archive', '--format=tar', '--output=' + str(archive_path), COMMIT, *source], cwd=ROOT, check=True)
    with tarfile.open(archive_path) as archive:
        assert all(member.isfile() and member.name in source for member in archive.getmembers() if not member.isdir())
        archive.extractall(OUT / 'source', filter='data')
    for name, expected in source.items():
        assert hashlib.sha256((OUT / 'source' / name).read_bytes()).hexdigest() == expected
    print(json.dumps({'commit': COMMIT, 'files': len(source), 'base_files': len(base),
                      'source_archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                      'package': str(OUT)}, indent=2))


if __name__ == '__main__':
    main()
