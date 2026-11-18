import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class MoodCheckIn(models.Model):
    MOOD_CHOICES = [
        ('great', '😄 Great'),
        ('good', '🙂 Good'),
        ('okay', '😐 Okay'),
        ('low', '😔 Low'),
        ('anxious', '😟 Anxious'),
        ('overwhelmed', '😣 Overwhelmed'),
        ('angry', '😡 Angry'),
    ]

    SLEEP_CHOICES = [
        ('excellent', 'Excellent (Restful & uninterrupted)'),
        ('good', 'Good (Slept adequately)'),
        ('fair', 'Fair (Broken sleep / light fatigue)'),
        ('poor', 'Poor (Tossing & turning / very tired)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mood_checkins'
    )
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, db_index=True)
    stress_level = models.IntegerField(default=5, help_text="Rating from 1 (Very Calm) to 10 (Extremely Stressed)")
    sleep_quality = models.CharField(max_length=20, choices=SLEEP_CHOICES, default='good')
    note = models.TextField(blank=True, default='', help_text="Private, personal reflection note")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mood Check-In'
        verbose_name_plural = 'Mood Check-Ins'

    def __str__(self):
        return f"{self.user.first_name} - {self.get_mood_display()} ({self.created_at:%Y-%m-%d})"

    @property
    def mood_emoji(self):
        mapping = {
            'great': '😄',
            'good': '🙂',
            'okay': '😐',
            'low': '😔',
            'anxious': '😟',
            'overwhelmed': '😣',
            'angry': '😡'
        }
        return mapping.get(self.mood, '😐')
