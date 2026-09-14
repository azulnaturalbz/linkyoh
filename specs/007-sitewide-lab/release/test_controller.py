"""Offline release guard and rollback tests; no host or Docker access."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('release_controller', Path(__file__).with_name('controller.py'))
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)


class ControllerTests(unittest.TestCase):
    def baseline(self):
        return {'containers': {'linkyoh-web-1': {'id': 'old'}, 'neighbor': {'id': 'fixed'}},
                **{k: 'fixed' for k in ('protected', 'timers', 'timer_unitfiles', 'firewall',
                                       'marketday_firewall', 'caddy_peer', 'web_aliases')}}

    def test_only_web_may_change(self):
        before = self.baseline()
        after = copy.deepcopy(before)
        after['containers']['linkyoh-web-1']['id'] = 'new'
        controller.unchanged(before, after)

    def test_only_current_container_id_alias_is_ignored(self):
        for container_id in ('a'*64, 'b'*64):
            row = {'Id': container_id, 'NetworkSettings': {'Networks': {'edge': {
                'Aliases': [container_id[:12], 'linkyoh-web', 'linkyoh-web-1', 'web']}}}}
            self.assertEqual(controller.stable_aliases(row), ['linkyoh-web', 'linkyoh-web-1', 'web'])
            row['NetworkSettings']['Networks']['edge']['Aliases'].append('unexpected-alias')
            with self.assertRaises(AssertionError):
                controller.stable_aliases(row)

    def test_neighbor_change_rejected(self):
        before = self.baseline()
        after = copy.deepcopy(before)
        after['containers']['neighbor']['id'] = 'changed'
        with self.assertRaisesRegex(AssertionError, 'Neighbor'):
            controller.unchanged(before, after)

    def test_all_protected_changes_rejected(self):
        for key in ('protected', 'timers', 'timer_unitfiles', 'firewall', 'marketday_firewall', 'caddy_peer', 'web_aliases'):
            before = self.baseline()
            after = copy.deepcopy(before)
            after[key] = 'changed'
            with self.subTest(key=key), self.assertRaises(AssertionError):
                controller.unchanged(before, after)

    def config(self, trust='172.20.0.2/32'):
        return {'services': {'web': {'environment': {'LYTRUSTED_PROXY_NETWORKS': trust}},
                             'directory_limits': {'networks': {'linkyoh_network': {}}, 'mem_limit': 67108864}}}

    def test_exact_proxy_allowed(self):
        with patch.object(controller, 'compose', return_value=json.dumps(self.config())), patch.object(controller, 'save'):
            controller.configuration({'caddy_peer': '172.20.0.2'})

    def test_compose_string_memory_allowed(self):
        config = self.config()
        config['services']['directory_limits']['mem_limit'] = '67108864'
        with patch.object(controller, 'compose', return_value=json.dumps(config)), patch.object(controller, 'save'):
            controller.configuration({'caddy_peer': '172.20.0.2'})

    def test_broad_proxy_trust_rejected(self):
        for trust in ('0.0.0.0/0', '172.20.0.0/16', '172.20.0.3/32'):
            with patch.object(controller, 'compose', return_value=json.dumps(self.config(trust))), self.assertRaises(AssertionError):
                controller.configuration({'caddy_peer': '172.20.0.2'})

    def test_public_redis_rejected(self):
        config = self.config()
        config['services']['directory_limits']['ports'] = ['6379:6379']
        with patch.object(controller, 'compose', return_value=json.dumps(config)), self.assertRaises(AssertionError):
            controller.configuration({'caddy_peer': '172.20.0.2'})

    def test_rollback_preserves_current_secret_and_restores_owned_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, release, static, archive_source = [Path(tmp) / name for name in ('app', 'release', 'static', 'archive')]
            for path in (root, release, static, archive_source):
                path.mkdir()
            (archive_source / '.env').write_text('old-secret')
            (archive_source / 'app.py').write_text('old-code')
            (archive_source / 'docker-compose.release.yml').write_text('old-pin')
            with tarfile.open(release / 'backup.tar.gz', 'w:gz') as archive:
                for path in archive_source.iterdir():
                    archive.add(path, arcname=path.name)
            (archive_source / 'app.css').write_text('old-style')
            with tarfile.open(release / 'static-backup.tar.gz', 'w:gz') as archive:
                archive.add(archive_source / 'app.css', arcname='staticfiles/app.css')
            (root / '.env').write_text('rotated-secret')
            (root / 'app.py').write_text('new-code')
            (root / 'new.py').write_text('new-file')
            manifest = {'base': {'app.py': 'unused'}, 'source': {'app.py': 'unused', 'new.py': hashlib.sha256(b'new-file').hexdigest()}}
            with patch.multiple(controller, ROOT=root, RELEASE=release, STATIC=static), patch.object(controller, 'run'), patch.object(controller, 'compose') as compose, patch.object(controller, 'ready'):
                controller.rollback(manifest)
            self.assertEqual((root / '.env').read_text(), 'rotated-secret')
            self.assertEqual((root / 'app.py').read_text(), 'old-code')
            self.assertEqual((static / 'app.css').read_text(), 'old-style')
            self.assertFalse((root / 'new.py').exists())
            compose.assert_called_once_with('up', '-d', '--no-deps', '--no-build', 'web')


if __name__ == '__main__':
    unittest.main()
