from django.urls import path
from django.urls import include
from django.conf.urls import url
from .models import State,Location
from linkyohapp import views

urlpatterns = [
    path('', views.home, name='home'),
    url(r'^gigs/(?P<id>[0-9]+)/$', views.gig_detail, name='gig_detail'),
    url(r'^my_gigs/$', views.my_gigs, name="my_gigs"),
    url(r'^create_gig/$', views.create_gig, name="create_gig"),
    url(r'^my_gigs/edit/(?P<id>[0-9]+)/$', views.edit_gig, name="edit_gig"),
    url(r'^profile/(?P<username>\w+)/$', views.profile, name='profile'),
    path('ajax/load-location/', views.load_locations, name='ajax_load_locations'),
    path('ajax/load-category/', views.load_categories, name='ajax_load_category'),
    path('ajax/load-sub-category/', views.load_sub_categories, name='ajax_load_sub_category'),


]

