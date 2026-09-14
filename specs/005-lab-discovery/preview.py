"""Local synthetic UI review. Never loads production settings or provider data."""

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ["DJANGO_SETTINGS_MODULE"] = "linkyoh.ecosystem_test_settings"
import django
from django.conf import settings

settings.DATABASES["default"]["NAME"] = str(
    Path(tempfile.mkdtemp(prefix="linkyoh-lab-")) / "db.sqlite3"
)
settings.ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
django.setup()
from django.core.management import call_command
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from linkyohapp.test_lab_ui import seed_lab_data
from linkyohapp.models import DEFAULT_CATEGORY_IMAGE, DEFAULT_GIG_IMAGE, Gig

call_command("migrate", verbosity=0)
for name in (DEFAULT_CATEGORY_IMAGE, DEFAULT_GIG_IMAGE):
    default_storage.save(
        name, ContentFile((ROOT / "static/img/linkyoh_banner_web.png").read_bytes())
    )
data = seed_lab_data()
for key, image in [
    ("gig", "plumbing.png"),
    ("wood", "workshop.jpg"),
    ("imported", "pipe-repair.png"),
]:
    # Approved prototype artwork is only attached to synthetic local QA records.
    name = default_storage.save(
        "qa/" + image,
        ContentFile((ROOT / "specs/revamp-prototype/assets" / image).read_bytes()),
    )
    Gig.objects.filter(pk=data[key].pk).update(photo=name)
data["profile"].cover_image = "qa/plumbing.png"
data["profile"].save(update_fields=["cover_image"])
routes = {
    "home": "/",
    "results": "/search/",
    "provider": data["profile"].get_absolute_url(),
    "gig": data["gig"].get_absolute_url(),
    "category": data["category"].get_absolute_url(),
    "subcategory": data["plumbing"].get_absolute_url(),
    "unknown": data["imported"].get_absolute_url(),
}
out = ROOT / "specs/005-lab-discovery/evidence"
out.mkdir(exist_ok=True)
(out / "routes.json").write_text(json.dumps(routes, indent=2) + "\n")
print("Synthetic-only preview: http://127.0.0.1:8097", flush=True)
call_command("runserver", "127.0.0.1:8097", use_reloader=False)
