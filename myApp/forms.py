from django import forms
from .models import *
from django.contrib.auth.models import User
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        fields = ['username', 'password', 'email']  # Add more fields as needed
        exclude = ['date_joined']