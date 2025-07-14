import io
from PIL import Image
from django import forms
from django.forms import ModelForm, inlineformset_factory, BaseInlineFormSet
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from .models import Gig, Location, Review, Contact, GigImage, GigContact, GigServiceArea, Profile, District
from .image_utils import validate_image, ImageValidationError


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
                  'call_for_pricing',
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
            'call_for_pricing': _('Check this if you prefer customers to call for pricing details instead of displaying a fixed price'),
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

        # Make photo field optional when editing (instance exists)
        self.fields['photo'].required = not bool(self.instance.pk)

        # Only add the MinValueValidator if this is not an instance with call_for_pricing
        # This allows -1 as a valid value for price when call_for_pricing is enabled
        if not (self.instance.pk and self.instance.call_for_pricing):
            self.fields['price'].validators.append(MinValueValidator(0, message=_('Price cannot be negative')))

        # Customize call_for_pricing widget
        self.fields['call_for_pricing'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'x-on:change': 'priceFieldVisible = !$event.target.checked'
        })

        # Add CSS classes for styling
        for field in self.fields:
            if field != 'call_for_pricing':  # Skip call_for_pricing as we've already customized it
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

    def clean(self):
        cleaned_data = super().clean()
        call_for_pricing = cleaned_data.get('call_for_pricing')
        price = cleaned_data.get('price')

        # If call_for_pricing is checked, set price to -1 as a special value
        # This will be used to identify gigs with "Call for pricing" in queries
        if call_for_pricing:
            cleaned_data['price'] = -1
        elif price is None or price < -1:
            # Only validate price if call_for_pricing is not checked
            self.add_error('price', _('Please enter a valid price (0 or greater)'))

        return cleaned_data

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo == 'gigs_img/empty_cover.jpg':
            return photo
        if photo:
            try:
                validate_image(photo)
            except ImageValidationError as e:
                raise forms.ValidationError(_(str(e)))
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
            'image': _('Upload an additional image (jpg, jpeg, png, gif, heic, heif)'),
            'caption': _('Add a caption for this image (optional)'),
            'is_primary': _('Set as the primary image for this gig'),
            'order': _('Set the display order (lower numbers appear first)'),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            try:
                validate_image(image)
            except ImageValidationError as e:
                raise forms.ValidationError(_(str(e)))
        return image

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # "order" is optional – default to 0 when the user leaves it blank.
        self.fields['order'].required = False

    def clean_order(self):
        """Return 0 when order is omitted so validation doesn't complain."""
        order = self.cleaned_data.get('order')
        return 0 if order in (None, '') else order


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].required = False

    def clean_order(self):
        order = self.cleaned_data.get('order')
        return 0 if order in (None, '') else order


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

        # "order" optional
        self.fields['order'].required = False

        # Build the correct key for the posted district (formsets prefix each field name)
        district_key = f'{self.prefix}-district' if self.prefix else 'district'

        if district_key in self.data:
            try:
                district_id = self.data.get(district_key)
                self.fields['location'].queryset = (
                    Location.objects
                    .filter(local__local_district=district_id)
                    .select_related('local')
                    .order_by('local')
                )
            except (ValueError, TypeError):
                # Invalid input; keep an empty queryset
                pass
        elif self.instance.pk and getattr(self.instance, 'district', None):
            # Populate when editing an existing instance
            self.fields['location'].queryset = (
                Location.objects
                .filter(local__local_district=self.instance.district_id)
                .select_related('local')
                .order_by('local')
            )

    def clean_order(self):
        order = self.cleaned_data.get('order')
        return 0 if order in (None, '') else order


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


class ProfileForm(forms.ModelForm):
    """Form for editing user profiles"""
    class Meta:
        model = Profile
        fields = [
            'profile_type', 'avatar', 'cover_image', 'gender', 'about', 'slogan',
            'phone_number', 'email_public', 'website',
            'facebook', 'twitter', 'instagram', 'linkedin',
            'company_name', 'business_type', 'business_description', 'year_established',
            'address', 'district', 'location', 'show_qr_code'
        ]
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell potential customers about yourself or your business'}),
            'slogan': forms.TextInput(attrs={'placeholder': 'Add a catchy slogan'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
            'facebook': forms.URLInput(attrs={'placeholder': 'https://facebook.com/yourusername'}),
            'twitter': forms.URLInput(attrs={'placeholder': 'https://twitter.com/yourusername'}),
            'instagram': forms.URLInput(attrs={'placeholder': 'https://instagram.com/yourusername'}),
            'linkedin': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/yourusername'}),
            'business_description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your business'}),
            'address': forms.TextInput(attrs={'placeholder': 'Your address'}),
            'year_established': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
        }
        help_texts = {
            'profile_type': _('Select whether this is an individual or business profile'),
            'avatar': _('Upload your profile picture'),
            'cover_image': _('Upload a cover image for your profile header (optional)'),
            'gender': _('Your gender (optional)'),
            'about': _('Tell potential customers about yourself or your business'),
            'slogan': _('A short, catchy phrase that describes you or your business'),
            'phone_number': _('Your contact phone number in international format (e.g., +5016550000)'),
            'email_public': _('Check this if you want your email to be visible on your profile'),
            'website': _('Your website URL (if you have one)'),
            'facebook': _('Link to your Facebook profile or page'),
            'twitter': _('Link to your Twitter profile'),
            'instagram': _('Link to your Instagram profile'),
            'linkedin': _('Link to your LinkedIn profile'),
            'company_name': _('Your business name (for business profiles)'),
            'business_type': _('Type of business (e.g., LLC, Corporation, Sole Proprietor)'),
            'business_description': _('Detailed description of your business'),
            'year_established': _('Year your business was established'),
            'address': _('Your physical address'),
            'district': _('Select your district'),
            'location': _('Select your location within the district'),
            'show_qr_code': _('Display a QR code on your profile for easy sharing'),
        }
        labels = {
            'profile_type': _('Profile Type'),
            'avatar': _('Profile Picture'),
            'cover_image': _('Profile Header Image'),
            'gender': _('Gender'),
            'about': _('About'),
            'slogan': _('Slogan'),
            'phone_number': _('Phone Number'),
            'email_public': _('Make Email Public'),
            'website': _('Website'),
            'facebook': _('Facebook'),
            'twitter': _('Twitter'),
            'instagram': _('Instagram'),
            'linkedin': _('LinkedIn'),
            'company_name': _('Company Name'),
            'business_type': _('Business Type'),
            'business_description': _('Business Description'),
            'year_established': _('Year Established'),
            'address': _('Address'),
            'district': _('District'),
            'location': _('Location'),
            'show_qr_code': _('Show QR Code'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add CSS classes for styling
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Make checkbox fields have the correct class
        if 'email_public' in self.fields:
            self.fields['email_public'].widget.attrs.update({'class': 'form-check-input'})
        if 'show_qr_code' in self.fields:
            self.fields['show_qr_code'].widget.attrs.update({'class': 'form-check-input'})

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

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            try:
                validate_image(avatar)
            except ImageValidationError as e:
                raise forms.ValidationError(_(str(e)))
        return avatar

    def clean_cover_image(self):
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            try:
                validate_image(cover_image)
            except ImageValidationError as e:
                raise forms.ValidationError(_(str(e)))
        return cover_image


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)
    phone_number = PhoneNumberField(
        help_text="Enter your Belize phone number (e.g., +5016550000)",
        required=True,
        region="BZ"  # Set Belize as the default region
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Ensure the phone number is from Belize
            if not str(phone_number).startswith('+501'):
                raise forms.ValidationError('Please enter a valid Belize phone number starting with +501.')
        return phone_number
