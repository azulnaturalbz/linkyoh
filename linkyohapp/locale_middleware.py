from django.middleware.locale import LocaleMiddleware


class DiscoveryLocaleMiddleware(LocaleMiddleware):
    """Allow shareable bilingual pages without changing existing canonical paths."""

    def process_request(self, request):
        language = request.GET.get("lang")
        if language in ("en", "es"):
            request.COOKIES["django_language"] = language
        super().process_request(request)
