from django.test import TestCase, Client
from django.urls import reverse
from apps.resources.models import CrisisResource
from apps.professionals.models import Professional
from apps.coping.models import CopingTool

class ResourcesAndProfessionalsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_crisis_support_page_and_seeding(self):
        resp = self.client.get(reverse('resources:crisis_support'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Mentally Aware Nigeria Initiative')
        self.assertContains(resp, 'She Writes Woman')
        self.assertContains(resp, '08091116264')

    def test_crisis_support_state_filter(self):
        resp = self.client.get(reverse('resources:crisis_support') + '?state=Lagos')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Lagos')

    def test_professionals_directory_page(self):
        resp = self.client.get(reverse('professionals:directory'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Federal Neuro-Psychiatric Hospital Yaba')
        self.assertContains(resp, 'Verified')

    def test_professionals_search_filter(self):
        resp = self.client.get(reverse('professionals:directory') + '?q=UCH')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'University College Hospital')

    def test_coping_tools_page_and_interactive_detail(self):
        resp = self.client.get(reverse('coping:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Box Breathing')

        detail_resp = self.client.get(reverse('coping:detail', args=['box-breathing']))
        # In detail view, authentication is required
        self.assertIn(detail_resp.status_code, [200, 302])
