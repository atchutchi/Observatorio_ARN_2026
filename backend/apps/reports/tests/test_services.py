from decimal import Decimal

from django.test import TestCase
from django.template.loader import render_to_string

from apps.data_entry.models import DataEntry
from apps.indicators.models import Indicator, IndicatorCategory, OperatorTypeIndicator, Period
from apps.operators.models import Operator, OperatorType
from apps.reports.services.pdf_generator import PDFReportGenerator


class PDFReportGeneratorTest(TestCase):

    def setUp(self):
        op_type = OperatorType.objects.create(
            code='MOBILE',
            name='Móvel',
            description='Operadores móveis',
        )
        operator = Operator.objects.create(
            name='Telecel',
            code='TELECEL',
            operator_type=op_type,
            brand_color='#E30613',
        )
        category = IndicatorCategory.objects.create(
            code='estacoes_moveis',
            name='Estações Móveis',
            order=1,
        )
        indicator = Indicator.objects.create(
            category=category,
            code='1',
            name='Total Assinantes',
            unit='number',
            level=0,
            order=1,
        )
        OperatorTypeIndicator.objects.create(
            operator_type=op_type,
            indicator=indicator,
            is_applicable=True,
            is_mandatory=True,
        )
        current_period = Period.objects.create(
            year=2024,
            quarter=1,
            month=3,
            start_date='2024-03-01',
            end_date='2024-03-31',
        )
        previous_period = Period.objects.create(
            year=2023,
            quarter=4,
            month=12,
            start_date='2023-12-01',
            end_date='2023-12-31',
        )
        DataEntry.objects.create(
            indicator=indicator,
            operator=operator,
            period=current_period,
            value=Decimal('500000'),
        )
        DataEntry.objects.create(
            indicator=indicator,
            operator=operator,
            period=previous_period,
            value=Decimal('400000'),
        )

    def test_quarterly_template_renders_category_sections(self):
        context = PDFReportGenerator(
            year=2024,
            quarter=1,
            report_type='quarterly',
        )._build_context()

        html = render_to_string('reports/quarterly_report.html', context)

        self.assertIn('Estações Móveis', html)
        self.assertIn('Crescimento Anual', html)
        self.assertIn('Telecel', html)
