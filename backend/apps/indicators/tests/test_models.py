from django.test import TestCase
from apps.indicators.models import IndicatorCategory, Indicator, Period
from apps.operators.models import OperatorType
from apps.indicators.models import OperatorTypeIndicator


class IndicatorCategoryTest(TestCase):

    def test_create_category(self):
        cat = IndicatorCategory.objects.create(
            code='test_cat', name='Test Category', order=1,
        )
        self.assertEqual(str(cat), 'Test Category')
        self.assertFalse(cat.is_cumulative)

    def test_cumulative_category(self):
        cat = IndicatorCategory.objects.create(
            code='receitas', name='Receitas', order=1, is_cumulative=True,
        )
        self.assertTrue(cat.is_cumulative)


class IndicatorTest(TestCase):

    def setUp(self):
        self.cat = IndicatorCategory.objects.create(
            code='test', name='Test', order=1,
        )

    def test_create_indicator(self):
        ind = Indicator.objects.create(
            category=self.cat, code='1', name='Test Indicator',
            unit='number', level=0, order=1,
        )
        self.assertEqual(ind.category, self.cat)

    def test_hierarchy(self):
        parent = Indicator.objects.create(
            category=self.cat, code='1', name='Parent', unit='number', level=0, order=1,
        )
        child = Indicator.objects.create(
            category=self.cat, code='1.1', name='Child', unit='number',
            level=1, order=2, parent=parent,
        )
        self.assertEqual(child.parent, parent)

    def test_unique_together(self):
        Indicator.objects.create(
            category=self.cat, code='1', name='Ind 1', unit='number', level=0, order=1,
        )
        with self.assertRaises(Exception):
            Indicator.objects.create(
                category=self.cat, code='1', name='Ind 1 Dup', unit='number', level=0, order=2,
            )


class PeriodTest(TestCase):

    def test_create_period(self):
        p = Period.objects.create(
            year=2024, quarter=1, month=1,
            start_date='2024-01-01', end_date='2024-01-31',
        )
        self.assertEqual(p.year, 2024)
        self.assertFalse(p.is_locked)

    def test_unique_together(self):
        Period.objects.create(
            year=2024, quarter=1, month=1,
            start_date='2024-01-01', end_date='2024-01-31',
        )
        with self.assertRaises(Exception):
            Period.objects.create(
                year=2024, quarter=1, month=1,
                start_date='2024-01-01', end_date='2024-01-31',
            )


class OperatorTypeIndicatorTest(TestCase):

    def test_applicability(self):
        op_type = OperatorType.objects.create(code='T', name='Telecom')
        cat = IndicatorCategory.objects.create(code='test', name='Test', order=1)
        ind = Indicator.objects.create(
            category=cat, code='1', name='Ind', unit='number', level=0, order=1,
        )
        oti = OperatorTypeIndicator.objects.create(
            operator_type=op_type, indicator=ind,
            is_applicable=True, is_mandatory=True,
        )
        self.assertTrue(oti.is_applicable)
        self.assertTrue(oti.is_mandatory)
