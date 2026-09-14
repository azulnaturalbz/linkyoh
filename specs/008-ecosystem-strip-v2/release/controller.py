"""One authorized app-only release; run as root on the verified shared host."""
import datetime
import fcntl
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request

ROOT = Path('/opt/linkyoh')
RELEASE = ROOT / 'releases/60d5af7-20260914'
OLD = 'sha256:ff3ce873f0c0546f0b3dee0d1338fd682c909e914020689eff90fb06eefdf66c'
STATIC = Path('/var/lib/docker/volumes/linkyoh_static_volume/_data')
LOCKS = ('/run/marketday-checkout-feedback-release.lock',
         '/opt/wop-releases/.agent-runtime-dark-deploy.lock',
         '/opt/linkyoh/releases/.release.lock')


def run(*args, timeout=180):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=timeout)
    if result.returncode:
        (RELEASE / 'last-command-error.log').write_bytes(result.stdout + result.stderr)
        raise RuntimeError('Command failed; protected error log retained: ' + args[0])
    return result.stdout.decode().strip()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, data):
    (RELEASE / name).write_text(json.dumps(data, indent=2) + '\n')


def compose(*args):
    return run('docker', 'compose', '--project-directory', str(ROOT), '--env-file',
               str(ROOT / '.env'), '-p', 'linkyoh', '-f', str(ROOT / 'docker-compose.aws.yml'),
               '-f', str(ROOT / 'docker-compose.release.yml'), *args)


def stable_aliases(container):
    aliases = container['NetworkSettings']['Networks']['edge']['Aliases']
    result = sorted(a for a in aliases if a not in (container['Id'], container['Id'][:12]))
    assert set(result) == {'linkyoh-web', 'linkyoh-web-1', 'web'}, 'Unexpected web routing aliases'
    return result


def snapshot(name):
    rows = json.loads(run('docker', 'inspect', *run('docker', 'ps', '-q').split()))
    containers = {c['Name'].lstrip('/'): {
        'id': c['Id'], 'image': c['Image'], 'started': c['State']['StartedAt'],
        'restarts': c['RestartCount'], 'status': c['State']['Status'],
        'oom': c['State']['OOMKilled'], 'health': c['State'].get('Health', {}).get('Status'),
    } for c in rows}
    caddy = next(c for c in rows if c['Name'] == '/edge-caddy-1')
    web = next(c for c in rows if c['Name'] == '/linkyoh-web-1')
    peer = caddy['NetworkSettings']['Networks']['edge']['IPAddress']
    protected = {p: digest(p) for p in ('/opt/edge/Caddyfile', '/opt/linkyoh/.env',
                                       '/opt/linkyoh/docker-compose.aws.yml')}
    timer_names = run('systemctl', 'list-units', '--type=timer', '--all', '--plain', '--no-legend', '--no-pager')
    timers = {line.split()[0]: run('systemctl', 'show', line.split()[0], '-p', 'ActiveState', '-p', 'UnitFileState')
              for line in timer_names.splitlines() if line.split()[0].endswith('.timer')}
    memory = {line.split(':')[0]: int(line.split()[1]) * 1024 for line in
              Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemAvailable:', 'SwapFree:'))}
    data = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'containers': containers, 'protected': protected, 'timers': timers,
            'timer_unitfiles': run('systemctl', 'list-unit-files', '--type=timer', '--no-legend', '--no-pager'),
            'firewall': run('iptables', '-S', 'DOCKER-USER'),
            'marketday_firewall': run('iptables', '-S', 'MD-IMDS-V1'),
            'caddy_peer': peer, 'web_aliases': stable_aliases(web),
            'memory': memory, 'disk_free_bytes': shutil.disk_usage('/').free}
    assert memory['MemAvailable'] > 2 * 1024**3, 'RAM reserve below 2 GiB'
    assert data['disk_free_bytes'] > 5 * 1024**3, 'Disk reserve below 5 GiB'
    assert containers['edge-caddy-1']['health'] == 'healthy'
    assert containers['linkyoh-directory_limits-1']['health'] == 'healthy'
    save(name, data)
    return data


def unchanged(before, after):
    def neighbors(data):
        return {k: v for k, v in data['containers'].items() if k != 'linkyoh-web-1'}
    assert neighbors(before) == neighbors(after), 'Neighbor drift'
    for key in ('protected', 'timers', 'timer_unitfiles', 'firewall', 'marketday_firewall', 'caddy_peer', 'web_aliases'):
        assert before[key] == after[key], key + ' drift'


def configuration(before):
    config = json.loads(compose('config', '--format', 'json'))
    trust = config['services']['web']['environment']['LYTRUSTED_PROXY_NETWORKS']
    expected = before['caddy_peer'] + '/32'
    assert trust == expected and ipaddress.ip_network(trust).num_addresses == 1
    redis = config['services']['directory_limits']
    assert not redis.get('ports') and set(redis['networks']) == {'linkyoh_network'}
    assert int(redis['mem_limit']) == 67108864
    save('trust.json', {'caddy_peer': before['caddy_peer'], 'trusted_proxy_cidrs': [trust],
                        'private_redis': True, 'redis_memory_limit': redis['mem_limit']})
    return config


def source_proof(image, manifest):
    code = ('import hashlib,json,pathlib; m=' + repr(manifest) +
            '; bad=[p for p,h in m.items() if hashlib.sha256((pathlib.Path("/linkyoh")/p).read_bytes()).hexdigest()!=h]; '
            'print(json.dumps({"files":len(m),"mismatches":bad})); assert not bad')
    proof = json.loads(run('docker', 'run', '--rm', '--network', 'none', '--memory', '128m', image, 'python', '-c', code))
    save('image-source-proof.json', proof)


def prepare():
    assert not (RELEASE / 'backup.tar.gz').exists(), 'Existing backup; reconcile first'
    before = snapshot('before.json')
    assert before['containers']['linkyoh-web-1']['image'] == OLD
    configuration(before)
    manifest = json.loads((RELEASE / 'manifest.json').read_text())
    drift = [p for p, h in manifest['base'].items() if not (ROOT / p).is_file() or digest(ROOT / p) != h]
    assert not drift, 'Live source drift: ' + ', '.join(drift)
    source_proof((RELEASE / 'image-id').read_text().strip(), manifest['source'])
    with tarfile.open(RELEASE / 'backup.tar.gz', 'w:gz') as archive:
        for p in sorted(set(manifest['base']) | {'.env', 'docker-compose.release.yml'}):
            archive.add(ROOT / p, arcname=p, recursive=False)
    with tarfile.open(RELEASE / 'static-backup.tar.gz', 'w:gz') as archive:
        archive.add(STATIC, arcname='staticfiles')
    checksums = {p: digest(RELEASE / p) for p in ('backup.tar.gz', 'static-backup.tar.gz')}
    save('backup-checksums.json', checksums)
    run('docker', 'tag', OLD, 'linkyoh-web:rollback-pre-60d5af7')
    print(json.dumps({'state': 'BACKED_UP', 'files': len(manifest['source']), 'checksums': checksums}))


def ready(new_strip=True):
    for _ in range(45):
        try:
            with urllib.request.urlopen('https://linkyoh.com/', timeout=8) as response:
                body = response.read()
                if response.status == 200 and (not new_strip or (
                    b'data-strip-version="v2"' in body and b'data-track="games_clickout"' in body
                )):
                    return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError('Public web readiness failed')


def rollback(manifest):
    # Never restore .env: a source rollback must not reverse secret rotation.
    with tarfile.open(RELEASE / 'backup.tar.gz') as archive:
        archive.extractall(ROOT, members=[m for m in archive.getmembers() if m.name != '.env'])
    for p in set(manifest['source']) - set(manifest['base']):
        if (ROOT / p).is_file() and digest(ROOT / p) == manifest['source'][p]:
            (ROOT / p).unlink()
    run('docker', 'tag', OLD, 'linkyoh-web:latest')
    with tarfile.open(RELEASE / 'static-backup.tar.gz') as archive:
        for member in archive.getmembers():
            parts = Path(member.name).parts[1:]
            if parts and member.isfile():
                destination = STATIC.joinpath(*parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as src, destination.open('wb') as dst:
                    shutil.copyfileobj(src, dst)
    compose('up', '-d', '--no-deps', '--no-build', 'web')
    ready(False)


def deploy():
    assert (RELEASE / 'offhost-verified.json').exists(), 'Off-host recovery not verified'
    assert not (RELEASE / 'cutover-started.json').exists(), 'Attempt exists; reconcile first'
    manifest = json.loads((RELEASE / 'manifest.json').read_text())
    new = (RELEASE / 'image-id').read_text().strip()
    before = snapshot('cutover-before.json')
    assert before['containers']['linkyoh-web-1']['image'] == OLD
    old_config = configuration(before)
    assert old_config['services']['web']['image'] == OLD
    for p, h in json.loads((RELEASE / 'backup-checksums.json').read_text()).items():
        assert digest(RELEASE / p) == h
    assert before['protected'] == json.loads((RELEASE / 'before.json').read_text())['protected']
    assert all(digest(ROOT / p) == h for p, h in manifest['base'].items())
    save('cutover-started.json', {'utc': before['utc'], 'old': OLD, 'new': new})
    try:
        for p in manifest['source']:
            destination = ROOT / p
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(RELEASE / 'source' / p, destination)
        override = ROOT / 'docker-compose.release.yml'
        content = override.read_text()
        assert content.count(OLD) == 1
        temporary = ROOT / '.compose-release-candidate'
        temporary.write_text(content.replace(OLD, new))
        os.replace(temporary, override)
        current_config = json.loads(compose('config', '--format', 'json'))
        old_config['services']['web']['image'] = new
        assert current_config == old_config, 'Unexpected Compose change'
        run('docker', 'tag', new, 'linkyoh-web:latest')
        compose('up', '-d', '--no-deps', '--no-build', 'web')
        ready()
        after = snapshot('cutover-after.json')
        assert after['containers']['linkyoh-web-1']['image'] == new
        unchanged(before, after)
        assert all(digest(ROOT / p) == h for p, h in manifest['source'].items())
        save('cutover-result.json', {'state': 'LIVE', 'utc': after['utc'], 'image': new,
                                   'commit': manifest['commit'], 'files': len(manifest['source']),
                                   'unchanged_neighbors': len(before['containers']) - 1})
        print((RELEASE / 'cutover-result.json').read_text())
    except Exception:
        rollback(manifest)
        after = snapshot('rollback-after.json')
        unchanged(before, after)
        save('rollback-result.json', {'state': 'ROLLED_BACK', 'utc': after['utc'], 'image': OLD})
        raise


if __name__ == '__main__':
    assert os.geteuid() == 0
    os.umask(0o077)
    handles = []
    for path in LOCKS:
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        handles.append(fd)
    {'prepare': prepare, 'deploy': deploy}[sys.argv[1]]()
