"""Fixed ecosystem navigation, separate from canonical schema identities."""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django import template
from django.utils.translation import get_language

from linkyohapp.ecosystem import SISTER_URLS

register = template.Library()
DESTINATIONS = dict(zip(
    ('hub', 'visitbelize', 'chillbout', 'linkyoh', 'marketday', 'wop',
     'payments', 'consulta', 'logistics', 'games'),
    SISTER_URLS,
))
QUERY_LOCALES = {'visitbelize', 'linkyoh', 'wop', 'consulta', 'logistics'}
PLACEMENTS = {'strip', 'forward', 'powered_by'}


@register.simple_tag
def ecosystem_url(destination, placement='strip'):
    if placement not in PLACEMENTS:
        raise ValueError('Unknown ecosystem placement')
    url = urlsplit(DESTINATIONS[destination])
    language = 'es' if (get_language() or 'en').split('-')[0] == 'es' else 'en'
    query = dict(parse_qsl(url.query, keep_blank_values=True))
    if destination in QUERY_LOCALES:
        query['lang'] = language
    query.update(utm_source='linkyoh', utm_medium='ecosystem', utm_campaign=placement)
    path = '/es/' if destination == 'hub' and language == 'es' else url.path
    return urlunsplit((url.scheme, url.netloc, path, urlencode(query), url.fragment))
