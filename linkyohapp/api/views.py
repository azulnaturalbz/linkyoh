from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from linkyohapp.models import Profile

from .permissions import CanImportGig, has_valid_import_api_key
from .serializers import ImportedGigSerializer


class GigImportView(APIView):
    """Create claimable business listings from trusted AI/admin imports."""

    permission_classes = [CanImportGig]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        serializer = ImportedGigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        duplicate, reason = serializer.find_duplicate()
        if duplicate:
            return Response(
                self._response_payload(
                    request,
                    duplicate,
                    status_label='duplicate',
                    warnings=[f'Existing listing matched by {reason}.'],
                ),
                status=status.HTTP_200_OK,
            )

        import_user = self._get_listing_owner(request)
        gig = serializer.save(user=import_user, imported_by=request.user if request.user.is_authenticated else import_user)
        return Response(
            self._response_payload(request, gig, status_label='created'),
            status=status.HTTP_201_CREATED,
        )

    def _get_listing_owner(self, request):
        if request.user.is_authenticated and request.user.is_staff and not has_valid_import_api_key(request):
            return request.user

        username = getattr(settings, 'LINKYOH_IMPORT_USER_USERNAME', 'linkyoh-ai-admin')
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@linkyoh.local',
                'first_name': 'Linkyoh',
                'last_name': 'AI Admin',
                'is_staff': True,
                'is_active': True,
            },
        )
        update_fields = []
        if not user.is_staff:
            user.is_staff = True
            update_fields.append('is_staff')
        if not user.is_active:
            user.is_active = True
            update_fields.append('is_active')
        if update_fields:
            user.save(update_fields=update_fields)

        profile, _ = Profile.objects.get_or_create(user=user)
        profile_updates = []
        if profile.profile_type != 'business':
            profile.profile_type = 'business'
            profile_updates.append('profile_type')
        if profile.company_name != 'Linkyoh AI Admin':
            profile.company_name = 'Linkyoh AI Admin'
            profile_updates.append('company_name')
        if profile.slogan != 'AI-assisted business listing curator for Belize':
            profile.slogan = 'AI-assisted business listing curator for Belize'
            profile_updates.append('slogan')
        if profile_updates:
            profile.save(update_fields=profile_updates)

        return user

    def _response_payload(self, request, gig, status_label, warnings=None):
        canonical_url = request.build_absolute_uri(gig.get_absolute_url())
        claim_url = request.build_absolute_uri(reverse('claim_gig', kwargs={'gig_id': gig.id}))
        return {
            'id': gig.id,
            'status': status_label,
            'active': gig.status,
            'canonical_url': canonical_url,
            'claim_url': claim_url,
            'image_url': request.build_absolute_uri(gig.get_photo_url()),
            'warnings': warnings or [],
        }
