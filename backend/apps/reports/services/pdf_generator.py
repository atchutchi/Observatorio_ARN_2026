import io
from django.template.loader import render_to_string
from apps.dashboards.services import DashboardService
from apps.indicators.models import IndicatorCategory


class PDFReportGenerator:

    def __init__(self, year, quarter=None, report_type='quarterly'):
        self.year = year
        self.quarter = quarter
        self.report_type = report_type

    def generate(self):
        context = self._build_context()

        try:
            from .chart_generator import generate_all_charts
            context['charts'] = generate_all_charts(self.year, self.quarter)
        except Exception:
            context['charts'] = {}

        template = 'reports/quarterly_report.html' if self.report_type == 'quarterly' else 'reports/annual_report.html'
        html_content = render_to_string(template, context)

        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        except ImportError:
            return self._fallback_pdf(html_content)

    def _build_context(self):
        summary = DashboardService.get_summary(self.year, self.quarter)
        categories = IndicatorCategory.objects.all().order_by('order')

        market_shares = {}
        for market in ['mobile', 'fixed_internet', 'revenue']:
            market_shares[market] = DashboardService.get_market_share(
                self.year, self.quarter, market,
            )

        category_data = {}
        for cat in categories:
            category_data[cat.code] = {
                'name': cat.name,
                'data': DashboardService.get_indicator_data(cat.code, self.year, self.quarter),
                'growth': DashboardService.get_growth_rates(cat.code, self.year),
            }

        hhi_mobile = DashboardService.get_hhi(self.year, 'mobile')
        hhi_internet = DashboardService.get_hhi(self.year, 'fixed_internet')

        period_label = f"Q{self.quarter} {self.year}" if self.quarter else str(self.year)

        return {
            'year': self.year,
            'quarter': self.quarter,
            'period_label': period_label,
            'report_type': self.report_type,
            'summary': summary,
            'market_shares': market_shares,
            'category_data': category_data,
            'hhi_mobile': hhi_mobile,
            'hhi_internet': hhi_internet,
            'categories': categories,
        }

    def _fallback_pdf(self, html_content):
        return html_content.encode('utf-8')
