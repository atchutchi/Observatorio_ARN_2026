import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_excel_upload(self, file_upload_id: int):
    """
    Task Celery para processar ficheiro Excel em background.
    Detecta o tipo, lê as sheets, extrai dados, valida e carrega na BD.
    """
    from apps.data_entry.models import FileUpload
    from apps.data_entry.etl.processor import ExcelProcessor

    try:
        upload = FileUpload.objects.get(id=file_upload_id)
    except FileUpload.DoesNotExist:
        logger.error(f"FileUpload {file_upload_id} não encontrado")
        return

    logger.info(f"Processando upload #{upload.id}: {upload.original_filename}")

    processor = ExcelProcessor(upload)
    success = processor.process()

    if success:
        logger.info(
            f"Upload #{upload.id} processado: "
            f"{processor.records_imported} registos, {processor.records_errors} erros"
        )
    else:
        logger.error(f"Upload #{upload.id} falhou")
