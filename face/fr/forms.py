from django import forms
from .models import KnownFace  # Make sure you're importing the model

class KnownFaceForm(forms.ModelForm):
    class Meta:
        model = KnownFace
        fields = ['name', 'encoding', 'class_name']  # List the fields you want
