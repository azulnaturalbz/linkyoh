"""Disposable synthetic preview; no production environment, DB, or outbound sends."""

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'evidence'
sys.path.insert(0, str(ROOT))
os.environ['DJANGO_SETTINGS_MODULE'] = 'linkyoh.ecosystem_test_settings'
os.environ['LYPHONE_VERIFICATION_ENABLED'] = 'False'
import django
from django.conf import settings

work = Path(tempfile.mkdtemp(prefix='linkyoh-strip-v2-'))
settings.DATABASES['default']['NAME'] = str(work / 'db.sqlite3')
settings.MEDIA_ROOT = str(work / 'media')
settings.ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
django.setup()
from django.core.management import call_command
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from linkyohapp.test_lab_ui import seed_lab_data
from linkyohapp.models import DEFAULT_CATEGORY_IMAGE, DEFAULT_GIG_IMAGE, Gig

call_command('migrate', verbosity=0)
data = seed_lab_data()
art = ROOT / 'specs/revamp-prototype/assets'
for name in (DEFAULT_CATEGORY_IMAGE, DEFAULT_GIG_IMAGE):
    default_storage.save(name, ContentFile((art / 'workshop.jpg').read_bytes()))
for key, image in [('gig', 'plumbing.png'), ('wood', 'workshop.jpg'), ('imported', 'pipe-repair.png')]:
    saved = default_storage.save('qa/' + image, ContentFile((art / image).read_bytes()))
    Gig.objects.filter(pk=data[key].pk).update(photo=saved)
data['profile'].cover_image = 'qa/plumbing.png'
data['profile'].save(update_fields=['cover_image'])
routes = {'home': '/', 'provider': data['profile'].get_absolute_url(), 'login': '/login/'}
OUT.mkdir(exist_ok=True)
(OUT / 'routes.json').write_text(json.dumps(routes, indent=2) + '\n')
print('Synthetic strip v2 QA: http://127.0.0.1:8099', flush=True)
call_command('runserver', '127.0.0.1:8099', use_reloader=False)
