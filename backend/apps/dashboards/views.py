from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.indicators.models import IndicatorCategory, Indicator
from apps.indicators.serializers import IndicatorCategorySerializer
from .services import DashboardService


DASHBOARD_CACHE_TIMEOUT = int(getattr(settings, 'DASHBOARD_CACHE_TIMEOUT', 300))


def _cache_part(value):
    if value is None or value == '':
        return 'all'
    return str(value).strip().lower()


def _dashboard_cache_key(namespace, *parts):
    safe_parts = ':'.join(_cache_part(part) for part in parts)
    return f'dashboard:v1:{namespace}:{safe_parts}'


def _get_cached_dashboard_data(namespace, parts, factory):
    cache_key = _dashboard_cache_key(namespace, *parts)
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    data = factory()
    cache.set(cache_key, data, DASHBOARD_CACHE_TIMEOUT)
    return data


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = int(request.query_params.get('year', datetime.now().year))
        quarter = request.query_params.get('quarter')
        quarter = int(quarter) if quarter else None
        operator = request.query_params.get('operator')

        data = _get_cached_dashboard_data(
            'summary',
            (year, quarter, operator),
            lambda: DashboardService.get_summary(year, quarter, operator),
        )
        return Response(data)


class DashboardLatestYearView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = _get_cached_dashboard_data(
            'latest_year',
            (),
            lambda: DashboardService.get_latest_data_year() or datetime.now().year,
        )
        return Response({'year': year})


class DashboardIndicatorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, category_code):
        year = int(request.query_params.get('year', datetime.now().year))
        quarter = request.query_params.get('quarter')
        quarter = int(quarter) if quarter else None
        operator = request.query_params.get('operator')
        indicator_code = request.query_params.get('indicator_code')

        try:
            data = DashboardService.get_indicator_data(
                category_code, year, quarter, operator, indicator_code,
            )
        except IndicatorCategory.DoesNotExist:
            return Response(
                {'error': f'Categoria "{category_code}" não encontrada'},
                status=status.HTTP_404_NOT_FOUND,
            )

        category = IndicatorCategory.objects.get(code=category_code)
        indicators = Indicator.objects.filter(
            category=category, level=0,
        ).order_by('order').values('code', 'name', 'unit')

        return Response({
            'category': {
                'code': category.code,
                'name': category.name,
                'is_cumulative': category.is_cumulative,
            },
            'root_indicators': list(indicators),
            'data': data,
        })


class DashboardMarketShareView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = int(request.query_params.get('year', datetime.now().year))
        quarter = request.query_params.get('quarter')
        quarter = int(quarter) if quarter else None
        market = request.query_params.get('market', 'mobile')
        operator = request.query_params.get('operator')

        data = _get_cached_dashboard_data(
            'market_share',
            (year, quarter, market, operator),
            lambda: DashboardService.get_market_share(year, quarter, market, operator),
        )
        return Response({'market': market, 'year': year, 'data': data})


class DashboardTrendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get('category', 'estacoes_moveis')
        indicator = request.query_params.get('indicator')
        start_year = int(request.query_params.get('start_year', 2018))
        end_year = int(request.query_params.get('end_year', datetime.now().year))
        operator = request.query_params.get('operator')

        payload = _get_cached_dashboard_data(
            'trends',
            (category, indicator, start_year, end_year, operator),
            lambda: {
                'data': DashboardService.get_trends(
                    category, indicator, start_year, end_year, operator,
                ),
                'operators': [
                    {'code': op.code, 'name': op.name, 'color': op.brand_color}
                    for op in DashboardService.get_applicable_operators(category, operator)
                ],
            },
        )

        return Response({
            'category': category,
            'indicator': indicator,
            'operators': payload['operators'],
            'data': payload['data'],
        })


class DashboardComparativeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = int(request.query_params.get('year', datetime.now().year))
        operator = request.query_params.get('operator')
        categories = request.query_params.getlist('categories')
        if not categories:
            categories = list(
                IndicatorCategory.objects.values_list('code', flat=True),
            )

        category_to_market = {
            'estacoes_moveis': 'mobile',
            'trafego_originado': 'voice',
            'trafego_terminado': 'voice',
            'trafego_roaming': 'mobile',
            'internet_fixo': 'fixed_internet',
            'internet_trafic': 'data',
            'receitas': 'revenue',
            'empregos': 'employment',
            'investimento': 'revenue',
            'lbi': 'data',
            'tarifario_voz': 'voice',
        }

        results = {}
        for cat_code in categories:
            try:
                growth = DashboardService.get_growth_rates(cat_code, year, operator)
                market_key = category_to_market.get(cat_code, 'mobile')
                market = DashboardService.get_market_share(year, market=market_key, operator_code=operator)
                results[cat_code] = {
                    'growth': growth,
                    'market_share': market,
                }
            except IndicatorCategory.DoesNotExist:
                continue

        return Response({'year': year, 'categories': results})


class DashboardCAGRView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get('category', 'estacoes_moveis')
        start_year = int(request.query_params.get('start_year', 2018))
        end_year = int(request.query_params.get('end_year', datetime.now().year))
        operator = request.query_params.get('operator')

        data = DashboardService.get_cagr(category, start_year, end_year, operator)
        return Response({
            'category': category,
            'start_year': start_year,
            'end_year': end_year,
            'data': data,
        })


class DashboardHHIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = int(request.query_params.get('year', datetime.now().year))
        market = request.query_params.get('market', 'mobile')

        data = _get_cached_dashboard_data(
            'hhi',
            (year, market),
            lambda: DashboardService.get_hhi(year, market),
        )
        return Response(data)


class DashboardHHIHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        market = request.query_params.get('market', 'mobile')
        start_year = int(request.query_params.get('start_year', 2018))
        end_year = int(request.query_params.get('end_year', datetime.now().year))

        return Response({
            'market': market,
            'start_year': start_year,
            'end_year': end_year,
            'data': DashboardService.get_hhi_history(start_year, end_year, market),
        })


class DashboardExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get('category')
        year = int(request.query_params.get('year', datetime.now().year))
        fmt = request.query_params.get('format', 'json')
        operator = request.query_params.get('operator')

        if not category:
            return Response(
                {'error': 'Parâmetro "category" obrigatório'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = DashboardService.get_indicator_data(category, year, operator_code=operator)

        if fmt == 'json':
            return Response(data)

        from django.http import HttpResponse
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment

        wb = openpyxl.Workbook()
        ws = wb.active

        cat = IndicatorCategory.objects.get(code=category)
        ws.title = cat.name[:31]

        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='1B2A4A', end_color='1B2A4A', fill_type='solid')

        headers = ['Indicador', 'Código', 'Operador', 'Período', 'Valor', 'Unidade']
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')

        for row_idx, item in enumerate(data, 2):
            ws.cell(row=row_idx, column=1, value=item['indicator_name'])
            ws.cell(row=row_idx, column=2, value=item['indicator_code'])
            ws.cell(row=row_idx, column=3, value=item['operator_name'])
            ws.cell(row=row_idx, column=4, value=item['period'])
            ws.cell(row=row_idx, column=5, value=item['value'])
            ws.cell(row=row_idx, column=6, value=item['unit'])

        for col in range(1, 7):
            ws.column_dimensions[chr(64 + col)].width = 20

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        suffix = f"_{operator}" if operator else ''
        response['Content-Disposition'] = f'attachment; filename="{category}_{year}{suffix}.xlsx"'
        wb.save(response)
        return response
