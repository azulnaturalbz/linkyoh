"""Isolated UI preview: real public taxonomy, synthetic providers, no outbound sends."""

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ["DJANGO_SETTINGS_MODULE"] = "linkyoh.ecosystem_test_settings"
os.environ["LYPHONE_VERIFICATION_ENABLED"] = "False"
import django
from django.conf import settings

work = Path(tempfile.mkdtemp(prefix="linkyoh-sitewide-"))
settings.DATABASES["default"]["NAME"] = str(work / "db.sqlite3")
settings.MEDIA_ROOT = str(work / "media")
settings.ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
django.setup()
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.urls import reverse
from django.utils import timezone
from linkyohapp.models import (
    Category,
    SubCategory,
    District,
    Location,
    Profile,
    Gig,
    GigServiceArea,
    GigClaimRequest,
    ImportedGigSource,
    Conversation,
    Message,
    Notification,
    DEFAULT_CATEGORY_IMAGE,
    DEFAULT_GIG_IMAGE,
)
from import_reference_data import import_snapshot

call_command("migrate", verbosity=0)
evidence = import_snapshot(sys.argv[1])
category = Category.objects.get(category="Housing & Construction")
plumbing = SubCategory.objects.filter(
    category=category, subcategory__icontains="plumb"
).first()
carpentry = SubCategory.objects.filter(
    category=category, subcategory__icontains="cabinet"
).first()
if not plumbing or not carpentry:
    raise ValueError("Review actual reference taxonomy before seeding examples")
cayo = District.objects.get(district_name="Cayo")
san_ignacio = Location.objects.get(
    local__local_name="San Ignacio and Santa Elena Town", local__local_district=cayo
)
belmopan = Location.objects.get(
    local__local_name="Belmopan City", local__local_district=cayo
)
user = User.objects.create_user(
    "qa-provider",
    password="Local-review-only-2026",
    first_name="Example",
    last_name="Owner",
)
profile = Profile.objects.create(
    user=user,
    profile_type="business",
    company_name="Example Plumbing",
    district=cayo,
    location=san_ignacio,
    about="Synthetic local review record. Not a real business.",
    is_verified=True,
    verified_date=timezone.now() - timedelta(days=10),
)
unknown = User.objects.create_user("qa-unconfirmed")
Profile.objects.create(user=unknown)
staff = User.objects.create_user("qa-import-bot", is_staff=True)
Profile.objects.create(user=staff)
gigs = []
for owner, title, sub, location, image in [
    (user, "Tap and sink repairs", plumbing, san_ignacio, "plumbing.png"),
    (unknown, "Cabinet and shelving repairs", carpentry, belmopan, "workshop.jpg"),
    (staff, "Example imported repairs", plumbing, san_ignacio, "pipe-repair.png"),
]:
    photo = default_storage.save(
        "qa/" + image,
        ContentFile((ROOT / "specs/revamp-prototype/assets" / image).read_bytes()),
    )
    gigs.append(
        Gig.objects.create(
            user=owner,
            title=title,
            description="Synthetic review listing. No real contact details.",
            category=category,
            sub_category=sub,
            district=cayo,
            location=location,
            price=-1,
            photo=photo,
        )
    )
gig, wood, imported = gigs
profile.cover_image = gig.photo.name
profile.avatar = gig.photo.name
profile.save(update_fields=["avatar", "cover_image"])
GigServiceArea.objects.create(gig=gig, district=cayo, location=belmopan)
GigClaimRequest.objects.create(
    gig=gig, user=user, status="approved", reason="Synthetic QA claim"
)
ImportedGigSource.objects.create(
    gig=imported, imported_by=staff, source_notes="Synthetic QA"
)
conversation = Conversation.objects.create(initiator=user, recipient=unknown, gig=wood)
Message.objects.create(
    conversation=conversation,
    sender=unknown,
    content="Synthetic review conversation. Could you share the dimensions of the cabinet?",
)
Notification.objects.create(
    user=user,
    notification_type="system",
    title="Synthetic review notification",
    message="This is local UI test data. No notification was sent.",
)
for name in (DEFAULT_CATEGORY_IMAGE, DEFAULT_GIG_IMAGE):
    default_storage.save(
        name,
        ContentFile((ROOT / "specs/revamp-prototype/assets/workshop.jpg").read_bytes()),
    )
routes = {
    "home": "/",
    "results": "/search/",
    "provider": profile.get_absolute_url(),
    "gig": gig.get_absolute_url(),
    "category": category.get_absolute_url(),
    "subcategory": plumbing.get_absolute_url(),
    "unknown": imported.get_absolute_url(),
    "profile-edit": profile.get_absolute_url() + "?edit=1",
    "edit-gig": reverse("edit_gig", args=[gig.pk]),
    "claim": reverse("claim_gig", args=[imported.pk]),
}
for name in (
    "login",
    "register",
    "password_reset",
    "password_reset_done",
    "password_reset_complete",
    "password_change",
    "password_change_done",
    "my_gigs",
    "create_gig",
    "messaging_unified",
    "notification_list",
    "about",
    "contact",
    "terms",
    "privacy",
    "thanks",
    "help_center",
    "help_add_gig",
    "help_search",
    "help_profile",
    "help_dashboard",
    "help_metrics",
    "help_faq",
):
    routes[name] = reverse(name)
routes["password-reset-invalid"] = "/reset/invalid/invalid/"
routes["conversation"] = reverse(
    "messaging_unified_with_conversation", args=[conversation.pk]
)
routes["conversation-detail"] = reverse("conversation_detail", args=[conversation.pk])
routes["message-draft"] = (
    reverse("messaging_unified") + "?recipient_id=" + str(unknown.pk)
)
out = ROOT / "specs/007-sitewide-lab/evidence"
out.mkdir(exist_ok=True)
(out / "routes.json").write_text(json.dumps(routes, indent=2) + "\n")
(out / "reference-parity.json").write_text(json.dumps(evidence, indent=2) + "\n")
print(
    "Reference-data preview with synthetic accounts: http://127.0.0.1:8098", flush=True
)
call_command("runserver", "127.0.0.1:8098", use_reloader=False)
