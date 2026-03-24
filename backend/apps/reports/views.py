from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsARNStaff
from .models import Report
from .serializers import ReportSerializer, ReportGenerateSerializer
from .tasks import generate_report_task


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Report.objects.all()
        year = self.request.query_params.get('year')
        report_type = self.request.query_params.get('report_type')
        if year:
            qs = qs.filter(year=year)
        if report_type:
            qs = qs.filter(report_type=report_type)
        return qs

    @action(detail=False, methods=['post'], permission_classes=[IsARNStaff])
    def generate(self, request):
        ser = ReportGenerateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        data = ser.validated_data
        report_type = data['report_type']
        year = data['year']
        quarter = data.get('quarter')

        title = data.get('title') or self._build_title(report_type, year, quarter)

        report = Report.objects.create(
            title=title,
            report_type=report_type,
            year=year,
            quarter=quarter,
            generated_by=request.user,
            status='draft',
            sections=data.get('sections', {}),
        )

        generate_report_task.delay(report.id)

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

    def _build_title(self, report_type, year, quarter):
        if report_type == 'quarterly' and quarter:
            return f"Observatório Telecom GB — Q{quarter} {year}"
        return f"Observatório Telecom GB — {year}"
