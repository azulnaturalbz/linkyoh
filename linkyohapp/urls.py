from django.urls import path, include
from django.contrib.auth import views as auth_views

from linkyohapp import views

urlpatterns = [
    # Ad system
    path('ads/', include('linkyohapp.urls_ad')),

    # Home and listings
    path('', views.home, name="home"),
    path('gigs/<int:id>/', views.gig_detail, name='gig_detail'),
    path('my-gigs/', views.my_gigs, name="my_gigs"),
    path('create-gig/', views.create_gig, name="create_gig"),
    path('my-gigs/edit/<int:id>/', views.edit_gig, name="edit_gig"),
    path('gigs/<int:gig_id>/claim/', views.claim_gig, name="claim_gig"),
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
    path('track-event/', views.track_event, name="track_event"),

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

    # Help pages
    path('help/', views.help_center, name="help_center"),
    path('help/add-gig/', views.help_add_gig, name="help_add_gig"),
    path('help/search/', views.help_search, name="help_search"),
    path('help/profile/', views.help_profile, name="help_profile"),
    path('help/dashboard/', views.help_dashboard, name="help_dashboard"),
    path('help/metrics/', views.help_metrics, name="help_metrics"),
    path('help/faq/', views.help_faq, name="help_faq"),

    # Authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('verify-phone/', views.verify_phone, name='verify_phone'),
    path('resend-code/', views.resend_code, name='resend_code'),

    # Password Change
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Messaging System
    path('messages/', views.messages_index, name='conversation_list'),
    path('messages/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('messages/new/', views.start_conversation, name='create_conversation'),
    path('messages/new/user/<int:recipient_id>/', views.start_conversation, name='create_conversation_with_user'),
    path('messages/new/gig/<int:gig_id>/', views.start_conversation, name='create_conversation_about_gig'),
    path('messages/new/user/<int:recipient_id>/gig/<int:gig_id>/', views.start_conversation, name='create_conversation_with_user_about_gig'),
    path('messages/<int:pk>/delete/', views.delete_conversation, name='delete_conversation'),

    # HTMX endpoints for messaging
    path('messages/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('messages/<int:conversation_id>/upload/', views.upload_message_file, name='upload_message_file'),
    path('messages/search-gigs/', views.search_gigs_for_mention, name='search_gigs_for_mention'),
]
