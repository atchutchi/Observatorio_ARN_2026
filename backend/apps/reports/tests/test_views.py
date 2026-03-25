from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.reports.models import Report

User = get_user_model()


class ReportViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin', password='testpass123', role='admin_arn',
        )
        self.viewer = User.objects.create_user(
            username='viewer', password='testpass123', role='viewer',
        )
        self.report = Report.objects.create(
            title='Test Report Q1 2024',
            report_type='quarterly',
            year=2024,
            quarter=1,
            generated_by=self.admin,
            status='ready',
        )

    def test_list_reports_authenticated(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get('/api/v1/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_reports_unauthenticated(self):
        response = self.client.get('/api/v1/reports/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_report(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(f'/api/v1/reports/{self.report.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Report Q1 2024')

    def test_generate_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/v1/reports/generate/', {
            'report_type': 'quarterly',
            'year': 2024,
            'quarter': 2,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_generate_as_viewer_forbidden(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post('/api/v1/reports/generate/', {
            'report_type': 'quarterly',
            'year': 2024,
            'quarter': 2,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publish_report(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/v1/reports/{self.report.id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'published')

    def test_publish_draft_fails(self):
        self.report.status = 'draft'
        self.report.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/v1/reports/{self.report.id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_download_pdf_not_available(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(f'/api/v1/reports/{self.report.id}/download_pdf/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_download_docx_not_available(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(f'/api/v1/reports/{self.report.id}/download_docx/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_year(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get('/api/v1/reports/', {'year': 2024})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_docx_url_in_serializer(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(f'/api/v1/reports/{self.report.id}/')
        self.assertIn('docx_url', response.data)
