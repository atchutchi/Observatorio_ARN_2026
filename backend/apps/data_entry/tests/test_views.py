from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.data_entry.models import DataEntry, FileUpload, ReceivedDocument
from apps.indicators.models import IndicatorCategory, Indicator, Period
from apps.operators.models import Operator, OperatorType

User = get_user_model()


class DataEntryViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin', password='testpass123', role='admin_arn',
        )
        self.operator_type = OperatorType.objects.create(code='MOBILE', name='Móvel')
        self.telecel = Operator.objects.create(
            name='Telecel', code='TELECEL', operator_type=self.operator_type,
        )
        self.orange = Operator.objects.create(
            name='Orange', code='ORANGE', operator_type=self.operator_type,
        )
        self.category = IndicatorCategory.objects.create(
            code='estacoes_moveis', name='Estações Móveis', order=1,
        )
        self.indicator = Indicator.objects.create(
            category=self.category, code='1', name='Parque', unit='number', level=0, order=1,
        )
        self.period_2024 = Period.objects.create(
            year=2024, quarter=4, month=12,
            start_date='2024-12-01', end_date='2024-12-31',
        )
        self.period_2023 = Period.objects.create(
            year=2023, quarter=4, month=12,
            start_date='2023-12-01', end_date='2023-12-31',
        )

    def test_pending_validation_applies_filters(self):
        DataEntry.objects.create(
            indicator=self.indicator,
            operator=self.telecel,
            period=self.period_2024,
            value=Decimal('10'),
            source='manual',
        )
        DataEntry.objects.create(
            indicator=self.indicator,
            operator=self.orange,
            period=self.period_2023,
            value=Decimal('20'),
            source='manual',
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get('/api/v1/data/pending_validation/', {
            'operator__code': 'TELECEL',
            'period__year': '2024',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['operator_code'], 'TELECEL')


class FileUploadViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.operator_type = OperatorType.objects.create(code='MOBILE', name='Móvel')
        self.telecel = Operator.objects.create(
            name='Telecel', code='TELECEL', operator_type=self.operator_type,
        )
        self.orange = Operator.objects.create(
            name='Orange', code='ORANGE', operator_type=self.operator_type,
        )
        self.admin = User.objects.create_user(
            username='admin', password='testpass123', role='admin_arn',
        )
        self.operator_user = User.objects.create_user(
            username='operator', password='testpass123',
            role='operator_telecel', operator=self.telecel,
        )

    def _file(self):
        return SimpleUploadedFile(
            'dados.xlsx',
            b'fake spreadsheet',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_admin_upload_requires_operator(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/v1/uploads/', {
            'file': self._file(),
            'file_type': 'other',
            'year': 2024,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_upload_uses_selected_operator(self):
        self.client.force_authenticate(user=self.admin)
        with patch('apps.data_entry.tasks.process_excel_upload.delay'):
            response = self.client.post('/api/v1/uploads/', {
                'file': self._file(),
                'file_type': 'other',
                'year': 2024,
                'operator': self.orange.id,
            }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        upload = FileUpload.objects.get(id=response.data['id'])
        self.assertEqual(upload.operator, self.orange)

    def test_operator_upload_ignores_submitted_operator(self):
        self.client.force_authenticate(user=self.operator_user)
        with patch('apps.data_entry.tasks.process_excel_upload.delay'):
            response = self.client.post('/api/v1/uploads/', {
                'file': self._file(),
                'file_type': 'other',
                'year': 2024,
                'operator': self.orange.id,
            }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        upload = FileUpload.objects.get(id=response.data['id'])
        self.assertEqual(upload.operator, self.telecel)


class ReceivedDocumentViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.operator_type = OperatorType.objects.create(code='MOBILE', name='Móvel')
        self.orange = Operator.objects.create(
            name='Orange', code='ORANGE', operator_type=self.operator_type,
        )
        self.admin = User.objects.create_user(
            username='admin_docs', password='testpass123', role='admin_arn',
        )
        self.viewer = User.objects.create_user(
            username='viewer_docs', password='testpass123', role='viewer',
        )

    def _file(self, name='orange_2024.xlsx'):
        return SimpleUploadedFile(
            name,
            b'fake spreadsheet',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_staff_can_register_received_document(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/v1/received-documents/', {
            'operator': self.orange.id,
            'file': self._file(),
            'document_type': 'questionnaire',
            'year': 2024,
            'priority': 'high',
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        document = ReceivedDocument.objects.get(id=response.data['id'])
        self.assertEqual(document.operator, self.orange)
        self.assertEqual(document.received_by, self.admin)
        self.assertEqual(document.assigned_to, self.admin)
        self.assertEqual(document.original_filename, 'orange_2024.xlsx')

    def test_viewer_cannot_register_received_document(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post('/api/v1/received-documents/', {
            'operator': self.orange.id,
            'file': self._file(),
            'document_type': 'questionnaire',
            'year': 2024,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_summary_counts_open_overdue_and_high_priority(self):
        ReceivedDocument.objects.create(
            operator=self.orange,
            file=self._file('late.xlsx'),
            original_filename='late.xlsx',
            year=2024,
            status='reviewing',
            priority='high',
            due_date=timezone.localdate() - timedelta(days=1),
            received_by=self.admin,
            assigned_to=self.admin,
        )
        ReceivedDocument.objects.create(
            operator=self.orange,
            file=self._file('done.xlsx'),
            original_filename='done.xlsx',
            year=2024,
            status='imported',
            priority='normal',
            received_by=self.admin,
            assigned_to=self.admin,
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get('/api/v1/received-documents/summary/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(response.data['open'], 1)
        self.assertEqual(response.data['overdue'], 1)
        self.assertEqual(response.data['high_priority'], 1)

    def test_send_to_import_creates_linked_upload(self):
        document = ReceivedDocument.objects.create(
            operator=self.orange,
            file=self._file('orange.xlsx'),
            original_filename='orange.xlsx',
            document_type='kpi_summary',
            year=2024,
            received_by=self.admin,
            assigned_to=self.admin,
        )
        self.client.force_authenticate(user=self.admin)

        with patch('apps.data_entry.tasks.process_excel_upload.delay') as task_delay:
            response = self.client.post(
                f'/api/v1/received-documents/{document.id}/send_to_import/',
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        upload = FileUpload.objects.get(received_document=document)
        self.assertEqual(upload.operator, self.orange)
        self.assertEqual(upload.file_type, 'kpi_orange')
        self.assertEqual(upload.original_filename, 'orange.xlsx')
        self.assertEqual(upload.file.name, document.file.name)
        task_delay.assert_called_once_with(upload.id)

        document.refresh_from_db()
        self.assertEqual(document.status, 'extracting')

    def test_send_to_import_reuses_active_upload(self):
        document = ReceivedDocument.objects.create(
            operator=self.orange,
            file=self._file('orange.xlsx'),
            original_filename='orange.xlsx',
            year=2024,
            received_by=self.admin,
            assigned_to=self.admin,
        )
        upload = FileUpload.objects.create(
            operator=self.orange,
            uploaded_by=self.admin,
            received_document=document,
            file=document.file.name,
            original_filename='orange.xlsx',
            file_type='questionnaire_orange',
            year=2024,
            status='processed',
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f'/api/v1/received-documents/{document.id}/send_to_import/',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['upload']['id'], upload.id)
        self.assertEqual(FileUpload.objects.filter(received_document=document).count(), 1)
