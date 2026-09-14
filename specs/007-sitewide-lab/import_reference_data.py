"""Restore public reference data only into a new, disposable local preview DB."""

import json
import hashlib
from pathlib import Path

from django.apps import apps
from django.contrib.auth.models import User
from django.core import serializers
from django.db import connection, transaction
from django.db.models.signals import post_save
from linkyohapp.models import Category, process_category_image

MODELS = (
    "linkyohapp.country",
    "linkyohapp.district",
    "linkyohapp.localtype",
    "linkyohapp.local",
    "linkyohapp.location",
    "linkyohapp.category",
    "linkyohapp.subcategory",
)


def import_snapshot(path):
    database = Path(connection.settings_dict["NAME"]).resolve()
    if connection.vendor != "sqlite" or not database.parent.name.startswith(
        "linkyoh-sitewide-"
    ):
        raise ValueError(
            "Import requires a fresh disposable linkyoh-sitewide SQLite database"
        )
    models = {label: apps.get_model(label) for label in MODELS}
    if User.objects.exists() or any(
        model.objects.exists() for model in models.values()
    ):
        raise ValueError("Refusing to overwrite existing records")
    payload = json.loads(Path(path).read_text())
    if payload.get("version") != 1 or payload.get("transaction_read_only") is not True:
        raise ValueError("Expected a verified read-only reference export")
    records = payload["records"]
    counts = {label: 0 for label in MODELS}
    keys = {label: set() for label in MODELS}
    for record in records:
        label, pk = record["model"], record["pk"]
        if label not in models or pk in keys[label] or not isinstance(pk, int):
            raise ValueError("Unknown model or invalid/duplicate identifier")
        counts[label] += 1
        keys[label].add(pk)
    if counts != payload["counts"] or any(count > 20000 for count in counts.values()):
        raise ValueError("Reference counts do not match")
    for record in records:
        model = models[record["model"]]
        allowed = {f.name for f in model._meta.fields if not f.primary_key}
        if set(record["fields"]) != allowed:
            raise ValueError("Reference schema differs; review before importing")
        for field in model._meta.fields:
            if field.many_to_one:
                target = field.related_model._meta.label_lower
                if record["fields"][field.name] not in keys[target]:
                    raise ValueError("Broken reference relationship")
    countries = [r for r in records if r["model"] == MODELS[0]]
    if len(countries) != 1 or countries[0]["fields"]["country_name"] != "Belize":
        raise ValueError("Only the Belize hierarchy is permitted")
    # A reference fixture does not include category media. Never start image work.
    post_save.disconnect(process_category_image, sender=Category)
    try:
        with transaction.atomic():
            for label in MODELS:
                rows = [r for r in records if r["model"] == label]
                for obj in serializers.deserialize("json", json.dumps(rows)):
                    obj.save()
            connection.check_constraints()
            actual = {label: model.objects.count() for label, model in models.items()}
            if actual != counts:
                raise ValueError("Local counts differ after import")
            restored = []
            for label in MODELS:
                restored.extend(
                    json.loads(
                        serializers.serialize(
                            "json", models[label].objects.order_by("pk")
                        )
                    )
                )
            ordered = sorted(
                records, key=lambda row: (MODELS.index(row["model"]), row["pk"])
            )
            if restored != ordered:
                raise ValueError(
                    "Local values differ from the source reference snapshot"
                )
    finally:
        post_save.connect(process_category_image, sender=Category)
    digest = hashlib.sha256(json.dumps(ordered, sort_keys=True).encode()).hexdigest()
    return {
        "captured_at": payload["captured_at"],
        "counts": actual,
        "relationships": "valid",
        "field_parity": "exact",
        "reference_sha256": digest,
    }
