import os
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator

import os
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import DecimalField
from django.db.models import PositiveIntegerField
from django.db.models import TextField
from django_extensions.db.fields import AutoSlugField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth import models as auth_models
from django.db import models as models
from simple_history.models import HistoricalRecords
from django_extensions.db import fields as extension_fields

from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


def cover_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)

    return '/'.join(['gigs_img', str(instance.id), filename])


def banner_upload_path(instance, filename):
    return '/'.join(['category_img', str(instance.category), filename])


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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=500)
    first_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    gender = models.CharField(max_length=8, blank=True, null=True)
    email = models.CharField(max_length=128, blank=True, null=True)
    link = models.CharField(max_length=500, blank=True, null=True)
    locale = models.CharField(max_length=128, blank=True, null=True)
    timezone = models.CharField(max_length=64, blank=True, null=True)
    about = models.CharField(max_length=1000)
    slogan = models.CharField(max_length=500)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{7,15}$',
                                 message="Phone number must be entered in the "
                                         "format: '+999999999'. Up to 15 digits allowed.")
    user_phone_number = models.CharField(validators=[phone_regex], max_length=17,
                                         blank=True)  # validators should be a list

    def __str__(self):
        return self.user.username


class Category(models.Model):
    category = models.CharField(max_length=128)
    short_category = models.CharField(max_length=8)
    description = models.CharField(max_length=1000, blank=True, null=True)
    create_time = models.DateTimeField(default=timezone.now)
    photo = models.FileField(upload_to=banner_upload_path, default='category_img/linkyoh_banner_web.png')

    def __str__(self):
        return self.category


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
    price = models.PositiveIntegerField(default=0)
    photo = models.FileField(upload_to=cover_upload_path, default='gigs_img/empty_cover.jpg')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{7,15}$',
                                 message="Phone number must be entered in the "
                                         "format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    address_1 = models.CharField(max_length=128)
    address_2 = models.CharField(max_length=128, blank=True)
    status = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()


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