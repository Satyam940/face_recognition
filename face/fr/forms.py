from django import forms
from .models import KnownFace

class KnownFaceForm(forms.ModelForm):
    class Meta:
        model = KnownFace
        fields = ['name', 'uid', 'class_name']
