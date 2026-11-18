from rest_framework import serializers
from .models import CopingTool

class CopingToolSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = CopingTool
        fields = [
            'id', 'slug', 'title', 'category', 'category_display',
            'short_description', 'duration_minutes', 'icon', 'overview',
            'steps', 'disclaimer', 'is_interactive'
        ]
