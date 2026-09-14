"""Run only inside the disposable local QA PostgreSQL/Redis network namespace."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ["DJANGO_SETTINGS_MODULE"] = "linkyoh.ecosystem_test_settings"
os.environ["LINKYOH_TEST_REDIS_URL"] = "redis://127.0.0.1:6379/15"
import django
from django.conf import settings

settings.DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "linkyoh_local_qa",
        "USER": "postgres",
        "PASSWORD": "synthetic-local-qa-only",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
django.setup()
from django.test.runner import DiscoverRunner

sys.exit(bool(DiscoverRunner(verbosity=1, interactive=False).run_tests(["linkyohapp"])))
