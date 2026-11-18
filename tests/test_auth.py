import json
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser, UserProfile

class AccountsAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'first_name': 'Chinedu',
            'last_name': 'Okafor',
            'email': 'chinedu@example.com',
            'phone_number': '+2348012345678',
            'password': 'SecurePassword2026!',
            'confirm_password': 'SecurePassword2026!',
            'age_range': '25_34',
            'gender': 'male',
            'state_region': 'Lagos',
            'preferred_language': 'pcm',
            'preferred_communication_style': 'gentle',
        }
        self.user = CustomUser.objects.create_user(
            email='existing@example.com',
            password='Password123!',
            first_name='Amina',
            last_name='Bello',
            state_region='Kano',
            preferred_language='en'
        )

    def test_registration_success(self):
        response = self.client.post(reverse('accounts:register'), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('conversations:chat'))
        self.assertTrue('_auth_user_id' in self.client.session)
        created_user = CustomUser.objects.filter(email='chinedu@example.com').first()
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.first_name, 'Chinedu')
        self.assertEqual(created_user.preferred_language, 'pcm')
        self.assertTrue(hasattr(created_user, 'profile'))

    def test_login_and_logout(self):
        login_resp = self.client.post(reverse('accounts:login'), {
            'email': 'existing@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(login_resp.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

        logout_resp = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_resp.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_profile_update(self):
        self.client.login(email='existing@example.com', password='Password123!')
        resp = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Amina Updated',
            'last_name': 'Bello',
            'phone_number': '+2348099998888',
            'age_range': '18_24',
            'gender': 'female',
            'state_region': 'FCT',
            'preferred_language': 'ha',
            'preferred_communication_style': 'encouraging',
            'support_choices': ['family', 'faith', 'professional'],
            'faith_preference': 'Islam',
            'allow_ai_personalization': 'on',
            'explicit_screening_consent': 'on',
            'daily_checkin_reminder': 'on'
        })
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Amina Updated')
        self.assertEqual(self.user.preferred_language, 'ha')
        self.assertEqual(self.user.profile.faith_preference, 'Islam')

    def test_export_personal_data_json(self):
        self.client.login(email='existing@example.com', password='Password123!')
        resp = self.client.get(reverse('accounts:export_data'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json')
        data = json.loads(resp.content)
        self.assertEqual(data['user']['email'], 'existing@example.com')
        self.assertIn('conversations', data)
        self.assertIn('mood_checkins', data)
        self.assertIn('screenings', data)

    def test_delete_account(self):
        self.client.login(email='existing@example.com', password='Password123!')
        resp = self.client.post(reverse('accounts:delete_account'), {'confirm_text': 'DELETE'})
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(CustomUser.objects.filter(email='existing@example.com').exists())
