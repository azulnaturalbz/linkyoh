from .seo import default_seo_context


def seo(request):
    return default_seo_context(request)


def discovery(request):
    from django.utils import translation
    from .discovery import finder_context

    allowed = (
        "q",
        "param",
        "category",
        "subcategory",
        "district",
        "location",
        "town",
        "min_price",
        "max_price",
        "page",
        "edit",
    )
    params = request.GET.copy()
    for key in list(params):
        if key not in allowed:
            del params[key]
    links = {}
    for language in ("en", "es"):
        params["lang"] = language
        links["language_" + language + "_url"] = request.path + "?" + params.urlencode()
    return {
        "discovery_language": translation.get_language()[:2],
        **links,
        **finder_context(request),
    }
