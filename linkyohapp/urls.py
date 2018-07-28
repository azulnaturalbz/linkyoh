from django.urls import path
from django.urls import include
from django.conf.urls import url
from linkyohapp import views

urlpatterns = [
    path('', views.home, name='home'),
    url(r'^gigs/(?P<id>[0-9]+)/$', views.gig_detail, name='gig_detail'),

]

