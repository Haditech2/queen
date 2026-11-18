from datetime import timedelta
from unittest.mock import patch
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.conversations.models import Conversation, Message


class ChatbotFocusTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='chat@example.com', password='Password123!', first_name='Ada'
        )

    def test_logged_in_landing_goes_to_chat(self):
        self.client.login(email='chat@example.com', password='Password123!')
        resp = self.client.get(reverse('core:landing'))
        self.assertRedirects(resp, reverse('conversations:chat'), fetch_redirect_response=False)

    def test_login_redirects_to_chat(self):
        resp = self.client.post(reverse('accounts:login'), {'email': 'chat@example.com', 'password': 'Password123!'})
        self.assertEqual(resp.url, reverse('conversations:chat'))

    def test_login_ignores_external_next_url(self):
        resp = self.client.post(
            reverse('accounts:login') + '?next=https://evil.example.com/',
            {'email': 'chat@example.com', 'password': 'Password123!'},
        )
        self.assertEqual(resp.url, reverse('conversations:chat'))

    def test_landing_page_is_about_the_chatbot(self):
        resp = self.client.get(reverse('core:landing'))
        self.assertContains(resp, 'Start Chatting')
        self.assertContains(resp, 'Safety Pipeline')

    def test_chat_history_sends_most_recent_messages(self):
        self.client.login(email='chat@example.com', password='Password123!')
        conv = Conversation.objects.create(user=self.user, title='History')
        base = timezone.now() - timedelta(hours=1)
        for i in range(15):
            m = Message.objects.create(conversation=conv, role='user' if i % 2 == 0 else 'assistant', content=f'msg-{i}')
            Message.objects.filter(pk=m.pk).update(created_at=base + timedelta(minutes=i))

        with patch('apps.chatbot.service.ChatbotSafetyPipeline.process_message', return_value={
            'content': 'ok', 'risk_level': 'LOW', 'is_crisis': False, 'category': 'NORMAL'
        }) as mock_process:
            resp = self.client.post(reverse('conversations:api_chat_send'), {
                'conversation_id': str(conv.id), 'message': 'latest'
            }, content_type='application/json')

        self.assertEqual(resp.status_code, 200)
        history = mock_process.call_args.kwargs['conversation_history']
        self.assertEqual(len(history), 10)
        self.assertEqual(history[0]['content'], 'msg-5')
        self.assertEqual(history[-1]['content'], 'msg-14')
