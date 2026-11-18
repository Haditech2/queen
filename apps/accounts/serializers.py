from rest_framework import serializers
from .models import CustomUser, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'comfortable_support_systems',
            'faith_preference', 'allow_ai_personalization',
            'explicit_screening_consent', 'daily_checkin_reminder', 'reminder_time'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'is_nsuk_affiliate', 'nsuk_status', 'faculty', 'department', 'level', 'residence_location',
            'age_range', 'gender', 'state_region', 'preferred_language',
            'preferred_communication_style', 'is_verified', 'profile'
        ]
        read_only_fields = ['id', 'is_verified']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'first_name', 'last_name', 'phone_number',
            'is_nsuk_affiliate', 'nsuk_status', 'faculty', 'department', 'level', 'residence_location',
            'age_range', 'gender', 'state_region', 'preferred_language',
            'preferred_communication_style'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user
