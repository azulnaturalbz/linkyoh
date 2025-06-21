import io
from PIL import Image
from django import forms
from django.forms import ModelForm, inlineformset_factory, BaseInlineFormSet
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from .models import Gig, Location, Review, Contact, GigImage, GigContact, GigServiceArea


# Declaring Extensions that will be allowed to be uploaded(Not to be used yet)
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
#
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class GigForm(ModelForm):
    class Meta:
        model = Gig
        fields = ['title',
                  'category',
                  'sub_category',
                  'description',
                  'price',
                  'photo',
                  'status',
                  'phone_number',
                  'address_1',
                  'address_2',
                  'district',
                  'location']
        help_texts = {
            'title': _('Enter a clear, descriptive title for your gig (max 500 characters)'),
            'description': _('Describe your service in detail (max 1000 characters)'),
            'price': _('Enter your price in dollars'),
            'photo': _('Upload a main image for your gig (jpg, jpeg, png, gif only)'),
            'phone_number': _('Enter your primary phone number in international format (e.g., +5016550000)'),
            'address_1': _('Enter your primary address'),
            'address_2': _('Enter additional address information (optional)'),
        }
        error_messages = {
            'title': {
                'required': _('Please enter a title for your gig'),
                'max_length': _('Title is too long, please keep it under 500 characters'),
            },
            'description': {
                'required': _('Please provide a description for your gig'),
                'max_length': _('Description is too long, please keep it under 1000 characters'),
            },
            'price': {
                'required': _('Please enter a price for your gig'),
                'invalid': _('Please enter a valid price'),
            },
            'phone_number': {
                'invalid': _('Please enter a valid phone number in international format'),
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add custom validators
        self.fields['price'].validators.append(MinValueValidator(0, message=_('Price cannot be negative')))

        # Add CSS classes for styling
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Handle dynamic location dropdown
        self.fields['location'].queryset = Location.objects.none()
        if 'district' in self.data:
            try:
                district_id = self.data.get('district')
                self.fields['location'].queryset = Location.objects.filter(
                    local__local_district=district_id
                ).select_related('local').order_by('local')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty location queryset
        elif self.instance.pk and hasattr(self.instance, 'district'):
            self.fields['location'].queryset = Location.objects.filter(
                local__local_district=self.instance.district_id
            ).select_related('local').order_by('local')

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check file extension
            ext = photo.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                raise forms.ValidationError(_('Only jpg, jpeg, png, and gif files are allowed'))

            # Check file size (max 10MB)
            if photo.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_('File size must be no more than 10MB'))
        return photo


class GigImageForm(ModelForm):
    """Form for additional gig images"""
    class Meta:
        model = GigImage
        fields = ['image', 'caption', 'is_primary', 'order']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Image caption (optional)'}),
            'order': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }
        help_texts = {
            'image': _('Upload an additional image (jpg, jpeg, png, gif only)'),
            'caption': _('Add a caption for this image (optional)'),
            'is_primary': _('Set as the primary image for this gig'),
            'order': _('Set the display order (lower numbers appear first)'),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file extension
            ext = image.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                raise forms.ValidationError(_('Only jpg, jpeg, png, and gif files are allowed'))

            # Check file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_('File size must be no more than 10MB'))
        return image


class GigContactForm(ModelForm):
    """Form for additional gig contact numbers"""
    class Meta:
        model = GigContact
        fields = ['phone_number', 'description', 'is_whatsapp', 'is_primary', 'order']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'e.g., Work, Mobile, Office'}),
            'order': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }
        help_texts = {
            'phone_number': _('Enter a phone number in international format (e.g., +5016550000)'),
            'description': _('Add a description for this contact (optional)'),
            'is_whatsapp': _('Check if this number is available on WhatsApp'),
            'is_primary': _('Set as the primary contact for this gig'),
            'order': _('Set the display order (lower numbers appear first)'),
        }


class GigServiceAreaForm(ModelForm):
    """Form for additional gig service areas"""
    class Meta:
        model = GigServiceArea
        fields = ['district', 'location', 'description', 'is_primary', 'order']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'e.g., Main Area, Secondary Area'}),
            'order': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }
        help_texts = {
            'district': _('Select a district'),
            'location': _('Select a location within the district'),
            'description': _('Add a description for this service area (optional)'),
            'is_primary': _('Set as the primary service area for this gig'),
            'order': _('Set the display order (lower numbers appear first)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Handle dynamic location dropdown
        self.fields['location'].queryset = Location.objects.none()
        if 'district' in self.data:
            try:
                district_id = self.data.get('district')
                self.fields['location'].queryset = Location.objects.filter(
                    local__local_district=district_id
                ).select_related('local').order_by('local')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty location queryset
        elif self.instance.pk and hasattr(self.instance, 'district') and self.instance.district:
            self.fields['location'].queryset = Location.objects.filter(
                local__local_district=self.instance.district_id
            ).select_related('local').order_by('local')


# Create formsets for the related models
GigImageFormSet = inlineformset_factory(
    Gig, GigImage, form=GigImageForm, 
    extra=1, can_delete=True, max_num=10
)

GigContactFormSet = inlineformset_factory(
    Gig, GigContact, form=GigContactForm,
    extra=1, can_delete=True, max_num=5
)

GigServiceAreaFormSet = inlineformset_factory(
    Gig, GigServiceArea, form=GigServiceAreaForm,
    extra=1, can_delete=True, max_num=5
)

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['content',
                  'rating']
        fields_required = ['content',
                           'rating']


class ContactForm(forms.ModelForm):
    name = forms.CharField(help_text="John Doe")
    email = forms.EmailField(label='E-Mail', help_text="example@example.com", )
    phone = PhoneNumberField(help_text="+5016550000")
    category = forms.ChoiceField(
        choices=[('question', 'Question'),
                 ('suggestions', 'Suggestions'),
                 ('complaints', 'Complaints'),
                 ('investor relations', 'Investor Relations')])
    subject = forms.CharField(required=False, help_text="Subject")
    body = forms.CharField(widget=forms.Textarea, label="Message", help_text="Message")

    class Meta:
        model = Contact
        fields = {'name', 'email', 'phone', 'category', 'subject', 'body'}

    field_order = ['name', 'email', 'phone', 'category', 'subject', 'body']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
