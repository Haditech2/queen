import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    CATEGORY_CHOICES = [
        ('checkin', 'Daily Check-In Reminder'),
        ('reflection', 'Wellbeing Reflection'),
        ('system', 'System / Privacy Notice'),
        ('resource', 'Resource Verification Update'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=120)
    # Generic, privacy-preserving body that never reveals sensitive conditions
    message = models.TextField(help_text="Safe, privacy-preserving notification content")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='checkin')
    action_url = models.CharField(max_length=200, default='/dashboard/')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.title} -> {self.user.email}"


class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('info', 'Information'),
        ('success', 'New Feature'),
        ('warning', 'Important Notice'),
        ('danger', 'Urgent Alert'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='info')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'

    def __str__(self):
        return self.title
