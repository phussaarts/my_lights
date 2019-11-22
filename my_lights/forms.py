from django.forms import ModelForm
from .models import HueAuth

class HueAuthForm(ModelForm):
    class Meta:
        model = HueAuth
        fields = ['client_id', 'client_secret', 'app_id', 'device_id']

