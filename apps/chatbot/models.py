from django.db import models

class AIProvider(models.Model):
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('nvidia', 'NVIDIA API'),
        ('deepseek', 'DeepSeek'),
        ('kimi', 'Kimi (Moonshot)'),
        ('glm', 'GLM (Zhipu AI)'),
        ('openai', 'OpenAI'),
        ('custom', 'Custom OpenAI-Compatible API'),
    ]

    name = models.CharField(max_length=60, unique=True)
    provider_type = models.CharField(max_length=40, choices=PROVIDER_CHOICES, default='nvidia')
    base_url = models.URLField(max_length=255, default='https://integrate.api.nvidia.com/v1')
    api_key_env_var = models.CharField(max_length=100, default='AI_API_KEY')
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'AI Provider'
        verbose_name_plural = 'AI Providers'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"


class AIModel(models.Model):
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='models')
    model_identifier = models.CharField(
        max_length=120,
        help_text="e.g. deepseek-ai/deepseek-v4.1-flash or deepseek-chat or gpt-4o-mini"
    )
    display_name = models.CharField(max_length=120)
    is_default = models.BooleanField(default=False)
    max_tokens = models.IntegerField(default=1024)
    temperature = models.FloatField(default=0.7)
    context_window = models.IntegerField(default=8192)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'AI Model'
        verbose_name_plural = 'AI Models'
        ordering = ['-is_default', 'display_name']

    def __str__(self):
        return f"{self.display_name} [{self.model_identifier}] ({self.provider.name})"

    def save(self, *args, **kwargs):
        if self.is_default:
            AIModel.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
