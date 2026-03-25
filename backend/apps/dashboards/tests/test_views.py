from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.operators.models import OperatorType, Operator
from apps.indicators.models import IndicatorCategory, Indicator, OperatorTypeIndicator, Period
from apps.data_entry.models import DataEntry

User = get_user_model()


class DashboardViewsTestMixin:

    def create_test_data(self):
        self.op_type = OperatorType.objects.create(
            code='T', name='Telecomunicações', description='Telecom',
        )
        self.telecel = Operator.objects.create(
            name='Telecel', code='TELECEL', operator_type=self.op_type,
            brand_color='#E30613',
        )
        self.cat = IndicatorCategory.objects.create(
            code='estacoes_moveis', name='Estações Móveis', order=1,
        )
        self.ind = Indicator.objects.create(
            category=self.cat, code='1', name='Total Assinantes',
            unit='number', level=0, order=1,
        )
        OperatorTypeIndicator.objects.create(
            operator_type=self.op_type, indicator=self.ind,
            is_applicable=True, is_mandatory=True,
        )
        self.period = Period.objects.create(
            year=2024, quarter=4, month=12,
            start_date='2024-12-01', end_date='2024-12-31',
        )
        DataEntry.objects.create(
            indicator=self.ind, operator=self.telecel,
            period=self.period, value=Decimal('500000'),
        )


class DashboardSummaryViewTest(DashboardViewsTestMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', role='analyst_arn',
        )
        self.client.force_authenticate(user=self.user)
        self.create_test_data()

    def test_get_summary(self):
        response = self.client.get('/api/v1/dashboard/summary/', {'year': 2024})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_subscribers', response.data)

    def test_summary_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DashboardMarketShareViewTest(DashboardViewsTestMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', role='analyst_arn',
        )
        self.client.force_authenticate(user=self.user)
        self.create_test_data()

    def test_get_market_share(self):
        response = self.client.get('/api/v1/dashboard/market-share/', {
            'year': 2024, 'market': 'mobile',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)


class DashboardHHIViewTest(DashboardViewsTestMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', role='analyst_arn',
        )
        self.client.force_authenticate(user=self.user)
        self.create_test_data()

    def test_get_hhi(self):
        response = self.client.get('/api/v1/dashboard/hhi/', {
            'year': 2024, 'market': 'mobile',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('hhi', response.data)
        self.assertIn('classification', response.data)


class DashboardCAGRViewTest(DashboardViewsTestMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', role='analyst_arn',
        )
        self.client.force_authenticate(user=self.user)
        self.create_test_data()

    def test_get_cagr(self):
        response = self.client.get('/api/v1/dashboard/cagr/', {
            'category': 'estacoes_moveis',
            'start_year': 2023,
            'end_year': 2024,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)


class DashboardTrendsViewTest(DashboardViewsTestMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', role='analyst_arn',
        )
        self.client.force_authenticate(user=self.user)
        self.create_test_data()

    def test_get_trends(self):
        response = self.client.get('/api/v1/dashboard/trends/', {
            'category': 'estacoes_moveis',
            'start_year': 2023,
            'end_year': 2024,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('operators', response.data)


class DashboardExportViewTest(DashboardViewsTestMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', role='analyst_arn',
        )
        self.client.force_authenticate(user=self.user)
        self.create_test_data()

    def test_export_json(self):
        response = self.client.get('/api/v1/dashboard/export/', {
            'category': 'estacoes_moveis', 'year': 2024, 'format': 'json',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_export_requires_category(self):
        response = self.client.get('/api/v1/dashboard/export/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
