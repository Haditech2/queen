from django.contrib import admin
from .models import AggregatedDailyMetric

@admin.register(AggregatedDailyMetric)
class AggregatedDailyMetricAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_registered_users', 'total_conversations', 'messages_sent_today', 'crisis_interventions_count', 'screenings_completed_today')
    list_filter = ('date',)
    readonly_fields = ('date', 'total_registered_users', 'active_users_today', 'total_conversations', 'messages_sent_today', 'crisis_interventions_count', 'screenings_completed_today', 'coping_exercises_used_today', 'top_languages_distribution')

    def has_add_permission(self, request):
        return False
