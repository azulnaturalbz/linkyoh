from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.html import escape
from rest_framework.test import APIClient
from PIL import Image

from .models import (
    Category,
    Country,
    District,
    Gig,
    ImportedGigSource,
    Local,
    LocalType,
    Location,
    Profile,
    SubCategory,
)


class GigImportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.country = Country.objects.create(country_name='Belize')
        self.district = District.objects.create(country=self.country, district_name='Belize')
        self.other_district = District.objects.create(country=self.country, district_name='Cayo')
        self.local_type = LocalType.objects.create(local_type_name='City')
        self.local = Local.objects.create(local_name='Belize City', local_district=self.district)
        self.location = Location.objects.create(local=self.local, local_type=self.local_type)
        self.other_local = Local.objects.create(local_name='San Ignacio', local_district=self.other_district)
        self.other_location = Location.objects.create(local=self.other_local, local_type=self.local_type)
        self.category = Category.objects.create(category='Services', short_category='Svc')
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            subcategory='Repairs',
            sub_short_category='Rep',
        )
        self.other_category = Category.objects.create(category='Health', short_category='Health')
        self.other_subcategory = SubCategory.objects.create(
            category=self.other_category,
            subcategory='Clinics',
            sub_short_category='Clin',
        )
        self.staff_user = User.objects.create_user(
            username='staff@example.com',
            email='staff@example.com',
            password='password',
            is_staff=True,
        )
        Profile.objects.create(user=self.staff_user)
        self.url = reverse('api_import_gig')

    def payload(self, **overrides):
        data = {
            'title': 'Luigi Repairs',
            'description': 'Appliance and home repair services in Belize City.',
            'category_id': self.category.id,
            'sub_category_id': self.subcategory.id,
            'district_id': self.district.id,
            'location_id': self.location.id,
            'address_1': 'Downtown Belize City',
            'phone_number': '6000000',
            'call_for_pricing': True,
            'source_url': 'https://www.facebook.com/luigi-repairs',
            'source_notes': 'Imported from supplied business ad.',
        }
        data.update(overrides)
        return data

    def test_import_requires_staff_or_api_key(self):
        response = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gig.objects.count(), 0)

    @override_settings(LINKYOH_IMPORT_API_KEY='test-key', LINKYOH_IMPORT_USER_USERNAME='linkyoh-ai-admin-test')
    def test_api_key_import_creates_claimable_staff_owned_listing(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer test-key')

        response = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(response.status_code, 201)
        gig = Gig.objects.get()
        self.assertTrue(gig.user.is_staff)
        self.assertEqual(gig.user.username, 'linkyoh-ai-admin-test')
        self.assertEqual(gig.phone_number, '+5016000000')
        self.assertTrue(gig.status)
        self.assertEqual(ImportedGigSource.objects.get(gig=gig).source_url, self.payload()['source_url'])
        self.assertIn(gig.get_absolute_url(), response.data['canonical_url'])
        self.assertIn(reverse('claim_gig', kwargs={'gig_id': gig.id}), response.data['claim_url'])
        self.assertEqual(response.data['status'], 'created')

    def test_staff_import_validates_subcategory_relationship(self):
        self.client.force_authenticate(user=self.staff_user)
        data = self.payload(sub_category_id=self.other_subcategory.id)

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('sub_category_id', response.data)

    def test_staff_import_validates_location_relationship(self):
        self.client.force_authenticate(user=self.staff_user)
        data = self.payload(location_id=self.other_location.id)

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('location_id', response.data)

    def test_staff_import_detects_duplicate_source_url(self):
        self.client.force_authenticate(user=self.staff_user)
        first = self.client.post(self.url, self.payload(), format='json')
        second = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.data['status'], 'duplicate')
        self.assertEqual(Gig.objects.count(), 1)

    def test_staff_import_supports_image_upload(self):
        self.client.force_authenticate(user=self.staff_user)
        buffer = BytesIO()
        Image.new('RGB', (4, 4), color='teal').save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        image = SimpleUploadedFile('listing.png', image_bytes, content_type='image/png')
        data = self.payload(source_url='https://example.com/listing-image', image=image)

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, 201)
        gig = Gig.objects.get()
        self.assertTrue(gig.photo.name)
        self.assertIn('/media/', response.data['image_url'])


class ProfileSeoUrlTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='belize-builder',
            email='builder@example.com',
            password='password',
            first_name='Belize',
            last_name='Builder',
        )
        self.profile = Profile.objects.create(
            user=self.user,
            profile_type='business',
            company_name='Belize Builder Services',
            slogan='Construction and repairs across Belize.',
            business_description='Reliable construction, repairs, and maintenance services.',
        )

    def test_profile_has_canonical_provider_url(self):
        self.assertEqual(
            self.profile.get_absolute_url(),
            f'/belize/providers/belize-builder-services-{self.user.id}/',
        )

    def test_legacy_numeric_profile_redirects_to_canonical_url(self):
        response = self.client.get(reverse('profile_legacy', kwargs={'pid': self.user.id}))

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], self.profile.get_absolute_url())

    @override_settings(LINKYOH_SITE_URL='http://testserver')
    def test_profile_renders_profile_seo_metadata(self):
        response = self.client.get(self.profile.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn(f'<link rel="canonical" href="http://testserver{self.profile.get_absolute_url()}">', html)
        self.assertIn(
            escape('Belize Builder Services | Belize Service Provider on Linkyoh'),
            html,
        )
        self.assertIn('og:image', html)
