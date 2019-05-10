from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
