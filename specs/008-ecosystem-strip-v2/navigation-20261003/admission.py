"""Read-only, bounded admission for the pinned app-only navigation release."""

import datetime
import json
import subprocess
import sys
from pathlib import Path

import ops

OUT = Path(__file__).resolve().parent / 'evidence'


def aws(*args):
    return json.loads(subprocess.check_output([
        'uvx', '--from', 'awscli', 'aws', '--profile', 'silvatech',
        '--region', 'us-east-1', *args, '--output', 'json',
    ]))


def main():
    ops.window()
    assert aws('sts', 'get-caller-identity')['Account'] == '944327601374'
    instance = aws('ec2', 'describe-instances', '--instance-ids',
                   'i-0df5dfaabc889f576')['Reservations'][0]['Instances'][0]
    assert instance['State']['Name'] == 'running'
    assert instance['InstanceType'] == 't3a.large'
    assert instance['Architecture'] == 'x86_64'
    assert instance['PublicIpAddress'] == ops.HOST.split('@')[1]
    now = datetime.datetime.now(datetime.timezone.utc)
    metrics = {}
    for metric, statistic in [('CPUUtilization', 'Average'), ('CPUCreditBalance', 'Minimum')]:
        points = aws('cloudwatch', 'get-metric-statistics', '--namespace', 'AWS/EC2',
                     '--metric-name', metric, '--dimensions',
                     'Name=InstanceId,Value=i-0df5dfaabc889f576', '--start-time',
                     (now - datetime.timedelta(hours=1)).isoformat(), '--end-time',
                     now.isoformat(), '--period', '300', '--statistics', statistic)['Datapoints']
        assert points, 'No recent CloudWatch samples'
        metrics[metric] = sorted(points, key=lambda p: p['Timestamp'])
    assert max(p['Average'] for p in metrics['CPUUtilization']) < 80
    assert min(p['Minimum'] for p in metrics['CPUCreditBalance']) > 0
    code = '''import datetime,json,pathlib,shutil,subprocess,time
def run(*args): return subprocess.check_output(args).decode()
def containers():
    rows=json.loads(run('docker','inspect',*run('docker','ps','-q').split()))
    return {c['Name']: {'id':c['Id'],'image':c['Image'],'start':c['State']['StartedAt'],
      'restarts':c['RestartCount'],'health':c['State'].get('Health',{}).get('Status')} for c in rows}
def sample():
    mem={line.split(':')[0]:int(line.split()[1])*1024 for line in pathlib.Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemAvailable:','SwapFree:'))}
    vm={line.split()[0]:int(line.split()[1]) for line in pathlib.Path('/proc/vmstat').read_text().splitlines() if line.startswith(('pswpin ','pswpout '))}
    return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'memory':mem,'paging':vm,
      'cpu':list(map(int,pathlib.Path('/proc/stat').read_text().splitlines()[0].split()[1:])),
      'disk_free_bytes':shutil.disk_usage('/').free}
before=containers(); samples=[]
stats=[json.loads(line) for line in run('docker','stats','--no-stream','--format','{{json .}}').splitlines()]
for i in range(101):
    samples.append(sample())
    if i<100: time.sleep(3)
after=containers()
print(json.dumps({'before':before,'after':after,'samples':samples,'container_stats':stats}))
'''
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-i', ops.KEY, ops.HOST,
                             'sudo python3 -'], input=code.encode(), capture_output=True, timeout=340)
    assert result.returncode == 0, 'Read-only host admission failed'
    host = json.loads(result.stdout)
    minimum = min(s['memory']['MemAvailable'] for s in host['samples'])
    disk = min(s['disk_free_bytes'] for s in host['samples'])
    # The temporary read-only Django preflight has a 256 MiB ceiling.
    passed = minimum >= (2 * 1024**3 + 256 * 1024**2) and disk >= 5 * 1024**3
    passed = passed and host['before'] == host['after']
    receipt = {'utc': now.isoformat(), 'account': '944327601374', 'region': 'us-east-1',
               'instance': instance['InstanceId'], 'type': instance['InstanceType'],
               'architecture': instance['Architecture'], 'public_ip': instance['PublicIpAddress'],
               'cloudwatch': metrics, 'host': host, 'passed': passed,
               'minimum_available_ram_bytes': minimum, 'minimum_disk_free_bytes': disk,
               'production_mutation': False, 'reserve_bytes': 2 * 1024**3,
               'temporary_preflight_ceiling_bytes': 256 * 1024**2}
    filename = 'admission-post-stage.json' if '--post-stage' in sys.argv else 'admission.json'
    path = OUT / filename
    with path.open('x') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: receipt[k] for k in ('passed', 'minimum_available_ram_bytes', 'minimum_disk_free_bytes')}))
    assert passed, 'Capacity or neighbor stability gate refused; no mutation'


if __name__ == '__main__':
    main()
