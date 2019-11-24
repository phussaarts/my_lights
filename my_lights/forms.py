from django.forms import ModelForm
from .models import HueAuth, UserProfile, User
from django import forms


class HueAuthForm(ModelForm):
    class Meta:
        model = HueAuth
        fields = ['device_id']


class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(ModelForm):
    device_id = forms.CharField()

    class Meta:
        model = UserProfile
        fields = ()



