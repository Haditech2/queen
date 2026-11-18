import uuid
from django.db import models
from django.conf import settings

class ScreeningTool(models.Model):
    TOOL_TYPES = [
        ('PHQ2', 'PHQ-2 (Brief Depression Screener)'),
        ('PHQ9', 'PHQ-9 (Patient Health Questionnaire - 9)'),
        ('GAD2', 'GAD-2 (Brief Anxiety Screener)'),
        ('GAD7', 'GAD-7 (Generalized Anxiety Disorder - 7)'),
    ]

    tool_type = models.CharField(max_length=20, choices=TOOL_TYPES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    instructions = models.TextField()
    disclaimer = models.TextField(
        default="This questionnaire cannot diagnose a mental-health condition. It is intended to help identify whether speaking with a qualified professional may be useful."
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.tool_type})"


class ScreeningSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='screening_sessions'
    )
    tool = models.ForeignKey(ScreeningTool, on_delete=models.CASCADE, related_name='sessions')
    total_score = models.IntegerField()
    severity_label = models.CharField(max_length=80)
    interpretation = models.TextField()
    has_consented_storage = models.BooleanField(default=True)
    completed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-completed_at']
        verbose_name = 'Screening Session'
        verbose_name_plural = 'Screening Sessions'

    def __str__(self):
        return f"{self.user.first_name} - {self.tool.name}: Score {self.total_score} ({self.severity_label})"


class ScreeningResponse(models.Model):
    session = models.ForeignKey(
        ScreeningSession,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question_index = models.IntegerField()
    question_text = models.CharField(max_length=255)
    selected_value = models.IntegerField()
    selected_label = models.CharField(max_length=100)

    class Meta:
        ordering = ['question_index']

    def __str__(self):
        return f"Q{self.question_index}: {self.selected_value} ({self.selected_label})"
