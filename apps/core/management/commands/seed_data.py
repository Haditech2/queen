from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import CustomUser, UserProfile
from apps.chatbot.models import AIProvider, AIModel
from apps.safety.models import SafetyRule
from apps.resources.seed_data import VERIFIED_NIGERIAN_CRISIS_RESOURCES
from apps.resources.models import CrisisResource, MentalHealthResource
from apps.professionals.seed_data import VERIFIED_NIGERIAN_PROFESSIONALS
from apps.professionals.models import Professional
from apps.coping.seed_data import DEFAULT_COPING_TOOLS
from apps.coping.models import CopingTool
from apps.screening.questionnaires import QUESTIONNAIRE_DEFINITIONS
from apps.screening.models import ScreeningTool
from apps.notifications.models import Announcement

class Command(BaseCommand):
    help = "Seeds database with verified Nigerian mental health resources, coping tools, screenings, safety rules, and an admin user."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting MindBridge database seeding..."))

        # 1. Superuser
        admin_email = "admin@mindbridge.africa"
        admin_pass = "AdminPassword2026!"
        if not CustomUser.objects.filter(email=admin_email).exists():
            admin_user = CustomUser.objects.create_superuser(
                email=admin_email,
                password=admin_pass,
                first_name="MindBridge",
                last_name="Administrator",
                state_region="Lagos",
                preferred_language="en",
                preferred_communication_style="gentle"
            )
            self.stdout.write(self.style.SUCCESS(f"Created Superuser: {admin_email} (Pass: {admin_pass})"))
        else:
            self.stdout.write(f"Superuser {admin_email} already exists.")

        # 2. AI Providers and Models
        p_nvidia, _ = AIProvider.objects.get_or_create(
            name="NVIDIA API",
            defaults={
                'provider_type': 'nvidia',
                'base_url': 'https://integrate.api.nvidia.com/v1',
                'description': 'NVIDIA NIM enterprise hosted OpenAI-compatible endpoint'
            }
        )
        AIModel.objects.get_or_create(
            provider=p_nvidia,
            model_identifier='deepseek-ai/deepseek-v4.1-flash',
            defaults={
                'display_name': 'DeepSeek v4.1 Flash (NVIDIA)',
                'is_default': True,
                'max_tokens': 1024,
                'temperature': 0.7
            }
        )

        p_deepseek, _ = AIProvider.objects.get_or_create(
            name="DeepSeek Direct",
            defaults={
                'provider_type': 'deepseek',
                'base_url': 'https://api.deepseek.com/v1',
                'description': 'DeepSeek Official API'
            }
        )
        AIModel.objects.get_or_create(
            provider=p_deepseek,
            model_identifier='deepseek-chat',
            defaults={
                'display_name': 'DeepSeek V3 Chat',
                'is_default': False,
                'max_tokens': 1024,
                'temperature': 0.7
            }
        )

        p_kimi, _ = AIProvider.objects.get_or_create(
            name="Kimi (Moonshot)",
            defaults={
                'provider_type': 'kimi',
                'base_url': 'https://api.moonshot.cn/v1',
                'description': 'Moonshot AI API'
            }
        )
        AIModel.objects.get_or_create(
            provider=p_kimi,
            model_identifier='moonshot-v1-8k',
            defaults={
                'display_name': 'Moonshot Kimi 8k',
                'is_default': False,
                'max_tokens': 1024,
                'temperature': 0.7
            }
        )

        p_glm, _ = AIProvider.objects.get_or_create(
            name="GLM (Zhipu AI)",
            defaults={
                'provider_type': 'glm',
                'base_url': 'https://open.bigmodel.cn/api/paas/v4',
                'description': 'Zhipu AI GLM API'
            }
        )
        AIModel.objects.get_or_create(
            provider=p_glm,
            model_identifier='glm-4',
            defaults={
                'display_name': 'GLM-4 General',
                'is_default': False,
                'max_tokens': 1024,
                'temperature': 0.7
            }
        )

        p_openai, _ = AIProvider.objects.get_or_create(
            name="OpenAI",
            defaults={
                'provider_type': 'openai',
                'base_url': 'https://api.openai.com/v1',
                'description': 'OpenAI API'
            }
        )
        AIModel.objects.get_or_create(
            provider=p_openai,
            model_identifier='gpt-4o-mini',
            defaults={
                'display_name': 'GPT-4o Mini',
                'is_default': False,
                'max_tokens': 1024,
                'temperature': 0.7
            }
        )
        self.stdout.write(self.style.SUCCESS("Configured AI Providers & Models (NVIDIA, DeepSeek, Kimi, GLM, OpenAI)."))

        # 3. Safety Rules
        SafetyRule.objects.get_or_create(
            name="Suicide & Self-Harm Prevention",
            defaults={
                'rule_type': 'SUICIDE',
                'risk_level': 'IMMINENT',
                'patterns': "kill myself\nend my life\ncommit suicide\ntake my life\nswallow sniper\ndrink sniper\njump off third mainland bridge\nmake i just die\ni wan kill myself\neasiest way to die\npainless suicide",
                'is_active': True,
                'custom_guidance': "I hear how much pain you are holding right now, and I care deeply about your life and safety. Please reach out to emergency support immediately: MANI Crisis Helpline at 0809 111 6264, She Writes Woman at 0800 800 2000, or call 112. You do not have to walk this alone."
            }
        )
        SafetyRule.objects.get_or_create(
            name="Medical Diagnosis Block",
            defaults={
                'rule_type': 'DIAGNOSIS',
                'risk_level': 'HIGH',
                'patterns': "you have depression\nyou have bipolar\nyou are suffering from clinical depression\nmy diagnosis is",
                'is_active': True,
                'custom_guidance': "I cannot diagnose any health condition. Only a qualified medical or mental health professional can provide a clinical diagnosis."
            }
        )
        SafetyRule.objects.get_or_create(
            name="Prescription & Dosage Block",
            defaults={
                'rule_type': 'PRESCRIPTION',
                'risk_level': 'HIGH',
                'patterns': "take 50mg\ntake 20mg\nswallow pills\nprescribe sertraline\nprescribe xanax",
                'is_active': True,
                'custom_guidance': "I am an AI assistant and cannot prescribe medication or advise on dosages. Please consult a licensed medical doctor or psychiatrist."
            }
        )
        self.stdout.write(self.style.SUCCESS("Seeded default Safety Rules."))

        # 4. Verified Crisis Resources
        for r_data in VERIFIED_NIGERIAN_CRISIS_RESOURCES:
            CrisisResource.objects.get_or_create(
                organization=r_data['organization'],
                phone=r_data['phone'],
                defaults=r_data
            )
        self.stdout.write(self.style.SUCCESS("Seeded verified Nigerian Crisis Resources."))

        # 5. Verified Professionals & Healthcare Centers
        for p_data in VERIFIED_NIGERIAN_PROFESSIONALS:
            Professional.objects.get_or_create(
                name=p_data['name'],
                state=p_data['state'],
                defaults=p_data
            )
        self.stdout.write(self.style.SUCCESS("Seeded verified Nigerian Healthcare Professionals & Centers."))

        # 6. Coping Exercises
        for c_data in DEFAULT_COPING_TOOLS:
            CopingTool.objects.get_or_create(
                slug=c_data['slug'],
                defaults=c_data
            )
        self.stdout.write(self.style.SUCCESS("Seeded Coping Exercises (Breathing, 5-4-3-2-1, PMR, Study planner, Sleep)."))

        # 7. Screening Tools
        for s_key, s_data in QUESTIONNAIRE_DEFINITIONS.items():
            ScreeningTool.objects.get_or_create(
                tool_type=s_key,
                defaults={
                    'name': s_data['name'],
                    'description': s_data['description'],
                    'instructions': s_data['instructions'],
                }
            )
        self.stdout.write(self.style.SUCCESS("Seeded Screening Tool definitions (PHQ-2, PHQ-9, GAD-2, GAD-7)."))

        # 8. Announcements
        Announcement.objects.update_or_create(
            title="Welcome to MindBridge (NSUK Edition)",
            defaults={
                'message': "MindBridge provides culturally sensitive mental health support tailored for the students and campus community of Nasarawa State University, Keffi (NSUK). In an emergency, tap 'Need urgent help?' at the top of your screen to access the NSUK Health Centre, FMC Keffi, or 24/7 national helplines.",
                'priority': 'info',
                'is_active': True
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully completed MindBridge database seeding!"))
