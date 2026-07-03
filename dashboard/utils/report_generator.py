"""
Sistema de Geração de Relatórios ARN
Baseado na configuração YAML fornecida
"""
import json
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, Max, Min, F
from django.utils import timezone
from questionarios.models import (
    EstacoesMoveisIndicador, AssinantesIndicador, ReceitasIndicador,
    TrafegoOriginadoIndicador, TrafegoTerminadoIndicador,
    TrafegoRoamingInternacionalIndicador, LBIIndicador,
    TrafegoInternetIndicador, InternetFixoIndicador,
    InvestimentoIndicador, EmpregoIndicador
)

class ARNReportGenerator:
    """Gerador principal de relatórios ARN"""
    
    # Mapeamento de modelos por fonte de dados
    DATA_SOURCES = {
        'estacoes_moveis': EstacoesMoveisIndicador,
        'assinantes': AssinantesIndicador,
        'trafego_originado': TrafegoOriginadoIndicador,
        'trafego_terminado': TrafegoTerminadoIndicador,
        'trafego_roaming': TrafegoRoamingInternacionalIndicador,
        'lbi': LBIIndicador,
        'trafego_internet': TrafegoInternetIndicador,
        'internet_fixo': InternetFixoIndicador,
        'receitas': ReceitasIndicador,
        'investimentos': InvestimentoIndicador,
        'empregos': EmpregoIndicador,
    }
    
    # Configuração de cores para operadoras
    OPERATOR_COLORS = {
        'TELECEL': '#DC3545',
        'ORANGE': '#FF6600',
        'TELECEL': '#DC3545',
    }
    
    def __init__(self, year=None, quarter=None):
        self.year = year or timezone.now().year
        self.quarter = quarter
        self.report_data = {}
    
    def _calcular_receita_total_expression(self):
        """
        Retorna expressão F() para calcular receita total.
        Método helper para evitar repetição de código.
        """
        return Sum(
            F('receitas_mensalidades') +
            F('receitas_chamadas_on_net') +
            F('receitas_chamadas_off_net') +
            F('receitas_chamadas_telecel') +
            F('receitas_chamadas_rede_movel_b') +
            F('receitas_servico_telefonico_fixo') +
            F('receitas_chamadas_cedeao') +
            F('receitas_chamadas_cplp') +
            F('receitas_chamadas_palop') +
            F('receitas_chamadas_resto_africa') +
            F('receitas_chamadas_resto_mundo') +
            F('receitas_voz_roaming_out') +
            F('receitas_mensagens') +
            F('receitas_dados_moveis') +
            F('receitas_internet_banda_larga') +
            F('outras_receitas_retalhistas') +
            F('receitas_terminacao_voz') +
            F('outras_receitas_grossistas')
        )
        
    def generate_market_report(self):
        """Gera relatório completo do mercado"""
        return {
            'panorama_geral': self.get_market_overview(),
            'trafego_voz': self.get_voice_traffic_analysis(),
            'mobile_money': self.get_mobile_money_analysis(),
            'banda_larga': self.get_broadband_analysis(),
            'receitas': self.get_revenue_analysis(),
        }
    
    def get_market_overview(self):
        """Panorama geral do mercado"""
        # Assinantes
        assinantes_data = AssinantesIndicador.objects.filter(ano=self.year)
        
        total_assinantes = assinantes_data.aggregate(
            total=Sum(F('assinantes_pre_pago') + F('assinantes_pos_pago'))
        )['total'] or 0
        
        # Crescimento
        previous_year_data = AssinantesIndicador.objects.filter(ano=self.year-1)
        previous_total = previous_year_data.aggregate(
            total=Sum(F('assinantes_pre_pago') + F('assinantes_pos_pago'))
        )['total'] or 0
        
        growth_rate = 0
        if previous_total > 0:
            growth_rate = ((total_assinantes - previous_total) / previous_total) * 100
        
        # Quota de mercado por operadora
        market_share = {}
        for operadora in ['ORANGE', 'TELECEL']:
            operadora_total = assinantes_data.filter(operadora=operadora).aggregate(
                total=Sum(F('assinantes_pre_pago') + F('assinantes_pos_pago'))
            )['total'] or 0
            
            if total_assinantes > 0:
                market_share[operadora] = (operadora_total / total_assinantes) * 100
            else:
                market_share[operadora] = 0
        
        # Taxa de penetração (assumindo população de 2M)
        penetration_rate = (total_assinantes / 2000000) * 100 if total_assinantes else 0
        
        return {
            'total_assinantes': total_assinantes,
            'crescimento_percentual': round(growth_rate, 2),
            'market_share': market_share,
            'taxa_penetracao': round(penetration_rate, 2),
            'dados_por_operadora': [
                {
                    'operadora': item['operadora'],
                    'assinantes': item['total_assinantes'],
                    'percentual': market_share.get(item['operadora'], 0)
                }
                for item in assinantes_data.values('operadora').annotate(
                    total_assinantes=Sum(F('assinantes_pre_pago') + F('assinantes_pos_pago'))
                )
            ]
        }
    
    def get_voice_traffic_analysis(self):
        """Análise de tráfego de voz (em minutos)"""
        trafego_originado = TrafegoOriginadoIndicador.objects.filter(ano=self.year)
        
        # Volume total de minutos de voz por operadora
        traffic_by_operator = {}
        total_traffic = 0
        
        for operadora in ['ORANGE', 'TELECEL']:
            op_data = trafego_originado.filter(operadora=operadora)
            
            # Usar minutos de voz (voz_*_minutos) em vez de chamadas
            on_net = op_data.aggregate(total=Sum('voz_on_net_minutos'))['total'] or 0
            off_net = op_data.aggregate(total=Sum('voz_off_net_nacional_minutos'))['total'] or 0
            international = op_data.aggregate(total=Sum('voz_internacional_total_minutos'))['total'] or 0
            
            operator_total = on_net + off_net + international
            total_traffic += operator_total
            
            traffic_by_operator[operadora] = {
                'on_net': on_net,
                'off_net': off_net,
                'internacional': international,
                'total': operator_total
            }
        
        # Distribuição por tipo
        total_on_net = sum(op['on_net'] for op in traffic_by_operator.values())
        total_off_net = sum(op['off_net'] for op in traffic_by_operator.values())
        total_international = sum(op['internacional'] for op in traffic_by_operator.values())
        
        distribution = {}
        if total_traffic > 0:
            distribution = {
                'on_net': round((total_on_net / total_traffic) * 100, 1),
                'off_net': round((total_off_net / total_traffic) * 100, 1),
                'internacional': round((total_international / total_traffic) * 100, 1),
            }
        
        return {
            'volume_total': total_traffic,  # Total em minutos
            'por_operadora': traffic_by_operator,
            'distribuicao_percentual': distribution,
            'evolucao_mensal': self.get_monthly_evolution('trafego_originado')
        }
    
    def get_mobile_money_analysis(self):
        """Análise Mobile Money - dados simulados baseados no exemplo"""
        # Esta implementação seria baseada em dados reais quando disponíveis
        return {
            'carregamentos': {
                'valor_fcfa': 173891000000,
                'numero_transacoes': 45000000,
                'crescimento': 152
            },
            'levantamentos': {
                'valor_fcfa': 174564000000,
                'numero_transacoes': 38000000,
                'crescimento': 235
            },
            'transferencias': {
                'valor_fcfa': 96460000000,
                'numero_transacoes': 12000000,
                'crescimento': 465
            },
            'distribuicao_genero': {
                'mulher': 45,
                'homem': 55
            }
        }
    
    def get_broadband_analysis(self):
        """Análise de banda larga móvel e internet fixa"""
        # Usar EstacoesMoveisIndicador para dados de utilizadores móveis por tecnologia
        estacoes_data = EstacoesMoveisIndicador.objects.filter(ano=self.year)
        
        # TrafegoOriginadoIndicador tem dados de tráfego de dados móveis em MB
        trafego_movel = TrafegoOriginadoIndicador.objects.filter(ano=self.year)
        
        # TrafegoInternetIndicador tem dados de internet fixa
        internet_fixa = TrafegoInternetIndicador.objects.filter(ano=self.year)
        
        # Utilizadores de banda larga móvel por tecnologia
        tech_3g = estacoes_data.aggregate(
            total=Sum('utilizadores_servico_3g_upgrades')
        )['total'] or 0
        
        tech_4g = estacoes_data.aggregate(
            total=Sum('utilizadores_servico_4g')
        )['total'] or 0
        
        # Tráfego de dados móveis (em MB)
        trafego_dados_moveis = trafego_movel.aggregate(
            dados_2g=Sum('trafego_dados_2g_mbytes'),
            dados_3g=Sum('trafego_dados_3g_upgrade_mbytes'),
            dados_4g=Sum('trafego_dados_4g_mbytes')
        )
        
        # Tráfego internet fixa total (em Mbit/s)
        trafego_internet_fixa = internet_fixa.aggregate(
            total=Sum('trafego_total'),
            banda_larga=Sum('banda_larga_total')
        )
        
        return {
            'assinantes_por_tecnologia': {
                '3G': tech_3g,
                '4G': tech_4g,
                '5G': 0  # Placeholder para futuro
            },
            'trafego_dados_moveis_mb': {
                '2G': trafego_dados_moveis['dados_2g'] or 0,
                '3G': trafego_dados_moveis['dados_3g'] or 0,
                '4G': trafego_dados_moveis['dados_4g'] or 0,
                'total': (
                    (trafego_dados_moveis['dados_2g'] or 0) +
                    (trafego_dados_moveis['dados_3g'] or 0) +
                    (trafego_dados_moveis['dados_4g'] or 0)
                )
            },
            'internet_fixa_mbps': {
                'total': float(trafego_internet_fixa['total'] or 0),
                'banda_larga': float(trafego_internet_fixa['banda_larga'] or 0)
            },
            'taxa_penetracao_dados': self.calculate_data_penetration(tech_3g + tech_4g)
        }
    
    def get_revenue_analysis(self):
        """Análise de receitas"""
        receitas_data = ReceitasIndicador.objects.filter(ano=self.year)
        
        # Volume de negócios por operadora
        # ReceitasIndicador não tem campo receita_total, calculamos a soma de todas as receitas
        revenue_by_operator = {}
        total_revenue = 0
        
        for operadora in ['ORANGE', 'TELECEL']:
            op_data = receitas_data.filter(operadora=operadora)
            
            # Calcular total de receitas usando helper
            op_revenue = op_data.aggregate(
                total=self._calcular_receita_total_expression()
            )['total'] or 0
            
            revenue_by_operator[operadora] = float(op_revenue) if op_revenue else 0
            total_revenue += revenue_by_operator[operadora]
        
        # Quota de receitas
        revenue_share = {}
        if total_revenue > 0:
            for operadora, revenue in revenue_by_operator.items():
                revenue_share[operadora] = round((revenue / total_revenue) * 100, 1)
        
        # Evolução anual
        evolution_data = self.get_revenue_evolution()
        
        return {
            'volume_total': total_revenue,
            'por_operadora': revenue_by_operator,
            'quota_receitas': revenue_share,
            'evolucao_anual': evolution_data,
            'crescimento_percentual': self.calculate_revenue_growth()
        }
    
    def get_monthly_evolution(self, data_source):
        """Evolução mensal de um indicador"""
        if data_source not in self.DATA_SOURCES:
            return []
        
        model = self.DATA_SOURCES[data_source]
        
        evolution = []
        for month in range(1, 13):
            monthly_data = model.objects.filter(
                ano=self.year,
                mes=month
            ).aggregate(
                total=Sum('total_assinantes') if hasattr(model, 'total_assinantes') 
                      else Sum('chamadas_on_net')  # Default field
            )
            
            evolution.append({
                'mes': month,
                'valor': monthly_data['total'] or 0
            })
        
        return evolution
    
    def get_revenue_evolution(self):
        """Evolução das receitas nos últimos 5 anos"""
        years = range(self.year - 4, self.year + 1)
        evolution = []
        
        for year in years:
            yearly_data = ReceitasIndicador.objects.filter(ano=year)
            
            # Calcular total de receitas usando helper
            yearly_revenue = yearly_data.aggregate(
                total=self._calcular_receita_total_expression()
            )['total'] or 0
            
            evolution.append({
                'ano': year,
                'receita': float(yearly_revenue) if yearly_revenue else 0
            })
        
        return evolution
    
    def calculate_data_penetration(self, total_subscribers):
        """Calcula taxa de penetração de dados"""
        # Assumindo população de 2 milhões
        population = 2000000
        return round((total_subscribers / population) * 100, 2) if total_subscribers else 0
    
    def calculate_revenue_growth(self):
        """Calcula crescimento de receita anual"""
        current_data = ReceitasIndicador.objects.filter(ano=self.year)
        previous_data = ReceitasIndicador.objects.filter(ano=self.year - 1)
        
        # Calcular receita total do ano atual usando helper
        current_revenue = current_data.aggregate(
            total=self._calcular_receita_total_expression()
        )['total'] or 0
        
        # Calcular receita total do ano anterior usando helper
        previous_revenue = previous_data.aggregate(
            total=self._calcular_receita_total_expression()
        )['total'] or 0
        
        if previous_revenue > 0:
            return round(((float(current_revenue) - float(previous_revenue)) / float(previous_revenue)) * 100, 2)
        return 0
    
    def generate_dashboard_data(self):
        """Gera dados para o dashboard executivo"""
        market_data = self.get_market_overview()
        traffic_data = self.get_voice_traffic_analysis()
        revenue_data = self.get_revenue_analysis()
        
        return {
            'kpis_principais': {
                'total_assinantes': {
                    'valor': market_data['total_assinantes'],
                    'variacao': f"+{market_data['crescimento_percentual']}%",
                    'cor': 'verde' if market_data['crescimento_percentual'] > 0 else 'vermelho'
                },
                'taxa_penetracao': {
                    'valor': f"{market_data['taxa_penetracao']}%",
                    'variacao': '+2pp',  # Placeholder
                    'cor': 'azul'
                },
                'volume_trafego': {
                    'valor': f"{traffic_data['volume_total'] / 1000000:.1f}M min",
                    'variacao': '+28%',  # Placeholder
                    'cor': 'verde'
                },
                'receita_total': {
                    'valor': f"{revenue_data['volume_total'] / 1000000:.0f}M FCFA",
                    'variacao': f"+{revenue_data['crescimento_percentual']}%",
                    'cor': 'verde' if revenue_data['crescimento_percentual'] > 0 else 'vermelho'
                }
            },
            'market_share': market_data['market_share'],
            'tendencia_mensal': traffic_data['evolucao_mensal']
        }
    
    def generate_comparative_report(self):
        """Relatório comparativo entre operadoras"""
        market_data = self.get_market_overview()
        traffic_data = self.get_voice_traffic_analysis()
        revenue_data = self.get_revenue_analysis()
        
        comparison = []
        for operadora in ['ORANGE', 'TELECEL']:
            assinantes = next((item['assinantes'] for item in market_data['dados_por_operadora'] 
                             if item['operadora'] == operadora), 0)
            
            comparison.append({
                'operadora': operadora,
                'assinantes': assinantes,
                'market_share': f"{market_data['market_share'].get(operadora, 0):.1f}%",
                'trafego_voz': traffic_data['por_operadora'].get(operadora, {}).get('total', 0),
                'receitas': revenue_data['por_operadora'].get(operadora, 0)
            })
        
        return comparison
    
    def export_to_json(self, data):
        """Exporta dados para JSON"""
        return json.dumps(data, indent=2, default=str, ensure_ascii=False)
    
    def get_chart_config(self, chart_type, data):
        """Configuração padrão para gráficos"""
        base_config = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'labels': {
                        'color': '#F0F0F0',
                        'usePointStyle': True,
                        'family': 'Inter'
                    }
                }
            }
        }
        
        if chart_type == 'line':
            base_config['scales'] = {
                'x': {
                    'grid': {'color': '#474D57'},
                    'ticks': {'color': '#F0F0F0', 'font': {'family': 'Inter'}}
                },
                'y': {
                    'grid': {'color': '#474D57'},
                    'ticks': {'color': '#F0F0F0', 'font': {'family': 'Inter'}}
                }
            }
        
        return base_config
