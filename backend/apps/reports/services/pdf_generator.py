import io
from django.template.loader import render_to_string
from apps.dashboards.services import DashboardService
from apps.indicators.models import IndicatorCategory
from apps.operators.models import Operator


class PDFReportGenerator:

    def __init__(self, year, quarter=None, report_type='quarterly', operator_code=None, operator_scope='all'):
        self.year = year
        self.quarter = quarter
        self.report_type = report_type
        self.operator_code = operator_code
        self.operator_scope = operator_scope

    def generate(self):
        context = self._build_context()

        try:
            from .chart_generator import generate_all_charts
            context['charts'] = generate_all_charts(
                self.year, self.quarter, self.operator_code,
            )
        except Exception:
            context['charts'] = {}

        for section in context['category_sections']:
            section['chart'] = context['charts'].get(f"trends_{section['code']}")

        template = 'reports/quarterly_report.html' if self.report_type == 'quarterly' else 'reports/annual_report.html'
        html_content = render_to_string(template, context)

        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        except ImportError:
            return self._fallback_pdf(html_content)

    def _build_context(self):
        summary = DashboardService.get_summary(self.year, self.quarter, self.operator_code)
        categories = IndicatorCategory.objects.all().order_by('order')
        operators = DashboardService.get_operators(self.operator_code)

        market_shares = {}
        for market in ['mobile', 'fixed_internet', 'revenue']:
            market_shares[market] = DashboardService.get_market_share(
                self.year, self.quarter, market, self.operator_code,
            )

        category_data = {}
        category_sections = []
        for cat in categories:
            data = DashboardService.get_indicator_data(
                cat.code, self.year, self.quarter, self.operator_code,
            )
            growth = DashboardService.get_growth_rates(cat.code, self.year, self.operator_code)
            category_data[cat.code] = {
                'name': cat.name,
                'data': data,
                'growth': growth,
            }
            category_sections.append(self._build_category_section(cat, data, growth))

        hhi_mobile = DashboardService.get_hhi(self.year, 'mobile')
        hhi_internet = DashboardService.get_hhi(self.year, 'fixed_internet')

        period_label = f"Q{self.quarter} {self.year}" if self.quarter else str(self.year)
        operator_label = self._get_operator_label()

        return {
            'year': self.year,
            'quarter': self.quarter,
            'period_label': period_label,
            'report_type': self.report_type,
            'operator_scope': self.operator_scope,
            'operator_code': self.operator_code,
            'operator_label': operator_label,
            'is_operator_report': self.operator_scope != 'all',
            'operators': operators,
            'summary': summary,
            'market_shares': market_shares,
            'category_data': category_data,
            'category_sections': category_sections,
            'hhi_mobile': hhi_mobile,
            'hhi_internet': hhi_internet,
            'categories': categories,
        }

    def _get_operator_label(self):
        if self.operator_scope == 'others':
            return 'Outros operadores'
        if self.operator_code:
            operator = Operator.objects.filter(code=self.operator_code).first()
            if operator:
                return operator.name
        return 'Mercado geral'

    def _build_category_section(self, category, data, growth):
        operators = []
        indicators = {}

        for item in data:
            operator_name = item['operator_name']
            if operator_name not in operators:
                operators.append(operator_name)

            code = item['indicator_code']
            if code not in indicators:
                indicators[code] = {
                    'code': code,
                    'name': item['indicator_name'],
                    'level': item['indicator_level'],
                    'indent': item['indicator_level'] * 12,
                    'values': {},
                }

            if item['value'] is not None:
                indicators[code]['values'][operator_name] = item['value']

        indicator_rows = []
        for indicator in indicators.values():
            indicator_rows.append({
                'code': indicator['code'],
                'name': indicator['name'],
                'level': indicator['level'],
                'indent': indicator['indent'],
                'values': [
                    indicator['values'].get(operator_name)
                    for operator_name in operators
                ],
            })

        return {
            'order': category.order,
            'code': category.code,
            'name': category.name,
            'operators': operators,
            'indicator_rows': indicator_rows,
            'growth': growth,
            'narrative': self._build_category_narrative(category, data, growth),
        }

    def _build_category_narrative(self, category, data, growth):
        if not data and not growth:
            return ''

        period = f"no {self.quarter}.º trimestre de {self.year}" if self.quarter else f"em {self.year}"
        scope = 'o mercado' if self.operator_scope == 'all' else self._get_operator_label()

        root_values = [
            item for item in data
            if item.get('indicator_level') == 0 and item.get('value') is not None
        ]
        if root_values:
            total = sum(item['value'] for item in root_values)
            return (
                f"{category.name}: {scope} apresentou {len(root_values)} indicadores principais "
                f"com dados {period}, totalizando {total:,.0f} nas métricas reportadas."
            )

        if growth:
            best = max(growth, key=lambda item: item.get('pct_change', 0))
            return (
                f"{category.name}: {scope} registou variação anual relevante {period}; "
                f"o maior crescimento observado foi de {best['pct_change']}% em {best['operator_name']}."
            )

        return f"{category.name}: existem dados reportados {period} para análise regulatória."

    def _fallback_pdf(self, html_content):
        return html_content.encode('utf-8')
