import json
import re
from urllib.parse import urlencode

from django.conf import settings
from django.templatetags.static import static
from django.utils.html import strip_tags
from django.utils.text import Truncator, slugify


SITE_NAME = 'Linkyoh'
PARENT_ORG_NAME = 'Silvatech'
PARENT_ORG_URL = 'https://silvatech.bz'
DEFAULT_TITLE = 'Linkyoh | Find Services and Local Businesses in Belize'
DEFAULT_DESCRIPTION = (
    'Find local services and businesses across Belize. Browse categories, compare '
    'listings, contact providers, and claim your business on Linkyoh, a Silvatech '
    'product.'
)
DEFAULT_KEYWORDS = (
    'Belize services, local businesses Belize, service providers Belize, Belize '
    'business directory, Linkyoh, Silvatech'
)
DEFAULT_IMAGE_PATH = 'img/linkyoh_banner_web.png'
DEFAULT_LOCALE = 'en_BZ'


def get_site_url():
    site_url = getattr(settings, 'LINKYOH_SITE_URL', 'https://linkyoh.com') or 'https://linkyoh.com'
    if not site_url.startswith(('http://', 'https://')):
        site_url = f'https://{site_url}'
    return site_url.rstrip('/')


def to_absolute_url(path_or_url):
    if not path_or_url:
        return ''

    value = str(path_or_url)
    if value.startswith(('http://', 'https://')):
        return value
    if value.startswith('//'):
        return f'https:{value}'
    if not value.startswith('/'):
        value = f'/{value}'
    return f'{get_site_url()}{value}'


def current_url(request):
    return to_absolute_url(request.path if request else '/')


def default_image_url():
    return to_absolute_url(static(DEFAULT_IMAGE_PATH))


def clean_text(value, max_chars=160):
    text = strip_tags(str(value or ''))
    text = re.sub(r'\s+', ' ', text).strip()
    return Truncator(text).chars(max_chars) if len(text) > max_chars else text


def seo_slug(value, fallback='item'):
    slug = slugify(str(value or ''), allow_unicode=False)
    return slug[:80].strip('-') or fallback


def category_path(category):
    return f'/belize/services/{seo_slug(category.category, "services")}-{category.pk}/'


def subcategory_path(sub_category):
    category_slug = seo_slug(sub_category.category.category, 'services')
    subcategory_slug = seo_slug(sub_category.subcategory, 'category')
    return f'/belize/services/{category_slug}/{subcategory_slug}-{sub_category.pk}/'


def gig_path(gig):
    category_slug = seo_slug(gig.category.category, 'services')
    district_slug = seo_slug(gig.district, 'belize')
    location_slug = seo_slug(gig.location, 'local')
    title_slug = seo_slug(gig.title, 'service')
    return f'/belize/{category_slug}/{district_slug}/{location_slug}/{title_slug}-{gig.pk}/'


def profile_path(profile):
    profile_slug = seo_slug(profile.get_display_name(), 'provider')
    return f'/belize/providers/{profile_slug}-{profile.user_id}/'


def facebook_share_url(url):
    return f'https://www.facebook.com/sharer/sharer.php?{urlencode({"u": url})}'


def json_ld(data):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def organization_schema():
    return {
        '@type': 'Organization',
        '@id': f'{PARENT_ORG_URL}#organization',
        'name': PARENT_ORG_NAME,
        'url': PARENT_ORG_URL,
    }


def website_schema():
    site_url = get_site_url()
    return {
        '@type': 'WebSite',
        '@id': f'{site_url}#website',
        'name': SITE_NAME,
        'url': site_url,
        'description': DEFAULT_DESCRIPTION,
        'publisher': {'@id': f'{PARENT_ORG_URL}#organization'},
        'potentialAction': {
            '@type': 'SearchAction',
            'target': f'{site_url}/search/?param={{search_term_string}}',
            'query-input': 'required name=search_term_string',
        },
    }


def breadcrumb_schema(items):
    return {
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': index,
                'name': name,
                'item': to_absolute_url(path),
            }
            for index, (name, path) in enumerate(items, start=1)
        ],
    }


def graph_schema(*items):
    return json_ld({
        '@context': 'https://schema.org',
        '@graph': [organization_schema(), website_schema(), *items],
    })


def build_seo_context(
    *,
    title,
    description,
    url,
    image=None,
    image_alt=None,
    og_type='website',
    json_ld_payload=None,
    robots='index,follow',
):
    canonical_url = to_absolute_url(url)
    image_url = to_absolute_url(image) if image else default_image_url()
    normalized_title = clean_text(title, 70)
    normalized_description = clean_text(description, 170) or DEFAULT_DESCRIPTION

    context = {
        'seo_title': normalized_title,
        'seo_description': normalized_description,
        'seo_keywords': DEFAULT_KEYWORDS,
        'seo_url': canonical_url,
        'seo_image': image_url,
        'seo_image_alt': clean_text(image_alt or normalized_title, 120),
        'seo_site_name': SITE_NAME,
        'seo_locale': DEFAULT_LOCALE,
        'seo_type': og_type,
        'seo_robots': robots,
        'seo_author': PARENT_ORG_NAME,
        'facebook_share_url': facebook_share_url(canonical_url),
    }
    if json_ld_payload:
        context['seo_json_ld'] = json_ld_payload
    return context


def default_seo_context(request):
    return build_seo_context(
        title=DEFAULT_TITLE,
        description=DEFAULT_DESCRIPTION,
        url=current_url(request),
        image=default_image_url(),
        image_alt='Linkyoh service marketplace in Belize',
        json_ld_payload=graph_schema(),
    )


def home_seo_context(request):
    return build_seo_context(
        title=DEFAULT_TITLE,
        description=DEFAULT_DESCRIPTION,
        url='/',
        image=default_image_url(),
        image_alt='Linkyoh service marketplace in Belize',
        json_ld_payload=graph_schema(
            breadcrumb_schema([
                ('Home', '/'),
            ])
        ),
    )


def category_seo_context(category):
    title = f'{category.category} Services in Belize | Linkyoh'
    description = category.description or (
        f'Browse {category.category} services and local providers across Belize on '
        'Linkyoh, a Silvatech product.'
    )
    return build_seo_context(
        title=title,
        description=description,
        url=category.get_absolute_url(),
        image=category.get_photo_url(),
        image_alt=f'{category.category} services in Belize',
        json_ld_payload=graph_schema(
            {
                '@type': 'CollectionPage',
                '@id': f'{to_absolute_url(category.get_absolute_url())}#collection',
                'name': title,
                'description': clean_text(description, 220),
                'url': to_absolute_url(category.get_absolute_url()),
                'isPartOf': {'@id': f'{get_site_url()}#website'},
            },
            breadcrumb_schema([
                ('Home', '/'),
                (category.category, category.get_absolute_url()),
            ]),
        ),
    )


def subcategory_seo_context(sub_category):
    title = f'{sub_category.subcategory} Services in Belize | Linkyoh'
    description = sub_category.description or (
        f'Find {sub_category.subcategory} providers in Belize under '
        f'{sub_category.category.category} on Linkyoh.'
    )
    return build_seo_context(
        title=title,
        description=description,
        url=sub_category.get_absolute_url(),
        image=sub_category.category.get_photo_url(),
        image_alt=f'{sub_category.subcategory} services in Belize',
        json_ld_payload=graph_schema(
            {
                '@type': 'CollectionPage',
                '@id': f'{to_absolute_url(sub_category.get_absolute_url())}#collection',
                'name': title,
                'description': clean_text(description, 220),
                'url': to_absolute_url(sub_category.get_absolute_url()),
                'isPartOf': {'@id': f'{get_site_url()}#website'},
            },
            breadcrumb_schema([
                ('Home', '/'),
                (sub_category.category.category, sub_category.category.get_absolute_url()),
                (sub_category.subcategory, sub_category.get_absolute_url()),
            ]),
        ),
    )


def gig_seo_context(gig):
    location_label = f'{gig.location}, {gig.district}'
    title = f'{gig.title} in {location_label} | Linkyoh'
    description = (
        f'{gig.title}: {gig.description} {gig.category.category} service in '
        f'{location_label}, Belize.'
    )
    canonical_url = to_absolute_url(gig.get_absolute_url())
    business_schema = {
        '@type': 'LocalBusiness',
        '@id': f'{canonical_url}#business',
        'name': gig.title,
        'description': clean_text(gig.description, 500),
        'url': canonical_url,
        'image': to_absolute_url(gig.get_photo_url()),
        'category': gig.category.category,
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': clean_text(f'{gig.address_1} {gig.address_2}', 160),
            'addressLocality': str(gig.location),
            'addressRegion': str(gig.district),
            'addressCountry': 'BZ',
        },
        'areaServed': 'Belize',
        'parentOrganization': {'@id': f'{PARENT_ORG_URL}#organization'},
    }
    if gig.phone_number:
        business_schema['telephone'] = gig.phone_number
    if gig.call_for_pricing or gig.price == -1:
        business_schema['priceRange'] = 'Call for pricing'
    else:
        business_schema['priceRange'] = f'BZD {gig.price}'

    return build_seo_context(
        title=title,
        description=description,
        url=gig.get_absolute_url(),
        image=gig.get_photo_url(),
        image_alt=f'{gig.title} service listing on Linkyoh',
        og_type='article',
        json_ld_payload=graph_schema(
            business_schema,
            breadcrumb_schema([
                ('Home', '/'),
                (gig.category.category, gig.category.get_absolute_url()),
                (gig.sub_category.subcategory, gig.sub_category.get_absolute_url()),
                (gig.title, gig.get_absolute_url()),
            ]),
        ),
    )


def profile_seo_context(profile):
    display_name = profile.get_display_name()
    location_parts = []
    if profile.location:
        location_parts.append(str(profile.location))
    if profile.district:
        location_parts.append(str(profile.district))
    location_label = ', '.join(location_parts) or 'Belize'

    title = f'{display_name} | Belize Service Provider on Linkyoh'
    if location_parts:
        title = f'{display_name} in {location_label} | Linkyoh'

    description_source = (
        profile.business_description
        or profile.about
        or profile.slogan
        or f'View {display_name} services, contact details, and business profile on Linkyoh.'
    )
    description = (
        f'{display_name}: {description_source} Discover services and local businesses '
        'in Belize on Linkyoh, a Silvatech product.'
    )
    canonical_url = to_absolute_url(profile.get_absolute_url())
    image_url = profile.get_cover_image_url()
    same_as = [
        url for url in (
            profile.website,
            profile.facebook,
            profile.twitter,
            profile.instagram,
            profile.linkedin,
        )
        if url
    ]

    schema_type = 'LocalBusiness' if profile.profile_type == 'business' else 'Person'
    profile_schema = {
        '@type': schema_type,
        '@id': f'{canonical_url}#profile',
        'name': display_name,
        'description': clean_text(description_source, 500),
        'url': canonical_url,
        'image': to_absolute_url(image_url),
        'areaServed': 'Belize',
        'parentOrganization': {'@id': f'{PARENT_ORG_URL}#organization'},
    }
    if same_as:
        profile_schema['sameAs'] = same_as
    if profile.phone_number:
        profile_schema['telephone'] = profile.phone_number
    if profile.location or profile.district or profile.address:
        profile_schema['address'] = {
            '@type': 'PostalAddress',
            'streetAddress': clean_text(profile.address, 160),
            'addressLocality': str(profile.location) if profile.location else '',
            'addressRegion': str(profile.district) if profile.district else '',
            'addressCountry': 'BZ',
        }
    if profile.profile_type == 'business':
        profile_schema['category'] = profile.business_type or 'Local service provider'
        if profile.year_established:
            profile_schema['foundingDate'] = str(profile.year_established)

    return build_seo_context(
        title=title,
        description=description,
        url=profile.get_absolute_url(),
        image=image_url,
        image_alt=f'{display_name} profile on Linkyoh',
        og_type='profile',
        json_ld_payload=graph_schema(
            profile_schema,
            breadcrumb_schema([
                ('Home', '/'),
                (display_name, profile.get_absolute_url()),
            ]),
        ),
    )
