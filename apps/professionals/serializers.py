from rest_framework import serializers
from .models import Professional

class ProfessionalSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    consultation_mode_display = serializers.CharField(source='get_consultation_mode_display', read_only=True)

    class Meta:
        model = Professional
        fields = [
            'id', 'name', 'title', 'category', 'category_display',
            'organization_name', 'license_number', 'state', 'city',
            'physical_address', 'phone', 'email', 'website',
            'languages_spoken', 'consultation_mode', 'consultation_mode_display',
            'services_offered', 'availability_notes', 'bio', 'is_verified', 'verification_date'
        ]
