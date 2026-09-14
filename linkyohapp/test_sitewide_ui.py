"""Sitewide presentation contracts; no external accounts, messages or sends."""

from pathlib import Path

from django.template.loader import get_template
from django.test import TestCase
from django.urls import reverse

from .discovery import SmartSearch
from .models import Category, Conversation, Gig, Local, Location, Message, SubCategory
from .test_lab_ui import seed_lab_data


class SitewideUITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data = seed_lab_data()

    def test_every_template_compiles(self):
        root = Path(__file__).parent / "templates"
        for path in root.rglob("*.html"):
            with self.subTest(template=path.name):
                get_template(str(path.relative_to(root)))

    def test_shared_shell_on_public_pages(self):
        for name in (
            "home",
            "login",
            "register",
            "password_reset",
            "about",
            "contact",
            "help_center",
            "help_search",
            "help_faq",
            "terms",
            "privacy",
        ):
            for language in ("en", "es"):
                with self.subTest(page=name, language=language):
                    response = self.client.get(reverse(name), {"lang": language})
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, "lab/sitewide.css")
                    self.assertContains(response, "linkyoh-stitch-wordmark.png")
                    self.assertContains(response, "svt-ecosystem-strip")
                    self.assertContains(response, '<html lang="%s">' % language)
                    self.assertNotContains(response, "css/offcanvas.css")
                    self.assertNotContains(response, "data-wop-key=")

    def test_authenticated_surfaces_and_notification_content(self):
        self.client.force_login(self.data["user"])
        for name in (
            "create_gig",
            "my_gigs",
            "messaging_unified",
            "notification_list",
            "password_change",
        ):
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "lab/sitewide.css")
                self.assertContains(response, 'action="/logout/"')
        response = self.client.get(reverse("notification_list"))
        self.assertContains(response, "No notifications yet")

    def test_form_reference_options_exist_without_javascript(self):
        self.client.force_login(self.data["user"])
        response = self.client.get(reverse("create_gig"))
        self.assertContains(response, '<optgroup label="Housing &amp; Construction">')
        self.assertContains(response, ">Plumbing</option>")
        self.assertContains(response, ">San Ignacio</option>")
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_edit_keeps_selected_reference_ids(self):
        self.client.force_login(self.data["user"])
        response = self.client.get(reverse("edit_gig", args=[self.data["gig"].pk]))
        self.assertContains(response, "selected>Plumbing</option>")
        self.assertContains(response, "selected>San Ignacio</option>")

    def test_edit_permissions_unchanged(self):
        self.client.force_login(self.data["unknown"])
        response = self.client.get(reverse("edit_gig", args=[self.data["gig"].pk]))
        self.assertEqual(response.status_code, 302)
        self.assertNotContains(self.client.get(response.url), 'id="gigForm"')

    def test_spanish_account_copy(self):
        response = self.client.get(reverse("login"), {"lang": "es"})
        self.assertContains(response, "Bienvenido de nuevo")
        self.assertContains(response, "Nombre de usuario")

    def test_invalid_listing_keeps_input_and_shows_errors(self):
        self.client.force_login(self.data["user"])
        count = Gig.objects.count()
        response = self.client.post(
            reverse("create_gig"),
            {"title": "Keep this title", "description": "Keep this description"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'role="alert"')
        self.assertContains(response, 'value="Keep this title"')
        self.assertContains(response, "Keep this description</textarea>")
        self.assertEqual(Gig.objects.count(), count)

    def test_native_and_htmx_first_message_keep_separate_response_contracts(self):
        self.client.force_login(self.data["user"])
        url = (
            reverse("send_first_message")
            + "?recipient_id="
            + str(self.data["unknown"].pk)
        )
        for htmx in (False, True):
            with self.subTest(htmx=htmx):
                response = self.client.post(
                    url,
                    {"content": "Synthetic test message"},
                    **({"HTTP_HX_REQUEST": "true"} if htmx else {})
                )
                self.assertEqual(response.status_code, 204 if htmx else 302)
                target = response.get("HX-Redirect") if htmx else response.url
                self.assertIn("/messaging/", target)
        self.assertEqual(
            Message.objects.filter(content="Synthetic test message").count(), 2
        )

    def test_actual_production_labels_resolve_short_place_names(self):
        SubCategory.objects.filter(pk=self.data["plumbing"].pk).update(
            subcategory="Plumber"
        )
        Local.objects.filter(pk=self.data["san_ignacio"].local_id).update(
            local_name="San Ignacio and Santa Elena Town"
        )
        Local.objects.filter(pk=self.data["belmopan"].local_id).update(
            local_name="Belmopan City"
        )
        for query, location in (
            ("Plomero en San Ignacio", self.data["san_ignacio"]),
            ("Plumber in Santa Elena", self.data["san_ignacio"]),
            ("Plomero en Belmopán", self.data["belmopan"]),
        ):
            with self.subTest(query=query):
                search = SmartSearch({"q": query})
                self.assertFalse(search.issues)
                self.assertEqual(search.selected["location"].pk, location.pk)
                self.assertEqual(
                    search.selected["subcategory"].pk, self.data["plumbing"].pk
                )
                self.assertEqual(list(search.queryset()), [self.data["gig"]])
