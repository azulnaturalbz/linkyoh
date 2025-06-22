import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.storage import default_storage
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

def ad_image_upload_path(instance, filename):
    """
    Upload path for advertisement images
    Creates a path like: ads/ad_id/image_uuid.ext
    """
    # Get the file extension
    ext = filename.split('.')[-1].lower()
    
    # Generate a unique filename
    from uuid import uuid4
    unique_filename = f"{uuid4().hex}.{ext}"
    
    # Create a path with ad_id/filename
    ad_id = getattr(instance, 'id', 'new')
    return os.path.join('ads', str(ad_id), unique_filename)

class AdPlacement(models.Model):
    """
    Defines where ads can be placed in the application
    """
    PLACEMENT_CHOICES = [
        ('home_hero', 'Home Page - Hero Banner'),
        ('home_featured', 'Home Page - Featured Section'),
        ('home_categories', 'Home Page - Between Categories'),
        ('home_how_it_works', 'Home Page - After How It Works'),
        ('home_reviews', 'Home Page - After Reviews'),
        ('home_latest', 'Home Page - Within Latest Services'),
        ('home_footer', 'Home Page - Before Footer'),
        ('category_top', 'Category Page - Top'),
        ('category_bottom', 'Category Page - Bottom'),
        ('category_inline', 'Category Page - Inline with Results'),
        ('gig_detail_top', 'Gig Detail Page - Top'),
        ('gig_detail_bottom', 'Gig Detail Page - Bottom'),
        ('gig_detail_sidebar', 'Gig Detail Page - Sidebar'),
        ('profile_top', 'Profile Page - Top'),
        ('profile_bottom', 'Profile Page - Bottom'),
        ('search_top', 'Search Results - Top'),
        ('search_inline', 'Search Results - Inline with Results'),
        ('search_bottom', 'Search Results - Bottom'),
        ('global_header', 'Global - Below Header'),
        ('global_footer', 'Global - Above Footer'),
    ]
    
    name = models.CharField(max_length=50, choices=PLACEMENT_CHOICES, unique=True)
    description = models.TextField(help_text="Description of where this ad placement appears")
    is_active = models.BooleanField(default=True)
    max_ads = models.PositiveIntegerField(default=1, help_text="Maximum number of ads to show in this placement")
    
    # Dimensions for reference (not enforced)
    recommended_width = models.PositiveIntegerField(help_text="Recommended width in pixels", null=True, blank=True)
    recommended_height = models.PositiveIntegerField(help_text="Recommended height in pixels", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        ordering = ['name']
        verbose_name = "Ad Placement"
        verbose_name_plural = "Ad Placements"

class Advertisement(models.Model):
    """
    Represents an advertisement that can be displayed on the site
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    
    TYPE_CHOICES = [
        ('banner', 'Banner Ad'),
        ('card', 'Card Ad'),
        ('text', 'Text Ad'),
        ('sponsored', 'Sponsored Listing'),
    ]
    
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    advertiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advertisements')
    description = models.TextField(blank=True)
    
    # Ad content
    image = models.ImageField(upload_to=ad_image_upload_path, blank=True, null=True)
    html_content = models.TextField(blank=True, help_text="HTML content for the ad (if not using an image)")
    destination_url = models.URLField(help_text="URL where users will be directed when clicking the ad")
    
    # Ad type and placement
    ad_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    placements = models.ManyToManyField(AdPlacement, through='AdPlacementAssignment')
    
    # Targeting
    target_categories = models.ManyToManyField('Category', blank=True, related_name='targeted_ads')
    target_districts = models.ManyToManyField('District', blank=True, related_name='targeted_ads')
    
    # Status and scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    
    # Budget and impressions
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_impressions = models.PositiveIntegerField(blank=True, null=True, 
                                                help_text="Maximum number of impressions for this ad")
    
    # Tracking
    total_impressions = models.PositiveIntegerField(default=0)
    total_clicks = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def is_active(self):
        now = timezone.now()
        if self.status != 'active':
            return False
        if self.end_date and now > self.end_date:
            return False
        if now < self.start_date:
            return False
        if self.max_impressions and self.total_impressions >= self.max_impressions:
            return False
        return True
    
    def get_absolute_url(self):
        return reverse('ad_detail', args=[self.slug])
    
    def get_click_url(self):
        return reverse('ad_click', args=[self.slug])
    
    def record_impression(self):
        self.total_impressions += 1
        self.save(update_fields=['total_impressions'])
        
    def record_click(self):
        self.total_clicks += 1
        self.save(update_fields=['total_clicks'])
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Advertisement"
        verbose_name_plural = "Advertisements"

class AdPlacementAssignment(models.Model):
    """
    Associates an advertisement with a placement and tracks performance for that specific placement
    """
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    placement = models.ForeignKey(AdPlacement, on_delete=models.CASCADE)
    
    # Priority for this ad in this placement (higher number = higher priority)
    priority = models.PositiveIntegerField(default=1, 
                                          validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Tracking for this specific placement
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.ad.title} in {self.placement.get_name_display()}"
    
    class Meta:
        ordering = ['-priority', 'ad__title']
        unique_together = ('ad', 'placement')
        verbose_name = "Ad Placement Assignment"
        verbose_name_plural = "Ad Placement Assignments"

class AdImpression(models.Model):
    """
    Records individual ad impressions for detailed analytics
    """
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='impressions')
    placement = models.ForeignKey(AdPlacement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Impression of {self.ad.title} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Ad Impression"
        verbose_name_plural = "Ad Impressions"

class AdClick(models.Model):
    """
    Records individual ad clicks for detailed analytics
    """
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='clicks')
    placement = models.ForeignKey(AdPlacement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Click on {self.ad.title} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Ad Click"
        verbose_name_plural = "Ad Clicks"