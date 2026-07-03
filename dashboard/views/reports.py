# dashboard/views/reports.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.shortcuts import render
import csv
import json

from questionarios.models import (
   EstacoesMoveisIndicador, AssinantesIndicador,
   TrafegoOriginadoIndicador, TrafegoTerminadoIndicador,
   TrafegoRoamingInternacionalIndicador, LBIIndicador,
   TrafegoInternetIndicador, InternetFixoIndicador,
   TarifarioVozMTNIndicador, TarifarioVozOrangeIndicador,
   ReceitasIndicador, EmpregoIndicador, InvestimentoIndicador
)

from dashboard.models import ReportTemplate, GeneratedReport, ReportSchedule
from ..utils.report_generator import ARNReportGenerator
from ..services.export_service import ARNExportService

class ReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
   template_name = 'dashboard/reports.html'
   
   def test_func(self):
       return self.request.user.is_staff
   
   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       year = self.request.GET.get('year', timezone.now().year)
       
       context.update({
           'estacoes_moveis': self.get_mobile_stats(year),
           'trafego': self.get_traffic_stats(year),
           'internet': self.get_internet_stats(year),
           'receitas': self.get_revenue_stats(year),
           'anos_disponiveis': self.get_available_years(),
           'ano_selecionado': year
       })
       return context

   def get_mobile_stats(self, year):
       estacoes = EstacoesMoveisIndicador.objects.filter(ano=year)
       return {
           'total_assinantes': estacoes.aggregate(total=Sum('total_assinantes')),
           'por_operadora': {
               'telecel': estacoes.filter(operadora='TELECEL').aggregate(
                   total=Sum('total_assinantes')
               ),
               'orange': estacoes.filter(operadora='ORANGE').aggregate(
                   total=Sum('total_assinantes')
               )
           },
           'crescimento': self.calcular_crescimento(EstacoesMoveisIndicador, year, 'total_assinantes')
       }

   def get_traffic_stats(self, year):
       trafego_terminado = TrafegoTerminadoIndicador.objects.filter(ano=year)
       trafego_originado = TrafegoOriginadoIndicador.objects.filter(ano=year)
       
       return {
           'onnet': {
               'telecel': trafego_originado.filter(operadora='TELECEL').aggregate(
                   total=Sum('chamadas_on_net')
               ),
               'orange': trafego_originado.filter(operadora='ORANGE').aggregate(
                   total=Sum('chamadas_on_net')
               )
           },
           'offnet': {
               'telecel': trafego_originado.filter(operadora='TELECEL').aggregate(
                   total=Sum('chamadas_off_net')
               ),
               'orange': trafego_originado.filter(operadora='ORANGE').aggregate(
                   total=Sum('chamadas_off_net')
               )
           },
           'internacional': {
               'entrada': trafego_terminado.aggregate(
                   total=Sum('chamadas_internacionais')
               ),
               'saida': trafego_originado.aggregate(
                   total=Sum('chamadas_internacionais')
               )
           }
       }

   def get_internet_stats(self, year):
       return {
           '3g': LBIIndicador.objects.filter(
               ano=year, 
               tecnologia='3G'
           ).aggregate(total=Sum('total_assinantes')),
           '4g': LBIIndicador.objects.filter(
               ano=year, 
               tecnologia='4G'
           ).aggregate(total=Sum('total_assinantes')),
           'trafego': TrafegoInternetIndicador.objects.filter(
               ano=year
           ).aggregate(total=Sum('trafego_total'))
       }

   def get_revenue_stats(self, year):
       receitas = ReceitasIndicador.objects.filter(ano=year)
       return {
           'total': receitas.aggregate(total=Sum('receita_total')),
           'por_operadora': {
               'telecel': receitas.filter(operadora='TELECEL').aggregate(
                   total=Sum('receita_total')
               ),
               'orange': receitas.filter(operadora='ORANGE').aggregate(
                   total=Sum('receita_total')
               )
           },
           'crescimento': self.calcular_crescimento(ReceitasIndicador, year, 'receita_total')
       }

   def get_available_years(self):
       years = set()
       models = [
           EstacoesMoveisIndicador,
           TrafegoOriginadoIndicador,
           ReceitasIndicador
       ]
       for model in models:
           years.update(model.objects.values_list('ano', flat=True).distinct())
       return sorted(years, reverse=True)

   def calcular_crescimento(self, model, year, field):
       ano_atual = model.objects.filter(ano=year).aggregate(total=Sum(field))['total'] or 0
       ano_anterior = model.objects.filter(ano=year-1).aggregate(total=Sum(field))['total'] or 0
       
       if ano_anterior == 0:
           return 0
       return ((ano_atual - ano_anterior) / ano_anterior) * 100

class ExportReportView(LoginRequiredMixin, UserPassesTestMixin, View):
   def test_func(self):
       return self.request.user.is_staff
   
   def get(self, request, *args, **kwargs):
       year = request.GET.get('year', timezone.now().year)
       report_type = request.GET.get('type', 'completo')
       
       response = HttpResponse(content_type='text/csv')
       response['Content-Disposition'] = f'attachment; filename="relatorio_mercado_{year}_{report_type}.csv"'
       
       writer = csv.writer(response)
       self.write_report(writer, year, report_type)
       
       return response
       
   def write_report(self, writer, year, report_type):
       if report_type == 'estacoes':
           self.write_mobile_report(writer, year)
       elif report_type == 'trafego':
           self.write_traffic_report(writer, year)
       else:
           self.write_full_report(writer, year)
           
   def write_mobile_report(self, writer, year):
       writer.writerow(['Relatório de Estações Móveis', year])
       writer.writerow(['Operadora', 'Total Assinantes', 'Quota de Mercado (%)'])
       
       estacoes = EstacoesMoveisIndicador.objects.filter(ano=year)
       total = estacoes.aggregate(total=Sum('total_assinantes'))['total'] or 0
       
       for operadora in ['TELECEL', 'ORANGE']:
           subtotal = estacoes.filter(operadora=operadora).aggregate(
               total=Sum('total_assinantes')
           )['total'] or 0
           
           writer.writerow([
               operadora,
               subtotal,
               round(subtotal/total * 100, 2) if total > 0 else 0
           ])
           
   def write_traffic_report(self, writer, year):
       writer.writerow(['Relatório de Tráfego', year])
       writer.writerow(['Tipo', 'TELECEL', 'Orange', 'Total'])
       
       trafego = TrafegoOriginadoIndicador.objects.filter(ano=year)
       
       # On-Net
       onnet_telecel = trafego.filter(operadora='TELECEL').aggregate(
           total=Sum('chamadas_on_net')
       )['total'] or 0
       onnet_orange = trafego.filter(operadora='ORANGE').aggregate(
           total=Sum('chamadas_on_net')
       )['total'] or 0
       
       writer.writerow([
           'Tráfego On-Net',
           onnet_telecel,
           onnet_orange,
           onnet_telecel + onnet_orange
       ])
       
       # Continue with Off-Net and International traffic...
           
   def write_full_report(self, writer, year):
       self.write_mobile_report(writer, year)
       writer.writerow([])  # Empty row for separation
       self.write_traffic_report(writer, year)


# ===== NOVAS VIEWS COM SISTEMA DE RELATÓRIOS ARN =====

class MarketReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Relatório completo do mercado de telecomunicações"""
    template_name = 'dashboard/reports/market_report.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))
        
        # Usar o gerador de relatórios
        generator = ARNReportGenerator(year=year)
        market_data = generator.generate_market_report()
        
        context.update({
            'report_data': market_data,
            'year': year,
            'anos_disponiveis': self.get_available_years(),
            'chart_configs': self.get_chart_configurations(market_data)
        })
        
        return context
    
    def get_available_years(self):
        """Anos disponíveis nos dados"""
        years = set()
        models = [AssinantesIndicador, ReceitasIndicador, TrafegoOriginadoIndicador]
        
        for model in models:
            years.update(model.objects.values_list('ano', flat=True).distinct())
        
        return sorted(years, reverse=True)
    
    def get_chart_configurations(self, data):
        """Configurações dos gráficos para o template"""
        generator = ARNReportGenerator()
        
        return {
            'market_share': generator.get_chart_config('pie', data.get('panorama_geral', {})),
            'revenue_evolution': generator.get_chart_config('line', data.get('receitas', {})),
            'traffic_distribution': generator.get_chart_config('doughnut', data.get('trafego_voz', {}))
        }

class DashboardExecutiveView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Dashboard executivo com KPIs principais"""
    template_name = 'dashboard/reports/executive_dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))
        
        generator = ARNReportGenerator(year=year)
        dashboard_data = generator.generate_dashboard_data()
        
        context.update({
            'dashboard_data': dashboard_data,
            'year': year,
            'last_update': timezone.now()
        })
        
        return context

class ComparativeReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Análise comparativa entre operadoras"""
    template_name = 'dashboard/reports/comparative_report.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))
        
        generator = ARNReportGenerator(year=year)
        comparative_data = generator.generate_comparative_report()
        
        context.update({
            'comparative_data': comparative_data,
            'year': year,
            'anos_disponiveis': self.get_available_years()
        })
        
        return context
    
    def get_available_years(self):
        """Anos disponíveis nos dados"""
        years = set()
        models = [AssinantesIndicador, ReceitasIndicador]
        
        for model in models:
            years.update(model.objects.values_list('ano', flat=True).distinct())
        
        return sorted(years, reverse=True)

class ReportAPIView(LoginRequiredMixin, UserPassesTestMixin, View):
    """API para dados dos relatórios (para gráficos dinâmicos)"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get(self, request, *args, **kwargs):
        report_type = kwargs.get('report_type', 'market')
        year = int(request.GET.get('year', timezone.now().year))
        
        generator = ARNReportGenerator(year=year)
        
        if report_type == 'market':
            data = generator.generate_market_report()
        elif report_type == 'dashboard':
            data = generator.generate_dashboard_data()
        elif report_type == 'comparative':
            data = generator.generate_comparative_report()
        else:
            return JsonResponse({'error': 'Tipo de relatório inválido'}, status=400)
        
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

class GenerateReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Gerar relatório personalizado"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        try:
            # Parâmetros do relatório
            report_type = request.POST.get('report_type', 'market')
            year = int(request.POST.get('year', timezone.now().year))
            format_type = request.POST.get('format', 'json')
            
            # Gerar dados
            generator = ARNReportGenerator(year=year)
            
            if report_type == 'market':
                data = generator.generate_market_report()
                title = f"Relatório de Mercado {year}"
            elif report_type == 'dashboard':
                data = generator.generate_dashboard_data()
                title = f"Dashboard Executivo {year}"
            elif report_type == 'comparative':
                data = generator.generate_comparative_report()
                title = f"Análise Comparativa {year}"
            else:
                return JsonResponse({'error': 'Tipo de relatório inválido'}, status=400)
            
            # Salvar no histórico
            generated_report = GeneratedReport.objects.create(
                template=None,  # Template personalizado
                usuario=request.user,
                titulo=title,
                periodo_inicio=timezone.datetime(year, 1, 1),
                periodo_fim=timezone.datetime(year, 12, 31),
                parametros={'report_type': report_type, 'year': year, 'format': format_type},
                status='completed',
                completed_at=timezone.now()
            )
            
            # Retornar dados baseado no formato
            if format_type == 'csv':
                return self.export_csv(data, title)
            elif format_type == 'excel':
                return self.export_excel(data, title)
            else:
                return JsonResponse({
                    'success': True,
                    'report_id': generated_report.id,
                    'data': data
                }, json_dumps_params={'ensure_ascii': False})
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def export_csv(self, data, title):
        """Exportar para CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{title}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([title])
        writer.writerow(['Gerado em:', timezone.now().strftime('%d/%m/%Y %H:%M')])
        writer.writerow([])  # Linha vazia
        
        # Escrever dados de forma simples
        if isinstance(data, dict):
            for key, value in data.items():
                writer.writerow([key, str(value)])
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    writer.writerow(item.values())
                else:
                    writer.writerow([item])
        
        return response
    
    def export_excel(self, data, title):
        """Exportar para Excel (implementação futura)"""
        # Implementar com openpyxl quando necessário
        return JsonResponse({'error': 'Exportação Excel em desenvolvimento'}, status=501)

class ReportHistoryView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Histórico de relatórios gerados"""
    template_name = 'dashboard/reports/report_history.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Últimos 50 relatórios
        reports = GeneratedReport.objects.all()[:50]
        
        context.update({
            'reports': reports,
            'templates': ReportTemplate.objects.filter(ativo=True),
            'schedules': ReportSchedule.objects.filter(ativo=True)
        })
        
        return context