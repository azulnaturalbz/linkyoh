from django.urls import path
from django.urls import include
from django.conf.urls import url
from linkyohapp import views

urlpatterns = [
    path('', views.home, name='home'),
    url(r'^gigs/(?P<id>[0-9]+)/$', views.gig_detail, name='gig_detail'),
    # path('social/', include('social_django.urls', namespace='social')),
    # path('auth/', include('django.contrib.auth.urls', namespace='auth')),
]

