import uuid
from django.db import models
from django.utils import timezone

class Professional(models.Model):
    CATEGORY_CHOICES = [
        ('psychologist', 'Clinical Psychologist'),
        ('psychiatrist', 'Consultant Psychiatrist'),
        ('therapist', 'Psychotherapist / Family Therapist'),
        ('counselor', 'Licensed Professional Counselor'),
        ('social_worker', 'Medical / Psychiatric Social Worker'),
        ('hospital', 'Psychiatric & Teaching Hospital'),
        ('clinic', 'Mental Health & Wellness Clinic'),
        ('organization', 'Mental Health Organization'),
    ]

    MODE_CHOICES = [
        ('both', 'Online & In-Person'),
        ('in_person', 'In-Person Only'),
        ('online', 'Online Telehealth Only'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    title = models.CharField(max_length=100, help_text="e.g. Consultant Psychiatrist, Chief Medical Director")
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, db_index=True)
    organization_name = models.CharField(max_length=150, blank=True, default='')

    license_number = models.CharField(max_length=80, blank=True, default='', help_text="Official medical/psychological council registration")
    state = models.CharField(max_length=60, db_index=True)
    city = models.CharField(max_length=80)
    physical_address = models.TextField(blank=True, default='')

    phone = models.CharField(max_length=50)
    email = models.EmailField(blank=True, default='')
    website = models.URLField(blank=True, default='')

    languages_spoken = models.CharField(
        max_length=200,
        default='English, Nigerian Pidgin',
        help_text="e.g. English, Yoruba, Hausa, Igbo, Nigerian Pidgin"
    )
    consultation_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='both')
    services_offered = models.CharField(max_length=255, help_text="e.g. Depression therapy, CBT, youth counseling, trauma care")
    availability_notes = models.CharField(max_length=150, default='Mon - Fri: 8am - 4pm (By Appointment)')
    bio = models.TextField(blank=True, default='')

    is_verified = models.BooleanField(
        default=True,
        help_text="Only verified professionals and accredited centers are visible to public users"
    )
    verification_date = models.DateField(default=timezone.now)
    verified_by = models.CharField(max_length=100, default='MindBridge Clinical Board')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['state', 'name']
        verbose_name = 'Healthcare Professional / Center'
        verbose_name_plural = 'Healthcare Professionals & Centers'

    def __str__(self):
        return f"{self.name} - {self.get_category_display()} ({self.state})"
