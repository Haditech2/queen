from django.db import models
from django.utils import timezone

class AggregatedDailyMetric(models.Model):
    """
    Privacy-preserving daily metrics store.
    Contains strictly anonymized aggregate statistics with no PII.
    """
    date = models.DateField(default=timezone.now, unique=True, db_index=True)
    total_registered_users = models.IntegerField(default=0)
    active_users_today = models.IntegerField(default=0)
    total_conversations = models.IntegerField(default=0)
    messages_sent_today = models.IntegerField(default=0)
    crisis_interventions_count = models.IntegerField(default=0)
    screenings_completed_today = models.IntegerField(default=0)
    coping_exercises_used_today = models.IntegerField(default=0)
    top_languages_distribution = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Aggregated Daily Metric'
        verbose_name_plural = 'Aggregated Daily Metrics'

    def __str__(self):
        return f"Metrics for {self.date:%Y-%m-%d} (Users: {self.total_registered_users}, Messages: {self.messages_sent_today})"
