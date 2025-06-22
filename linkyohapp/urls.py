from django.urls import path
from django.contrib.auth import views as auth_views

from linkyohapp import views

urlpatterns = [
    # Home and listings
    path('', views.home, name="home"),
    path('gigs/<int:id>/', views.gig_detail, name='gig_detail'),
    path('my-gigs/', views.my_gigs, name="my_gigs"),
    path('create-gig/', views.create_gig, name="create_gig"),
    path('my-gigs/edit/<int:id>/', views.edit_gig, name="edit_gig"),
    path('profile/<int:pid>/', views.profile, name="profile"),

    # AJAX endpoints
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

    # AJAX endpoints for search filters
    path('ajax/subcategories/', views.ajax_load_subcategories, name="ajax_load_subcategories"),
    path('ajax/locations/', views.ajax_load_locations, name="ajax_load_locations_search"),
    path('like-gig/', views.like_gig, name="like_gig"),
    path('toggle-qr-code/', views.toggle_qr_code, name="toggle_qr_code"),

    # Category and search
    path('category/<int:id>/', views.category_listings, name="category_listing"),
    path('sub-category/<int:id>/', views.sub_category_listings, name="sub_category_listing"),
    path('search/', views.search, name="search"),

    # Static pages
    path('terms/', views.terms, name="terms"),
    path('privacy/', views.privacy, name="privacy"),
    path('about-us/', views.about, name="about"),
    path('contact-us/', views.contact, name="contact"),
    path('thanks/', views.thanks, name="thanks"),

    # Authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # Password Change
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete')
]
