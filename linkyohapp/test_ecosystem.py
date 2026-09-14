import ipaddress
import json
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from unittest import skipUnless
from unittest.mock import patch
from urllib.robotparser import RobotFileParser

import redis
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import resolve

from .directory_limits import DirectoryRateLimitMiddleware, client_address
from .ecosystem import PUBLIC_CRAWL_AGENTS, SISTER_URLS
from .models import Category, Country, District, Gig, GigServiceArea, Local, LocalType, Location, Profile, SubCategory
from .seo import gig_seo_context, profile_seo_context


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs))


class EcosystemPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        country = Country.objects.create(country_name='Belize')
        cls.district = District.objects.create(country=country, district_name='Cayo')
        local = Local.objects.create(local_name='San Ignacio', local_district=cls.district)
        local_type = LocalType.objects.create(local_type_name='Town')
        cls.location = Location.objects.create(local=local, local_type=local_type)
        cls.category = Category.objects.create(category='Home Services', short_category='Home')
        cls.subcategory = SubCategory.objects.create(category=cls.category, subcategory='Plumbing', sub_short_category='Plumb')
        cls.user = User.objects.create_user(username='synthetic-provider', first_name='Example', last_name='Provider')
        cls.profile = Profile.objects.create(user=cls.user, profile_type='business', company_name='Example Plumbing', district=cls.district, location=cls.location)
        cls.gig = Gig.objects.create(title='Example Plumbing', description='Synthetic test service.', category=cls.category, sub_category=cls.subcategory, district=cls.district, location=cls.location, user=cls.user, address_1='Example address', call_for_pricing=True)

    def test_public_pages_have_strip_marks_and_contextual_banner(self):
        for url in ('/', self.profile.get_absolute_url(), self.gig.get_absolute_url()):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                self.assertIn('aria-label="Silvatech ecosystem"', html)
                self.assertIn('Powered by Silvatech&trade;', html)
                from django.utils.html import strip_tags
                self.assertIn('Sell what you make. Open your own store on MarketDay', strip_tags(html))
                self.assertIn('trademarks of Silvatech, Belize City, Belize.', html)
                parser = LinkParser()
                parser.feed(html)
                ecosystem = [link for link in parser.links if link.get('href', '').startswith(SISTER_URLS)]
                self.assertEqual(len(ecosystem), 9)  # seven strip, forward, powered-by
                for link in ecosystem:
                    self.assertIn('utm_source=linkyoh', link['href'])
                    self.assertIn('utm_medium=ecosystem', link['href'])
                    self.assertTrue(link['data-track'].endswith('_clickout'))
                    self.assertNotIn('chillbout.com', link['href'])
                    self.assertNotIn('belizelogistics.com', link['href'])

    def test_llms_is_public_text_with_only_discovery_contract(self):
        response = self.client.get('/llms.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/plain', response['Content-Type'])
        self.assertContains(response, '## Related products')
        self.assertContains(response, 'https://linkyoh.com/sitemap.xml')
        self.assertNotContains(response, 'LYIMPORT_API_KEY')
        self.assertEqual(self.client.head('/llms.txt').status_code, 200)
        self.assertEqual(self.client.post('/llms.txt').status_code, 405)

    def test_named_crawlers_keep_private_exclusions(self):
        response = self.client.get('/robots.txt')
        robot = RobotFileParser()
        robot.parse(response.content.decode().splitlines())
        for agent in (*PUBLIC_CRAWL_AGENTS, 'Googlebot'):
            self.assertTrue(robot.can_fetch(agent, self.gig.get_absolute_url()))
            for path in ('/api/v1/imports/gigs/', '/admin/', '/messages/', '/my-gigs/', '/reset/token/'):
                self.assertFalse(robot.can_fetch(agent, path), (agent, path))
        for agent in ('CCBot', 'Bytespider', 'HTTrack', 'WebCopier', 'WebZIP'):
            self.assertFalse(robot.can_fetch(agent, '/'))

    def test_service_metadata_uses_recorded_areas_and_omits_private_data(self):
        other_local = Local.objects.create(local_name='Belmopan', local_district=self.district)
        other_location = Location.objects.create(local=other_local, local_type=self.location.local_type)
        GigServiceArea.objects.create(gig=self.gig, district=self.district, location=other_location)
        graph = json.loads(gig_seo_context(self.gig)['seo_json_ld'])['@graph']
        organization = next(item for item in graph if item['@type'] == 'Organization')
        self.assertEqual(organization['sameAs'], list(SISTER_URLS))
        business = next(item for item in graph if item['@type'] == 'LocalBusiness')
        service = next(item for item in graph if item['@type'] == 'Service')
        self.assertNotIn('parentOrganization', business)
        self.assertEqual(service['provider']['@id'], business['@id'])
        self.assertEqual(len(service['areaServed']), 2)
        self.assertNotIn('offers', service)
        self.assertNotIn('is_verified', json.dumps(graph))
        self.assertNotIn('raw_payload', json.dumps(graph))

    def test_profile_services_and_person_type_do_not_invent_business_or_coverage(self):
        graph = json.loads(profile_seo_context(self.profile, [self.gig])['seo_json_ld'])['@graph']
        provider = next(item for item in graph if item['@type'] == 'LocalBusiness')
        service = next(item for item in graph if item['@type'] == 'Service')
        self.assertEqual(service['provider']['@id'], provider['@id'])
        self.assertNotIn('areaServed', provider)
        self.profile.profile_type = 'individual'
        graph = json.loads(profile_seo_context(self.profile)['seo_json_ld'])['@graph']
        self.assertTrue(any(item['@type'] == 'Person' for item in graph))
        self.assertFalse(any(item['@type'] == 'LocalBusiness' for item in graph))

    def test_json_ld_cannot_close_script_from_provider_content(self):
        self.gig.description = '</script><script>alert(1)</script>'
        serialized = gig_seo_context(self.gig)['seo_json_ld']
        self.assertNotIn('</script>', serialized)
        json.loads(serialized)

    @skipUnless(os.environ.get('LINKYOH_TEST_REDIS_URL'), 'Requires isolated test Redis')
    def test_http_directory_limit_honors_proxy_identity_and_preserves_text_endpoints(self):
        with override_settings(
            LINKYOH_DIRECTORY_RATE_LIMIT_ENABLED=True,
            LINKYOH_RATE_LIMIT_REDIS_URL=os.environ['LINKYOH_TEST_REDIS_URL'],
            LINKYOH_TRUSTED_PROXY_NETWORKS=['172.30.0.0/24'],
            LINKYOH_DIRECTORY_RATE_WINDOWS=((2, 10), (4, 60)),
            SECRET_KEY=uuid.uuid4().hex,
        ):
            headers = {'REMOTE_ADDR': '172.30.0.2', 'HTTP_X_FORWARDED_FOR': '203.0.113.10'}
            self.assertEqual(self.client.get('/', **headers).status_code, 200)
            self.assertEqual(self.client.get(self.profile.get_absolute_url(), **headers).status_code, 200)
            headers['HTTP_X_FORWARDED_FOR'] = 'spoofed, 203.0.113.10'
            self.assertEqual(self.client.get(self.gig.get_absolute_url(), **headers).status_code, 429)
            self.assertEqual(self.client.get('/llms.txt', **headers).status_code, 200)
            headers['HTTP_X_FORWARDED_FOR'] = '203.0.113.11'
            self.assertEqual(self.client.get('/', **headers).status_code, 200)


class ClientAddressTests(SimpleTestCase):
    def test_untrusted_forwarded_headers_are_ignored(self):
        request = RequestFactory().get('/', REMOTE_ADDR='198.51.100.3', HTTP_X_FORWARDED_FOR='203.0.113.99')
        self.assertEqual(client_address(request, (ipaddress.ip_network('172.30.0.0/24'),)), '198.51.100.3')

    def test_trusted_proxy_uses_rightmost_client_and_normalizes_ipv6(self):
        request = RequestFactory().get('/', REMOTE_ADDR='172.30.0.2', HTTP_X_FORWARDED_FOR='spoofed, ::ffff:203.0.113.8')
        self.assertEqual(client_address(request, (ipaddress.ip_network('172.30.0.0/24'),)), '203.0.113.8')


@skipUnless(os.environ.get('LINKYOH_TEST_REDIS_URL'), 'Requires isolated test Redis')
class DirectoryRateLimitTests(SimpleTestCase):
    def setUp(self):
        self.config = override_settings(
            LINKYOH_DIRECTORY_RATE_LIMIT_ENABLED=True,
            LINKYOH_RATE_LIMIT_REDIS_URL=os.environ['LINKYOH_TEST_REDIS_URL'],
            LINKYOH_TRUSTED_PROXY_NETWORKS=['172.30.0.0/24'],
            LINKYOH_DIRECTORY_RATE_WINDOWS=((3, 10), (5, 60)),
            SECRET_KEY=uuid.uuid4().hex,
        )
        self.config.enable()
        self.addCleanup(self.config.disable)
        self.middleware = DirectoryRateLimitMiddleware(lambda request: HttpResponse('ok'))

    def request(self, path='/', ip='203.0.113.8', method='get', forwarded=''):
        request = getattr(RequestFactory(), method)(path, REMOTE_ADDR=ip, HTTP_X_FORWARDED_FOR=forwarded)
        request.resolver_match = resolve(path)
        return request

    def hit(self, request, middleware=None):
        return (middleware or self.middleware).process_view(request, None, (), {})

    def test_limit_shared_across_workers_and_routes_with_retry_headers(self):
        second_worker = DirectoryRateLimitMiddleware(lambda request: HttpResponse('ok'))
        for path in ('/', '/search/', '/gigs/1/'):
            self.assertIsNone(self.hit(self.request(path)))
        response = self.hit(self.request('/category/1/'), second_worker)
        self.assertEqual(response.status_code, 429)
        self.assertGreater(int(response['Retry-After']), 0)
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertIsNone(self.hit(self.request(ip='203.0.113.9')))

    def test_concurrent_calls_cannot_exceed_burst(self):
        def hit(_):
            response = self.hit(self.request())
            return response.status_code if response is not None else 200
        with ThreadPoolExecutor(max_workers=8) as pool:
            statuses = list(pool.map(hit, range(12)))
        self.assertEqual(statuses.count(200), 3)
        self.assertEqual(statuses.count(429), 9)

    @override_settings(LINKYOH_DIRECTORY_RATE_WINDOWS=((3, 1), (5, 3)))
    def test_window_expiry_preserves_longer_limit_then_recovers(self):
        middleware = DirectoryRateLimitMiddleware(lambda request: HttpResponse('ok'))
        for _ in range(3):
            self.assertIsNone(self.hit(self.request(), middleware))
        self.assertEqual(self.hit(self.request(), middleware).status_code, 429)
        time.sleep(1.1)
        for _ in range(2):
            self.assertIsNone(self.hit(self.request(), middleware))
        self.assertEqual(self.hit(self.request(), middleware).status_code, 429)
        time.sleep(2.1)
        self.assertIsNone(self.hit(self.request(), middleware))

    def test_post_accounts_api_and_assets_are_not_limited(self):
        with patch.object(self.middleware.redis, 'eval', side_effect=AssertionError('Redis must not be used')):
            for path in ('/login/', '/api/v1/imports/gigs/', '/robots.txt', '/llms.txt', '/sitemap.xml'):
                self.assertIsNone(self.hit(self.request(path)))
            self.assertIsNone(self.hit(self.request(method='post')))

    def test_head_and_crawler_user_agents_do_not_bypass_limits(self):
        for _ in range(3):
            self.hit(self.request())
        request = self.request(method='head')
        request.META['HTTP_USER_AGENT'] = 'Googlebot'
        self.assertEqual(self.hit(request).status_code, 429)

    def test_cache_failure_is_bounded_and_does_not_bypass(self):
        with patch.object(self.middleware.redis, 'eval', side_effect=redis.ConnectionError('private connection details')):
            response = self.hit(self.request())
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response['Retry-After'], '5')
        self.assertNotIn(b'private', response.content)
