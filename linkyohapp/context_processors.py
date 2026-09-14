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
    context = {
        "discovery_language": translation.get_language()[:2],
        **links,
        **finder_context(request),
    }
    route = getattr(request.resolver_match, "url_name", "")
    if route in ("create_gig", "edit_gig") or (
        route == "profile"
        and (request.GET.get("edit") == "1" or request.method == "POST")
    ):
        from .models import Category, SubCategory, District, Location

        context.update(
            {
                "reference_categories": Category.objects.order_by("category"),
                "reference_subcategories": SubCategory.objects.select_related(
                    "category"
                ).order_by("category__category", "subcategory"),
                "reference_districts": District.objects.order_by("district_name"),
                "reference_locations": Location.objects.select_related(
                    "local__local_district"
                ).order_by("local__local_district__district_name", "local__local_name"),
            }
        )
    return context
