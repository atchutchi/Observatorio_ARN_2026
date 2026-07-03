# dashboard/views/analytics.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from questionarios.models import (
    EstacoesMoveisIndicador,
    TrafegoOriginadoIndicador, 
    TrafegoTerminadoIndicador,
    TrafegoRoamingInternacionalIndicador,
    LBIIndicador,
    TrafegoInternetIndicador,
    InternetFixoIndicador,
    TarifarioVozMTNIndicador,  # Corrigido
    TarifarioVozOrangeIndicador,  # Adicionado
    ReceitasIndicador,
    EmpregoIndicador,
    InvestimentoIndicador
)

class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/analytics/overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Análise de Mercado - Visão Geral'
        return context

class MarketAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
   template_name = 'dashboard/analytics/market.html'
   
   def test_func(self):
       return self.request.user.is_staff
   
   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       ano = self.kwargs.get('ano', timezone.now().year)
       
       # Estações Móveis Analytics
       estacoes = EstacoesMoveisIndicador.objects.filter(ano=ano)
       context['estacoes_data'] = {
           'total_assinantes': estacoes.aggregate(total=Sum('total_assinantes')),
           'por_operadora': estacoes.values('operadora').annotate(
               total=Sum('total_assinantes')
           ),
           'crescimento': self.calcular_crescimento(estacoes, ano)
       }
       
       # Internet Analytics
       context['internet_data'] = {
           'assinantes_3g': LBIIndicador.objects.filter(
               ano=ano, 
               tecnologia='3G'
           ).aggregate(total=Sum('total_assinantes')),
           'assinantes_4g': LBIIndicador.objects.filter(
               ano=ano, 
               tecnologia='4G'
           ).aggregate(total=Sum('total_assinantes'))
       }
       
       # Emprego Analytics
       context['emprego_data'] = EmpregoIndicador.objects.filter(ano=ano).aggregate(
           total_direto=Sum('total_empregados'),
           total_indireto=Sum('empregados_indiretos')
       )
       
       return context
       
   def calcular_crescimento(self, queryset, ano):
       ano_anterior = ano - 1
       total_atual = queryset.aggregate(total=Sum('total_assinantes'))['total'] or 0
       total_anterior = EstacoesMoveisIndicador.objects.filter(
           ano=ano_anterior
       ).aggregate(total=Sum('total_assinantes'))['total'] or 0
       
       if total_anterior == 0:
           return 0
       return ((total_atual - total_anterior) / total_anterior) * 100

class TrafficAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
   template_name = 'dashboard/analytics/traffic.html'
   
   def test_func(self):
       return self.request.user.is_staff
   
   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       ano = self.kwargs.get('ano', timezone.now().year)
       
       # Tráfego Originado
       originado = TrafegoOriginadoIndicador.objects.filter(ano=ano)
       context['trafego_originado'] = {
           'total_minutos': originado.aggregate(total=Sum('total_minutos')),
           'por_operadora': originado.values('operadora').annotate(
               total=Sum('total_minutos')
           )
       }
       
       # Tráfego Terminado
       terminado = TrafegoTerminadoIndicador.objects.filter(ano=ano)
       context['trafego_terminado'] = {
           'total_minutos': terminado.aggregate(total=Sum('total_minutos')),
           'por_operadora': terminado.values('operadora').annotate(
               total=Sum('total_minutos')
           )
       }
       
       # Tráfego Roaming
       roaming = TrafegoRoamingInternacionalIndicador.objects.filter(ano=ano)
       context['trafego_roaming'] = {
           'total_minutos': roaming.aggregate(total=Sum('total_minutos')),
           'por_operadora': roaming.values('operadora').annotate(
               total=Sum('total_minutos')
           )
       }
       
       # Tráfego Internet
       internet = TrafegoInternetIndicador.objects.filter(ano=ano)
       context['trafego_internet'] = {
           'total_trafego': internet.aggregate(total=Sum('trafego_total')),
           'por_operadora': internet.values('operadora').annotate(
               total=Sum('trafego_total')
           )
       }
       
       return context

class RevenueAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
   template_name = 'dashboard/analytics/revenue.html'
   
   def test_func(self):
       return self.request.user.is_staff
   
   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       ano = self.kwargs.get('ano', timezone.now().year)
       
       receitas = ReceitasIndicador.objects.filter(ano=ano)
       context['receitas_data'] = {
           'total_receita': receitas.aggregate(total=Sum('receita_total')),
           'por_operadora': receitas.values('operadora').annotate(
               total=Sum('receita_total')
           ),
           'crescimento': self.calcular_crescimento_receita(receitas, ano)
       }
       
       # Dados de Investimento
       investimentos = InvestimentoIndicador.objects.filter(ano=ano)
       context['investimento_data'] = {
           'total_investimento': investimentos.aggregate(total=Sum('total_investimento')),
           'por_operadora': investimentos.values('operadora').annotate(
               total=Sum('total_investimento')
           )
       }
       
       return context
       
   def calcular_crescimento_receita(self, queryset, ano):
       ano_anterior = ano - 1
       total_atual = queryset.aggregate(total=Sum('receita_total'))['total'] or 0
       total_anterior = ReceitasIndicador.objects.filter(
           ano=ano_anterior
       ).aggregate(total=Sum('receita_total'))['total'] or 0
       
       if total_anterior == 0:
           return 0
       return ((total_atual - total_anterior) / total_anterior) * 100