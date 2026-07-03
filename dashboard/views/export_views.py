# dashboard/views/export_views.py
"""
Views para exportação de relatórios em PDF, Excel e CSV
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.http import HttpResponse
from django.utils import timezone

from ..utils.report_generator import ARNReportGenerator
from ..services.export_service import ARNExportService


class ExportReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View para exportar relatórios em diferentes formatos"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get(self, request, report_type, format_type):
        """
        Exporta relatório no formato solicitado
        
        Args:
            report_type: 'market', 'executive', 'comparative'
            format_type: 'pdf', 'excel', 'csv'
        """
        year = int(request.GET.get('year', timezone.now().year))
        
        # Gerar dados do relatório
        generator = ARNReportGenerator(year=year)
        
        if report_type == 'market':
            report_data = generator.generate_market_report()
            filename = f'relatorio_mercado_{year}'
        elif report_type == 'executive':
            report_data = generator.generate_dashboard_data()
            filename = f'dashboard_executivo_{year}'
        elif report_type == 'comparative':
            report_data = generator.generate_comparative_report()
            filename = f'analise_comparativa_{year}'
        else:
            return HttpResponse('Tipo de relatório inválido', status=400)
        
        # Criar serviço de exportação
        export_service = ARNExportService(report_data, year, report_type)
        
        # Exportar no formato solicitado
        if format_type == 'pdf':
            try:
                content = export_service.export_to_pdf()
                content_type = 'application/pdf'
                file_extension = 'pdf'
            except Exception as e:
                return HttpResponse(f'Erro ao gerar PDF: {str(e)}', status=500)
        
        elif format_type == 'excel':
            try:
                content = export_service.export_to_excel()
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_extension = 'xlsx'
            except ImportError:
                return HttpResponse(
                    'openpyxl não está instalado. Execute: pip install openpyxl',
                    status=500
                )
            except Exception as e:
                return HttpResponse(f'Erro ao gerar Excel: {str(e)}', status=500)
        
        elif format_type == 'csv':
            try:
                content = export_service.export_to_csv()
                content_type = 'text/csv'
                file_extension = 'csv'
            except Exception as e:
                return HttpResponse(f'Erro ao gerar CSV: {str(e)}', status=500)
        
        else:
            return HttpResponse('Formato de exportação inválido', status=400)
        
        # Preparar resposta HTTP
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}.{file_extension}"'
        
        return response


class QuickExportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View para exportação rápida (sem parâmetros complexos)"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get(self, request):
        """Exportação rápida baseada em parâmetros GET"""
        report_type = request.GET.get('report', 'market')
        format_type = request.GET.get('format', 'pdf')
        year = int(request.GET.get('year', timezone.now().year))
        
        # Redirecionar para a view principal de exportação
        return ExportReportView.as_view()(
            request,
            report_type=report_type,
            format_type=format_type
        )

