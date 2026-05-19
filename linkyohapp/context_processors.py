from .seo import default_seo_context


def seo(request):
    return default_seo_context(request)
