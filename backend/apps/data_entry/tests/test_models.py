from decimal import Decimal
from django.test import TestCase

from apps.operators.models import OperatorType, Operator
from apps.indicators.models import IndicatorCategory, Indicator, Period
from apps.data_entry.models import DataEntry, CumulativeData


class DataEntryModelTest(TestCase):

    def setUp(self):
        self.op_type = OperatorType.objects.create(code='T', name='Telecom')
        self.operator = Operator.objects.create(
            name='Telecel', code='TELECEL', operator_type=self.op_type,
        )
        self.cat = IndicatorCategory.objects.create(
            code='test', name='Test', order=1,
        )
        self.indicator = Indicator.objects.create(
            category=self.cat, code='1', name='Ind', unit='number', level=0, order=1,
        )
        self.period = Period.objects.create(
            year=2024, quarter=4, month=12,
            start_date='2024-12-01', end_date='2024-12-31',
        )

    def test_create_entry(self):
        entry = DataEntry.objects.create(
            indicator=self.indicator, operator=self.operator,
            period=self.period, value=Decimal('1000'),
        )
        self.assertEqual(entry.value, Decimal('1000'))
        self.assertFalse(entry.is_validated)
        self.assertEqual(entry.source, 'manual')

    def test_unique_together(self):
        DataEntry.objects.create(
            indicator=self.indicator, operator=self.operator,
            period=self.period, value=Decimal('1000'),
        )
        with self.assertRaises(Exception):
            DataEntry.objects.create(
                indicator=self.indicator, operator=self.operator,
                period=self.period, value=Decimal('2000'),
            )

    def test_str_representation(self):
        entry = DataEntry.objects.create(
            indicator=self.indicator, operator=self.operator,
            period=self.period, value=Decimal('1000'),
        )
        self.assertIn('1', str(entry))
        self.assertIn('TELECEL', str(entry))

    def test_history_tracked(self):
        entry = DataEntry.objects.create(
            indicator=self.indicator, operator=self.operator,
            period=self.period, value=Decimal('1000'),
        )
        self.assertEqual(entry.history.count(), 1)

        entry.value = Decimal('2000')
        entry.save()
        self.assertEqual(entry.history.count(), 2)


class CumulativeDataModelTest(TestCase):

    def setUp(self):
        self.op_type = OperatorType.objects.create(code='T', name='Telecom')
        self.operator = Operator.objects.create(
            name='Telecel', code='TELECEL', operator_type=self.op_type,
        )
        self.cat = IndicatorCategory.objects.create(
            code='receitas', name='Receitas', order=1, is_cumulative=True,
        )
        self.indicator = Indicator.objects.create(
            category=self.cat, code='8', name='Volume Negócios',
            unit='fcfa', level=0, order=1,
        )

    def test_create_cumulative(self):
        cd = CumulativeData.objects.create(
            indicator=self.indicator, operator=self.operator,
            year=2024, cumulative_type='12M', value=Decimal('5000000'),
        )
        self.assertEqual(cd.cumulative_type, '12M')
        self.assertEqual(cd.value, Decimal('5000000'))

    def test_unique_together(self):
        CumulativeData.objects.create(
            indicator=self.indicator, operator=self.operator,
            year=2024, cumulative_type='12M', value=Decimal('5000000'),
        )
        with self.assertRaises(Exception):
            CumulativeData.objects.create(
                indicator=self.indicator, operator=self.operator,
                year=2024, cumulative_type='12M', value=Decimal('6000000'),
            )
