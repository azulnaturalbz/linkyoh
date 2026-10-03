"""Synthetic local preview; never load production settings or credentials."""

import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
os.environ['DJANGO_SETTINGS_MODULE'] = 'linkyoh.ecosystem_test_settings'
os.environ['LYPHONE_VERIFICATION_ENABLED'] = 'False'
import django
from django.conf import settings

work = Path(tempfile.mkdtemp(prefix='linkyoh-navigation-'))
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
for key, filename in [('gig', 'plumbing.png'), ('wood', 'workshop.jpg'), ('imported', 'pipe-repair.png')]:
    saved = default_storage.save('qa/' + filename, ContentFile((art / filename).read_bytes()))
    Gig.objects.filter(pk=data[key].pk).update(photo=saved)
data['profile'].cover_image = 'qa/plumbing.png'
data['profile'].save(update_fields=['cover_image'])
print('Synthetic provider: ' + data['profile'].get_absolute_url(), flush=True)
call_command('runserver', '0.0.0.0:8099', use_reloader=False)
