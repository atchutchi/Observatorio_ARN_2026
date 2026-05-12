from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.data_entry.models import DataEntry, FileUpload
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
