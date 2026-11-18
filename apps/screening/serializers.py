from rest_framework import serializers
from .models import ScreeningTool, ScreeningSession, ScreeningResponse

class ScreeningResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningResponse
        fields = ['question_index', 'question_text', 'selected_value', 'selected_label']

class ScreeningSessionSerializer(serializers.ModelSerializer):
    tool_name = serializers.CharField(source='tool.name', read_only=True)
    tool_type = serializers.CharField(source='tool.tool_type', read_only=True)
    responses = ScreeningResponseSerializer(many=True, read_only=True)

    class Meta:
        model = ScreeningSession
        fields = [
            'id', 'tool_name', 'tool_type', 'total_score', 'severity_label',
            'interpretation', 'completed_at', 'responses'
        ]
