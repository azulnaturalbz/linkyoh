from django.contrib import admin
from .models import Profile, Gig, Country, State, Local, LocalType, Location, Category,SubCategory,Review, Rating


# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Gig)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Country)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(State)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Local)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(LocalType)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(SubCategory)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    pass

