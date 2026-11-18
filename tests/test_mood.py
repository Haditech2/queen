from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.mood.models import MoodCheckIn

class MoodTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='mooduser@example.com',
            password='TestPassword123!',
            first_name='Dayo',
            last_name='Adeleke'
        )
        self.client.login(email='mooduser@example.com', password='TestPassword123!')

    def test_mood_checkin_submission(self):
        resp = self.client.post(reverse('mood:dashboard'), {
            'mood': 'okay',
            'stress_level': 6,
            'sleep_quality': 'fair',
            'note': 'Hectic traffic on Ikorodu road today, but hanging in there.'
        })
        self.assertEqual(resp.status_code, 302)
        checkin = MoodCheckIn.objects.filter(user=self.user).first()
        self.assertIsNotNone(checkin)
        self.assertEqual(checkin.mood, 'okay')
        self.assertEqual(checkin.stress_level, 6)
        self.assertEqual(checkin.mood_emoji, '😐')

    def test_api_mood_checkin(self):
        resp = self.client.post(
            reverse('mood:api_mood_checkin'),
            data={'mood': 'good', 'stress_level': 4, 'sleep_quality': 'good', 'note': 'Restful morning.'},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['mood'], 'good')
        self.assertEqual(data['mood_emoji'], '🙂')
