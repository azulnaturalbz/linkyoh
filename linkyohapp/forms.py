from django import forms
from django.forms import ModelForm
from .models import Gig, Location, Review

# Declaring Extensions that will be allowed to be uploaded
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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
                  'state',
                  'location']
        fields_required = ['title',
                           'category',
                           'sub_category',
                           'description',
                           'price',
                           'photo',
                           'status',
                           'phone_number',
                           'address_1',
                           'state',
                           'location']
        
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['location'].queryset = Location.objects.none()

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['location'].queryset = Location.objects.filter(local__state__id=state_id).order_by('local')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['location'].queryset = self.instance.state.location_set.order_by('local')

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if not photo.name.endswith(".jpg") | photo.name.endswith(".jpeg") | photo.name.endswith(".png") | photo.name.endswith(".gif"):
            raise forms.ValidationError("Only .jpg image accepted")
        return photo


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['content',
                  'rating']
        fields_required = ['content',
                           'rating']


class ContactForm(forms.Form):
    contact_email = forms.EmailField(required=True, label="Email")
    content_subject = forms.CharField(required=True, label="Subject")
    content = forms.CharField(
        required=True,
        widget=forms.Textarea,
        label="Message"
    )