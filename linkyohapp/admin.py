from django.contrib import admin
from .models import Profile, Gig
# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Gig)
class ProfileAdmin(admin.ModelAdmin):
    pass