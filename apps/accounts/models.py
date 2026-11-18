import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    AGE_RANGES = [
        ('under_18', 'Under 18'),
        ('18_24', '18 - 24 years'),
        ('25_34', '25 - 34 years'),
        ('35_44', '35 - 44 years'),
        ('45_54', '45 - 54 years'),
        ('55_plus', '55 years and older'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('non_binary', 'Non-binary / Diverse'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('pcm', 'Nigerian Pidgin'),
        ('yo', 'Yoruba'),
        ('ha', 'Hausa'),
        ('ig', 'Igbo'),
    ]

    COMMUNICATION_STYLES = [
        ('gentle', 'Gentle & Reflective (Soothing, patient listener)'),
        ('direct', 'Direct & Solution-Focused (Practical steps & clarity)'),
        ('encouraging', 'Warm & Encouraging (Uplifting and reassuring)'),
        ('concise', 'Concise & Short (Brief check-ins, less reading)'),
    ]

    NIGERIAN_STATES = [
        ('Nasarawa', 'Nasarawa State (NSUK Host State)'),
        ('FCT', 'Federal Capital Territory (Abuja)'),
        ('Plateau', 'Plateau'), ('Benue', 'Benue'), ('Kaduna', 'Kaduna'), ('Kogi', 'Kogi'),
        ('Abia', 'Abia'), ('Adamawa', 'Adamawa'), ('Akwa Ibom', 'Akwa Ibom'),
        ('Anambra', 'Anambra'), ('Bauchi', 'Bauchi'), ('Bayelsa', 'Bayelsa'),
        ('Borno', 'Borno'), ('Cross River', 'Cross River'),
        ('Delta', 'Delta'), ('Ebonyi', 'Ebonyi'), ('Edo', 'Edo'),
        ('Ekiti', 'Ekiti'), ('Enugu', 'Enugu'),
        ('Gombe', 'Gombe'), ('Imo', 'Imo'), ('Jigawa', 'Jigawa'),
        ('Kano', 'Kano'), ('Katsina', 'Katsina'),
        ('Kebbi', 'Kebbi'), ('Kwara', 'Kwara'),
        ('Lagos', 'Lagos'), ('Niger', 'Niger'),
        ('Ogun', 'Ogun'), ('Ondo', 'Ondo'), ('Osun', 'Osun'),
        ('Oyo', 'Oyo'), ('Rivers', 'Rivers'),
        ('Sokoto', 'Sokoto'), ('Taraba', 'Taraba'), ('Yobe', 'Yobe'),
        ('Zamfara', 'Zamfara'), ('Diaspora', 'African Diaspora (Abroad)'),
        ('Other', 'Other African Country / Region'),
    ]

    NSUK_STATUS_CHOICES = [
        ('undergraduate', 'NSUK Undergraduate Student'),
        ('postgraduate', 'NSUK Postgraduate Student'),
        ('staff_academic', 'NSUK Academic Staff / Lecturer'),
        ('staff_non_academic', 'NSUK Non-Academic Staff'),
        ('alumni', 'NSUK Alumni'),
        ('keffi_resident', 'Keffi Community Member / Neighbor'),
    ]

    NSUK_FACULTIES = [
        ('Administration', 'Faculty of Administration'),
        ('Arts', 'Faculty of Arts'),
        ('Education', 'Faculty of Education'),
        ('Environmental_Science', 'Faculty of Environmental Science'),
        ('Law', 'Faculty of Law'),
        ('Natural_Applied_Sciences', 'Faculty of Natural & Applied Sciences'),
        ('Social_Sciences', 'Faculty of Social Sciences'),
        ('Agriculture', 'Faculty of Agriculture (Lafia Campus)'),
        ('Medical_Sciences', 'College of Medicine & Allied Health Sciences'),
        ('Engineering', 'Faculty of Engineering (Gudi Campus)'),
        ('General_Studies', 'School of General & Preliminary Studies'),
        ('Other', 'Other / Non-Student'),
    ]

    ACADEMIC_LEVELS = [
        ('100L', '100 Level (Freshman)'),
        ('200L', '200 Level'),
        ('300L', '300 Level'),
        ('400L', '400 Level (Final Year)'),
        ('500L', '500 Level (Professional / Final Year)'),
        ('Spillover', 'Spillover / Extra Year'),
        ('Postgraduate', 'Postgraduate (PGD / MSc / PhD)'),
        ('Staff_Community', 'Staff / Community Member'),
    ]

    KEFFI_RESIDENCES = [
        ('Angwan_Lambu', 'Angwan Lambu (Off-Campus, Keffi)'),
        ('High_Level', 'High Level (Off-Campus, Keffi)'),
        ('Main_Campus_Hostel', 'Main Campus Hostels (Keffi)'),
        ('Total_Junction', 'Total / Police Station Area (Keffi)'),
        ('Gidan_Zakari_GRA', 'Gidan Zakari / GRA (Keffi)'),
        ('Pyanku_Campus', 'Pyanku Campus Area'),
        ('Lafia_Gudi_Campus', 'Lafia / Gudi Campus Area'),
        ('Commuter_Abuja', 'Commuting from Mararaba / Nyanya / Abuja'),
        ('Other_Keffi', 'Other Keffi Residential Area'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=25, blank=True, null=True)

    # NSUK Case Study Profile Attributes
    is_nsuk_affiliate = models.BooleanField(default=True, help_text="Affiliated with Nasarawa State University Keffi")
    nsuk_status = models.CharField(max_length=40, choices=NSUK_STATUS_CHOICES, default='undergraduate', blank=True)
    faculty = models.CharField(max_length=60, choices=NSUK_FACULTIES, default='Administration', blank=True)
    department = models.CharField(max_length=100, blank=True, default='', help_text="e.g. Accounting, Computer Science, Mass Comm, Law")
    level = models.CharField(max_length=30, choices=ACADEMIC_LEVELS, default='200L', blank=True)
    residence_location = models.CharField(max_length=60, choices=KEFFI_RESIDENCES, default='Angwan_Lambu', blank=True)

    age_range = models.CharField(max_length=25, choices=AGE_RANGES, default='18_24')
    gender = models.CharField(max_length=25, choices=GENDER_CHOICES, default='prefer_not_to_say', blank=True)
    state_region = models.CharField(max_length=60, choices=NIGERIAN_STATES, default='Nasarawa', blank=True)
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    preferred_communication_style = models.CharField(max_length=25, choices=COMMUNICATION_STYLES, default='gentle')

    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, default='')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')

    emergency_contact_name = models.CharField(max_length=150, blank=True, default='')
    emergency_contact_phone = models.CharField(max_length=30, blank=True, default='')
    emergency_contact_relationship = models.CharField(max_length=60, blank=True, default='')

    # Cultural & support preferences (Never forced or assumed)
    # Stored as JSON array: ['family', 'friends', 'community', 'faith', 'professional', 'peer', 'anonymous']
    comfortable_support_systems = models.JSONField(
        default=list,
        blank=True,
        help_text="Types of support structures the user feels comfortable discussing"
    )

    # Faith mention voluntarily (Optional - never assumed!)
    faith_preference = models.CharField(
        max_length=60,
        blank=True,
        default='',
        help_text="Optional faith/spiritual context voluntarily disclosed by user"
    )

    # Privacy & consent controls
    allow_ai_personalization = models.BooleanField(
        default=True,
        help_text="Use profile communication styles and language preference in AI prompts"
    )
    explicit_screening_consent = models.BooleanField(
        default=True,
        help_text="Consent to store non-diagnostic screening results securely for user personal review"
    )
    daily_checkin_reminder = models.BooleanField(default=True)
    reminder_time = models.TimeField(null=True, blank=True, default='20:00:00')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"
