from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.screening.models import ScreeningTool, ScreeningSession
from apps.screening.questionnaires import QUESTIONNAIRE_DEFINITIONS

class ScreeningTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='screeninguser@example.com',
            password='TestPassword123!',
            first_name='Titi',
            last_name='Sowore'
        )
        self.client.login(email='screeninguser@example.com', password='TestPassword123!')

    def test_phq2_scoring_low(self):
        resp = self.client.post(reverse('screening:detail', args=['PHQ2']), {
            'q_0': '0',
            'q_1': '1',
            'consent': 'on'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Within Typical Screening Range')
        self.assertEqual(ScreeningSession.objects.filter(user=self.user).count(), 1)

    def test_phq9_scoring_and_harm_flag(self):
        # 9 questions, with Q9 (index 8) answered as 2 ("more than half the days")
        post_data = {f'q_{i}': '1' for i in range(8)}
        post_data['q_8'] = '2'  # Thoughts of hurting yourself or better off dead
        post_data['consent'] = 'on'

        resp = self.client.post(reverse('screening:detail', args=['PHQ9']), post_data)
        self.assertEqual(resp.status_code, 200)

        # Ensure safety alert is triggered for Q9 endorsement
        self.assertContains(resp, 'We Care About Your Life and Safety')
        self.assertContains(resp, '0809 111 6264') # MANI

        # Ensure Non-diagnostic disclaimer is rendered
        self.assertContains(resp, 'This questionnaire cannot diagnose a mental-health condition')

    def test_gad7_scoring(self):
        post_data = {f'q_{i}': '2' for i in range(7)}
        post_data['consent'] = 'on'
        resp = self.client.post(reverse('screening:detail', args=['GAD7']), post_data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Moderate Anxiety')
