from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from ..models.estacoes_moveis import EstacoesMoveisIndicador
from ..models.trafego_originado import TrafegoOriginadoIndicador
from ..models.trafego_terminado import TrafegoTerminadoIndicador
from ..models.trafego_roaming_internacional import TrafegoRoamingInternacionalIndicador
from ..models.trafego_internet import TrafegoInternetIndicador
from ..models.tarifario_voz import TarifarioVozOrangeIndicador, TarifarioVozMTNIndicador
from ..models.receitas import ReceitasIndicador
from ..models.lbi import LBIIndicador
from ..models.investimento import InvestimentoIndicador
from ..models.internet_fixo import InternetFixoIndicador
from ..models.emprego import EmpregoIndicador
from ..models.assinantes import AssinantesIndicador
from ..models.base import IndicadorBase
from django.db.models import Sum, Avg, F, Count, Q
import logging
import json
import decimal
from datetime import datetime
from django.db.models.functions import TruncMonth, TruncQuarter, ExtractYear, ExtractMonth
from django.db.models import FloatField, Case, When, Value, DecimalField
from decimal import Decimal
from django.db.models.functions import Cast
from django.core.exceptions import FieldDoesNotExist
from django.db import models

logger = logging.getLogger(__name__)

# Helper function for JSON serialization of Decimal values
def decimal_default(obj):
    """JSON serializer for decimal objects"""
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError

# Dashboard Views
class AdminDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Dashboard para gerenciamento dos indicadores"""
    template_name = 'questionarios/admin_dashboard.html'
    permission_required = 'questionarios.view_estacoesmoveisindicador'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estrutura dos indicadores com informações para o dashboard
        indicadores = [
            {
                'nome': 'Estações Móveis',
                'descricao': 'Gestão de informações sobre estações móveis',
                'modelo': EstacoesMoveisIndicador,
                'url': reverse_lazy('questionarios:estacoes_moveis_list'),
                'icone': 'fas fa-mobile-alt',
                'cor': 'primary'
            },
            {
                'nome': 'Tráfego Originado',
                'descricao': 'Gestão de informações sobre tráfego originado',
                'modelo': TrafegoOriginadoIndicador,
                'url': reverse_lazy('questionarios:trafego_originado_list'),
                'icone': 'fas fa-phone-alt',
                'cor': 'success'
            },
            {
                'nome': 'Tráfego Terminado',
                'descricao': 'Gestão de informações sobre tráfego terminado',
                'modelo': TrafegoTerminadoIndicador,
                'url': reverse_lazy('questionarios:trafego_terminado_list'),
                'icone': 'fas fa-phone-volume',
                'cor': 'info'
            },
            {
                'nome': 'Tráfego Roaming Internacional',
                'descricao': 'Gestão de informações sobre tráfego roaming internacional',
                'modelo': TrafegoRoamingInternacionalIndicador,
                'url': reverse_lazy('questionarios:trafego_roaming_internacional_list'),
                'icone': 'fas fa-globe',
                'cor': 'warning'
            },
            {
                'nome': 'Tráfego Internet',
                'descricao': 'Gestão de informações sobre tráfego internet',
                'modelo': TrafegoInternetIndicador,
                'url': reverse_lazy('questionarios:trafego_internet_list'),
                'icone': 'fas fa-wifi',
                'cor': 'danger'
            },
            {
                'nome': 'Tarifário Voz Orange',
                'descricao': 'Gestão de informações sobre tarifário voz Orange',
                'modelo': TarifarioVozOrangeIndicador,
                'url': reverse_lazy('questionarios:tarifario_voz_orange_list'),
                'icone': 'fas fa-comments-dollar',
                'cor': 'warning'
            },
            {
                'nome': 'Tarifário Voz MTN',
                'descricao': 'Gestão de informações sobre tarifário voz MTN',
                'modelo': TarifarioVozMTNIndicador,
                'url': reverse_lazy('questionarios:tarifario_voz_telecel_list'),
                'icone': 'fas fa-comments-dollar',
                'cor': 'success'
            },
            {
                'nome': 'Receitas',
                'descricao': 'Gestão de informações sobre receitas',
                'modelo': ReceitasIndicador,
                'url': reverse_lazy('questionarios:receitas_list'),
                'icone': 'fas fa-dollar-sign',
                'cor': 'secondary'
            },
            {
                'nome': 'LBI',
                'descricao': 'Gestão de informações sobre LBI',
                'modelo': LBIIndicador,
                'url': reverse_lazy('questionarios:lbi_list'),
                'icone': 'fas fa-chart-bar',
                'cor': 'dark'
            },
            {
                'nome': 'Investimento',
                'descricao': 'Gestão de informações sobre investimento',
                'modelo': InvestimentoIndicador,
                'url': reverse_lazy('questionarios:investimento_list'),
                'icone': 'fas fa-chart-line',
                'cor': 'info'
            },
            {
                'nome': 'Internet Fixo',
                'descricao': 'Gestão de informações sobre internet fixo',
                'modelo': InternetFixoIndicador,
                'url': reverse_lazy('questionarios:internet_fixo_list'),
                'icone': 'fas fa-network-wired',
                'cor': 'primary'
            },
            {
                'nome': 'Emprego',
                'descricao': 'Gestão de informações sobre emprego',
                'modelo': EmpregoIndicador,
                'url': reverse_lazy('questionarios:emprego_list'),
                'icone': 'fas fa-users',
                'cor': 'success'
            },
            {
                'nome': 'Assinantes',
                'descricao': 'Gestão de informações sobre assinantes',
                'modelo': AssinantesIndicador,
                'url': reverse_lazy('questionarios:assinantes_list'),
                'icone': 'fas fa-user-check',
                'cor': 'warning'
            }
        ]
        
        # Adicionar contagem de registros para cada indicador
        for indicador in indicadores:
            indicador['count'] = indicador['modelo'].objects.count()
            # Pegar a última atualização
            ultimo_registro = indicador['modelo'].objects.order_by('-data_atualizacao').first()
            indicador['ultima_atualizacao'] = ultimo_registro.data_atualizacao if ultimo_registro else None
        
        context['indicadores'] = indicadores
        return context

class AnalisesMercadoDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard para análises de mercado"""
    template_name = 'questionarios/analises_mercado_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estrutura das análises disponíveis
        analises = [
            {
                'nome': 'Relatório Anual de Mercado',
                'descricao': 'Visão abrangente do mercado com análises detalhadas',
                'url': reverse_lazy('questionarios:relatorio_anual'),
                'icone': 'fas fa-chart-pie',
                'cor': 'primary'
            },
            {
                'nome': 'Comparação Anual',
                'descricao': 'Compare indicadores entre diferentes anos',
                'url': reverse_lazy('questionarios:comparacao_anual'),
                'icone': 'fas fa-balance-scale',
                'cor': 'info'
            },
            {
                'nome': 'Evolução do Mercado',
                'descricao': 'Análise da evolução dos principais indicadores de mercado',
                'url': reverse_lazy('questionarios:evolucao_mercado'),
                'icone': 'fas fa-chart-line',
                'cor': 'success'
            },
            {
                'nome': 'Relatório de Crescimento',
                'descricao': 'Análise das taxas de crescimento dos indicadores',
                'url': reverse_lazy('questionarios:relatorio_crescimento'),
                'icone': 'fas fa-arrow-up',
                'cor': 'warning'
            },
            {
                'nome': 'Análise de Mercado',
                'descricao': 'Análise detalhada do mercado com indicadores-chave',
                'url': reverse_lazy('questionarios:analise_mercado'),
                'icone': 'fas fa-search-dollar',
                'cor': 'danger'
            },
            {
                'nome': 'Visão Geral do Mercado',
                'descricao': 'Resumo dos principais indicadores de mercado',
                'url': reverse_lazy('questionarios:visao_geral_mercado'),
                'icone': 'fas fa-globe',
                'cor': 'secondary'
            },
            {
                'nome': 'Evolução das Operadoras',
                'descricao': 'Análise da evolução das operadoras do mercado',
                'url': reverse_lazy('questionarios:evolucao_operadoras'),
                'icone': 'fas fa-building',
                'cor': 'dark'
            },
            {
                'nome': 'Panorama do Setor',
                'descricao': 'Visão completa do setor de telecomunicações',
                'url': reverse_lazy('questionarios:panorama_setor'),
                'icone': 'fas fa-broadcast-tower',
                'cor': 'primary'
            }
        ]
        
        context['analises'] = analises
        
        # Anos e trimestres disponíveis para relatórios
        anos_disponiveis = self.get_anos_disponiveis()
        context['anos_disponiveis'] = anos_disponiveis
        
        return context
    
    def get_anos_disponiveis(self):
        """Retorna anos disponíveis nos dados"""
        # Usar o primeiro modelo como referência para anos disponíveis
        anos = EstacoesMoveisIndicador.objects.values_list('ano', flat=True).distinct().order_by('ano')
        return list(anos)

# Analytical Views

class RelatorioAnualView(LoginRequiredMixin, TemplateView):
    """Relatório anual de mercado"""
    template_name = 'questionarios/relatorio_anual.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.request.GET.get('ano', datetime.now().year)
        try:
            ano = int(ano)
        except (ValueError, TypeError):
            ano = datetime.now().year
            
        # Obter dados para o ano selecionado
        context['ano'] = ano
        context['dados'] = self.get_dados_anuais(ano)
        context['anos_disponiveis'] = self.get_anos_disponiveis()
        context['dados_json'] = json.dumps(context['dados'], default=decimal_default)
        
        return context
        
    def get_dados_anuais(self, ano):
        """Obtém os dados anuais para o ano selecionado"""
        dados = {}
        
        # Obter dados de assinantes
        assinantes = AssinantesIndicador.objects.filter(ano=ano)
        dados['assinantes'] = {
            'total': sum(a.total_assinantes or 0 for a in assinantes),
            'por_operadora': {a.operadora: a.total_assinantes for a in assinantes}
        }
        
        # Obter dados de estações móveis
        estacoes = EstacoesMoveisIndicador.objects.filter(ano=ano)
        dados['estacoes_moveis'] = {
            'total': sum(e.calcular_total_estacoes_moveis() or 0 for e in estacoes),
            'por_operadora': {e.operadora: e.calcular_total_estacoes_moveis() for e in estacoes}
        }
        
        # Obter dados de receitas
        receitas = ReceitasIndicador.objects.filter(ano=ano)
        dados['receitas'] = {
            'total': sum(r.calcular_total_receitas() or 0 for r in receitas),
            'por_operadora': {}
        }
        for operadora in ['orange', 'telecel', 'telecel']:
            receitas_op = receitas.filter(operadora=operadora)
            dados['receitas']['por_operadora'][operadora] = sum(r.calcular_total_receitas() or 0 for r in receitas_op)
        
        # Obter dados de investimento
        investimentos = InvestimentoIndicador.objects.filter(ano=ano)
        dados['investimentos'] = {
            'total': sum(i.calcular_total_investimentos() or 0 for i in investimentos),
            'por_operadora': {i.operadora: i.calcular_total_investimentos() for i in investimentos}
        }
        
        # Obter dados de tráfego
        trafego_originado = TrafegoOriginadoIndicador.objects.filter(ano=ano)
        dados['trafego_originado'] = {
            'total': sum(t.calcular_total_trafego() or 0 for t in trafego_originado),
            'por_operadora': {t.operadora: t.calcular_total_trafego() for t in trafego_originado}
        }
        
        # Obter dados de internet
        internet = TrafegoInternetIndicador.objects.filter(ano=ano)
        dados['trafego_internet'] = {
            'total': sum(i.calcular_total_trafego() or 0 for i in internet),
            'por_operadora': {i.operadora: i.calcular_total_trafego() for i in internet}
        }
        
        return dados
    
    def get_anos_disponiveis(self):
        """Retorna anos disponíveis nos dados"""
        anos = AssinantesIndicador.objects.values_list('ano', flat=True).distinct().order_by('ano')
        return list(anos)

class RelatorioTrimestralView(LoginRequiredMixin, TemplateView):
    """Relatório trimestral de mercado"""
    template_name = 'questionarios/relatorio_trimestral.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = self.request.GET.get('ano', datetime.now().year)
        trimestre = self.request.GET.get('trimestre', 1)
        
        try:
            ano = int(ano)
            trimestre = int(trimestre)
            if trimestre < 1 or trimestre > 4:
                trimestre = 1
        except (ValueError, TypeError):
            ano = datetime.now().year
            trimestre = 1
            
        # Obter meses do trimestre
        meses_trimestre = self.get_meses_trimestre(trimestre)
        
        # Obter dados para o trimestre selecionado
        context['ano'] = ano
        context['trimestre'] = trimestre
        context['meses_trimestre'] = meses_trimestre
        context['dados'] = self.get_dados_trimestrais(ano, meses_trimestre)
        context['anos_disponiveis'] = self.get_anos_disponiveis()
        context['dados_json'] = json.dumps(context['dados'], default=decimal_default)
        
        return context
    
    def get_meses_trimestre(self, trimestre):
        """Retorna os meses do trimestre"""
        return list(range((trimestre - 1) * 3 + 1, trimestre * 3 + 1))
    
    def get_dados_trimestrais(self, ano, meses):
        """Obtém os dados trimestrais para o ano e meses selecionados"""
        dados = {}
        
        # Obter dados de assinantes
        assinantes = AssinantesIndicador.objects.filter(ano=ano, mes__in=meses)
        dados['assinantes'] = {
            'total': sum(a.total_assinantes or 0 for a in assinantes),
            'por_operadora': {}
        }
        
        # Agrupar por operadora
        for operadora in ['orange', 'telecel', 'telecel']:
            assinantes_op = assinantes.filter(operadora=operadora)
            dados['assinantes']['por_operadora'][operadora] = sum(a.total_assinantes or 0 for a in assinantes_op)
        
        # Fazer o mesmo para os outros indicadores
        # Estações móveis
        estacoes = EstacoesMoveisIndicador.objects.filter(ano=ano, mes__in=meses)
        dados['estacoes_moveis'] = {
            'total': sum(e.calcular_total_estacoes_moveis() or 0 for e in estacoes),
            'por_operadora': {}
        }
        for operadora in ['orange', 'telecel', 'telecel']:
            estacoes_op = estacoes.filter(operadora=operadora)
            dados['estacoes_moveis']['por_operadora'][operadora] = sum(e.calcular_total_estacoes_moveis() or 0 for e in estacoes_op)
        
        # Receitas
        receitas = ReceitasIndicador.objects.filter(ano=ano, mes__in=meses)
        dados['receitas'] = {
            'total': sum(r.calcular_total_receitas() or 0 for r in receitas),
            'por_operadora': {}
        }
        for operadora in ['orange', 'telecel', 'telecel']:
            receitas_op = receitas.filter(operadora=operadora)
            dados['receitas']['por_operadora'][operadora] = sum(r.calcular_total_receitas() or 0 for r in receitas_op)
        
        # Investimentos
        investimentos = InvestimentoIndicador.objects.filter(ano=ano, mes__in=meses)
        dados['investimentos'] = {
            'total': sum(i.calcular_total_investimentos() or 0 for i in investimentos),
            'por_operadora': {}
        }
        for operadora in ['orange', 'telecel', 'telecel']:
            investimentos_op = investimentos.filter(operadora=operadora)
            dados['investimentos']['por_operadora'][operadora] = sum(i.calcular_total_investimentos() or 0 for i in investimentos_op)
        
        # Tráfego originado
        trafego_originado = TrafegoOriginadoIndicador.objects.filter(ano=ano, mes__in=meses)
        dados['trafego_originado'] = {
            'total': sum(t.calcular_total_trafego() or 0 for t in trafego_originado),
            'por_operadora': {}
        }
        for operadora in ['orange', 'telecel', 'telecel']:
            trafego_op = trafego_originado.filter(operadora=operadora)
            dados['trafego_originado']['por_operadora'][operadora] = sum(t.calcular_total_trafego() or 0 for t in trafego_op)
        
        # Internet
        internet = TrafegoInternetIndicador.objects.filter(ano=ano, mes__in=meses)
        dados['trafego_internet'] = {
            'total': sum(i.calcular_total_trafego() or 0 for i in internet),
            'por_operadora': {}
        }
        for operadora in ['orange', 'telecel', 'telecel']:
            internet_op = internet.filter(operadora=operadora)
            dados['trafego_internet']['por_operadora'][operadora] = sum(i.calcular_total_trafego() or 0 for i in internet_op)
        
        return dados
    
    def get_anos_disponiveis(self):
        """Retorna anos disponíveis nos dados"""
        anos = AssinantesIndicador.objects.values_list('ano', flat=True).distinct().order_by('ano')
        return list(anos)

class EvolucaoMercadoView(LoginRequiredMixin, TemplateView):
    """Evolução do mercado ao longo do tempo"""
    template_name = 'questionarios/evolucao_mercado.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter anos disponíveis
        anos = self.get_anos_disponiveis()
        context['anos'] = anos
        
        # Obter dados de evolução para cada indicador principal
        evolucao = {}
        
        # Evolução de assinantes
        evolucao['assinantes'] = self.get_evolucao_indicador(AssinantesIndicador, 'total_assinantes', anos)
        
        # Evolução de estações móveis
        estacoes_por_ano = {}
        for ano in anos:
            estacoes = EstacoesMoveisIndicador.objects.filter(ano=ano)
            estacoes_por_ano[ano] = sum(e.calcular_total_estacoes_moveis() or 0 for e in estacoes)
        evolucao['estacoes_moveis'] = estacoes_por_ano
        
        # Evolução de receitas
        receitas_por_ano = {}
        for ano in anos:
            receitas = ReceitasIndicador.objects.filter(ano=ano)
            receitas_por_ano[ano] = sum(r.calcular_total_receitas() or 0 for r in receitas)
        evolucao['receitas'] = receitas_por_ano
        
        # Evolução de investimentos
        investimentos_por_ano = {}
        for ano in anos:
            investimentos = InvestimentoIndicador.objects.filter(ano=ano)
            investimentos_por_ano[ano] = sum(i.calcular_total_investimentos() or 0 for i in investimentos)
        evolucao['investimentos'] = investimentos_por_ano
        
        # Evolução de tráfego internet
        trafego_por_ano = {}
        for ano in anos:
            trafego = TrafegoInternetIndicador.objects.filter(ano=ano)
            trafego_por_ano[ano] = sum(t.calcular_total_trafego() or 0 for t in trafego)
        evolucao['trafego_internet'] = trafego_por_ano
        
        context['evolucao'] = evolucao
        context['evolucao_json'] = json.dumps(evolucao, default=decimal_default)
        
        return context
    
    def get_anos_disponiveis(self):
        """Retorna anos disponíveis nos dados"""
        anos = AssinantesIndicador.objects.values_list('ano', flat=True).distinct().order_by('ano')
        return list(anos)
    
    def get_evolucao_indicador(self, modelo, campo, anos):
        """Obtém a evolução de um indicador ao longo dos anos"""
        evolucao = {}
        for ano in anos:
            registros = modelo.objects.filter(ano=ano)
            total = sum(getattr(r, campo) or 0 for r in registros)
            evolucao[ano] = total
        return evolucao

class ComparacaoAnualView(LoginRequiredMixin, TemplateView):
    """Comparação anual de indicadores"""
    template_name = 'questionarios/comparacao_anual.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter anos para comparação
        anos = self.get_anos_disponiveis()
        
        if len(anos) < 2:
            context['erro'] = "É necessário ter pelo menos dois anos de dados para comparação"
            return context
        
        # Obter anos selecionados para comparação
        ano1 = self.request.GET.get('ano1', anos[-2])  # Penúltimo ano por padrão
        ano2 = self.request.GET.get('ano2', anos[-1])  # Último ano por padrão
        
        try:
            ano1 = int(ano1)
            ano2 = int(ano2)
        except (ValueError, TypeError):
            ano1 = anos[-2] if len(anos) >= 2 else anos[0]
            ano2 = anos[-1] if len(anos) >= 2 else anos[0]
        
        # Obter dados para comparação
        context['ano1'] = ano1
        context['ano2'] = ano2
        context['anos'] = anos
        context['comparacao'] = self.get_dados_comparacao(ano1, ano2)
        context['comparacao_json'] = json.dumps(context['comparacao'], default=decimal_default)
        
        return context
    
    def get_dados_comparacao(self, ano1, ano2):
        """Obtém dados para comparação entre dois anos"""
        comparacao = {}
        
        # Comparar assinantes
        assinantes1 = AssinantesIndicador.objects.filter(ano=ano1)
        assinantes2 = AssinantesIndicador.objects.filter(ano=ano2)
        
        total_assinantes1 = sum(a.total_assinantes or 0 for a in assinantes1)
        total_assinantes2 = sum(a.total_assinantes or 0 for a in assinantes2)
        
        comparacao['assinantes'] = {
            'ano1': total_assinantes1,
            'ano2': total_assinantes2,
            'variacao': calcular_variacao_percentual(total_assinantes1, total_assinantes2),
            'por_operadora': {}
        }
        
        # Comparar por operadora
        for operadora in ['orange', 'telecel', 'telecel']:
            assinantes_op1 = assinantes1.filter(operadora=operadora)
            assinantes_op2 = assinantes2.filter(operadora=operadora)
            
            total_op1 = sum(a.total_assinantes or 0 for a in assinantes_op1)
            total_op2 = sum(a.total_assinantes or 0 for a in assinantes_op2)
            
            comparacao['assinantes']['por_operadora'][operadora] = {
                'ano1': total_op1,
                'ano2': total_op2,
                'variacao': calcular_variacao_percentual(total_op1, total_op2)
            }
        
        # Fazer o mesmo para os outros indicadores principais
        # Estações móveis
        comparacao['estacoes_moveis'] = self.comparar_indicador(
            EstacoesMoveisIndicador, 'calcular_total_estacoes_moveis', ano1, ano2
        )
            
            # Receitas
        comparacao['receitas'] = self.comparar_indicador(
            ReceitasIndicador, 'calcular_total_receitas', ano1, ano2
        )
            
            # Investimentos
        comparacao['investimentos'] = self.comparar_indicador(
            InvestimentoIndicador, 'calcular_total_investimentos', ano1, ano2
        )
        
        # Tráfego Internet
        comparacao['trafego_internet'] = self.comparar_indicador(
            TrafegoInternetIndicador, 'calcular_total_trafego', ano1, ano2
        )
        
        return comparacao
    
    def comparar_indicador(self, modelo, metodo, ano1, ano2):
        """Compara um indicador entre dois anos usando um método específico do modelo"""
        registros1 = modelo.objects.filter(ano=ano1)
        registros2 = modelo.objects.filter(ano=ano2)
        
        # Calcular totais usando o método do modelo
        total1 = sum(getattr(r, metodo)() or 0 for r in registros1)
        total2 = sum(getattr(r, metodo)() or 0 for r in registros2)
        
        resultado = {
            'ano1': total1,
            'ano2': total2,
            'variacao': calcular_variacao_percentual(total1, total2),
            'por_operadora': {}
        }
        
        # Comparar por operadora
        for operadora in ['orange', 'telecel', 'telecel']:
            registros_op1 = registros1.filter(operadora=operadora)
            registros_op2 = registros2.filter(operadora=operadora)
            
            total_op1 = sum(getattr(r, metodo)() or 0 for r in registros_op1)
            total_op2 = sum(getattr(r, metodo)() or 0 for r in registros_op2)
            
            resultado['por_operadora'][operadora] = {
                'ano1': total_op1,
                'ano2': total_op2,
                'variacao': calcular_variacao_percentual(total_op1, total_op2)
            }
            
        return resultado
    
    def get_anos_disponiveis(self):
        """Retorna anos disponíveis nos dados"""
        anos = AssinantesIndicador.objects.values_list('ano', flat=True).distinct().order_by('ano')
        return list(anos)

# Função auxiliar para calcular variação percentual
def calcular_variacao_percentual(valor_anterior, valor_atual):
    """Calcula a variação percentual entre dois valores"""
    if valor_anterior is None or valor_atual is None:
        return None
    
    if valor_anterior == 0:
        return 100 if valor_atual > 0 else 0
    
    return ((valor_atual - valor_anterior) / abs(valor_anterior)) * 100 

# --- Helper Functions for Aggregation --- 

def get_available_years(model):
    """Get distinct years available for a given indicator model."""
    # Add try-except block for safety
    try:
        years = model.objects.values_list('ano', flat=True).distinct()
        return sorted(list(years)) if years else []
    except Exception as e:
        logger.error(f"Error getting available years for {model.__name__}: {e}")
        return []

def get_quarterly_data(model, year, operadora=None, aggregate_fields={}):
    """Aggregates data quarterly for a given model, year, and fields."""
    queryset = model.objects.filter(ano=year)
    if operadora:
        queryset = queryset.filter(operadora=operadora)
    
    quarterly_results = {}
    for q in range(1, 5):
        start_month = (q - 1) * 3 + 1
        end_month = q * 3
        quarter_queryset = queryset.filter(mes__gte=start_month, mes__lte=end_month)
        
        aggregates = {}
        if aggregate_fields:
            valid_aggregates = {}
            for field, agg_func in aggregate_fields.items():
                try:
                    model._meta.get_field(field)
                    valid_aggregates[f'total_{field}'] = agg_func(field)
                except FieldDoesNotExist:
                    logger.warning(f"Field '{field}' does not exist on model {model.__name__}. Skipping aggregation.")
                    # Use a default value since we don't know the field type
                    valid_aggregates[f'total_{field}'] = Value(Decimal('0.0'), output_field=DecimalField())
            
            if valid_aggregates:
                try:
                    quarter_aggregates = quarter_queryset.aggregate(**valid_aggregates)
                    for key, value in quarter_aggregates.items():
                         aggregates[key] = float(value) if isinstance(value, Decimal) else (value or 0)
                except Exception as agg_error:
                    logger.error(f"Error during quarterly aggregation for model {model.__name__}, quarter {q}: {agg_error}")
                    # Populate with zeros on error
                    for field in aggregate_fields.keys():
                         aggregates[f'total_{field}'] = 0
            else:
                 for field in aggregate_fields.keys():
                      aggregates[f'total_{field}'] = 0
        
        quarterly_results[f'Q{q}'] = aggregates
        
    return quarterly_results

def get_annual_data(model, year, operadora=None, aggregate_fields={}):
    """Aggregates data annually for a given model, year, and fields."""
    queryset = model.objects.filter(ano=year)
    if operadora:
        queryset = queryset.filter(operadora=operadora)
        
    aggregates = {}
    if aggregate_fields:
        valid_aggregates = {}
        for field, agg_func in aggregate_fields.items():
            try:
                field_obj = model._meta.get_field(field)
                output_field_type = DecimalField() if isinstance(field_obj, (models.DecimalField, models.FloatField)) else None
                if output_field_type:
                     valid_aggregates[f'total_{field}'] = agg_func(field, output_field=output_field_type)
                else:
                     valid_aggregates[f'total_{field}'] = agg_func(field)
            except FieldDoesNotExist:
                logger.warning(f"Field '{field}' does not exist on model {model.__name__}. Skipping aggregation.")
                # Provide appropriate zero value since we don't know the field type
                valid_aggregates[f'total_{field}'] = Value(Decimal('0.0'))
        
        if valid_aggregates:
            try:
                annual_aggregates = queryset.aggregate(**valid_aggregates)
                for key, value in annual_aggregates.items():
                    aggregates[key] = float(value) if isinstance(value, Decimal) else (value or 0)
            except Exception as agg_error:
                logger.error(f"Error during annual aggregation for model {model.__name__}, year {year}: {agg_error}")
                for field in aggregate_fields.keys():
                    aggregates[f'total_{field}'] = 0
        else:
            for field in aggregate_fields.keys():
                 aggregates[f'total_{field}'] = 0
            
    return aggregates

# --- Base Analysis View --- 

class BaseAnalysisView(TemplateView):
    """Base view for market analysis, providing common context."""
    analysis_title = "Análise de Mercado"
    indicator_model = None # Must be set by subclass
    aggregate_fields = {} # Must be set by subclass {field_name: AggregationFunction}
    template_name = 'questionarios/analise/base_analise.html' # Default template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['analysis_title'] = self.analysis_title
        context['indicator_name'] = self.indicator_model._meta.verbose_name_plural if self.indicator_model else "Indicador"
        
        if not self.indicator_model or not self.aggregate_fields:
            context['error'] = "Configuração da view incompleta (modelo ou campos de agregação não definidos)."
            context['anos_disponiveis'] = []
            context['operadoras'] = []
            context['analysis_data_json'] = json.dumps({})
            return context # Return early if config is bad

        anos_disponiveis = get_available_years(self.indicator_model)
        from .base_views import OPERADORAS_CHOICES
        operadoras = [choice[0] for choice in OPERADORAS_CHOICES if choice[0]]
        
        context['anos_disponiveis'] = anos_disponiveis
        context['operadoras'] = [op.upper() for op in operadoras]
        
        if not anos_disponiveis:
            context['error'] = f"Nenhum dado encontrado para {context['indicator_name']}."
            context['analysis_data_json'] = json.dumps({})
            return context # Return early if no data years

        # Ensure year is extracted correctly
        try:
            ano_selecionado_str = self.request.GET.get('ano')
            if ano_selecionado_str:
                ano_selecionado = int(ano_selecionado_str)
                if ano_selecionado not in anos_disponiveis:
                    ano_selecionado = anos_disponiveis[-1] # Default to latest if invalid year selected
            else:
                 ano_selecionado = anos_disponiveis[-1] # Default to latest if no year selected
        except (ValueError, TypeError):
             ano_selecionado = anos_disponiveis[-1] # Fallback on error
        
        context['ano_selecionado'] = ano_selecionado
        
        analysis_data = {}
        # Get total market data (all operators)
        analysis_data['TOTAL'] = {
            'quarterly': get_quarterly_data(self.indicator_model, ano_selecionado, aggregate_fields=self.aggregate_fields),
            'annual': get_annual_data(self.indicator_model, ano_selecionado, aggregate_fields=self.aggregate_fields)
        }
        
        # Get data per operator
        for op in operadoras:
            # Ensure operadora code is lowercase if models use lowercase
            op_code = op.lower()
            analysis_data[op.upper()] = { # Keep UPPER for keys in context if templates expect it
                'quarterly': get_quarterly_data(self.indicator_model, ano_selecionado, operadora=op_code, aggregate_fields=self.aggregate_fields),
                'annual': get_annual_data(self.indicator_model, ano_selecionado, operadora=op_code, aggregate_fields=self.aggregate_fields)
            }
            
        context['analysis_data_json'] = json.dumps(analysis_data, default=decimal_default)
        context['analysis_data'] = analysis_data # Pass raw data too if needed by template
        
        return context

# --- Specific Analysis Views --- 

class AssinantesAnalysisView(BaseAnalysisView):
    analysis_title = "Análise de Assinantes"
    indicator_model = AssinantesIndicador
    aggregate_fields = {
        'assinantes_pre_pago': Sum,
        'assinantes_pos_pago': Sum,
        'assinantes_fixo': Sum,
        'assinantes_internet_movel': Sum,
        'assinantes_internet_fixa': Sum,
    }
    template_name = 'questionarios/analise/analise_assinantes.html'

class ReceitasAnalysisView(BaseAnalysisView):
    analysis_title = "Análise de Receitas"
    indicator_model = ReceitasIndicador
    aggregate_fields = {
        'receitas_mensalidades': Sum,
        'receitas_chamadas_on_net': Sum,
        'receitas_chamadas_off_net': Sum,
        'receitas_chamadas_telecel': Sum,
        'receitas_chamadas_rede_movel_b': Sum,
        'receitas_chamadas_outros': Sum,
        'receitas_servico_telefonico_fixo': Sum,
        'receitas_chamadas_cedeao': Sum,
        'receitas_chamadas_cplp': Sum,
        'receitas_chamadas_palop': Sum,
        'receitas_chamadas_resto_africa': Sum,
        'receitas_chamadas_resto_mundo': Sum,
        'receitas_voz_roaming_out': Sum,
        'receitas_mensagens': Sum,
        'receitas_mms': Sum,
        'receitas_dados_moveis': Sum,
        'receitas_internet_banda_larga': Sum,
        'receitas_videochamadas': Sum,
        'receitas_mobile_tv': Sum,
        'receitas_outros_servicos_dados': Sum,
        'receitas_roaming_out_dados': Sum,
        'receitas_internet_roaming_out': Sum,
        'outras_receitas_retalhistas': Sum,
        'receitas_terminacao_voz': Sum,
        'receitas_terminacao_dados': Sum,
        'receitas_originacao_trafego': Sum,
        'receitas_servicos_especiais': Sum,
        'outras_receitas_grossistas': Sum,
    }
    template_name = 'questionarios/analise/analise_receitas.html'

class InvestimentoAnalysisView(BaseAnalysisView):
    analysis_title = "Análise de Investimento"
    indicator_model = InvestimentoIndicador
    aggregate_fields = {
        'servicos_telecomunicacoes': Sum,
        'servicos_internet': Sum,
        'servicos_telecomunicacoes_incorporeo': Sum,
        'servicos_internet_incorporeo': Sum,
    }
    template_name = 'questionarios/analise/analise_investimento.html'

class EmpregoAnalysisView(BaseAnalysisView):
    analysis_title = "Análise de Emprego"
    indicator_model = EmpregoIndicador
    aggregate_fields = {
        'emprego_direto_total': Sum,
        'nacionais_total': Sum,
        'nacionais_homem': Sum,
        'nacionais_mulher': Sum,
        'emprego_indireto': Sum,
    }
    template_name = 'questionarios/analise/analise_emprego.html'

class TrafegoOriginadoAnalysisView(BaseAnalysisView):
    analysis_title = "Análise de Tráfego Originado"
    indicator_model = TrafegoOriginadoIndicador
    aggregate_fields = {
        'total_chamadas': Sum,
        'on_net_mesma_operadora': Sum,
        'off_net_outra_operadora_movel': Sum,
        'fixa_nacional': Sum,
        'internacional_saida': Sum,
        'roaming_out': Sum,
        'total_minutos': Sum,
        'duracao_media_chamada_segundos': Avg,
        'sms_total': Sum,
        'sms_on_net': Sum,
        'sms_off_net': Sum,
        'sms_internacional': Sum,
        'sms_roaming_out': Sum,
        'mms_total': Sum,
        'videochamadas_total': Sum,
    }
    template_name = 'questionarios/analise/analise_trafego_originado.html'

class TrafegoTerminadoAnalysisView(BaseAnalysisView):
    analysis_title = "Análise de Tráfego Terminado"
    indicator_model = TrafegoTerminadoIndicador
    aggregate_fields = {
        'total_chamadas': Sum,
        'movel_origem_mesma_operadora': Sum,
        'movel_origem_outra_operadora': Sum,
        'fixa_nacional': Sum,
        'internacional_entrada': Sum,
        'roaming_in': Sum,
        'total_minutos': Sum,
        'duracao_media_chamada_segundos': Avg,
        'sms_total': Sum,
        'sms_origem_mesma_operadora': Sum,
        'sms_origem_outra_operadora': Sum,
        'sms_internacional_entrada': Sum,
        'sms_roaming_in': Sum,
        'mms_total': Sum,
    }
    template_name = 'questionarios/analise/analise_trafego_terminado.html'

class TrafegoRoamingAnalysisView(BaseAnalysisView):
    analysis_title = "Análise de Tráfego Roaming"
    indicator_model = TrafegoRoamingInternacionalIndicador
    aggregate_fields = {
        'roaming_out_total_assinantes': Sum,
        'roaming_out_voz_minutos': Sum,
        'roaming_out_sms_unidades': Sum,
        'roaming_out_dados_mb': Sum,
        'roaming_in_total_visitantes': Sum,
        'roaming_in_voz_minutos': Sum,
        'roaming_in_sms_unidades': Sum,
        'roaming_in_dados_mb': Sum,
    }
    template_name = 'questionarios/analise/analise_trafego_roaming.html'

class LBIAnalysisView(BaseAnalysisView):
    analysis_title = "Análise LBI (Links Banda Larga Internacional)"
    indicator_model = LBIIndicador
    aggregate_fields = {
        'contratada_down': Sum,
        'contratada_up': Sum,
        'utilizada_down': Sum,
        'utilizada_up': Sum,
        'satelite': Sum,
        'cabo_fibra_optica': Sum,
        'feixe_hertziano': Sum,
    }
    template_name = 'questionarios/analise/analise_lbi.html'

class TrafegoInternetAnalysisView(BaseAnalysisView):
    analysis_title = "Análise de Tráfego Internet"
    indicator_model = TrafegoInternetIndicador
    aggregate_fields = {
        'trafego_total': Sum,
        'por_via_satelite': Sum,
        'por_sistema_hertziano_fixo_terra': Sum,
        'fibra_otica': Sum,
        'banda_estreita_256kbps': Sum,
        'kbps_64_128': Sum,
        'kbps_128_256': Sum,
        'banda_estreita_outros': Sum,
        'banda_larga_total': Sum,
        'kbits_256_2mbits': Sum,
        'mbits_2_4': Sum,
        'mbits_10': Sum,
        'banda_larga_outros': Sum,
        'residencial': Sum,
        'corporativo_empresarial': Sum,
        'instituicoes_publicas': Sum,
        'instituicoes_ensino': Sum,
        'instituicoes_saude': Sum,
        'ong_outros': Sum,
        'cidade_bissau': Sum,
        'bafata': Sum,
        'biombo': Sum,
        'bolama_bijagos': Sum,
        'cacheu': Sum,
        'gabu': Sum,
        'oio': Sum,
        'quinara': Sum,
        'tombali': Sum,
    }
    template_name = 'questionarios/analise/analise_trafego_internet.html'

class InternetFixoAnalysisView(BaseAnalysisView):
    analysis_title = "Análise de Internet Fixo"
    indicator_model = InternetFixoIndicador
    aggregate_fields = {
        'cidade_bissau': Sum,
        'bafata': Sum,
        'biombo': Sum,
        'bolama_bijagos': Sum,
        'cacheu': Sum,
        'gabu': Sum,
        'oio': Sum,
        'quinara': Sum,
        'tombali': Sum,
        'airbox': Sum,
        'sistema_hertziano_fixo_terra': Sum,
        'outros_proxim': Sum,
        'fibra_otica': Sum,
        'banda_larga_256kbits_2mbits': Sum,
        'banda_larga_2_4mbits': Sum,
        'banda_larga_5_10mbits': Sum,
        'banda_larga_outros': Sum,
        'residencial': Sum,
        'corporativo_empresarial': Sum,
        'instituicoes_publicas': Sum,
        'instituicoes_ensino': Sum,
        'instituicoes_saude': Sum,
        'ong_outros': Sum,
    }
    template_name = 'questionarios/analise/analise_internet_fixo.html'

# --- END OF SPECIFIC VIEWS --- 