from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from linkyohapp import views

urlpatterns = [
    path('', views.home, name="home"),
    url(r'^gigs/(?P<id>[0-9]+)/$', views.gig_detail, name='gig_detail'),
    url(r'^my_gigs/$', views.my_gigs, name="my_gigs"),
    url(r'^create_gig/$', views.create_gig, name="create_gig"),
    url(r'^my_gigs/edit/(?P<id>[0-9]+)/$', views.edit_gig, name="edit_gig"),
    url(r'^profile/(?P<pid>[0-9]+)/$', views.profile, name="profile"),
    path('ajax/load-district/', views.load_districts, name="ajax_load_states"),
    path('ajax/load-district/<int:did>/', views.load_districts, name="ajax_load_states"),
    path('ajax/load-location/', views.load_locations, name="ajax_load_locations"),
    path('ajax/load-location/<int:did>/<int:lid>/', views.load_locations, name="ajax_load_locations"),
    path('ajax/load-category/', views.load_categories, name="ajax_load_category"),
    path('ajax/load-category/<int:catid>/', views.load_categories, name="ajax_load_category"),
    path('ajax/load-sub-category/', views.load_sub_categories, name="ajax_load_sub_category"),
    path('ajax/load-sub-category/<int:catid>/', views.load_sub_categories, name="ajax_load_sub_category"),
    path('ajax/load-sub-category/<int:catid>/<int:subcatid>/', views.load_sub_categories, name="ajax_load_sub_category"),
    path('ajax/load-menu-category/', views.load_menu_categories, name="ajax_load_menu_category"),
    url(r'^category/(?P<id>[0-9]+)/$', views.category_listings, name="category_listing"),
    url(r'^sub-category/(?P<id>[0-9]+)/$', views.sub_category_listings, name="sub_category_listing"),
    url(r'^search/$', views.search, name="search"),
    url(r'^terms/$', views.terms, name="terms"),
    url(r'^privacy/$', views.privacy, name="privacy"),
    url(r'^about-us/$', views.about, name="about"),
    url(r'contact-us/$', views.contact, name="contact"),
    url(r'thanks/$', views.thanks, name="thanks"),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    # Password Change
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete')

]
