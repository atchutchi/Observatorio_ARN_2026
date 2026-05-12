import logging

from django.conf import settings
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsARNStaff
from .models import Report
from .serializers import ReportSerializer, ReportGenerateSerializer
from .tasks import generate_report_task

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Report.objects.all()
        year = self.request.query_params.get('year')
        report_type = self.request.query_params.get('report_type')
        operator_scope = self.request.query_params.get('operator_scope')
        operator = self.request.query_params.get('operator')
        if year:
            qs = qs.filter(year=year)
        if report_type:
            qs = qs.filter(report_type=report_type)
        if operator_scope:
            qs = qs.filter(operator_scope=operator_scope)
        if operator:
            qs = qs.filter(operator__code=operator)
        return qs

    @action(detail=False, methods=['post'], permission_classes=[IsARNStaff])
    def generate(self, request):
        ser = ReportGenerateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        data = ser.validated_data
        report_type = data['report_type']
        year = data['year']
        quarter = data.get('quarter')
        operator_scope = data.get('operator_scope') or 'all'
        operator = data.get('operator')

        title = data.get('title') or self._build_title(
            report_type, year, quarter, operator_scope, operator,
        )

        report = Report.objects.create(
            title=title,
            report_type=report_type,
            year=year,
            quarter=quarter,
            operator_scope=operator_scope,
            operator=operator,
            generated_by=request.user,
            status='generating',
            sections=data.get('sections', {}),
        )

        try:
            if settings.REPORTS_GENERATE_SYNC:
                generate_report_task(report.id)
                report.refresh_from_db()
            else:
                generate_report_task.delay(report.id)
        except Exception as exc:
            logger.exception("Failed starting report generation")
            report.status = 'error'
            report.error_log = str(exc)
            report.save(update_fields=['status', 'error_log'])
            response_data = ReportSerializer(report).data
            response_data['detail'] = 'Não foi possível iniciar a geração do relatório.'
            return Response(
                response_data,
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        report = self.get_object()
        if not report.pdf_file:
            return Response(
                {'error': 'PDF não disponível'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return FileResponse(
            report.pdf_file.open(),
            as_attachment=True,
            filename=f"{report.title}.pdf",
        )

    @action(detail=True, methods=['get'])
    def download_excel(self, request, pk=None):
        report = self.get_object()
        if not report.excel_file:
            return Response(
                {'error': 'Excel não disponível'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return FileResponse(
            report.excel_file.open(),
            as_attachment=True,
            filename=f"{report.title}.xlsx",
        )

    @action(detail=True, methods=['get'])
    def download_docx(self, request, pk=None):
        report = self.get_object()
        if not report.docx_file:
            return Response(
                {'error': 'Word não disponível'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return FileResponse(
            report.docx_file.open(),
            as_attachment=True,
            filename=f"{report.title}.docx",
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )

    @action(detail=True, methods=['post'], permission_classes=[IsARNStaff])
    def publish(self, request, pk=None):
        report = self.get_object()
        if report.status != 'ready':
            return Response(
                {'error': 'Relatório não está pronto para publicação'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        report.status = 'published'
        report.save(update_fields=['status'])
        return Response(ReportSerializer(report).data)

    def _build_title(self, report_type, year, quarter, operator_scope='all', operator=None):
        if report_type == 'quarterly' and quarter:
            title = f"Observatório Telecom GB — Q{quarter} {year}"
        else:
            title = f"Observatório Telecom GB — {year}"

        if operator_scope == 'operator' and operator:
            return f"{title} — {operator.name}"
        if operator_scope == 'others':
            return f"{title} — Outros operadores"
        return title
