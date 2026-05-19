from xml.etree.ElementTree import Element, SubElement, tostring

from django.utils import timezone

from .models import Category, Gig, Profile, SubCategory
from .seo import to_absolute_url


def _lastmod(value):
    if not value:
        return None
    if hasattr(value, 'date'):
        return timezone.localtime(value).date().isoformat()
    return str(value)


def _add_url(urlset, loc, changefreq='weekly', priority='0.5', lastmod=None):
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = to_absolute_url(loc)
    if lastmod:
        SubElement(url, 'lastmod').text = _lastmod(lastmod)
    SubElement(url, 'changefreq').text = changefreq
    SubElement(url, 'priority').text = priority


def build_sitemap_xml():
    urlset = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    today = timezone.localdate().isoformat()

    static_pages = [
        ('/', 'daily', '1.0'),
        ('/about-us/', 'monthly', '0.6'),
        ('/contact-us/', 'monthly', '0.5'),
        ('/privacy/', 'yearly', '0.3'),
        ('/terms/', 'yearly', '0.3'),
    ]
    for path, changefreq, priority in static_pages:
        _add_url(urlset, path, changefreq=changefreq, priority=priority, lastmod=today)

    for category in Category.objects.order_by('category'):
        _add_url(
            urlset,
            category.get_absolute_url(),
            changefreq='weekly',
            priority='0.8',
            lastmod=category.create_time,
        )

    for sub_category in SubCategory.objects.select_related('category').order_by('category__category', 'subcategory'):
        _add_url(
            urlset,
            sub_category.get_absolute_url(),
            changefreq='weekly',
            priority='0.7',
            lastmod=sub_category.create_time,
        )

    gigs = Gig.objects.filter(status=True).select_related(
        'category', 'sub_category', 'district', 'location'
    ).order_by('-create_time')
    for gig in gigs:
        _add_url(
            urlset,
            gig.get_absolute_url(),
            changefreq='weekly',
            priority='0.9' if gig.featured else '0.7',
            lastmod=gig.create_time,
        )

    profiles = Profile.objects.filter(user__gig__status=True).select_related(
        'user', 'district', 'location'
    ).distinct().order_by('user_id')
    for profile in profiles:
        _add_url(
            urlset,
            profile.get_absolute_url(),
            changefreq='weekly',
            priority='0.6',
            lastmod=today,
        )

    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(urlset, encoding='utf-8')
