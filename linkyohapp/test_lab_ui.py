from datetime import timedelta
import ast
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import connection
from django.test import RequestFactory, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone, translation
from django.template.base import Lexer, TokenType

from .discovery import (
    SmartSearch,
    checked_record,
    decorate,
    finder_context,
    public_gigs,
)
from .models import (
    Category,
    Country,
    District,
    Gig,
    GigClaimRequest,
    GigServiceArea,
    ImportedGigSource,
    Local,
    LocalType,
    Location,
    Profile,
    SubCategory,
)


def seed_lab_data():
    country = Country.objects.create(country_name="Belize")
    cayo = District.objects.create(country=country, district_name="Cayo")
    belize = District.objects.create(country=country, district_name="Belize")
    town_type = LocalType.objects.create(local_type_name="Town")

    def town(name, district):
        local = Local.objects.create(local_name=name, local_district=district)
        return Location.objects.create(local=local, local_type=town_type)

    san_ignacio = town("San Ignacio", cayo)
    belmopan = town("Belmopan", cayo)
    city = town("Belize City", belize)
    category = Category.objects.create(
        category="Housing & Construction", short_category="Home"
    )
    services = Category.objects.create(category="Services", short_category="Svc")
    plumbing = SubCategory.objects.create(
        category=category, subcategory="Plumbing", sub_short_category="Plumb"
    )
    carpentry = SubCategory.objects.create(
        category=category, subcategory="Carpentry", sub_short_category="Carp"
    )
    banking = SubCategory.objects.create(
        category=services, subcategory="Banking", sub_short_category="Bank"
    )
    user = User.objects.create_user(
        username="qa-provider", first_name="Example", last_name="Owner"
    )
    profile = Profile.objects.create(
        user=user,
        profile_type="business",
        company_name="Example Plumbing",
        district=cayo,
        location=san_ignacio,
        phone_number="0000000",
        about="Synthetic QA record, not a real provider.",
        is_verified=True,
        verified_date=timezone.now() - timedelta(days=10),
    )
    gig = Gig.objects.create(
        user=user,
        category=category,
        sub_category=plumbing,
        district=cayo,
        location=san_ignacio,
        title="Tap and sink repairs",
        description="Tap repairs and fitting installation.",
        address_1="Synthetic QA address",
        phone_number="0000000",
        price=-1,
    )
    GigClaimRequest.objects.create(
        gig=gig,
        user=user,
        status="approved",
        contact_number="0000000",
        reason="Private ownership document",
        admin_notes="PRIVATE-REVIEW-NOTE",
    )
    unknown = User.objects.create_user(username="qa-unconfirmed")
    Profile.objects.create(user=unknown)
    wood = Gig.objects.create(
        user=unknown,
        category=category,
        sub_category=carpentry,
        district=cayo,
        location=belmopan,
        title="Cabinet and shelving repairs",
        description="Custom shelving and cabinet repairs.",
        address_1="Synthetic QA address",
        price=175,
    )
    area = GigServiceArea.objects.create(gig=gig, district=cayo, location=belmopan)
    staff = User.objects.create_user(username="qa-import-bot", is_staff=True)
    Profile.objects.create(user=staff, is_verified=True, verified_date=timezone.now())
    imported = Gig.objects.create(
        user=staff,
        category=category,
        sub_category=plumbing,
        district=belize,
        location=city,
        title="Example imported repairs",
        description="Synthetic imported plumbing record.",
        address_1="Synthetic QA address",
        price=-1,
    )
    ImportedGigSource.objects.create(
        gig=imported,
        imported_by=staff,
        source_notes="PRIVATE-SOURCE",
        raw_payload={"secret": "PRIVATE-RAW"},
    )
    hidden = Gig.objects.create(
        user=user,
        category=category,
        sub_category=plumbing,
        district=cayo,
        location=san_ignacio,
        title="HIDDEN-QA-LISTING",
        status=False,
    )
    return locals()


class LabDiscoveryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for key, value in seed_lab_data().items():
            if key not in ("cls", "town"):
                setattr(cls, key, value)

    def ids(self, params):
        return set(SmartSearch(params).queryset().values_list("pk", flat=True))

    def test_english_need_parses_service_area_and_urgency(self):
        search = SmartSearch({"q": "I need a plumber in Cayo tonight"})
        self.assertTrue(search.urgent)
        self.assertEqual(search.selected["subcategory"], self.plumbing)
        self.assertEqual(list(search.queryset()), [self.gig])

    def test_spanish_accents_and_town(self):
        self.assertEqual(
            self.ids({"q": "Necesito un carpintero en Belmopán"}), {self.wood.pk}
        )

    def test_generic_services_word_does_not_force_services_category(self):
        self.assertEqual(self.ids({"q": "plumbing services in Cayo"}), {self.gig.pk})
        self.assertEqual(
            self.ids({"q": "servicios de plomería en Cayo"}), {self.gig.pk}
        )

    def test_belize_city_not_mistaken_for_district(self):
        self.assertEqual(self.ids({"q": "plumber in Belize City"}), {self.imported.pk})

    def test_explicit_filters_win(self):
        self.assertEqual(
            self.ids({"q": "plumber in Cayo", "district": str(self.belize.pk)}),
            {self.imported.pk},
        )

    def test_unmatched_words_are_not_dropped(self):
        self.assertEqual(self.ids({"q": "plumber in Cayo unicorn"}), set())

    def test_legacy_query_names_work(self):
        self.assertEqual(
            self.ids({"param": "Tap", "location": str(self.belmopan.pk)}), {self.gig.pk}
        )

    def test_ambiguous_location_requires_choice(self):
        local = Local.objects.create(
            local_name="San Ignacio", local_district=self.belize
        )
        Location.objects.create(local=local, local_type=self.town_type)
        search = SmartSearch({"q": "plumber in San Ignacio"})
        self.assertTrue(search.issues)
        self.assertFalse(search.queryset().exists())
        self.assertEqual(
            self.ids({"q": "plumber in San Ignacio", "district": str(self.cayo.pk)}),
            {self.gig.pk},
        )

    def test_invalid_filters_fail_honestly_without_500(self):
        for params in (
            {"district": "oops"},
            {"location": "9999999999999999999999"},
            {"q": "x" * 201},
            {"min_price": "nan"},
            {"min_price": "10", "max_price": "5"},
            {"q": "tonight"},
            {"category": str(self.services.pk), "subcategory": str(self.plumbing.pk)},
        ):
            with self.subTest(params=params):
                response = self.client.get("/search/", params)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["search_issues"])
                self.assertEqual(response.context["total_count"], 0)

    def test_mismatched_geography_does_not_cross_coverage_rows(self):
        GigServiceArea.objects.create(
            gig=self.wood, district=self.belize, location=self.city
        )
        self.assertEqual(
            self.ids(
                {"district": str(self.belize.pk), "location": str(self.belmopan.pk)}
            ),
            set(),
        )
        self.assertEqual(
            self.ids({"district": str(self.belize.pk), "location": str(self.city.pk)}),
            {self.wood.pk, self.imported.pk},
        )

    def test_price_filter_retains_call_for_pricing(self):
        self.assertEqual(
            self.ids({"max_price": "100"}), {self.gig.pk, self.imported.pk}
        )

    def test_hidden_listing_never_in_discovery(self):
        self.assertNotIn(self.hidden.pk, self.ids({}))

    def test_bounded_queries_do_not_grow_per_card(self):
        with CaptureQueriesContext(connection) as queries:
            decorate(list(public_gigs()))
        self.assertLessEqual(len(queries), 3)

    def test_checked_review_scope_does_not_claim_phone(self):
        checks = checked_record(self.profile, self.gig)
        self.assertTrue(checks["reviewed"])
        self.assertTrue(checks["claimed"])
        self.assertEqual(checks["date"], self.profile.verified_date)
        response = self.client.get(self.gig.get_absolute_url())
        self.assertContains(response, "Phone confirmation unknown")
        self.assertContains(response, "Claim date unknown")
        self.assertNotContains(response, "Phone confirmed")
        self.assertNotContains(response, "PRIVATE-REVIEW-NOTE")

    def test_importer_verification_does_not_verify_business(self):
        checks = checked_record(self.staff.profile, self.imported)
        self.assertFalse(checks["known"])
        response = self.client.get(self.imported.get_absolute_url())
        self.assertNotContains(response, "PRIVATE-RAW")
        self.assertNotContains(response, "PRIVATE-SOURCE")
        self.assertNotContains(response, "qa-import-bot")

    def test_revoked_or_future_dates_not_positive_proof(self):
        self.profile.is_verified = False
        self.assertIsNone(checked_record(self.profile)["date"])
        self.profile.is_verified = True
        self.profile.verified_date = timezone.now() + timedelta(days=1)
        self.assertIsNone(checked_record(self.profile)["date"])

    def test_claim_must_match_current_owner(self):
        self.gig.user = self.unknown
        self.assertFalse(checked_record(self.unknown.profile, self.gig)["claimed"])

    def test_business_and_person_display_fallback(self):
        self.assertEqual(decorate([self.gig])[0].lab["name"], "Example Plumbing")
        self.profile.company_name = ""
        self.profile.save()
        self.gig.user.refresh_from_db()
        self.assertEqual(decorate([self.gig])[0].lab["name"], "Example Owner")
        self.user.first_name = self.user.last_name = ""
        self.user.save()
        self.gig.user.refresh_from_db()
        self.assertEqual(decorate([self.gig])[0].lab["name"], "qa-provider")

    def test_all_card_surfaces_have_checked(self):
        for path in (
            "/",
            "/search/",
            self.category.get_absolute_url(),
            self.plumbing.get_absolute_url(),
            self.profile.get_absolute_url(),
        ):
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                self.assertEqual(
                    html.count('class="provider-card"'),
                    html.count("data-checked>")
                    - (1 if path == self.profile.get_absolute_url() else 0),
                )

    def test_spanish_discovery_uses_django_catalog(self):
        response = self.client.get("/", {"lang": "es"})
        self.assertContains(response, "¿Qué necesitas resolver?")
        self.assertContains(response, '<html lang="es">')
        self.assertContains(response, "Comprobado")
        self.assertEqual(response["Content-Language"], "es")

    def test_every_discovery_ui_literal_has_spanish_translation(self):
        templates = Path(__file__).parent / "templates"
        paths = list((templates / "lab").glob("*.html"))
        paths += [
            templates / name
            for name in ("home.html", "profile.html", "gig_detail.html")
        ]
        missing = set()
        with translation.override("es"):
            for path in paths:
                for token in Lexer(path.read_text()).tokenize():
                    if token.token_type == TokenType.BLOCK:
                        bits = token.split_contents()
                        if bits and bits[0] == "translate" and bits[1][0] in ('"', "'"):
                            message = ast.literal_eval(bits[1])
                            if translation.gettext(message) == message:
                                missing.add(message)
        self.assertEqual(missing, set())

    def test_get_search_is_shareable_and_locale_preserved(self):
        response = self.client.get("/search/", {"q": "plomero en Cayo", "lang": "es"})
        self.assertEqual(response.context["total_count"], 1)
        self.assertIn("lang=es", response.context["page_query"])
        self.assertIn("district=", response.context["page_query"])
        self.assertIn("q=plomero", response.context["language_en_url"])

    def test_pagination_keeps_search_and_area(self):
        Gig.objects.bulk_create(
            [
                Gig(
                    user=self.user,
                    category=self.category,
                    sub_category=self.plumbing,
                    district=self.cayo,
                    location=self.san_ignacio,
                    title="Plumbing fixture " + str(i),
                    description="Tap repairs",
                )
                for i in range(12)
            ]
        )
        response = self.client.get(
            "/search/", {"q": "plumber in Cayo", "lang": "es", "page": "2"}
        )
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(response.context["total_count"], 13)
        self.assertContains(response, "page=1")
        self.assertIn("q=plumber+in+Cayo", response.context["page_query"])

    def test_profile_editor_is_owner_only_and_kept(self):
        self.assertTemplateUsed(
            self.client.get(self.profile.get_absolute_url(), {"edit": "1"}),
            "profile.html",
        )
        self.client.force_login(self.user)
        self.assertTemplateUsed(
            self.client.get(self.profile.get_absolute_url(), {"edit": "1"}),
            "profile_manage.html",
        )

    def test_stitch_shortcuts_use_real_categories_and_existing_routes(self):
        response = self.client.get("/", {"lang": "es"})
        self.assertContains(response, 'id="categories"')
        self.assertContains(response, self.category.get_absolute_url() + "?lang=es")
        self.assertContains(response, "?lang=es#categories")
        self.assertContains(response, "Navegación rápida")
        self.assertNotContains(response, 'href="#"')
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertContains(response, self.profile.get_absolute_url() + "?lang=en")

    def test_provider_facts_never_invent_opening_hours(self):
        for path in (self.gig.get_absolute_url(), self.profile.get_absolute_url()):
            response = self.client.get(path)
            self.assertContains(response, 'class="provider-facts"')
            self.assertContains(response, "Not confirmed")
            self.assertNotContains(response, "Open Now")

    def test_no_widget_or_lead_capture_until_review(self):
        response = self.client.get("/")
        self.assertContains(response, 'data-finder-mode="search"')
        self.assertNotContains(response, "loader.v2.js")
        self.assertNotContains(response, "quote-form")

    @override_settings(LINKYOH_WOP_REVIEWED=True, LINKYOH_WOP_WEBSITE_KEY="linkyoh")
    def test_future_mode_requires_exact_https_origin(self):
        factory = RequestFactory()
        with override_settings(
            ALLOWED_HOSTS=["linkyoh.com", "testserver", "preview.linkyoh.com"]
        ):
            self.assertEqual(
                finder_context(factory.get("/", secure=True, HTTP_HOST="linkyoh.com"))[
                    "finder_mode"
                ],
                "conversation",
            )
            self.assertEqual(
                finder_context(factory.get("/", HTTP_HOST="linkyoh.com"))[
                    "finder_mode"
                ],
                "search",
            )
            self.assertEqual(
                finder_context(
                    factory.get("/", secure=True, HTTP_HOST="preview.linkyoh.com")
                )["finder_mode"],
                "search",
            )
            response = self.client.get("/", secure=True, HTTP_HOST="linkyoh.com")
            self.assertContains(response, 'data-wop-key="linkyoh"')
            self.assertContains(response, 'name="q"')

    def test_legacy_routes_and_canonicals_preserved(self):
        for old, obj in (
            (f"/gigs/{self.gig.pk}/", self.gig),
            (f"/profile/{self.user.pk}/", self.profile),
            (f"/category/{self.category.pk}/", self.category),
            (f"/sub-category/{self.plumbing.pk}/", self.plumbing),
        ):
            response = self.client.get(old)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.url, obj.get_absolute_url())
            html = self.client.get(
                obj.get_absolute_url(), {"lang": "es"}
            ).content.decode()
            self.assertIn(
                'rel="canonical" href="https://linkyoh.com' + obj.get_absolute_url(),
                html,
            )
            self.assertEqual(html.count('property="og:image"'), 1)

    def test_like_plain_post_redirects_and_htmx_returns_scoped_partial(self):
        self.client.force_login(self.user)
        response = self.client.post("/like-gig/", {"id": self.gig.pk})
        self.assertRedirects(response, self.gig.get_absolute_url())
        self.assertEqual(self.gig.likes.count(), 1)
        response = self.client.post(
            "/like-gig/", {"id": self.gig.pk}, HTTP_HX_REQUEST="true"
        )
        self.assertTemplateUsed(response, "lab/likes.html")
        self.assertEqual(self.gig.likes.count(), 0)
