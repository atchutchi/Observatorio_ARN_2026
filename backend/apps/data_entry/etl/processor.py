"""
Pipeline ETL para ficheiros Excel dos operadores.
Suporta Questionário Telecel (ex-MTN), KPI Orange e Questionário Starlink.
"""
import logging
from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd
from django.utils import timezone

from apps.operators.models import Operator
from apps.indicators.models import IndicatorCategory, Indicator, OperatorTypeIndicator, Period
from apps.data_entry.models import DataEntry, CumulativeData, FileUpload
from .sheet_mappings import (
    SHEET_TO_CATEGORY, OPERATOR_NAME_MAPPING,
    MONTHLY_COLUMN_LAYOUT, CUMULATIVE_COLUMN_LAYOUT, CUMULATIVE_CATEGORIES,
)

logger = logging.getLogger(__name__)


class ExcelProcessor:
    def __init__(self, file_upload: FileUpload):
        self.file_upload = file_upload
        self.operator = file_upload.operator
        self.year = file_upload.year
        self.quarter = file_upload.quarter
        self.log_entries: list[str] = []
        self.records_imported = 0
        self.records_errors = 0

    def log(self, message: str, level: str = 'info'):
        self.log_entries.append(f"[{level.upper()}] {message}")
        getattr(logger, level)(message)

    def process(self) -> bool:
        try:
            self.file_upload.status = 'processing'
            self.file_upload.save()
            self.log(f"Iniciando processamento: {self.file_upload.original_filename}")

            xl = pd.ExcelFile(self.file_upload.file.path)
            self.log(f"Sheets encontradas: {xl.sheet_names}")

            applicable_categories = self._get_applicable_categories()
            self.log(f"Categorias aplicáveis a {self.operator.name}: {[c.code for c in applicable_categories]}")

            for sheet_name in xl.sheet_names:
                category_code = SHEET_TO_CATEGORY.get(sheet_name)
                if not category_code:
                    self.log(f"Sheet '{sheet_name}' não mapeada — ignorada", 'warning')
                    continue

                category = IndicatorCategory.objects.filter(code=category_code).first()
                if not category:
                    self.log(f"Categoria '{category_code}' não encontrada na BD", 'warning')
                    continue

                if category not in applicable_categories:
                    self.log(f"Categoria '{category.name}' não aplicável a {self.operator.name} — ignorada")
                    continue

                df = xl.parse(sheet_name, header=None)
                self.log(f"Processando sheet '{sheet_name}' ({len(df)} linhas)")

                if category_code in CUMULATIVE_CATEGORIES:
                    self._process_cumulative_sheet(df, category)
                else:
                    self._process_monthly_sheet(df, category)

            self.file_upload.status = 'processed'
            self.file_upload.records_imported = self.records_imported
            self.file_upload.records_errors = self.records_errors
            self.file_upload.processing_log = '\n'.join(self.log_entries)
            self.file_upload.processed_at = timezone.now()
            self.file_upload.save()

            self.log(f"Processamento completo: {self.records_imported} registos, {self.records_errors} erros")
            return True

        except Exception as e:
            self.log(f"Erro fatal: {str(e)}", 'error')
            self.file_upload.status = 'error'
            self.file_upload.processing_log = '\n'.join(self.log_entries)
            self.file_upload.save()
            return False

    def _get_applicable_categories(self) -> list[IndicatorCategory]:
        applicable_indicator_ids = OperatorTypeIndicator.objects.filter(
            operator_type=self.operator.operator_type,
            is_applicable=True,
        ).values_list('indicator__category_id', flat=True).distinct()

        return list(IndicatorCategory.objects.filter(id__in=applicable_indicator_ids))

    def _process_monthly_sheet(self, df: pd.DataFrame, category: IndicatorCategory):
        layout = MONTHLY_COLUMN_LAYOUT
        indicators = {
            ind.code: ind for ind in
            Indicator.objects.filter(category=category)
        }

        for row_idx in range(len(df)):
            raw_code = df.iloc[row_idx, layout['indicator_code_col']]
            if pd.isna(raw_code):
                continue

            code = str(raw_code).strip()
            indicator = indicators.get(code)
            if not indicator:
                continue

            if not self._is_indicator_applicable(indicator):
                continue

            for quarter_num, quarter_info in layout['quarters'].items():
                if self.quarter and quarter_num != self.quarter:
                    continue

                for i, month in enumerate(quarter_info['months']):
                    col_idx = quarter_info['start_col'] + i
                    if col_idx >= len(df.columns):
                        continue

                    raw_value = df.iloc[row_idx, col_idx]
                    value = self._parse_value(raw_value)

                    if value is None:
                        continue

                    period = Period.objects.filter(
                        year=self.year, month=month,
                    ).first()

                    if not period:
                        self.log(f"Período {self.year}/{month} não encontrado", 'warning')
                        continue

                    try:
                        DataEntry.objects.update_or_create(
                            indicator=indicator,
                            operator=self.operator,
                            period=period,
                            defaults={
                                'value': value,
                                'source': 'upload',
                                'submitted_by': self.file_upload.uploaded_by,
                                'is_validated': False,
                            },
                        )
                        self.records_imported += 1
                    except Exception as e:
                        self.records_errors += 1
                        self.log(f"Erro ao gravar {indicator.code} / {month}: {e}", 'error')

    def _process_cumulative_sheet(self, df: pd.DataFrame, category: IndicatorCategory):
        layout = CUMULATIVE_COLUMN_LAYOUT
        indicators = {
            ind.code: ind for ind in
            Indicator.objects.filter(category=category)
        }

        for row_idx in range(len(df)):
            raw_code = df.iloc[row_idx, layout['indicator_code_col']]
            if pd.isna(raw_code):
                continue

            code = str(raw_code).strip()
            indicator = indicators.get(code)
            if not indicator:
                continue

            if not self._is_indicator_applicable(indicator):
                continue

            for cum_type, col_idx in layout['periods'].items():
                if col_idx >= len(df.columns):
                    continue

                raw_value = df.iloc[row_idx, col_idx]
                value = self._parse_value(raw_value)

                if value is None:
                    continue

                try:
                    CumulativeData.objects.update_or_create(
                        indicator=indicator,
                        operator=self.operator,
                        year=self.year,
                        cumulative_type=cum_type,
                        defaults={
                            'value': value,
                            'source': 'upload',
                            'submitted_by': self.file_upload.uploaded_by,
                            'is_validated': False,
                        },
                    )
                    self.records_imported += 1
                except Exception as e:
                    self.records_errors += 1
                    self.log(f"Erro ao gravar {indicator.code} / {cum_type}: {e}", 'error')

    def _is_indicator_applicable(self, indicator: Indicator) -> bool:
        return OperatorTypeIndicator.objects.filter(
            operator_type=self.operator.operator_type,
            indicator=indicator,
            is_applicable=True,
        ).exists()

    @staticmethod
    def _parse_value(raw) -> Optional[Decimal]:
        if pd.isna(raw):
            return None
        if isinstance(raw, (int, float)):
            try:
                return Decimal(str(raw))
            except (InvalidOperation, ValueError):
                return None
        s = str(raw).strip().replace(' ', '').replace(',', '.')
        if not s or s in ('-', 'N/A', 'n/a', 'NA', '—', '–'):
            return None
        try:
            return Decimal(s)
        except (InvalidOperation, ValueError):
            return None

    @classmethod
    def detect_operator_from_file(cls, filepath: str) -> Optional[str]:
        """Detect operator from filename or content, with historical name mapping"""
        import os
        filename = os.path.basename(filepath).upper()

        for name, code in OPERATOR_NAME_MAPPING.items():
            if name.upper() in filename:
                return code

        try:
            xl = pd.ExcelFile(filepath)
            first_sheet = xl.parse(xl.sheet_names[0], header=None, nrows=5)
            for row_idx in range(min(5, len(first_sheet))):
                for col_idx in range(min(5, len(first_sheet.columns))):
                    cell = str(first_sheet.iloc[row_idx, col_idx])
                    for name, code in OPERATOR_NAME_MAPPING.items():
                        if name.upper() in cell.upper():
                            return code
        except Exception:
            pass

        return None
