from django.contrib import admin
from .models import Profile, Gig, Country, District, Local, LocalType, Location, Category,SubCategory,Review, Rating,Contact


# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'profile_type', 'is_verified', 'phone_number', 'district')
    list_filter = ('profile_type', 'is_verified', 'gender', 'district')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number', 'company_name')
    actions = ['verify_profiles', 'unverify_profiles']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar', 'gender', 'profile_type', 'is_verified')
        }),
        ('Basic Information', {
            'fields': ('slogan', 'about')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email_public', 'address', 'district', 'location')
        }),
        ('Social Media', {
            'fields': ('website', 'facebook', 'twitter', 'instagram', 'linkedin'),
            'classes': ('collapse',)
        }),
        ('Business Information', {
            'fields': ('company_name', 'business_type', 'year_established', 'business_description'),
            'classes': ('collapse',),
            'description': 'These fields are only relevant for business profiles'
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Name'

    def verify_profiles(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} profiles have been verified.')
    verify_profiles.short_description = 'Mark selected profiles as verified'

    def unverify_profiles(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} profiles have been unverified.')
    unverify_profiles.short_description = 'Mark selected profiles as unverified'


@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'sub_category', 'price', 'status', 'featured', 'create_time')
    list_filter = ('status', 'category', 'district', 'featured', 'featured_in_category', 'featured_in_subcategory', 'featured_in_location', 'featured_in_district')
    search_fields = ('title', 'description', 'user__username', 'user__email')
    actions = ['approve_gigs', 'disapprove_gigs', 'feature_gigs', 'unfeature_gigs']
    date_hierarchy = 'create_time'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'price', 'status')
        }),
        ('Categories', {
            'fields': ('category', 'sub_category')
        }),
        ('Location', {
            'fields': ('district', 'location')
        }),
        ('Media', {
            'fields': ('photo',)
        }),
        ('Featured Status', {
            'fields': ('featured', 'featured_in_category', 'featured_in_subcategory', 'featured_in_location', 'featured_in_district'),
            'description': 'Control where this gig appears as featured. Featured gigs appear at the top of listings and have a special badge.'
        }),
    )

    def approve_gigs(self, request, queryset):
        updated = queryset.update(status=True)
        self.message_user(request, f'{updated} gigs have been approved.')
    approve_gigs.short_description = 'Approve selected gigs'

    def disapprove_gigs(self, request, queryset):
        updated = queryset.update(status=False)
        self.message_user(request, f'{updated} gigs have been disapproved.')
    disapprove_gigs.short_description = 'Disapprove selected gigs'

    def feature_gigs(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} gigs have been marked as featured.')
    feature_gigs.short_description = 'Mark selected gigs as featured'

    def unfeature_gigs(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} gigs have been unmarked as featured.')
    unfeature_gigs.short_description = 'Remove featured status from selected gigs'


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('country_name',)
    search_fields = ('country_name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('district_name', 'country')
    list_filter = ('country',)
    search_fields = ('district_name',)


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ('local_name', 'local_district')
    list_filter = ('local_district',)
    search_fields = ('local_name',)


@admin.register(LocalType)
class LocalTypeAdmin(admin.ModelAdmin):
    list_display = ('local_type_name',)
    search_fields = ('local_type_name',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('local', 'get_district', 'get_type')
    list_filter = ('local__local_district', 'local_type')
    search_fields = ('local__local_name',)

    def get_district(self, obj):
        return obj.local.local_district.district_name if obj.local and obj.local.local_district else ''
    get_district.short_description = 'District'

    def get_type(self, obj):
        return obj.local.local_type.local_type if obj.local and obj.local.local_type else ''
    get_type.short_description = 'Type'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'photo')
    search_fields = ('category',)

    fieldsets = (
        (None, {
            'fields': ('category', 'photo')
        }),
    )


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('subcategory', 'category')
    list_filter = ('category',)
    search_fields = ('subcategory', 'category__category')

    fieldsets = (
        (None, {
            'fields': ('category', 'subcategory')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('gig', 'user', 'content', 'create_time')
    list_filter = ('create_time',)
    search_fields = ('content', 'user__username', 'gig__title')
    date_hierarchy = 'create_time'
    actions = ['approve_reviews', 'disapprove_reviews']

    fieldsets = (
        (None, {
            'fields': ('gig', 'user', 'content')
        }),
    )

    def approve_reviews(self, request, queryset):
        updated = queryset.update(status=True)
        self.message_user(request, f'{updated} reviews have been approved.')
    approve_reviews.short_description = 'Approve selected reviews'

    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(status=False)
        self.message_user(request, f'{updated} reviews have been disapproved.')
    disapprove_reviews.short_description = 'Disapprove selected reviews'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('rating', 'rating_description')
    list_filter = ('rating',)
    search_fields = ('rating_description',)

    fieldsets = (
        (None, {
            'fields': ('rating', 'rating_description')
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'category')
    search_fields = ('name', 'email', 'subject', 'body')

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'category', 'subject')
        }),
        ('Message', {
            'fields': ('body',)
        }),
    )
