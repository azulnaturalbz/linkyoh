from django.urls import path
from . import views_ad

urlpatterns = [
    path('ad/click/<slug:slug>/', views_ad.ad_click, name='ad_click'),
]