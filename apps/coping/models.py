import uuid
from django.db import models

class CopingTool(models.Model):
    CATEGORY_CHOICES = [
        ('breathing', 'Breathwork & Calming'),
        ('grounding', 'Sensory Grounding (5-4-3-2-1)'),
        ('mindfulness', 'Mindfulness & Relaxation'),
        ('journaling', 'Journaling & Reflection'),
        ('academic', 'Academic & Study Stress'),
        ('sleep', 'Sleep Hygiene & Rest'),
        ('social', 'Social Connection & Boundaries'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=100)
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)
    short_description = models.CharField(max_length=255)
    duration_minutes = models.IntegerField(default=5)
    icon = models.CharField(max_length=50, default='bi-heart-pulse')
    overview = models.TextField()
    steps = models.JSONField(
        default=list,
        help_text="Ordered list of steps: [{'title': 'Step 1', 'instruction': '...', 'hint': '...'}]"
    )
    disclaimer = models.TextField(
        default="This tool offers general wellbeing exercises and is not a substitute for formal diagnosis or professional mental healthcare."
    )
    is_interactive = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Coping Tool'
        verbose_name_plural = 'Coping Tools'

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
