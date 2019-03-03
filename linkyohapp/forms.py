import io
from PIL import Image
from django import forms
from django.forms import ModelForm
from .models import Gig, Location, Review

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
        #Conditional Below ensures that state and location have the right mapping from state to location belize to belize city eg.
        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['location'].queryset = Location.objects.filter(local__state__id=state_id).order_by('local')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['location'].queryset = self.instance.state.location_set.order_by('local')
    # Function Below makes sure that the image is only jpg , jpeg ,png or gif.
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if not photo.name.endswith(".jpg") | photo.name.endswith(".jpeg") | photo.name.endswith(".png") | photo.name.endswith(".gif"):
            raise forms.ValidationError("Only .jpg image accepted")
        else:
            # photo_field = self.cleaned_data.get('photo')
            photo_file = io.BytesIO(photo.read())

            photon = Image.open(photo_file)
            photon = photon.resize((160,300), photon.ANTIALIAS)

            photo_file = io.BytesIO()
            photon.save(photo_file,optimize=True,quality=95)

            photo.file = photo_file
        return photo


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['content',
                  'rating']
        fields_required = ['content',
                           'rating']


# Not Developed Yet
# class SearchForm(forms.Form):
#     search_form = forms.CharField()

class ContactForm(forms.Form):
    contact_email = forms.EmailField(required=True, label="Email")
    content_subject = forms.CharField(required=True, label="Subject")
    content = forms.CharField(
        required=True,
        widget=forms.Textarea,
        label="Message"
    )