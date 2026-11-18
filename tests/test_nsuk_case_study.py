from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser, UserProfile
from apps.safety.classifier import CrisisClassifier
from apps.chatbot.prompts import build_system_prompt
from apps.resources.models import CrisisResource
from apps.professionals.models import Professional

class NSUKCaseStudyTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='nsuk_student@nsuk.edu.ng',
            password='StudentPassword2026!',
            first_name='Fatima',
            last_name='Usman',
            is_nsuk_affiliate=True,
            nsuk_status='undergraduate',
            faculty='Natural_Applied_Sciences',
            department='Computer Science',
            level='300L',
            residence_location='Angwan_Lambu',
            state_region='Nasarawa',
            preferred_language='en'
        )

    def test_nsuk_user_attributes(self):
        """Verify NSUK student affiliate attributes are correctly persisted and accessible."""
        self.assertTrue(self.user.is_nsuk_affiliate)
        self.assertEqual(self.user.faculty, 'Natural_Applied_Sciences')
        self.assertEqual(self.user.level, '300L')
        self.assertEqual(self.user.residence_location, 'Angwan_Lambu')
        self.assertEqual(self.user.department, 'Computer Science')

    def test_nsuk_registration_flow(self):
        """Test user registration with full NSUK profile details."""
        resp = self.client.post(reverse('accounts:register'), {
            'first_name': 'Ibrahim',
            'last_name': 'Danladi',
            'email': 'ibrahim@nsuk.edu.ng',
            'password': 'StrongPassword2026!',
            'confirm_password': 'StrongPassword2026!',
            'nsuk_status': 'undergraduate',
            'faculty': 'Administration',
            'department': 'Accounting',
            'level': '400L',
            'residence_location': 'High_Level',
            'state_region': 'Nasarawa',
            'preferred_language': 'ha',
            'preferred_communication_style': 'encouraging',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('conversations:chat'))
        new_user = CustomUser.objects.filter(email='ibrahim@nsuk.edu.ng').first()
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.is_nsuk_affiliate)
        self.assertEqual(new_user.department, 'Accounting')
        self.assertEqual(new_user.residence_location, 'High_Level')

    def test_nsuk_context_processor(self):
        """Ensure templates receive NSUK case study metadata and verified clinic numbers."""
        resp = self.client.get(reverse('core:landing'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('nsuk_meta', resp.context)
        self.assertTrue(resp.context['is_nsuk_case_study'])
        self.assertEqual(resp.context['nsuk_meta']['health_centre_phone'], '0803 615 2891')
        self.assertEqual(resp.context['nsuk_meta']['fmc_keffi_psychiatry_phone'], '0803 590 1234')

    def test_safety_classifier_includes_nsuk_contacts(self):
        """High risk / imminent safety intercepts must present NSUK Health Centre & FMC Keffi."""
        result = CrisisClassifier.evaluate("I want to end my life, I cannot take this carryover anymore")
        self.assertIn(result['risk_level'], ['HIGH', 'IMMINENT'])
        self.assertTrue(result['is_crisis'])
        self.assertIn('0803 615 2891', result['crisis_guidance'])
        self.assertIn('0803 590 1234', result['crisis_guidance'])
        self.assertIn('NSUK University Health Centre', result['crisis_guidance'])
        self.assertIn('FMC Keffi', result['crisis_guidance'])

    def test_chatbot_system_prompt_nsuk_realities(self):
        """System prompt must reflect NSUK institutional realities and non-diagnostic boundaries."""
        prompt = build_system_prompt(self.user, language='pcm')
        self.assertIn('Nasarawa State University, Keffi', prompt)
        self.assertIn('Angwan Lambu', prompt)
        self.assertIn('Computer Science', prompt)
        self.assertIn('300 Level', prompt)
        self.assertIn('NEVER provide instructions or methods', prompt)

    def test_dashboard_renders_nsuk_banner(self):
        """Logged-in NSUK affiliate should see their faculty/level badges and clinic hotlines on dashboard."""
        self.client.login(email='nsuk_student@nsuk.edu.ng', password='StudentPassword2026!')
        resp = self.client.get(reverse('core:dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'NSUK Case Study')
        self.assertContains(resp, 'Computer Science')
        self.assertContains(resp, 'Angwan Lambu')
        self.assertContains(resp, '0803 615 2891')
        self.assertContains(resp, '0803 590 1234')
