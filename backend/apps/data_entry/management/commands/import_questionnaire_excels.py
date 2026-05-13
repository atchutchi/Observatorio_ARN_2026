"""
Importa questionários Excel de operadores para o pipeline de uploads.

Exemplo:
    python manage.py import_questionnaire_excels --operator TELECEL --year 2023 --file /path/Q1.xlsx
"""
import re
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from apps.data_entry.etl.processor import ExcelProcessor
from apps.data_entry.models import FileUpload
from apps.operators.models import Operator


class Command(BaseCommand):
    help = 'Importa questionários Excel de operadores para a base de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            action='append',
            required=True,
            help='Caminho do ficheiro Excel. Pode ser repetido.',
        )
        parser.add_argument(
            '--operator',
            default='TELECEL',
            help='Código do operador. Ex: TELECEL, ORANGE.',
        )
        parser.add_argument('--year', type=int, required=True)
        parser.add_argument(
            '--file-type',
            default='questionnaire_telecel',
            help='Tipo de ficheiro FileUpload.',
        )
        parser.add_argument(
            '--quarter',
            type=int,
            choices=[1, 2, 3, 4],
            help='Trimestre. Obrigatório apenas quando não for inferido do nome.',
        )

    def handle(self, *args, **options):
        try:
            operator = Operator.objects.get(code=options['operator'].upper())
        except Operator.DoesNotExist as exc:
            raise CommandError(f"Operador {options['operator']} não encontrado") from exc

        uploaded_by = get_user_model().objects.filter(
            role__in=['admin_arn', 'analyst_arn'],
        ).order_by('id').first()

        total_imported = 0
        total_errors = 0

        for raw_file in options['file']:
            path = Path(raw_file).expanduser()
            if not path.is_absolute():
                path = Path.cwd() / path
            if not path.exists():
                raise CommandError(f'Ficheiro não encontrado: {path}')

            quarter = options.get('quarter') or self._infer_quarter(path.name)
            if not quarter:
                raise CommandError(f'Não consegui inferir o trimestre em: {path.name}')

            upload = FileUpload(
                operator=operator,
                uploaded_by=uploaded_by,
                original_filename=path.name,
                file_type=options['file_type'],
                year=options['year'],
                quarter=quarter,
                status='uploaded',
            )
            with path.open('rb') as source:
                upload.file.save(path.name, File(source), save=False)
            upload.save()

            self.stdout.write(
                self.style.HTTP_INFO(f'Processando {path.name} | Q{quarter}'),
            )
            processor = ExcelProcessor(upload)
            success = processor.process()
            upload.refresh_from_db()

            total_imported += upload.records_imported
            total_errors += upload.records_errors
            status_style = self.style.SUCCESS if success else self.style.ERROR
            self.stdout.write(status_style(
                f'  {upload.status}: {upload.records_imported} registos, '
                f'{upload.records_errors} erros',
            ))

        self._compute_derived_totals()

        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída: {total_imported} registos, {total_errors} erros',
        ))

    @staticmethod
    def _infer_quarter(filename: str):
        match = re.search(r'[_\-\s]Q([1-4])(?:[_\-\s.]|$)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))

        normalized = re.sub(r'[_\-.]+', ' ', filename).lower()
        match = re.search(r'\b([1-4])\s*(?:o|º)?\s*trim', normalized)
        if match:
            return int(match.group(1))

        roman_quarters = {
            'i trim': 1,
            'ii trim': 2,
            'iii trim': 3,
            'iv trim': 4,
        }
        for label, quarter in roman_quarters.items():
            if label in normalized:
                return quarter
        return None

    @staticmethod
    def _compute_derived_totals():
        from apps.data_entry.management.commands.import_kpi_json import Command as ImportKpiCommand

        ImportKpiCommand()._compute_root_totals(False)
