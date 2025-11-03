from django import forms
from .models import Challenge

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['image', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': 'any', 'class': 'border p-2 rounded w-full'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'class': 'border p-2 rounded w-full'}),
            'image': forms.ClearableFileInput(attrs={'class': 'border p-2 rounded w-full'}),
        }