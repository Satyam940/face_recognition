from django import forms
from django.contrib.auth.models import User
from .models import KnownFace

class KnownFaceForm(forms.ModelForm):
    class Meta:
        model = KnownFace
        fields = ['name', 'uid', 'class_name']

