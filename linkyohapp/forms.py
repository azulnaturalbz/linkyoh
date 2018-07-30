from django.forms import ModelForm
from .models import Gig, Location


class GigForm(ModelForm):
    class Meta:
        model = Gig
        fields = ['title', 'category', 'sub_category', 'description', 'price', 'photo', 'status', 'phone_number',
                  'address_1','address_2', 'state', 'location']

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
