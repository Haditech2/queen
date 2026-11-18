from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('REGISTER', 'User Registration'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('PROFILE_UPDATE', 'Profile Updated'),
        ('EXPORT_DATA', 'User Data Exported'),
        ('DELETE_DATA', 'User Data Deleted'),
        ('CRISIS_TRIGGERED', 'Crisis Support Triggered'),
        ('SAFETY_VIOLATION', 'Safety Policy Violation'),
        ('SCREENING_COMPLETED', 'Screening Completed'),
        ('ADMIN_ACTION', 'Administrative Action'),
    ]

    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        user_repr = self.user.email if self.user else "Anonymous"
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {self.action} by {user_repr}"
