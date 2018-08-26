from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator


# Create your models here.


def cover_upload_path(instance, filename):
    return '/'.join(['gigs_img', str(instance.user), filename])


def banner_upload_path(instance, filename):
    return '/'.join(['category_img', str(instance.category), filename])


class Country(models.Model):
    country = models.CharField(max_length=20)

    def __str__(self):
        return "%s " % (self.country)


class State(models.Model):
    state = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    description = models.TextField(default='No Description')

    def __str__(self):
        return "%s " % (self.state)


class Local(models.Model):
    local = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    description = models.TextField(default='No Description')

    def __str__(self):
        return "%s " % (self.local)


class LocalType(models.Model):
    local = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s " % (self.local)


class Location(models.Model):
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    localType = models.ForeignKey(LocalType, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s " % (self.local)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=500)
    first_name = models.CharField(max_length=128,blank=True,null=True)
    last_name = models.CharField(max_length=128,blank=True,null=True)
    gender = models.CharField(max_length=8,blank=True,null=True)
    email = models.CharField(max_length=128,blank=True,null=True)
    link = models.CharField(max_length=500,blank=True,null=True)
    locale = models.CharField(max_length=128,blank=True,null=True)
    timezone = models.CharField(max_length=64,blank=True,null=True)
    about = models.CharField(max_length=1000)
    slogan = models.CharField(max_length=500)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{7,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    user_phone_number = models.CharField(validators=[phone_regex], max_length=17,
                                         blank=True)  # validators should be a list

    def __str__(self):
        return self.user.username


class Category(models.Model):
    category = models.CharField(max_length=128)
    short_category = models.CharField(max_length=8)
    description = models.CharField(max_length=1000,blank=True,null=True)
    create_time = models.DateTimeField(default=timezone.now)
    photo = models.FileField(upload_to=banner_upload_path, default='category_img/linkyoh_banner_web.png')

    def __str__(self):
        return self.category


class SubCategory(models.Model):
    subcategory = models.CharField(max_length=128)
    sub_short_category = models.CharField(max_length=8)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    description = models.CharField(max_length=1000,blank=True,null=True)
    create_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subcategory


class Gig(models.Model):
    CATEGORY_CHOICES = (
        ("GD", " Graphics & Design"),
        ("DM", " Digital & Marketing"),
        ("VA", " Video & Animation"),
        ("MA", " Music & Audio"),
        ("PT", " Programming & Tech"),
    )

    title = models.CharField(max_length=500)
    # category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    price = models.PositiveIntegerField(default=0)
    photo = models.FileField(upload_to=cover_upload_path, default='gigs_img/empty_cover.jpg')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{7,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    address_1 = models.CharField(max_length=128)
    address_2 = models.CharField(max_length=128, blank=True)
    status = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


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
