from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models_ad import AdPlacement, Advertisement, AdPlacementAssignment, AdImpression, AdClick

class AdPlacementAssignmentInline(admin.TabularInline):
    model = AdPlacementAssignment
    extra = 1
    fields = ('placement', 'priority', 'impressions', 'clicks')
    readonly_fields = ('impressions', 'clicks')

@admin.register(AdPlacement)
class AdPlacementAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_name_display', 'is_active', 'max_ads', 'recommended_dimensions', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active', 'max_ads')
        }),
        ('Dimensions', {
            'fields': ('recommended_width', 'recommended_height')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def recommended_dimensions(self, obj):
        if obj.recommended_width and obj.recommended_height:
            return f"{obj.recommended_width}px × {obj.recommended_height}px"
        return "Not specified"
    recommended_dimensions.short_description = "Recommended Dimensions"

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'advertiser', 'ad_type', 'status', 'active_status', 'impressions_clicks', 'start_date', 'end_date')
    list_filter = ('status', 'ad_type', 'start_date', 'placements')
    search_fields = ('title', 'description', 'advertiser__username', 'advertiser__email')
    readonly_fields = ('created_at', 'updated_at', 'total_impressions', 'total_clicks', 'preview_image', 'ctr')
    filter_horizontal = ('target_categories', 'target_districts')
    inlines = [AdPlacementAssignmentInline]
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'advertiser', 'description')
        }),
        ('Content', {
            'fields': ('ad_type', 'image', 'preview_image', 'html_content', 'destination_url')
        }),
        ('Targeting', {
            'fields': ('target_categories', 'target_districts')
        }),
        ('Scheduling', {
            'fields': ('status', 'start_date', 'end_date')
        }),
        ('Budget & Limits', {
            'fields': ('budget', 'max_impressions')
        }),
        ('Performance', {
            'fields': ('total_impressions', 'total_clicks', 'ctr'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def active_status(self, obj):
        if obj.is_active():
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Inactive')
    active_status.short_description = "Active"
    
    def impressions_clicks(self, obj):
        return f"{obj.total_impressions} / {obj.total_clicks}"
    impressions_clicks.short_description = "Impressions / Clicks"
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 300px;" />', obj.image.url)
        return "No image"
    preview_image.short_description = "Preview"
    
    def ctr(self, obj):
        if obj.total_impressions > 0:
            ctr_value = (obj.total_clicks / obj.total_impressions) * 100
            return f"{ctr_value:.2f}%"
        return "0.00%"
    ctr.short_description = "CTR"

class AdImpressionAdmin(admin.ModelAdmin):
    list_display = ('ad', 'placement', 'user', 'timestamp', 'ip_address')
    list_filter = ('timestamp', 'placement')
    search_fields = ('ad__title', 'user__username', 'ip_address')
    readonly_fields = ('ad', 'placement', 'user', 'session_id', 'ip_address', 'user_agent', 'referrer', 'timestamp')
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

class AdClickAdmin(admin.ModelAdmin):
    list_display = ('ad', 'placement', 'user', 'timestamp', 'ip_address')
    list_filter = ('timestamp', 'placement')
    search_fields = ('ad__title', 'user__username', 'ip_address')
    readonly_fields = ('ad', 'placement', 'user', 'session_id', 'ip_address', 'user_agent', 'referrer', 'timestamp')
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# Register the models
admin.site.register(AdImpression, AdImpressionAdmin)
admin.site.register(AdClick, AdClickAdmin)