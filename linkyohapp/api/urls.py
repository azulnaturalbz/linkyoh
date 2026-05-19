from django.urls import path

from .views import GigImportView

urlpatterns = [
    path('imports/gigs/', GigImportView.as_view(), name='api_import_gig'),
]
