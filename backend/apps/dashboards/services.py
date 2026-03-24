from decimal import Decimal
from django.conf import settings
from django.db.models import Sum, Q, F, Value, CharField
from django.db.models.functions import Coalesce

from apps.operators.models import Operator
from apps.indicators.models import (
    IndicatorCategory, Indicator, OperatorTypeIndicator, Period,
)
from apps.data_entry.models import DataEntry, CumulativeData


class DashboardService:

    @staticmethod
    def get_operators():
        return Operator.objects.filter(is_active=True).select_related('operator_type')

    @staticmethod
    def get_applicable_operators(category_code):
        category = IndicatorCategory.objects.get(code=category_code)
        root_indicators = Indicator.objects.filter(category=category, level=0)
        if not root_indicators.exists():
            return Operator.objects.none()

        first_root = root_indicators.first()
        applicable_type_ids = OperatorTypeIndicator.objects.filter(
            indicator=first_root, is_applicable=True,
        ).values_list('operator_type_id', flat=True)

        return Operator.objects.filter(
            operator_type_id__in=applicable_type_ids, is_active=True,
        )

    @staticmethod
    def get_summary(year, quarter=None):
        period_filter = Q(period__year=year)
        if quarter:
            period_filter &= Q(period__quarter=quarter)

        operators = Operator.objects.filter(is_active=True)

        mobile_cat = IndicatorCategory.objects.filter(code='estacoes_moveis').first()
        total_subscribers = Decimal('0')
        if mobile_cat:
            root = Indicator.objects.filter(category=mobile_cat, code='1').first()
            if root:
                latest_period = Period.objects.filter(year=year).order_by('-month').first()
                if latest_period:
                    total_subscribers = DataEntry.objects.filter(
                        indicator=root, period=latest_period,
                    ).aggregate(total=Coalesce(Sum('value'), Decimal('0')))['total']

        revenue_cat = IndicatorCategory.objects.filter(code='receitas').first()
        total_revenue = Decimal('0')
        if revenue_cat:
            root = Indicator.objects.filter(category=revenue_cat, code='8').first()
            if root:
                cum = CumulativeData.objects.filter(
                    indicator=root, year=year, cumulative_type='12M',
                ).aggregate(total=Coalesce(Sum('value'), Decimal('0')))['total']
                if cum == Decimal('0'):
                    cum = CumulativeData.objects.filter(
                        indicator=root, year=year,
                    ).order_by('-cumulative_type').values_list('value', flat=True).first()
                    if cum:
                        total_revenue = CumulativeData.objects.filter(
                            indicator=root, year=year,
                        ).order_by('-cumulative_type').aggregate(
                            total=Coalesce(Sum('value'), Decimal('0')),
                        )['total']
                else:
                    total_revenue = cum

        data_cat = IndicatorCategory.objects.filter(code='trafego_originado').first()
        total_data_traffic = Decimal('0')
        if data_cat:
            root = Indicator.objects.filter(category=data_cat, code='4').first()
            if root:
                total_data_traffic = DataEntry.objects.filter(
                    indicator=root, period__year=year,
                ).aggregate(total=Coalesce(Sum('value'), Decimal('0')))['total']

        population = settings.POPULATION_REFERENCE
        penetration_rate = (
            float(total_subscribers) / population * 100 if population and total_subscribers else 0
        )

        prev_subscribers = Decimal('0')
        if mobile_cat:
            root = Indicator.objects.filter(category=mobile_cat, code='1').first()
            if root:
                prev_period = Period.objects.filter(year=year - 1).order_by('-month').first()
                if prev_period:
                    prev_subscribers = DataEntry.objects.filter(
                        indicator=root, period=prev_period,
                    ).aggregate(total=Coalesce(Sum('value'), Decimal('0')))['total']

        sub_change = 0
        if prev_subscribers and prev_subscribers > 0:
            sub_change = float((total_subscribers - prev_subscribers) / prev_subscribers * 100)

        return {
            'total_subscribers': float(total_subscribers),
            'total_revenue': float(total_revenue),
            'total_data_traffic': float(total_data_traffic),
            'penetration_rate': round(penetration_rate, 1),
            'subscriber_change': round(sub_change, 1),
            'active_operators': operators.count(),
            'year': year,
            'quarter': quarter,
        }

    @staticmethod
    def get_indicator_data(category_code, year, quarter=None, operator_code=None, indicator_code=None):
        category = IndicatorCategory.objects.get(code=category_code)
        indicators = Indicator.objects.filter(category=category).order_by('order')

        if indicator_code:
            indicators = indicators.filter(code=indicator_code)

        operator_filter = Q()
        if operator_code:
            operator_filter = Q(operator__code=operator_code)

        applicable_ops = DashboardService.get_applicable_operators(category_code)

        if category.is_cumulative:
            entries = CumulativeData.objects.filter(
                indicator__in=indicators, year=year,
            ).filter(operator__in=applicable_ops).filter(operator_filter).select_related(
                'indicator', 'operator',
            ).order_by('indicator__order', 'cumulative_type')

            result = []
            for entry in entries:
                result.append({
                    'indicator_code': entry.indicator.code,
                    'indicator_name': entry.indicator.name,
                    'indicator_level': entry.indicator.level,
                    'operator_code': entry.operator.code,
                    'operator_name': entry.operator.name,
                    'operator_color': entry.operator.brand_color,
                    'period': f"{year}-{entry.cumulative_type}",
                    'cumulative_type': entry.cumulative_type,
                    'value': float(entry.value) if entry.value else None,
                    'unit': entry.indicator.unit,
                })
            return result

        period_filter = Q(period__year=year)
        if quarter:
            period_filter &= Q(period__quarter=quarter)

        entries = DataEntry.objects.filter(
            indicator__in=indicators,
        ).filter(period_filter).filter(
            operator__in=applicable_ops,
        ).filter(operator_filter).select_related(
            'indicator', 'operator', 'period',
        ).order_by('indicator__order', 'period__year', 'period__month')

        result = []
        for entry in entries:
            result.append({
                'indicator_code': entry.indicator.code,
                'indicator_name': entry.indicator.name,
                'indicator_level': entry.indicator.level,
                'operator_code': entry.operator.code,
                'operator_name': entry.operator.name,
                'operator_color': entry.operator.brand_color,
                'period': f"{entry.period.year}-{entry.period.month:02d}",
                'month': entry.period.month,
                'quarter': entry.period.quarter,
                'value': float(entry.value) if entry.value else None,
                'unit': entry.indicator.unit,
            })
        return result

    @staticmethod
    def get_market_share(year, quarter=None, market='mobile'):
        market_config = {
            'mobile': {'category': 'estacoes_moveis', 'indicator_code': '1'},
            'voice': {'category': 'trafego_originado', 'indicator_code': '1'},
            'sms': {'category': 'trafego_originado', 'indicator_code': '3'},
            'data': {'category': 'trafego_originado', 'indicator_code': '4'},
            'fixed_internet': {'category': 'internet_fixo', 'indicator_code': '1'},
            'revenue': {'category': 'receitas', 'indicator_code': '8'},
            'employment': {'category': 'empregos', 'indicator_code': '1'},
        }

        config = market_config.get(market, market_config['mobile'])
        category_code = config['category']
        indicator_code = config['indicator_code']

        category = IndicatorCategory.objects.get(code=category_code)
        indicator = Indicator.objects.filter(
            category=category, code=indicator_code,
        ).first()
        if not indicator:
            return []

        applicable_ops = DashboardService.get_applicable_operators(category_code)

        if category.is_cumulative:
            cum_type = '12M'
            if quarter:
                cum_type = f"{quarter * 3}M"

            entries = CumulativeData.objects.filter(
                indicator=indicator, year=year, cumulative_type=cum_type,
                operator__in=applicable_ops,
            ).select_related('operator')
        else:
            latest_period = Period.objects.filter(year=year).order_by('-month').first()
            if quarter:
                latest_period = Period.objects.filter(
                    year=year, quarter=quarter,
                ).order_by('-month').first()
            if not latest_period:
                return []

            entries = DataEntry.objects.filter(
                indicator=indicator, period=latest_period,
                operator__in=applicable_ops,
            ).select_related('operator')

        values = []
        total = Decimal('0')
        for entry in entries:
            val = entry.value or Decimal('0')
            total += val
            values.append({
                'operator_code': entry.operator.code,
                'operator_name': entry.operator.name,
                'operator_color': entry.operator.brand_color,
                'value': float(val),
            })

        for item in values:
            item['share_pct'] = round(
                item['value'] / float(total) * 100, 1,
            ) if total > 0 else 0

        return sorted(values, key=lambda x: x['value'], reverse=True)

    @staticmethod
    def get_trends(category_code, indicator_code=None, start_year=2018, end_year=2026):
        category = IndicatorCategory.objects.get(code=category_code)

        target_code = indicator_code or '1'
        indicator = Indicator.objects.filter(
            category=category, code=target_code,
        ).first()
        if not indicator:
            return []

        applicable_ops = DashboardService.get_applicable_operators(category_code)

        if category.is_cumulative:
            entries = CumulativeData.objects.filter(
                indicator=indicator,
                year__gte=start_year, year__lte=end_year,
                cumulative_type='12M',
                operator__in=applicable_ops,
            ).select_related('operator').order_by('year')

            data_by_year = {}
            for entry in entries:
                key = str(entry.year)
                if key not in data_by_year:
                    data_by_year[key] = {'period': key, 'total': 0}
                val = float(entry.value) if entry.value else 0
                data_by_year[key][entry.operator.code] = val
                data_by_year[key]['total'] += val

            return list(data_by_year.values())

        entries = DataEntry.objects.filter(
            indicator=indicator,
            period__year__gte=start_year, period__year__lte=end_year,
            operator__in=applicable_ops,
        ).select_related('operator', 'period').order_by('period__year', 'period__quarter')

        annual_data = {}
        for entry in entries:
            year_key = str(entry.period.year)
            if year_key not in annual_data:
                annual_data[year_key] = {'period': year_key, 'total': 0, '_counts': {}}
            op_code = entry.operator.code
            val = float(entry.value) if entry.value else 0

            if entry.period.quarter == 4 and entry.period.month % 3 == 0:
                annual_data[year_key][op_code] = val
            elif op_code not in annual_data[year_key] or annual_data[year_key].get(op_code, 0) < val:
                annual_data[year_key][op_code] = val

        for year_data in annual_data.values():
            year_data.pop('_counts', None)
            total = sum(v for k, v in year_data.items() if k not in ('period', 'total'))
            year_data['total'] = total

        return list(annual_data.values())

    @staticmethod
    def get_growth_rates(category_code, year):
        current = DashboardService.get_trends(
            category_code, start_year=year, end_year=year,
        )
        previous = DashboardService.get_trends(
            category_code, start_year=year - 1, end_year=year - 1,
        )

        if not current or not previous:
            return []

        curr = current[0]
        prev = previous[0]

        applicable_ops = DashboardService.get_applicable_operators(category_code)
        results = []

        for op in applicable_ops:
            curr_val = curr.get(op.code, 0)
            prev_val = prev.get(op.code, 0)
            abs_change = curr_val - prev_val
            pct_change = (abs_change / prev_val * 100) if prev_val else 0

            results.append({
                'operator_code': op.code,
                'operator_name': op.name,
                'operator_color': op.brand_color,
                'current_value': curr_val,
                'previous_value': prev_val,
                'absolute_change': abs_change,
                'pct_change': round(pct_change, 1),
            })

        return results

    @staticmethod
    def get_hhi(year, market='mobile'):
        shares = DashboardService.get_market_share(year, market=market)
        if not shares:
            return {'hhi': 0, 'classification': 'N/A', 'operators': []}

        hhi = sum(s['share_pct'] ** 2 for s in shares)

        if hhi > 2500:
            classification = 'Altamente concentrado'
        elif hhi > 1500:
            classification = 'Moderadamente concentrado'
        else:
            classification = 'Competitivo'

        return {
            'hhi': round(hhi, 0),
            'classification': classification,
            'operators': shares,
        }
