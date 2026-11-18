import json
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.conversations.models import Conversation, Message

class ConversationsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='testchat@example.com',
            password='TestPassword123!',
            first_name='Zainab',
            last_name='Aliyu',
            preferred_language='en'
        )
        self.client.login(email='testchat@example.com', password='TestPassword123!')
        self.conv = Conversation.objects.create(
            user=self.user,
            title='Initial Reflection',
            language='en'
        )

    def test_chat_view_render(self):
        resp = self.client.get(reverse('conversations:chat_detail', args=[self.conv.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Initial Reflection')

    from unittest.mock import patch

    @patch('apps.chatbot.ai_client.LLMClient.generate_chat_completion', return_value="I hear you. Balancing family and school duties can be heavy, but you are not alone.")
    def test_api_chat_send_message(self, mock_generate):
        payload = {
            'conversation_id': str(self.conv.id),
            'message': 'I have been having trouble balancing work and family duties.',
            'language': 'en'
        }
        resp = self.client.post(
            reverse('conversations:api_chat_send'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('user_message', data)
        self.assertIn('assistant_message', data)
        self.assertEqual(data['user_message']['content'], payload['message'])
        self.assertTrue(len(data['assistant_message']['content']) > 10)

        # Check messages saved to database
        self.assertEqual(self.conv.messages.count(), 2)

    def test_rename_and_delete_conversation(self):
        # Rename
        rename_resp = self.client.post(
            reverse('conversations:rename_conversation', args=[self.conv.id]),
            {'title': 'Updated Title Reflection'}
        )
        self.assertEqual(rename_resp.status_code, 302)
        self.conv.refresh_from_db()
        self.assertEqual(self.conv.title, 'Updated Title Reflection')

        # Delete
        delete_resp = self.client.post(
            reverse('conversations:delete_conversation', args=[self.conv.id])
        )
        self.assertEqual(delete_resp.status_code, 302)
        self.assertFalse(Conversation.objects.filter(id=self.conv.id).exists())

    def test_report_message(self):
        msg = Message.objects.create(
            conversation=self.conv,
            role='assistant',
            content='Test message to report.'
        )
        report_resp = self.client.post(
            reverse('conversations:api_message_report', args=[msg.id]),
            data=json.dumps({'reason': 'Felt inappropriate'}),
            content_type='application/json'
        )
        self.assertEqual(report_resp.status_code, 200)
        msg.refresh_from_db()
        self.assertTrue(msg.is_reported)
        self.assertEqual(msg.report_reason, 'Felt inappropriate')

    def test_gemini_client_configuration(self):
        """Verify LLMClient properly detects Gemini configuration and sets endpoints."""
        from apps.chatbot.ai_client import LLMClient
        with self.settings(AI_PROVIDER='gemini', AI_API_KEY='test-gemini-key-123', GEMINI_API_KEY='test-gemini-key-123'):
            client = LLMClient()
            self.assertEqual(client.provider, 'gemini')
            self.assertIn('gemini', client.model)
            self.assertIn('googleapis.com', client.base_url)
            self.assertEqual(client.api_key, 'test-gemini-key-123')

    def test_gemini_direct_native_call(self):
        """Verify LLMClient calls Google Gemini native REST endpoint directly with proper API key and candidate model."""
        from unittest.mock import patch, MagicMock
        from apps.chatbot.ai_client import LLMClient

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Hello from Google Gemini! I hear your concerns and I am here with you.'}]
                }
            }]
        }

        with self.settings(AI_PROVIDER='gemini', AI_API_KEY='test-gemini-key-123', GEMINI_API_KEY='test-gemini-key-123'):
            client = LLMClient()
            with patch('requests.post', return_value=mock_resp) as mock_post:
                result = client.generate_chat_completion([
                    {'role': 'system', 'content': 'You are MindBridge.'},
                    {'role': 'user', 'content': 'I am feeling overwhelmed with my semester courses.'}
                ])
                self.assertEqual(result, 'Hello from Google Gemini! I hear your concerns and I am here with you.')
                mock_post.assert_called_once()
                call_url = mock_post.call_args[0][0]
                self.assertIn('generativelanguage.googleapis.com', call_url)
                # The key must travel in a header, never in the URL (URLs end up in logs).
                self.assertNotIn('test-gemini-key-123', call_url)
                self.assertEqual(mock_post.call_args[1]['headers']['x-goog-api-key'], 'test-gemini-key-123')

    def test_gemini_native_rest_model_failover(self):
        """Verify automatic failover across candidate models if one model returns non-200."""
        from unittest.mock import patch, MagicMock
        from apps.chatbot.ai_client import LLMClient

        # First model returns 502, second model candidate returns 200
        mock_err_resp = MagicMock()
        mock_err_resp.status_code = 502
        mock_err_resp.text = 'Bad Gateway'

        mock_native_resp = MagicMock()
        mock_native_resp.status_code = 200
        mock_native_resp.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Hello from Gemini failover model candidate. You are safe.'}]
                }
            }]
        }

        with self.settings(AI_PROVIDER='gemini', AI_API_KEY='test-gemini-key-123', GEMINI_API_KEY='test-gemini-key-123'):
            client = LLMClient()
            with patch('requests.post', side_effect=[mock_err_resp, mock_native_resp]) as mock_post:
                result = client.generate_chat_completion([
                    {'role': 'system', 'content': 'You are MindBridge.'},
                    {'role': 'user', 'content': 'Feeling nervous.'}
                ])
                self.assertEqual(result, 'Hello from Gemini failover model candidate. You are safe.')
                self.assertEqual(mock_post.call_count, 2)

