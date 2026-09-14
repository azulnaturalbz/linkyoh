"""Stream only public reference data through the running app's RDS connection.

Run over SSH stdin; redirect stdout to a protected path outside the repository.
No application secrets or unrelated records are serialized.
"""

import json
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "linkyoh.settings")
os.environ["PGOPTIONS"] = (
    "-c default_transaction_read_only=on -c statement_timeout=15000"
)
import django

django.setup()
from django.core import serializers
from django.db import connection, transaction
from django.utils import timezone
from linkyohapp.models import (
    Category,
    Country,
    District,
    Local,
    LocalType,
    Location,
    SubCategory,
)

if connection.vendor != "postgresql":
    raise SystemExit("Expected PostgreSQL; no export performed")
with transaction.atomic():
    with connection.cursor() as cursor:
        cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        cursor.execute("SHOW transaction_read_only")
        if cursor.fetchone()[0] != "on":
            raise SystemExit("Read-only guard failed")
    country = Country.objects.filter(country_name__iexact="Belize")
    if country.count() != 1:
        raise SystemExit("Expected exactly one Belize country record")
    districts = District.objects.filter(country__in=country)
    locals_ = Local.objects.filter(local_district__in=districts)
    locations = Location.objects.filter(local__in=locals_)
    sources = [
        country,
        districts,
        LocalType.objects.filter(pk__in=locations.values("local_type_id")),
        locals_,
        locations,
        Category.objects.all(),
        SubCategory.objects.all(),
    ]
    records, counts = [], {}
    for queryset in sources:
        count = queryset.count()
        if count > 20000:
            raise SystemExit("Reference table exceeds bounded export size")
        counts[queryset.model._meta.label_lower] = count
        records.extend(
            json.loads(serializers.serialize("json", queryset.order_by("pk")))
        )
    result = {
        "version": 1,
        "captured_at": timezone.now().isoformat(),
        "source": "linkyoh-production-rds",
        "transaction_read_only": True,
        "counts": counts,
        "records": records,
    }
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
