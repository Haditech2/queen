from django.db import models
from django.conf import settings

class SafetyRule(models.Model):
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low Risk - Normal Emotional Support'),
        ('MODERATE', 'Moderate Risk - Careful Questioning & Support Suggestions'),
        ('HIGH', 'High Risk - Crisis Guidance & Immediate Resource Recommendations'),
        ('IMMINENT', 'Imminent Danger - Emergency Safety Protocol & Direct Crisis Intervention'),
    ]

    RULE_TYPE_CHOICES = [
        ('SUICIDE', 'Suicide / Self-Harm Ideation'),
        ('VIOLENCE', 'Harm to Others / Violence'),
        ('ABUSE', 'Abuse / Exploitation'),
        ('EMERGENCY', 'Medical Emergency / Overdose'),
        ('DIAGNOSIS', 'Medical / Diagnostic Claim (Output)'),
        ('PRESCRIPTION', 'Prescription / Dosage Advice (Output)'),
        ('STEREOTYPE', 'Cultural Stereotype / Generalization (Output)'),
    ]

    name = models.CharField(max_length=120)
    rule_type = models.CharField(max_length=30, choices=RULE_TYPE_CHOICES)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='HIGH')
    patterns = models.TextField(
        help_text="Comma-separated or newline-separated keywords / regex patterns (case-insensitive)"
    )
    is_active = models.BooleanField(default=True)
    custom_guidance = models.TextField(
        blank=True,
        help_text="Specific safe guidance response or intervention text to return"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-risk_level', 'name']
        verbose_name = 'Safety Rule'
        verbose_name_plural = 'Safety Rules'

    def __str__(self):
        return f"[{self.risk_level}] {self.name} ({self.rule_type})"


class SafetyEvent(models.Model):
    RISK_LEVELS = [
        ('LOW', 'Low'),
        ('MODERATE', 'Moderate'),
        ('HIGH', 'High'),
        ('IMMINENT', 'Imminent'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_events'
    )
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, db_index=True)
    category = models.CharField(max_length=60, default='CRISIS_DETECTED')
    matched_rule = models.ForeignKey(SafetyRule, on_delete=models.SET_NULL, null=True, blank=True)
    matched_pattern_sanitized = models.CharField(max_length=150, blank=True)
    intervention_taken = models.CharField(max_length=200)
    location_state = models.CharField(max_length=60, blank=True, default='')
    session_id = models.CharField(max_length=100, blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Safety Event'
        verbose_name_plural = 'Safety Events'

    def __str__(self):
        return f"[{self.risk_level}] Safety Event at {self.timestamp:%Y-%m-%d %H:%M}"
