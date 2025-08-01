import os
import logging
import uuid
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.storage import default_storage
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.exceptions import ValidationError
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from django.db.models import CharField, DateTimeField, DecimalField, PositiveIntegerField, TextField, BooleanField
from django.db.models import JSONField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth import models as auth_models
from simple_history.models import HistoricalRecords
from django_extensions.db import fields as extension_fields

from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField

# Import for file upload validation
from django.core.validators import FileExtensionValidator

# Import image processing utilities
from .image_utils import process_avatar, process_cover, process_gig_photo, process_image, ImageProcessingError

# Import for notification timestamps
from django.utils.timesince import timesince

# Define claim request status choices
GIG_CLAIM_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

# Create your models here.

# Default images for when files are missing
DEFAULT_GIG_IMAGE = 'gigs_img/empty_cover.jpg'
DEFAULT_CATEGORY_IMAGE = 'category_img/linkyoh_banner_web.png'

def file_exists(file_path):
    """Check if a file exists in storage"""
    if not file_path:
        return False
    return default_storage.exists(file_path)

def sanitize_filename(filename):
    """Sanitize filename to prevent issues with special characters"""
    # Get the file extension
    ext = filename.split('.')[-1].lower()

    # Generate a random filename with the original extension
    return f"{uuid4().hex}.{ext}"

def cover_upload_path(instance, filename):
    """
    Upload path for the main gig cover image
    Creates a path like: gigs_img/user_id/gig_id/cover_uuid.ext
    """
    # Sanitize the filename
    filename = sanitize_filename(filename)

    # Get the user ID, defaulting to 'unknown' if not available
    user_id = getattr(instance, 'user_id', 'unknown')

    # For new instances, use a temporary ID
    gig_id = getattr(instance, 'id', 'new')

    # Create a path with user_id/gig_id/cover_filename
    return os.path.join('gigs_img', str(user_id), str(gig_id), 'cover', filename)

def gig_image_upload_path(instance, filename):
    """
    Upload path for additional gig images
    Creates a path like: gigs_img/user_id/gig_id/additional/uuid.ext
    """
    # Sanitize the filename
    filename = sanitize_filename(filename)

    # Get the gig and user IDs, defaulting to 'unknown' if not available
    gig_id = getattr(instance.gig, 'id', 'unknown')
    user_id = getattr(instance.gig, 'user_id', 'unknown')

    # Create a path with user_id/gig_id/additional/filename
    return os.path.join('gigs_img', str(user_id), str(gig_id), 'additional', filename)

def banner_upload_path(instance, filename):
    """
    Upload path for category banner images
    Creates a path like: category_img/category_id/uuid.ext
    """
    # Sanitize the filename
    filename = sanitize_filename(filename)

    # Get the category ID or name, defaulting to 'unknown' if not available
    category_id = getattr(instance, 'id', None)
    if category_id is None:
        category_id = getattr(instance, 'category', 'unknown')

    # Create a path with category_id/filename
    return os.path.join('category_img', str(category_id), filename)

def profile_cover_upload_path(instance, filename):
    """
    Upload path for profile cover images
    Creates a path like: profile_covers/user_id/uuid.ext
    """
    # Sanitize the filename
    filename = sanitize_filename(filename)

    # Get the user ID, defaulting to 'unknown' if not available
    user_id = getattr(instance, 'user_id', 'unknown')

    # Create a path with user_id/filename
    return os.path.join('profile_covers', str(user_id), filename)


class Country(models.Model):
    # Fields
    country_name = models.CharField(max_length=255)
    slug = extension_fields.AutoSlugField(populate_from='country_name', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    history = HistoricalRecords()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.country_name)

    def get_absolute_url(self):
        return reverse('linkyohapp_country_detail', args=(self.slug,))

    def get_update_url(self):
        return reverse('linkyohapp_country_update', args=(self.slug,))


class District(models.Model):
    # Fields
    district_name = models.CharField(max_length=255)
    slug = extension_fields.AutoSlugField(populate_from='district_name', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    history = HistoricalRecords()

    # Relationship Fields
    country = models.ForeignKey(
        'linkyohapp.Country',
        on_delete=models.CASCADE, related_name="districts",
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.district_name)

    def get_absolute_url(self):
        return reverse('linkyohapp_district_detail', args=(self.slug,))

    def get_update_url(self):
        return reverse('linkyohapp_district_update', args=(self.slug,))


class LocalType(models.Model):
    # Fields
    local_type_name = models.CharField(max_length=255)
    slug = extension_fields.AutoSlugField(populate_from='local_type_name', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    history = HistoricalRecords()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.local_type_name)

    def get_absolute_url(self):
        return reverse('linkyohapp_localtype_detail', args=(self.slug,))

    def get_update_url(self):
        return reverse('linkyohapp_localtype_update', args=(self.slug,))


class Local(models.Model):
    # Fields
    local_name = models.CharField(max_length=255)
    slug = extension_fields.AutoSlugField(populate_from='local_name', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    history = HistoricalRecords()

    # Relationship Fields
    local_district = models.ForeignKey(
        'linkyohapp.District',
        on_delete=models.CASCADE, related_name="locals",
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.local_name)

    def get_absolute_url(self):
        return reverse('linkyohapp_local_detail', args=(self.slug,))

    def get_update_url(self):
        return reverse('linkyohapp_local_update', args=(self.slug,))


class Location(models.Model):
    # Fields
    location_description = models.TextField(max_length=255, blank=True)
    slug = extension_fields.AutoSlugField(populate_from='local', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    history = HistoricalRecords()

    # Relationship Fields
    local = models.ForeignKey(
        'linkyohapp.Local',
        on_delete=models.CASCADE, related_name="locations",
    )
    local_type = models.ForeignKey(
        'linkyohapp.LocalType',
        on_delete=models.CASCADE, related_name="locations",
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.local)

    def get_absolute_url(self):
        return reverse('linkyohapp_location_detail', args=(self.slug,))

    def get_update_url(self):
        return reverse('linkyohapp_location_update', args=(self.slug,))


class Profile(models.Model):
    PROFILE_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('business', 'Business'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_type = models.CharField(max_length=20, choices=PROFILE_TYPE_CHOICES, default='individual')
    avatar = models.FileField(upload_to='profile_avatars/', blank=True, null=True)
    cover_image = models.FileField(upload_to=profile_cover_upload_path, blank=True, null=True)
    gender = models.CharField(max_length=8, blank=True, null=True)
    about = models.TextField(blank=True)
    slogan = models.CharField(max_length=500, blank=True)
    show_qr_code = models.BooleanField(default=False, help_text="Show QR code on your profile for easy sharing")

    # Contact information
    phone_regex = RegexValidator(regex=r'^\+?1?\d{7,15}$',
                                 message="Phone number must be entered in the "
                                         "format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex],
                                    max_length=17,
                                    blank=True)  # validators should be a list
    email_public = models.BooleanField(default=False, help_text="Make email public on profile")
    website = models.URLField(max_length=200, blank=True)

    # Social media links
    facebook = models.URLField(max_length=200, blank=True)
    twitter = models.URLField(max_length=200, blank=True)
    instagram = models.URLField(max_length=200, blank=True)
    linkedin = models.URLField(max_length=200, blank=True)

    # Business specific fields
    company_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    business_description = models.TextField(blank=True)
    year_established = models.PositiveIntegerField(null=True, blank=True)

    # Location
    address = models.CharField(max_length=255, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    # Verification
    is_verified = models.BooleanField(default=False, help_text="Verified status - can only be set by admins")
    verified_date = models.DateTimeField(null=True, blank=True)

    # Timestamps
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def get_full_name(self):
        """Return the user's full name or username if not available"""
        if self.profile_type == 'business' and self.company_name:
            return self.company_name
        return self.user.get_full_name() or self.user.username

    def get_display_name(self):
        """Return the appropriate display name based on profile type"""
        if self.profile_type == 'business' and self.company_name:
            return self.company_name
        return self.user.get_full_name() or self.user.username

    def get_cover_image_url(self):
        """
        Returns the URL of the profile cover image if it exists, otherwise returns the default image URL
        """
        if self.cover_image and file_exists(self.cover_image.name):
            return self.cover_image.url
        return os.path.join(settings.STATIC_URL, 'img/linkyoh_banner_web.png')


class Category(models.Model):
    category = models.CharField(max_length=128)
    short_category = models.CharField(max_length=8)
    description = models.CharField(max_length=1000, blank=True, null=True)
    create_time = models.DateTimeField(default=timezone.now)
    photo = models.FileField(upload_to=banner_upload_path, default=DEFAULT_CATEGORY_IMAGE)

    def __str__(self):
        return self.category

    def get_photo_url(self):
        """
        Returns the URL of the category photo if it exists, otherwise returns the default image URL
        """
        if self.photo and file_exists(self.photo.name):
            return self.photo.url
        return os.path.join(settings.MEDIA_URL, DEFAULT_CATEGORY_IMAGE)


class SubCategory(models.Model):
    subcategory = models.CharField(max_length=128)
    sub_short_category = models.CharField(max_length=8)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, blank=True, null=True)
    create_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subcategory


class Gig(models.Model):
    title = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    price = models.IntegerField(default=0, help_text="Use -1 for 'Call for pricing'")
    call_for_pricing = models.BooleanField(default=False, help_text="Hide price and show 'Call for pricing details' instead")
    photo = models.FileField(upload_to=cover_upload_path, default=DEFAULT_GIG_IMAGE)
    # Main phone number is kept for backward compatibility
    phone_regex = RegexValidator(regex=r'^\+?1?\d{7,15}$',
                                 message="Phone number must be entered in the "
                                         "format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list
    # Main location is kept for backward compatibility
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    address_1 = models.CharField(max_length=128)
    address_2 = models.CharField(max_length=128, blank=True)
    status = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)

    # Featured flags
    featured = models.BooleanField(default=False, help_text="Featured across the entire site")
    featured_in_category = models.BooleanField(default=False, help_text="Featured within its category")
    featured_in_subcategory = models.BooleanField(default=False, help_text="Featured within its subcategory")
    featured_in_location = models.BooleanField(default=False, help_text="Featured within its location")
    featured_in_district = models.BooleanField(default=False, help_text="Featured within its district")

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def get_photo_url(self):
        """
        Returns the URL of the gig's main photo if it exists, otherwise returns the default image URL
        """
        if self.photo and file_exists(self.photo.name):
            return self.photo.url
        return os.path.join(settings.MEDIA_URL, DEFAULT_GIG_IMAGE)

    def get_main_image(self):
        """Return the main image (photo field) for backward compatibility"""
        return self.photo

    def get_main_image_url(self):
        """Return the URL of the main image, with fallback to default if missing"""
        return self.get_photo_url()

    def get_additional_images(self):
        """Return all additional images"""
        return self.images.all()

    def get_additional_image_urls(self):
        """Return URLs for all additional images, filtering out any missing files"""
        return [img.get_image_url() for img in self.get_additional_images()]

    def get_all_images(self):
        """Return all images including the main one"""
        return [self.photo] + list(self.images.values_list('image', flat=True))

    def get_all_image_urls(self):
        """Return URLs for all images including the main one, with fallbacks for missing files"""
        return [self.get_main_image_url()] + self.get_additional_image_urls()

    def get_all_contacts(self):
        """Return all contact numbers including the main one"""
        contacts = list(self.contacts.all())
        if self.phone_number:
            # Add the main phone number as the first in the list
            main_contact = {
                'number': self.phone_number,
                'is_whatsapp': False,
                'description': 'Main Contact'
            }
            contacts.insert(0, main_contact)
        return contacts

    def get_all_service_areas(self):
        """Return all service areas including the main one"""
        areas = list(self.service_areas.all())
        if self.location:
            # Add the main location as the first in the list
            main_area = {
                'district': self.district,
                'location': self.location,
                'description': 'Main Service Area'
            }
            areas.insert(0, main_area)
        return areas


class Rating(models.Model):
    rating = models.PositiveIntegerField(default=0)
    rating_description = models.CharField(max_length=128)

    def __str__(self):
        return self.rating_description


class Review(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=70,blank=True, null= True, unique= True)
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    category = models.CharField(max_length=100)
    subject = models.CharField(max_length=32)
    body = models.TextField()

    def __str__(self):
        return self.email


class PhoneVerification(models.Model):
    """Model for storing phone verification codes"""
    VERIFICATION_METHOD_CHOICES = (
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    )

    phone_number = PhoneNumberField()
    verification_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=10, choices=VERIFICATION_METHOD_CHOICES, default='sms')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Phone Verification"
        verbose_name_plural = "Phone Verifications"

    def __str__(self):
        return f"{self.phone_number} - {self.verification_code}"

    def is_expired(self):
        """Check if the verification code has expired"""
        return timezone.now() > self.expires_at


class GigImage(models.Model):
    """Model for additional gig images"""
    gig = models.ForeignKey(Gig, related_name='images', on_delete=models.CASCADE)
    image = models.FileField(upload_to=gig_image_upload_path)
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created']

    def __str__(self):
        return f"Image for {self.gig.title} ({self.id})"

    def get_image_url(self):
        """
        Returns the URL of the image if it exists, otherwise returns the default image URL
        """
        if self.image and file_exists(self.image.name):
            return self.image.url
        return os.path.join(settings.MEDIA_URL, DEFAULT_GIG_IMAGE)


class GigContact(models.Model):
    """Model for additional gig contact numbers"""
    gig = models.ForeignKey(Gig, related_name='contacts', on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{7,15}$',
                               message="Phone number must be entered in the "
                                       "format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    description = models.CharField(max_length=100, blank=True)
    is_whatsapp = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.phone_number} ({self.description})"


class GigServiceArea(models.Model):
    """Model for additional gig service areas"""
    gig = models.ForeignKey(Gig, related_name='service_areas', on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Service Area"
        verbose_name_plural = "Service Areas"

    def __str__(self):
        return f"{self.district.district_name} - {self.location.local}"


# Signal handlers for file management and image processing

@receiver(post_save, sender=Profile)
def process_profile_images(sender, instance, **kwargs):
    """
    Process profile images after save:
    1. Resize and compress avatar
    2. Resize and compress cover image
    """
    # Process avatar if it exists
    if instance.avatar:
        try:
            process_avatar(instance.avatar)
        except ImageProcessingError as e:
            # Log the error
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing avatar for profile {instance.id}: {str(e)}")
            # We don't want to raise the exception here as it would prevent the profile from being saved

    # Process cover image if it exists
    if instance.cover_image:
        try:
            process_cover(instance.cover_image)
        except ImageProcessingError as e:
            # Log the error
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing cover image for profile {instance.id}: {str(e)}")
            # We don't want to raise the exception here as it would prevent the profile from being saved

@receiver(post_save, sender=Gig)
def update_gig_image_paths(sender, instance, created, **kwargs):
    """
    After a gig is saved:
    1. Update the file paths if needed (for new instances)
    2. Process the gig photo (resize and compress)
    """
    # Update paths for new instances or when a new photo is uploaded
    if instance.photo:
        # For new instances or when the path contains 'new'
        if (created and 'new' in instance.photo.name) or (not created and 'new' in instance.photo.name):
            # Get the old file path
            old_path = instance.photo.path

            # Generate the new path with the correct ID
            filename = os.path.basename(instance.photo.name)
            new_path = os.path.join('gigs_img', str(instance.user_id), str(instance.id), 'cover', filename)

            # Update the file path in the database
            instance.photo.name = new_path
            instance.save(update_fields=['photo'])

            # If the old file exists, move it to the new location
            if os.path.exists(old_path):
                # Ensure the directory exists
                os.makedirs(os.path.dirname(instance.photo.path), exist_ok=True)
                # Move the file
                os.rename(old_path, instance.photo.path)

        # Process the gig photo
        try:
            process_gig_photo(instance.photo)
        except ImageProcessingError as e:
            # Log the error
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing photo for gig {instance.id}: {str(e)}")
            # We don't want to raise the exception here as it would prevent the gig from being saved

@receiver(post_save, sender=GigImage)
def update_gig_additional_image_paths(sender, instance, created, **kwargs):
    """
    After a gig image is saved:
    1. Update the file paths if needed (for new instances)
    2. Process the image (resize and compress)
    3. Ensure only one image is set as primary
    """
    # Update paths for new instances or when a new image is uploaded
    if instance.image:
        # For new instances or when the path contains 'unknown'
        if (created and 'unknown' in instance.image.name) or (not created and 'unknown' in instance.image.name):
            # Get the old file path
            old_path = instance.image.path

            # Generate the new path with the correct ID
            filename = os.path.basename(instance.image.name)
            new_path = os.path.join('gigs_img', str(instance.gig.user_id), str(instance.gig.id), 'additional', filename)

            # Update the file path in the database
            instance.image.name = new_path
            instance.save(update_fields=['image'])

            # If the old file exists, move it to the new location
            if os.path.exists(old_path):
                # Ensure the directory exists
                os.makedirs(os.path.dirname(instance.image.path), exist_ok=True)
                # Move the file
                os.rename(old_path, instance.image.path)

        # Process the additional image
        try:
            process_image(instance.image, (800, 600), format=None)
        except ImageProcessingError as e:
            # Log the error
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing additional image {instance.id} for gig {instance.gig.id}: {str(e)}")
            # We don't want to raise the exception here as it would prevent the image from being saved

    # If this image is set as primary, ensure all other images for this gig are not primary
    if instance.is_primary:
        # Get all other images for this gig
        other_images = GigImage.objects.filter(gig=instance.gig).exclude(id=instance.id)
        # Set is_primary to False for all other images
        other_images.update(is_primary=False)

        # If this is set as primary, we should also update the main gig photo
        # This ensures that when a user sets an additional image as primary,
        # it becomes the main image for the gig
        if instance.image:
            # Update the main gig photo
            instance.gig.photo = instance.image
            instance.gig.save(update_fields=['photo'])

@receiver(post_save, sender=Category)
def process_category_image(sender, instance, **kwargs):
    """Process category banner image after save"""
    if instance.photo:
        try:
            process_image(instance.photo, (1200, 400), format='JPEG')
        except ImageProcessingError as e:
            # Log the error
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing photo for category {instance.id}: {str(e)}")
            # We don't want to raise the exception here as it would prevent the category from being saved


class GigClaimRequest(models.Model):
    """
    Model for tracking requests to claim ownership of gigs that were created by admins.
    Users can submit a claim request with supporting information, and admins can approve or reject it.
    """
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='claim_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gig_claims')
    contact_number = models.CharField(validators=[RegexValidator(regex=r'^\+?1?\d{7,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")], 
                                 max_length=17)
    reason = models.TextField(help_text="Explain why you should be the owner of this gig")
    supporting_document = models.FileField(upload_to='claim_documents/', blank=True, null=True, 
                                          help_text="Upload any supporting documents (business license, ID, etc.)")
    status = models.CharField(max_length=10, choices=GIG_CLAIM_STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Admin notes about this claim request")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Gig Claim Request"
        verbose_name_plural = "Gig Claim Requests"

    def __str__(self):
        return f"Claim for {self.gig.title} by {self.user.username} ({self.get_status_display()})"

    def approve(self):
        """Approve the claim request and transfer ownership of the gig"""
        if self.status != 'approved':
            # Update the gig's owner
            self.gig.user = self.user
            self.gig.save()

            # Update the request status
            self.status = 'approved'
            self.save()
            
            # Create notification for the user
            Notification.create_claim_status_notification(self)

            return True
        return False

    def reject(self):
        """Reject the claim request"""
        if self.status != 'rejected':
            self.status = 'rejected'
            self.save()
            
            # Create notification for the user
            Notification.create_claim_status_notification(self)
            
            return True
        return False


class Stats(models.Model):
    """
    Stats model for tracking various metrics and analytics for the platform.
    This includes views, clicks, and other interactions with gigs, categories, and subcategories.
    """
    # Choices for metric types
    VIEW = 'view'
    CONTACT_CLICK = 'contact_click'
    SHARE = 'share'
    FAVORITE = 'favorite'
    CATEGORY_VIEW = 'category_view'
    SUBCATEGORY_VIEW = 'subcategory_view'
    SEARCH = 'search'

    # Messaging metrics
    CONVERSATION_STARTED = 'conversation_started'
    MESSAGE_SENT = 'message_sent'
    FILE_SHARED = 'file_shared'
    GIG_MENTIONED = 'gig_mentioned'

    METRIC_TYPE_CHOICES = [
        (VIEW, 'View'),
        (CONTACT_CLICK, 'Contact Click'),
        (SHARE, 'Share'),
        (FAVORITE, 'Favorite'),
        (CATEGORY_VIEW, 'Category View'),
        (SUBCATEGORY_VIEW, 'Subcategory View'),
        (SEARCH, 'Search'),

        # Messaging metrics
        (CONVERSATION_STARTED, 'Conversation Started'),
        (MESSAGE_SENT, 'Message Sent'),
        (FILE_SHARED, 'File Shared'),
        (GIG_MENTIONED, 'Gig Mentioned'),
    ]

    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Content type and object ID for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Direct foreign keys for common models (for easier querying)
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, null=True, blank=True, related_name='stats')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='stats')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='stats')

    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stats')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    metadata = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Stat'
        verbose_name_plural = 'Stats'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['metric_type']),
            models.Index(fields=['gig']),
            models.Index(fields=['category']),
            models.Index(fields=['subcategory']),
        ]

    def __str__(self):
        content_str = ''
        if self.gig:
            content_str = f"Gig: {self.gig.title}"
        elif self.category:
            content_str = f"Category: {self.category.category}"
        elif self.subcategory:
            content_str = f"Subcategory: {self.subcategory.subcategory}"

        return f"{self.get_metric_type_display()} - {content_str} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    # Class methods for tracking different types of events
    @classmethod
    def track_view(cls, obj, user=None, ip_address=None, user_agent=None):
        """Track a view event for a gig, category, or subcategory"""
        kwargs = {
            'metric_type': cls.VIEW,
            'user': user,
            'ip_address': ip_address,
            'user_agent': user_agent
        }

        # Set the appropriate foreign key based on object type
        if isinstance(obj, Gig):
            kwargs['gig'] = obj
        elif isinstance(obj, Category):
            kwargs['category'] = obj
            kwargs['metric_type'] = cls.CATEGORY_VIEW
        elif isinstance(obj, SubCategory):
            kwargs['subcategory'] = obj
            kwargs['metric_type'] = cls.SUBCATEGORY_VIEW
        else:
            # Use generic relation for other object types
            kwargs['content_type'] = ContentType.objects.get_for_model(obj)
            kwargs['object_id'] = obj.id

        return cls.objects.create(**kwargs)

    @classmethod
    def track_contact_click(cls, gig, user=None, ip_address=None, contact_type=None):
        """Track a contact button click for a gig"""
        metadata = {'contact_type': contact_type} if contact_type else None

        return cls.objects.create(
            gig=gig,
            metric_type=cls.CONTACT_CLICK,
            user=user,
            ip_address=ip_address,
            metadata=metadata
        )

    @classmethod
    def track_share(cls, obj, user=None, platform=None):
        """Track a share event for a gig, category, or subcategory"""
        metadata = {'platform': platform} if platform else None
        kwargs = {
            'metric_type': cls.SHARE,
            'user': user,
            'metadata': metadata
        }

        # Set the appropriate foreign key based on object type
        if isinstance(obj, Gig):
            kwargs['gig'] = obj
        elif isinstance(obj, Category):
            kwargs['category'] = obj
        elif isinstance(obj, SubCategory):
            kwargs['subcategory'] = obj
        else:
            # Use generic relation for other object types
            kwargs['content_type'] = ContentType.objects.get_for_model(obj)
            kwargs['object_id'] = obj.id

        return cls.objects.create(**kwargs)

    @classmethod
    def track_favorite(cls, gig, user=None, ip_address=None):
        """Track a favorite/like event for a gig"""
        return cls.objects.create(
            gig=gig,
            metric_type=cls.FAVORITE,
            user=user,
            ip_address=ip_address
        )

    @classmethod
    def track_search(cls, user=None, ip_address=None, query=None, filters=None):
        """Track a search event"""
        metadata = {
            'query': query,
            'filters': filters
        }

        return cls.objects.create(
            metric_type=cls.SEARCH,
            user=user,
            ip_address=ip_address,
            metadata=metadata
        )

    @classmethod
    def track_conversation_started(cls, conversation, user=None, ip_address=None):
        """Track when a new conversation is started"""
        metadata = {
            'recipient_id': conversation.recipient.id,
            'has_gig': bool(conversation.gig)
        }

        if conversation.gig:
            metadata['gig_id'] = conversation.gig.id
            metadata['gig_title'] = conversation.gig.title

        return cls.objects.create(
            metric_type=cls.CONVERSATION_STARTED,
            user=user,
            ip_address=ip_address,
            metadata=metadata
        )

    @classmethod
    def track_message_sent(cls, message, user=None, ip_address=None):
        """Track when a message is sent"""
        metadata = {
            'conversation_id': str(message.conversation.id),
            'recipient_id': message.conversation.recipient.id if message.sender == message.conversation.initiator else message.conversation.initiator.id,
            'content_length': len(message.content),
            'has_files': message.files.exists(),
            'has_mentions': message.mentioned_gigs.exists()
        }

        return cls.objects.create(
            metric_type=cls.MESSAGE_SENT,
            user=user,
            ip_address=ip_address,
            metadata=metadata
        )

    @classmethod
    def track_file_shared(cls, message_file, user=None, ip_address=None):
        """Track when a file is shared in a message"""
        metadata = {
            'conversation_id': str(message_file.message.conversation.id),
            'file_type': message_file.file_type,
            'file_size': message_file.file_size
        }

        return cls.objects.create(
            metric_type=cls.FILE_SHARED,
            user=user,
            ip_address=ip_address,
            metadata=metadata
        )

    @classmethod
    def track_gig_mentioned(cls, message, gig, user=None, ip_address=None):
        """Track when a gig is mentioned in a message"""
        metadata = {
            'conversation_id': str(message.conversation.id),
            'gig_id': gig.id,
            'gig_title': gig.title
        }

        return cls.objects.create(
            metric_type=cls.GIG_MENTIONED,
            user=user,
            gig=gig,  # Direct foreign key for easier querying
            ip_address=ip_address,
            metadata=metadata
        )

    @classmethod
    def get_stats(cls, obj, metric_type=None, days=30):
        """Get stats for an object, optionally filtered by metric type and time period"""
        start_date = timezone.now() - timezone.timedelta(days=days)

        filters = {
            'created_at__gte': start_date
        }

        if metric_type:
            filters['metric_type'] = metric_type

        # Set the appropriate filter based on object type
        if isinstance(obj, Gig):
            filters['gig'] = obj
        elif isinstance(obj, Category):
            filters['category'] = obj
        elif isinstance(obj, SubCategory):
            filters['subcategory'] = obj
        else:
            # Use generic relation for other object types
            filters['content_type'] = ContentType.objects.get_for_model(obj)
            filters['object_id'] = obj.id

        return cls.objects.filter(**filters)

    @classmethod
    def get_total_views_for_active_gigs(cls):
        """Get the total number of views for all active gigs"""
        return cls.objects.filter(
            metric_type=cls.VIEW,
            gig__status=True
        ).count()

    @classmethod
    def get_total_views_for_user_gigs(cls, user, active_only=True):
        """Get the total number of views for a user's gigs"""
        # First check if the user has any gigs
        user_gigs = Gig.objects.filter(user=user)
        if not user_gigs.exists():
            return 0

        filters = {
            'metric_type': cls.VIEW,
            'gig__user': user
        }

        if active_only:
            filters['gig__status'] = True

        return cls.objects.filter(**filters).count()

    @classmethod
    def get_views_for_gig(cls, gig):
        """Get the number of views for a specific gig"""
        return cls.objects.filter(
            metric_type=cls.VIEW,
            gig=gig
        ).count()


class Conversation(models.Model):
    """
    Model representing a conversation between two users.
    A conversation can optionally be linked to a gig.
    """
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_conversations')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_conversations')
    gig = models.ForeignKey(Gig, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')

    # Deletion flags (for hiding conversations from users without actually deleting them)
    deleted_by_initiator = models.BooleanField(default=False)
    deleted_by_recipient = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        # Ensure we don't have duplicate conversations between the same users about the same gig
        unique_together = [['initiator', 'recipient', 'gig']]

    def __str__(self):
        gig_str = f" about {self.gig.title}" if self.gig else ""
        return f"Conversation between {self.initiator.username} and {self.recipient.username}{gig_str}"

    def get_absolute_url(self):
        return reverse('conversation_detail', args=[self.id])

    def get_last_message(self):
        """Return the last message in this conversation"""
        return self.messages.order_by('-created_at').first()

    def mark_as_deleted(self, user):
        """Mark the conversation as deleted for a specific user"""
        if user == self.initiator:
            self.deleted_by_initiator = True
            self.save(update_fields=['deleted_by_initiator'])
            return True
        elif user == self.recipient:
            self.deleted_by_recipient = True
            self.save(update_fields=['deleted_by_recipient'])
            return True
        return False

    def is_deleted_for(self, user):
        """Check if the conversation is deleted for a specific user"""
        if user == self.initiator:
            return self.deleted_by_initiator
        elif user == self.recipient:
            return self.deleted_by_recipient
        return False

    def is_participant(self, user):
        """Check if a user is a participant in this conversation"""
        return user == self.initiator or user == self.recipient

    def get_other_participant(self, user):
        """Get the other participant in the conversation"""
        if user == self.initiator:
            return self.recipient
        elif user == self.recipient:
            return self.initiator
        return None

    @classmethod
    def get_conversations_for_user(cls, user):
        """Get all conversations for a user that haven't been deleted by them"""
        return cls.objects.filter(
            (models.Q(initiator=user) & models.Q(deleted_by_initiator=False)) |
            (models.Q(recipient=user) & models.Q(deleted_by_recipient=False))
        ).order_by('-updated_at')

    def get_unread_count_for_user(self, user):
        """Get the count of unread messages in this conversation for a specific user"""
        if not self.is_participant(user):
            return 0

        return self.messages.filter(
            sender__in=[self.initiator, self.recipient]
        ).exclude(
            sender=user
        ).filter(
            is_read=False
        ).count()


class Message(models.Model):
    """
    Model representing an individual message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()

    # For tracking read status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # For tracking gig mentions
    mentioned_gigs = models.ManyToManyField(Gig, related_name='mentioned_in_messages', blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def mark_as_read(self):
        """Mark the message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
            return True
        return False

    @classmethod
    def get_unread_count_for_user(cls, user):
        """Get the count of unread messages for a user"""
        return cls.objects.filter(
            conversation__recipient=user,
            is_read=False,
            conversation__deleted_by_recipient=False
        ).exclude(sender=user).count()


class MessageFile(models.Model):
    """
    Model for file attachments in messages.
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(
        upload_to='message_files/%Y/%m/%d/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'mp3', 'mp4', 'zip']
        )]
    )
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=100, help_text="MIME type of the file")

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return self.file_name

    def get_file_url(self):
        """Return the URL of the file"""
        if self.file and file_exists(self.file.name):
            return self.file.url
        return None


class Notification(models.Model):
    """
    Model for user notifications.
    """
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('claim_request', 'Gig Claim Request'),
        ('claim_approved', 'Gig Claim Approved'),
        ('claim_rejected', 'Gig Claim Rejected'),
        ('mention', 'Gig Mention'),
        ('system', 'System Notification'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    
    # For linking to related objects
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # For email/WhatsApp notification tracking
    email_sent = models.BooleanField(default=False)
    whatsapp_sent = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'notification_type']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}"
    
    def mark_as_read(self):
        """Mark the notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read', 'updated_at'])
            return True
        return False
    
    def get_absolute_url(self):
        """Get the URL to view the related object"""
        if self.notification_type == 'message' and self.content_object:
            return reverse('conversation_detail', kwargs={'pk': self.object_id})
        elif self.notification_type in ['claim_request', 'claim_approved', 'claim_rejected'] and self.content_object:
            return reverse('gig_detail', kwargs={'id': self.object_id})
        return reverse('notification_list')
    
    def get_timesince(self):
        """Get the time since the notification was created"""
        return timesince(self.created_at)
    
    @classmethod
    def get_unread_count(cls, user):
        """Get the count of unread notifications for a user"""
        return cls.objects.filter(user=user, is_read=False).count()
    
    @classmethod
    def mark_all_as_read(cls, user):
        """Mark all notifications as read for a user"""
        return cls.objects.filter(user=user, is_read=False).update(is_read=True, updated_at=timezone.now())
    
    @classmethod
    def create_message_notification(cls, message):
        """Create a notification for a new message"""
        # Only create notification for the recipient
        recipient = message.conversation.recipient if message.sender == message.conversation.initiator else message.conversation.initiator
        
        # Create the notification
        notification = cls.objects.create(
            user=recipient,
            notification_type='message',
            title='New Message',
            message=f"You have a new message from {message.sender.profile.get_display_name()}",
            content_type=ContentType.objects.get_for_model(message.conversation),
            object_id=message.conversation.id
        )
        return notification
    
    @classmethod
    def create_claim_request_notification(cls, claim_request):
        """Create a notification for a new claim request"""
        # Notify the gig owner
        notification = cls.objects.create(
            user=claim_request.gig.user,
            notification_type='claim_request',
            title='New Gig Claim Request',
            message=f"{claim_request.user.profile.get_display_name()} has requested to claim your gig: {claim_request.gig.title}",
            content_type=ContentType.objects.get_for_model(claim_request.gig),
            object_id=claim_request.gig.id
        )
        return notification
    
    @classmethod
    def create_claim_status_notification(cls, claim_request):
        """Create a notification for a claim request status change"""
        notification_type = 'claim_approved' if claim_request.status == 'approved' else 'claim_rejected'
        title = 'Gig Claim Approved' if claim_request.status == 'approved' else 'Gig Claim Rejected'
        
        notification = cls.objects.create(
            user=claim_request.user,
            notification_type=notification_type,
            title=title,
            message=f"Your claim request for '{claim_request.gig.title}' has been {claim_request.status}.",
            content_type=ContentType.objects.get_for_model(claim_request.gig),
            object_id=claim_request.gig.id
        )
        return notification
    
    @classmethod
    def create_mention_notification(cls, message, gig):
        """Create a notification for a gig mention"""
        # Notify the gig owner
        notification = cls.objects.create(
            user=gig.user,
            notification_type='mention',
            title='Your Gig Was Mentioned',
            message=f"{message.sender.profile.get_display_name()} mentioned your gig '{gig.title}' in a message.",
            content_type=ContentType.objects.get_for_model(gig),
            object_id=gig.id
        )
        return notification
