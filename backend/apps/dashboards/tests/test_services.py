from decimal import Decimal
from django.test import TestCase

from apps.operators.models import OperatorType, Operator
from apps.indicators.models import IndicatorCategory, Indicator, OperatorTypeIndicator, Period
from apps.data_entry.models import DataEntry
from apps.dashboards.services import DashboardService


class DashboardServiceTestMixin:
    """Shared setup for dashboard tests — creates operators, indicators, periods, and data."""

    def create_test_data(self):
        self.op_type = OperatorType.objects.create(
            code='T', name='Telecomunicações', description='Telecom',
        )
        self.telecel = Operator.objects.create(
            name='Telecel', code='TELECEL', operator_type=self.op_type,
            brand_color='#E30613',
        )
        self.orange = Operator.objects.create(
            name='Orange', code='ORANGE', operator_type=self.op_type,
            brand_color='#FF6600',
        )

        self.cat_mobile = IndicatorCategory.objects.create(
            code='estacoes_moveis', name='Estações Móveis', order=1,
        )
        self.ind_total = Indicator.objects.create(
            category=self.cat_mobile, code='1', name='Total Assinantes',
            unit='number', level=0, order=1,
        )

        OperatorTypeIndicator.objects.create(
            operator_type=self.op_type, indicator=self.ind_total,
            is_applicable=True, is_mandatory=True,
        )

        self.period_2024_12 = Period.objects.create(
            year=2024, quarter=4, month=12,
            start_date='2024-12-01', end_date='2024-12-31',
        )
        self.period_2023_12 = Period.objects.create(
            year=2023, quarter=4, month=12,
            start_date='2023-12-01', end_date='2023-12-31',
        )

        DataEntry.objects.create(
            indicator=self.ind_total, operator=self.telecel,
            period=self.period_2024_12, value=Decimal('500000'),
        )
        DataEntry.objects.create(
            indicator=self.ind_total, operator=self.orange,
            period=self.period_2024_12, value=Decimal('300000'),
        )
        DataEntry.objects.create(
            indicator=self.ind_total, operator=self.telecel,
            period=self.period_2023_12, value=Decimal('450000'),
        )
        DataEntry.objects.create(
            indicator=self.ind_total, operator=self.orange,
            period=self.period_2023_12, value=Decimal('280000'),
        )


class GetSummaryTest(DashboardServiceTestMixin, TestCase):

    def setUp(self):
        self.create_test_data()

    def test_returns_summary_dict(self):
        result = DashboardService.get_summary(2024)
        self.assertIn('total_subscribers', result)
        self.assertIn('penetration_rate', result)
        self.assertIn('active_operators', result)
        self.assertEqual(result['year'], 2024)

    def test_total_subscribers_correct(self):
        result = DashboardService.get_summary(2024)
        self.assertEqual(result['total_subscribers'], 800000.0)

    def test_subscriber_change_positive(self):
        result = DashboardService.get_summary(2024)
        expected_change = round((800000 - 730000) / 730000 * 100, 1)
        self.assertAlmostEqual(result['subscriber_change'], expected_change, places=0)


class GetMarketShareTest(DashboardServiceTestMixin, TestCase):

    def setUp(self):
        self.create_test_data()

    def test_returns_operator_shares(self):
        result = DashboardService.get_market_share(2024, market='mobile')
        self.assertEqual(len(result), 2)

    def test_shares_sum_to_100(self):
        result = DashboardService.get_market_share(2024, market='mobile')
        total_pct = sum(s['share_pct'] for s in result)
        self.assertAlmostEqual(total_pct, 100.0, places=0)

    def test_telecel_leads(self):
        result = DashboardService.get_market_share(2024, market='mobile')
        self.assertEqual(result[0]['operator_code'], 'TELECEL')

    def test_empty_for_missing_year(self):
        result = DashboardService.get_market_share(2010, market='mobile')
        self.assertEqual(result, [])


class GetHHITest(DashboardServiceTestMixin, TestCase):

    def setUp(self):
        self.create_test_data()

    def test_hhi_calculated(self):
        result = DashboardService.get_hhi(2024, 'mobile')
        self.assertIn('hhi', result)
        self.assertIn('classification', result)
        self.assertGreater(result['hhi'], 0)

    def test_hhi_classification(self):
        result = DashboardService.get_hhi(2024, 'mobile')
        self.assertIn(result['classification'], [
            'Altamente concentrado', 'Moderadamente concentrado', 'Competitivo',
        ])


class GetGrowthRatesTest(DashboardServiceTestMixin, TestCase):

    def setUp(self):
        self.create_test_data()

    def test_growth_rates_returned(self):
        result = DashboardService.get_growth_rates('estacoes_moveis', 2024)
        self.assertEqual(len(result), 2)
        for item in result:
            self.assertIn('pct_change', item)
            self.assertIn('operator_code', item)

    def test_telecel_growth_positive(self):
        result = DashboardService.get_growth_rates('estacoes_moveis', 2024)
        telecel = next(r for r in result if r['operator_code'] == 'TELECEL')
        self.assertGreater(telecel['pct_change'], 0)


class GetCAGRTest(DashboardServiceTestMixin, TestCase):

    def setUp(self):
        self.create_test_data()

    def test_cagr_calculated(self):
        result = DashboardService.get_cagr('estacoes_moveis', 2023, 2024)
        self.assertGreater(len(result), 0)
        total = next(r for r in result if r['operator_code'] == 'TOTAL')
        self.assertIn('cagr', total)

    def test_cagr_returns_empty_for_same_year(self):
        result = DashboardService.get_cagr('estacoes_moveis', 2024, 2024)
        self.assertEqual(result, [])

    def test_cagr_positive_for_growing_market(self):
        result = DashboardService.get_cagr('estacoes_moveis', 2023, 2024)
        telecel = next(r for r in result if r['operator_code'] == 'TELECEL')
        self.assertGreater(telecel['cagr'], 0)
