import traceback
from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone


@shared_task
def generate_report_task(report_id):
    from .models import Report
    from .services.pdf_generator import PDFReportGenerator
    from .services.excel_generator import ExcelReportGenerator

    report = Report.objects.get(id=report_id)
    report.status = 'generating'
    report.save(update_fields=['status'])

    try:
        pdf_gen = PDFReportGenerator(
            year=report.year,
            quarter=report.quarter,
            report_type=report.report_type,
        )
        pdf_bytes = pdf_gen.generate()

        filename_base = f"observatorio_{report.report_type}_{report.year}"
        if report.quarter:
            filename_base += f"_Q{report.quarter}"

        report.pdf_file.save(
            f"{filename_base}.pdf",
            ContentFile(pdf_bytes),
            save=False,
        )

        excel_gen = ExcelReportGenerator(
            year=report.year,
            quarter=report.quarter,
        )
        excel_bytes = excel_gen.generate()

        report.excel_file.save(
            f"{filename_base}.xlsx",
            ContentFile(excel_bytes),
            save=False,
        )

        report.status = 'ready'
        report.save()

    except Exception as e:
        report.status = 'error'
        report.error_log = traceback.format_exc()
        report.save(update_fields=['status', 'error_log'])
        raise e
