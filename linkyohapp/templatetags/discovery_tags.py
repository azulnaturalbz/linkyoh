from django import template
from django.utils.translation import gettext

register = template.Library()


@register.simple_tag
def listing_checks(gig):
    from linkyohapp.discovery import checked_record

    return checked_record(getattr(gig.user, "profile", None), gig)


@register.filter
def taxonomy_label(value):
    """Translate reviewed taxonomy labels, never provider-authored facts."""
    return gettext(str(value))


@register.filter
def category_icon(value):
    """Known Lucide names only; category records remain the source of labels."""
    return {
        "housing & construction": "house",
        "services": "briefcase-business",
        "autos": "car-front",
        "health": "heart-pulse",
        "pets": "paw-print",
    }.get(str(value).casefold(), "layout-grid")
