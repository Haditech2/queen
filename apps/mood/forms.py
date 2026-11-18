from django import forms
from .models import MoodCheckIn

class MoodCheckInForm(forms.ModelForm):
    class Meta:
        model = MoodCheckIn
        fields = ['mood', 'stress_level', 'sleep_quality', 'note']
        widgets = {
            'mood': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'stress_level': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': '1', 'max': '10', 'step': '1'}),
            'sleep_quality': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional: What is contributing to how you feel today? (Family, work, study, health, peace...)'}),
        }
