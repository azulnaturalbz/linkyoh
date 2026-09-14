"""Read-only discovery and conservative presentation of existing evidence."""

import re
import unicodedata
from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Prefetch, Q
from django.utils import timezone, translation
from django.utils.translation import gettext as _

from .models import (
    Category,
    District,
    Gig,
    GigClaimRequest,
    GigServiceArea,
    Location,
    SubCategory,
)

ALIASES = {
    "plumbing": ("plumber", "plumbers", "plomero", "plomeros", "plomeria"),
    "carpentry": ("carpenter", "carpenters", "carpintero", "carpinteria"),
    "electrical": ("electrician", "electricista", "electricidad"),
    "electrical services": ("electrician", "electricista"),
    "air conditioning": ("ac repair", "aire acondicionado"),
    "painting": ("painter", "pintor", "pintura"),
    "banking": ("bank", "banks", "banco", "bancos"),
    "real estate": ("bienes raices", "inmobiliaria"),
    "housing & construction": ("construccion",),
}
STOP_WORDS = set(
    "i need a an the in near for please find me someone service services un una el la en de necesito busco por favor cerca alguien servicio servicios".split()
)
URGENT = ("tonight", "today", "urgent", "esta noche", "hoy", "urgente")
FIELDS = ("category", "subcategory", "district", "location")


def normalized(value):
    value = unicodedata.normalize("NFKD", str(value).casefold())
    return " ".join(
        re.sub(
            r"[^\w\s&]", " ", "".join(c for c in value if not unicodedata.combining(c))
        ).split()
    )


def public_gigs():
    return (
        Gig.objects.filter(status=True)
        .select_related(
            "user__profile",
            "category",
            "sub_category",
            "district",
            "location__local",
            "import_source",
        )
        .defer("import_source__raw_payload", "import_source__source_notes")
        .prefetch_related(
            Prefetch(
                "service_areas",
                queryset=GigServiceArea.objects.select_related(
                    "district", "location__local"
                ),
            ),
            Prefetch(
                "claim_requests",
                queryset=GigClaimRequest.objects.only(
                    "id", "gig_id", "user_id", "status", "updated_at"
                ),
                to_attr="public_claim_evidence",
            ),
        )
    )


def checked_record(profile, gig=None):
    # OTP rows lack an owner binding and confirmed_at. They are not public proof.
    staff = profile is None or profile.user.is_staff
    reviewed = bool(not staff and profile.is_verified)
    date = profile.verified_date if reviewed else None
    if date and date > timezone.now():
        date = None
    claimed = False
    if gig is not None and not staff:
        claims = getattr(gig, "public_claim_evidence", None)
        if claims is None:
            claims = gig.claim_requests.only("user_id", "status")
        claimed = any(
            c.status == "approved" and c.user_id == gig.user_id for c in claims
        )
    return {
        "reviewed": reviewed,
        "date": date,
        "claimed": claimed,
        "known": reviewed or claimed,
    }


def decorate(gigs):
    for gig in gigs:
        profile = getattr(gig.user, "profile", None)
        # An importer account represents multiple unrelated businesses.
        name = (
            gig.title
            if gig.user.is_staff
            else (
                profile.get_display_name()
                if profile
                else gig.user.get_full_name() or gig.user.username
            )
        )
        gig.lab = {"name": name, "checked": checked_record(profile, gig)}
    return gigs


def phone_digits(value):
    value = re.sub(r"[\s()+.-]", "", str(value or ""))
    if not value.isdigit() or not 7 <= len(value) <= 15:
        return ""
    return "501" + value if len(value) == 7 else value


def contact_context(gig=None, profile=None):
    contacts = list(gig.contacts.all()) if gig else []
    phone = phone_digits(gig.phone_number if gig else profile.phone_number)
    whatsapp = next(
        (
            phone_digits(c.phone_number)
            for c in contacts
            if c.is_whatsapp and phone_digits(c.phone_number)
        ),
        "",
    )
    # Preserve the existing main-number WhatsApp entry point; it is not a phone check.
    whatsapp = whatsapp or phone
    return {
        "public_phone": phone,
        "whatsapp_phone": whatsapp,
        "public_contacts": contacts,
    }


class SmartSearch:
    def __init__(self, params, category=None, subcategory=None):
        self.categories = list(Category.objects.order_by("category"))
        self.subcategories = list(
            SubCategory.objects.select_related("category").order_by("subcategory")
        )
        self.districts = list(District.objects.order_by("district_name"))
        self.locations = list(
            Location.objects.select_related("local__local_district").order_by(
                "local__local_name", "pk"
            )
        )
        self.catalog = {
            "category": self.categories,
            "subcategory": self.subcategories,
            "district": self.districts,
            "location": self.locations,
        }
        self.selected = {key: None for key in FIELDS}
        self.issues = []
        raw = params.get("q", params.get("param", ""))
        self.query = " ".join(raw.split())[:200]
        if len(raw) > 200:
            self.issues.append(_("Please keep your search under 200 characters."))
        self.urgent = False
        text = normalized(self.query)
        for phrase in URGENT:
            if re.search(r"\b" + re.escape(phrase) + r"\b", text):
                self.urgent = True
                text = re.sub(r"\b" + re.escape(phrase) + r"\b", " ", text)
        explicit = set()
        for key in FIELDS:
            value = params.get(key, params.get("town", "") if key == "location" else "")
            if value:
                explicit.add(key)
                self.selected[key] = next(
                    (o for o in self.catalog[key] if str(o.pk) == value), None
                )
                if self.selected[key] is None:
                    self.issues.append(
                        _("A selected filter is not available. Please choose again.")
                    )
        if category:
            self.selected["category"] = category
            explicit.add("category")
        if subcategory:
            self.selected["subcategory"] = subcategory
            self.selected["category"] = subcategory.category
            explicit.update(("category", "subcategory"))

        # Longest phrases first prevents Belize City becoming district Belize.
        candidates = []
        for key, records in self.catalog.items():
            for record in records:
                label = normalized(record)
                if key == "category" and label in ("services", "service", "servicios"):
                    continue
                for alias in (label,) + ALIASES.get(label, ()):
                    candidates.append((alias, key, record))
        phrases = sorted({p for p, _, _ in candidates}, key=lambda p: (-len(p), p))
        for phrase in phrases:
            if not phrase or not re.search(r"\b" + re.escape(phrase) + r"\b", text):
                continue
            matches = [(key, obj) for p, key, obj in candidates if p == phrase]
            # A selected district disambiguates identically named villages.
            district = self.selected["district"]
            if district:
                matches = [
                    (k, o)
                    for k, o in matches
                    if k != "location" or o.local.local_district_id == district.pk
                ]
            unique = {(k, o.pk): (k, o) for k, o in matches}
            if len(unique) == 1:
                key, obj = next(iter(unique.values()))
                if key not in explicit:
                    if self.selected[key] and self.selected[key].pk != obj.pk:
                        self.issues.append(
                            _(
                                "Please choose one service and one area using the filters."
                            )
                        )
                    else:
                        self.selected[key] = obj
            elif len(unique) > 1:
                self.issues.append(
                    _(
                        "This place or service is ambiguous. Please choose it using the filters."
                    )
                )
            else:
                self.issues.append(
                    _("The requested town does not match the selected district.")
                )
            text = re.sub(r"\b" + re.escape(phrase) + r"\b", " ", text)

        cat, sub, district, location = (self.selected[k] for k in FIELDS)
        if sub:
            if cat and sub.category_id != cat.pk:
                self.issues.append(
                    _("The service does not belong to the selected category.")
                )
            else:
                self.selected["category"] = sub.category
        if location:
            if district and location.local.local_district_id != district.pk:
                self.issues.append(
                    _("The requested town does not match the selected district.")
                )
            else:
                self.selected["district"] = location.local.local_district
        self.words = [word for word in text.split() if word not in STOP_WORDS]
        if self.query and not self.words and not any(self.selected.values()):
            self.issues.append(_("Add a service or place to your search."))
        self.prices = {}
        for key in ("min_price", "max_price"):
            value = params.get(key, "")
            if value:
                if value.isdigit() and len(value) <= 9:
                    self.prices[key] = int(value)
                else:
                    self.issues.append(_("Enter a valid price."))
        if self.prices.get("min_price", 0) > self.prices.get("max_price", 999999999):
            self.issues.append(_("Minimum price must not exceed maximum price."))

    def queryset(self):
        qs = public_gigs()
        if self.issues:
            return qs.none()
        for word in self.words:
            qs = qs.filter(
                Q(title__icontains=word)
                | Q(description__icontains=word)
                | Q(user__profile__company_name__icontains=word)
                | Q(category__category__icontains=word)
                | Q(sub_category__subcategory__icontains=word)
            )
        for key, field in (("category", "category"), ("subcategory", "sub_category")):
            if self.selected[key]:
                qs = qs.filter(**{field: self.selected[key]})
        primary, additional = {}, {}
        for key in ("district", "location"):
            if self.selected[key]:
                primary[key] = self.selected[key]
                additional["service_areas__" + key] = self.selected[key]
        if primary:
            qs = qs.filter(Q(**primary) | Q(**additional))
        for key, lookup in (("min_price", "gte"), ("max_price", "lte")):
            if key in self.prices:
                qs = qs.filter(
                    Q(**{"price__" + lookup: self.prices[key]}) | Q(price=-1)
                )
        return qs.distinct().order_by("-featured", "-create_time", "-pk")

    def context(self):
        params = {"q": self.query, "lang": translation.get_language()[:2]}
        params.update({k: str(v.pk) for k, v in self.selected.items() if v})
        params.update(self.prices)
        params = {k: v for k, v in params.items() if v != ""}
        return {
            "search_query": self.query,
            "search_issues": list(dict.fromkeys(self.issues)),
            "search_urgent": self.urgent,
            "search_chips": [str(v) for v in self.selected.values() if v],
            "search_categories": self.categories,
            "search_subcategories": self.subcategories,
            "search_districts": self.districts,
            "search_locations": self.locations,
            "page_query": urlencode(params),
            "has_filters": any(self.selected.values()),
            **{
                "selected_" + k: str(v.pk) if v else ""
                for k, v in self.selected.items()
            },
            **self.prices,
        }


def finder_context(request):
    # This public routing key is not a credential. Both approval and exact origin
    # are mandatory; GET search is the fail-closed default even when JS is absent.
    enabled = (
        getattr(settings, "LINKYOH_WOP_REVIEWED", False)
        and getattr(settings, "LINKYOH_WOP_WEBSITE_KEY", "") == "linkyoh"
        and request.build_absolute_uri("/").rstrip("/")
        in ("https://linkyoh.com", "https://www.linkyoh.com")
    )
    return {"finder_mode": "conversation" if enabled else "search"}
