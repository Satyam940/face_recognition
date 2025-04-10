from django import  forms
from .models import KnownFace


class knownFaceForm(forms.ModelForm):
    class Meta:
        model = KnownFace
        fields = ['name','uid', 'class', 'image']