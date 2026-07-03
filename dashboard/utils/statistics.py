# dashboard/utils/statistics.py
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from questionarios.models import (
    EstacoesMoveisIndicador,
    TrafegoOriginadoIndicador,
    TrafegoTerminadoIndicador,
    ReceitasIndicador
)

class DashboardStatistics:
    @staticmethod
    def get_market_overview():
        """Returns overall market statistics"""
        current_year = timezone.now().year
        
        return {
            'total_subscribers': EstacoesMoveisIndicador.objects.filter(
                ano=current_year
            ).aggregate(
                total=Sum('total_assinantes')
            )['total'] or 0,
            
            'total_revenue': ReceitasIndicador.objects.filter(
                ano=current_year
            ).aggregate(
                total=Sum('receita_total')
            )['total'] or 0,
            
            'operators_count': EstacoesMoveisIndicador.objects.filter(
                ano=current_year
            ).values('operadora').distinct().count(),
        }

    @staticmethod
    def get_operator_stats(operator_id):
        """Returns statistics for a specific operator"""
        current_year = timezone.now().year
        
        return {
            'subscribers': EstacoesMoveisIndicador.objects.filter(
                operadora=operator_id,
                ano=current_year
            ).aggregate(
                total=Sum('total_assinantes')
            )['total'] or 0,
            
            'traffic': TrafegoOriginadoIndicador.objects.filter(
                operadora=operator_id,
                ano=current_year
            ).aggregate(
                total=Sum('total_minutos')
            )['total'] or 0,
            
            'revenue': ReceitasIndicador.objects.filter(
                operadora=operator_id,
                ano=current_year
            ).aggregate(
                total=Sum('receita_total')
            )['total'] or 0,
        }

    @staticmethod
    def get_quarterly_stats():
        """Returns quarterly statistics for the current year"""
        current_year = timezone.now().year
        
        quarters = []
        for quarter in range(1, 5):
            months = range((quarter-1)*3+1, quarter*3+1)
            
            stats = {
                'quarter': f'Q{quarter}',
                'subscribers': EstacoesMoveisIndicador.objects.filter(
                    ano=current_year,
                    mes__in=months
                ).aggregate(
                    avg=Avg('total_assinantes')
                )['avg'] or 0,
                
                'revenue': ReceitasIndicador.objects.filter(
                    ano=current_year,
                    mes__in=months
                ).aggregate(
                    total=Sum('receita_total')
                )['total'] or 0,
            }
            quarters.append(stats)
            
        return quarters

    @staticmethod
    def get_yearly_comparison():
        """Returns year-over-year comparison"""
        current_year = timezone.now().year
        previous_year = current_year - 1
        
        def get_year_stats(year):
            return {
                'subscribers': EstacoesMoveisIndicador.objects.filter(
                    ano=year
                ).aggregate(
                    avg=Avg('total_assinantes')
                )['avg'] or 0,
                
                'revenue': ReceitasIndicador.objects.filter(
                    ano=year
                ).aggregate(
                    total=Sum('receita_total')
                )['total'] or 0,
                
                'traffic': TrafegoOriginadoIndicador.objects.filter(
                    ano=year
                ).aggregate(
                    total=Sum('total_minutos')
                )['total'] or 0,
            }
            
        return {
            'current_year': get_year_stats(current_year),
            'previous_year': get_year_stats(previous_year),
        }