import uuid
from django.db import models
from django.utils import timezone

class CrisisResource(models.Model):
    SERVICE_TYPES = [
        ('hotline', '24/7 Crisis Hotline'),
        ('toll_free', 'Toll-Free Helpline'),
        ('tele_counseling', 'Tele-Counseling & SMS/WhatsApp Support'),
        ('emergency_service', 'Government Emergency & Medical First Response'),
        ('hospital_er', 'Psychiatric Hospital Emergency Unit'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.CharField(max_length=150)
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES, default='hotline')
    phone = models.CharField(max_length=50)
    secondary_phone = models.CharField(max_length=50, blank=True, default='')
    whatsapp_or_sms = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    website = models.URLField(blank=True, default='')
    location_state = models.CharField(
        max_length=60,
        default='Nationwide',
        help_text="e.g. Nationwide, Lagos, Abuja, Oyo, etc."
    )
    operating_hours = models.CharField(max_length=100, default='24 Hours / 7 Days')
    is_24_7 = models.BooleanField(default=True)
    is_emergency_priority = models.BooleanField(
        default=False,
        help_text="Display prominently in immediate crisis overlays"
    )
    is_verified = models.BooleanField(default=True)
    verification_date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-is_emergency_priority', 'organization']
        verbose_name = 'Crisis Resource'
        verbose_name_plural = 'Crisis Resources'

    def __str__(self):
        return f"{self.organization} ({self.location_state}) - {self.phone}"


class MentalHealthResource(models.Model):
    RESOURCE_TYPES = [
        ('ngo', 'Non-Governmental Organization (NGO)'),
        ('advocacy', 'Mental Health Advocacy Group'),
        ('community', 'Community Support Group'),
        ('youth', 'Youth & Student Wellbeing Initiative'),
        ('research', 'Research & Policy Institute'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150)
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPES, default='ngo')
    organization = models.CharField(max_length=150)
    location_state = models.CharField(max_length=60, default='Nationwide')
    phone = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    website = models.URLField(blank=True, default='')
    description = models.TextField()
    services_offered = models.CharField(max_length=255, help_text="e.g. Free peer counseling, awareness, workshops")
    is_verified = models.BooleanField(default=True)
    verification_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['organization', 'title']
        verbose_name = 'Mental Health Resource'
        verbose_name_plural = 'Mental Health Resources'

    def __str__(self):
        return f"{self.title} - {self.organization}"
