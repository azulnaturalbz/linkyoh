from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework.permissions import BasePermission


def get_import_api_key(request):
    """Return the supplied import API key from supported headers."""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.lower().startswith('bearer '):
        return auth_header.split(' ', 1)[1].strip()
    return request.META.get('HTTP_X_LINKYOH_IMPORT_KEY', '').strip()


def has_valid_import_api_key(request):
    configured_key = getattr(settings, 'LINKYOH_IMPORT_API_KEY', '')
    supplied_key = get_import_api_key(request)
    return bool(configured_key and supplied_key and constant_time_compare(configured_key, supplied_key))


class CanImportGig(BasePermission):
    """Allow staff users or trusted API-key import agents to create listings."""

    message = 'Staff authentication or a valid Linkyoh import API key is required.'

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated and user.is_staff:
            return True
        return has_valid_import_api_key(request)
