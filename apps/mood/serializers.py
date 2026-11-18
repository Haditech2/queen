from rest_framework import serializers
from .models import MoodCheckIn

class MoodCheckInSerializer(serializers.ModelSerializer):
    mood_emoji = serializers.CharField(read_only=True)
    mood_display = serializers.CharField(source='get_mood_display', read_only=True)

    class Meta:
        model = MoodCheckIn
        fields = ['id', 'mood', 'mood_emoji', 'mood_display', 'stress_level', 'sleep_quality', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']
