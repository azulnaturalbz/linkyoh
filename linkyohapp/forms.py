import io
from PIL import Image
from django import forms
from django.forms import ModelForm
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from .models import Gig, Location, Review, Contact


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
            'photo': _('Upload an image for your gig (jpg, jpeg, png, gif only)'),
            'phone_number': _('Enter your phone number in international format (e.g., +5016550000)'),
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

    # Function Below makes sure that the image is only jpg , jpeg ,png or gif.
    # def clean_photo(self):
    #     if self.cleaned_data.get('photo') != "":
    #         photo = self.cleaned_data.get('photo')
    #         if not photo.name.endswith(".jpg") | photo.name.endswith(".jpeg") | photo.name.endswith(".png") | photo.name.endswith(".gif"):
    #             raise forms.ValidationError("Only .jpg image accepted")
    #         return photo
    #     else:
    #         pass


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
