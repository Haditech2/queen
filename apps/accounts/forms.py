from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'At least 8 characters', 'autocomplete': 'new-password'}),
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat your password', 'autocomplete': 'new-password'})
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'nsuk_status', 'faculty', 'department', 'level', 'residence_location',
            'age_range', 'gender', 'state_region',
            'preferred_language', 'preferred_communication_style'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amina or Chinedu'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Danladi or Balogun'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@nsuk.edu.ng or email@example.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +234 803 123 4567 (optional)'}),
            'nsuk_status': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science, Accounting, Law, Mass Comm'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'residence_location': forms.Select(attrs={'class': 'form-select'}),
            'age_range': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'state_region': forms.Select(attrs={'class': 'form-select'}),
            'preferred_language': forms.Select(attrs={'class': 'form-select'}),
            'preferred_communication_style': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in [
            'nsuk_status', 'faculty', 'department', 'level', 'residence_location',
            'phone_number', 'gender', 'state_region', 'age_range', 'preferred_language', 'preferred_communication_style'
        ]:
            if field in self.fields:
                self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com', 'autocomplete': 'email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password', 'autocomplete': 'current-password'})
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number',
            'nsuk_status', 'faculty', 'department', 'level', 'residence_location',
            'age_range', 'gender', 'state_region', 'preferred_language', 'preferred_communication_style'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'nsuk_status': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science, Law'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'residence_location': forms.Select(attrs={'class': 'form-select'}),
            'age_range': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'state_region': forms.Select(attrs={'class': 'form-select'}),
            'preferred_language': forms.Select(attrs={'class': 'form-select'}),
            'preferred_communication_style': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in [
            'nsuk_status', 'faculty', 'department', 'level', 'residence_location',
            'phone_number', 'gender', 'state_region', 'age_range', 'preferred_language', 'preferred_communication_style'
        ]:
            if field in self.fields:
                self.fields[field].required = False


class CulturalPreferencesForm(forms.ModelForm):
    SUPPORT_OPTIONS = [
        ('family', 'Family & Extended Relatives'),
        ('friends', 'Close Friends & Circles'),
        ('community', 'Community Leaders & Groups'),
        ('faith', 'Faith / Spiritual Support (Pastoral / Islamic / Traditional)'),
        ('professional', 'Professional Mental Health Specialists (Psychologists, Therapists)'),
        ('peer', 'Peer Support Networks'),
        ('anonymous', 'Anonymous / Autonomous Reflection Only'),
    ]

    support_choices = forms.MultipleChoiceField(
        choices=SUPPORT_OPTIONS,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Comfortable Support Systems"
    )

    class Meta:
        model = UserProfile
        fields = [
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'faith_preference', 'allow_ai_personalization', 'explicit_screening_consent', 'daily_checkin_reminder'
        ]
        widgets = {
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trusted person full name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +234 803 123 4567'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sister, Uncle, Friend, Mentor'}),
            'faith_preference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Christianity, Islam, Traditional, None (Optional)'}),
            'allow_ai_personalization': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'explicit_screening_consent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'daily_checkin_reminder': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['support_choices'].initial = self.instance.comfortable_support_systems or []

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.comfortable_support_systems = self.cleaned_data.get('support_choices', [])
        if commit:
            profile.save()
        return profile


class PasswordChangeCustomForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current password'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password (min 8 chars)'}),
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data
