from rest_framework import serializers
from .models import CrisisResource, MentalHealthResource

class CrisisResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrisisResource
        fields = [
            'id', 'organization', 'service_type', 'phone', 'secondary_phone',
            'whatsapp_or_sms', 'email', 'website', 'location_state',
            'operating_hours', 'is_24_7', 'is_emergency_priority',
            'description', 'notes', 'verification_date'
        ]

class MentalHealthResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentalHealthResource
        fields = [
            'id', 'title', 'resource_type', 'organization', 'location_state',
            'phone', 'email', 'website', 'description', 'services_offered'
        ]
