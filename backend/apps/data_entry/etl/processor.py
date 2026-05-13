"""
Pipeline ETL para ficheiros Excel dos operadores.
Suporta Questionário Telecel (ex-MTN), KPI Orange e Questionário Starlink.
"""
import logging
import re
import unicodedata
from datetime import date, datetime
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
    EXCEL_INDICATOR_MAPPINGS,
)

logger = logging.getLogger(__name__)


MONTH_ALIASES = {
    'jan': 1, 'janeiro': 1,
    'feb': 2, 'fev': 2, 'fevereiro': 2,
    'mar': 3, 'marco': 3, 'março': 3,
    'apr': 4, 'abr': 4, 'abril': 4,
    'may': 5, 'mai': 5, 'maio': 5,
    'jun': 6, 'junho': 6,
    'jul': 7, 'julho': 7,
    'aug': 8, 'ago': 8, 'agosto': 8,
    'sep': 9, 'set': 9, 'setembro': 9,
    'oct': 10, 'out': 10, 'outubro': 10,
    'nov': 11, 'novembro': 11,
    'dec': 12, 'dez': 12, 'dezembro': 12,
}

CUMULATIVE_LABELS = {
    '3 meses': '3M',
    '3m': '3M',
    '6 meses': '6M',
    '6m': '6M',
    '9 meses': '9M',
    '9m': '9M',
    '12 meses': '12M',
    '12m': '12M',
}


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
                category_code = self._category_code_for_sheet(sheet_name)
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
        month_columns = self._detect_month_columns(df, only_reported_quarter=True)
        if not month_columns:
            self.log(f"Nenhuma coluna mensal detectada em '{category.name}'", 'warning')
            return

        indicators = {
            ind.code: ind for ind in
            Indicator.objects.filter(category=category)
        }
        pending_values: dict[tuple[Indicator, Period], Decimal] = {}

        for row_idx in range(len(df)):
            raw_code = df.iloc[row_idx, MONTHLY_COLUMN_LAYOUT['indicator_code_col']]
            raw_name = (
                df.iloc[row_idx, MONTHLY_COLUMN_LAYOUT['indicator_name_col']]
                if MONTHLY_COLUMN_LAYOUT['indicator_name_col'] < len(df.columns)
                else None
            )

            code = self._resolve_target_indicator_code(
                category.code,
                raw_code,
                raw_name,
                indicators,
            )
            if not code:
                continue

            indicator = indicators.get(code)
            if not indicator:
                self.log(
                    f"Indicador '{code}' não encontrado na categoria '{category.code}'",
                    'warning',
                )
                continue

            if not self._is_indicator_applicable(indicator):
                continue

            for month, col_idx in month_columns:
                if col_idx >= len(df.columns):
                    continue

                raw_value = df.iloc[row_idx, col_idx]
                value = self._parse_value(raw_value)

                if value is None:
                    continue

                value = self._normalize_value_for_indicator(value, indicator)

                period = Period.objects.filter(
                    year=self.year, month=month,
                ).first()

                if not period:
                    self.log(f"Período {self.year}/{month} não encontrado", 'warning')
                    continue

                key = (indicator, period)
                pending_values[key] = pending_values.get(key, Decimal('0')) + value

        for (indicator, period), value in pending_values.items():
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
                self.log(f"Erro ao gravar {indicator.code} / {period.month}: {e}", 'error')

    def _process_cumulative_sheet(self, df: pd.DataFrame, category: IndicatorCategory):
        cumulative_columns = self._detect_cumulative_columns(df)
        if not cumulative_columns:
            self._process_monthly_cumulative_sheet(df, category)
            return

        indicators = {
            ind.code: ind for ind in
            Indicator.objects.filter(category=category)
        }
        pending_values: dict[tuple[Indicator, str], Decimal] = {}

        for row_idx in range(len(df)):
            raw_code = df.iloc[row_idx, CUMULATIVE_COLUMN_LAYOUT['indicator_code_col']]
            raw_name = (
                df.iloc[row_idx, CUMULATIVE_COLUMN_LAYOUT['indicator_name_col']]
                if CUMULATIVE_COLUMN_LAYOUT['indicator_name_col'] < len(df.columns)
                else None
            )

            code = self._resolve_target_indicator_code(
                category.code,
                raw_code,
                raw_name,
                indicators,
            )
            if not code:
                continue

            indicator = indicators.get(code)
            if not indicator:
                self.log(
                    f"Indicador '{code}' não encontrado na categoria '{category.code}'",
                    'warning',
                )
                continue

            if not self._is_indicator_applicable(indicator):
                continue

            for cum_type, col_idx in cumulative_columns:
                if col_idx >= len(df.columns):
                    continue

                raw_value = df.iloc[row_idx, col_idx]
                value = self._parse_value(raw_value)

                if value is None:
                    continue

                pending_values[(indicator, cum_type)] = self._normalize_value_for_indicator(
                    value, indicator,
                )

        for (indicator, cum_type), value in pending_values.items():
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

    def _process_monthly_cumulative_sheet(self, df: pd.DataFrame, category: IndicatorCategory):
        if not self.quarter:
            self.log(f"Trimestre não definido para '{category.name}'", 'warning')
            return

        month_columns = self._detect_month_columns(df, only_reported_quarter=False)
        if not month_columns:
            self.log(f"Nenhuma coluna mensal cumulativa detectada em '{category.name}'", 'warning')
            return

        target_month = self.quarter * 3
        current_columns = [
            (month, col_idx)
            for month, col_idx in month_columns
            if month <= target_month
        ]
        if not current_columns:
            return

        indicators = {
            ind.code: ind for ind in
            Indicator.objects.filter(category=category)
        }
        pending_values: dict[Indicator, tuple[Decimal, int]] = {}

        for row_idx in range(len(df)):
            raw_code = df.iloc[row_idx, MONTHLY_COLUMN_LAYOUT['indicator_code_col']]
            raw_name = (
                df.iloc[row_idx, MONTHLY_COLUMN_LAYOUT['indicator_name_col']]
                if MONTHLY_COLUMN_LAYOUT['indicator_name_col'] < len(df.columns)
                else None
            )

            code = self._resolve_target_indicator_code(
                category.code,
                raw_code,
                raw_name,
                indicators,
            )
            if not code:
                continue

            indicator = indicators.get(code)
            if not indicator or not self._is_indicator_applicable(indicator):
                continue

            row_total = Decimal('0')
            first_month_with_value = None
            for month, col_idx in current_columns:
                if col_idx >= len(df.columns):
                    continue
                value = self._parse_value(df.iloc[row_idx, col_idx])
                if value is None:
                    continue
                row_total += value
                first_month_with_value = (
                    month if first_month_with_value is None
                    else min(first_month_with_value, month)
                )

            if first_month_with_value is None:
                continue

            row_total = self._normalize_value_for_indicator(row_total, indicator)

            current_value, current_first_month = pending_values.get(
                indicator,
                (Decimal('0'), first_month_with_value),
            )
            pending_values[indicator] = (
                current_value + row_total,
                min(current_first_month, first_month_with_value),
            )

        cum_type = f"{target_month}M"
        for indicator, (value, first_month_with_value) in pending_values.items():
            if first_month_with_value > 1 and self.quarter > 1:
                previous_type = f"{(self.quarter - 1) * 3}M"
                previous = CumulativeData.objects.filter(
                    indicator=indicator,
                    operator=self.operator,
                    year=self.year,
                    cumulative_type=previous_type,
                ).first()
                if previous and previous.value is not None:
                    value += previous.value

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
        mapping = OperatorTypeIndicator.objects.filter(
            operator_type=self.operator.operator_type,
            indicator=indicator,
        ).first()
        if mapping is not None:
            return mapping.is_applicable

        if indicator.parent_id:
            return self._is_indicator_applicable(indicator.parent)

        return OperatorTypeIndicator.objects.filter(
            operator_type=self.operator.operator_type,
            indicator__category=indicator.category,
            is_applicable=True,
        ).exists()

    def _category_code_for_sheet(self, sheet_name: str) -> Optional[str]:
        direct_match = SHEET_TO_CATEGORY.get(sheet_name) or SHEET_TO_CATEGORY.get(sheet_name.strip())
        if direct_match:
            return direct_match

        normalized_sheet = self._normalize_text(sheet_name)
        for candidate, category_code in SHEET_TO_CATEGORY.items():
            if self._normalize_text(candidate) == normalized_sheet:
                return category_code
        return None

    def _resolve_target_indicator_code(
        self,
        category_code: str,
        raw_code,
        raw_name,
        indicators: Optional[dict[str, Indicator]] = None,
    ) -> Optional[str]:
        source_code = self._normalize_code(raw_code)
        source_name = self._normalize_text(raw_name)

        direct_code = self._match_internal_indicator_code(
            indicators,
            source_code,
            source_name,
            require_name=True,
        )
        if direct_code:
            return direct_code

        for mapping in EXCEL_INDICATOR_MAPPINGS.get(category_code, []):
            expected_code = mapping.get('code')
            if expected_code and self._normalize_code(expected_code) != source_code:
                continue

            expected_name = mapping.get('name_contains')
            if expected_name and self._normalize_text(expected_name) not in source_name:
                continue

            return mapping['target']

        return self._match_internal_indicator_code(
            indicators,
            source_code,
            source_name,
            require_name=False,
        )

    @classmethod
    def _match_internal_indicator_code(
        cls,
        indicators: Optional[dict[str, Indicator]],
        source_code: str,
        source_name: str,
        require_name: bool,
    ) -> Optional[str]:
        if not indicators or not source_code:
            return None

        for indicator_code, indicator in indicators.items():
            if cls._normalize_code(indicator_code) != source_code:
                continue

            if require_name:
                indicator_name = cls._normalize_text(indicator.name)
                if not indicator_name or not source_name:
                    continue
                if indicator_name not in source_name and source_name not in indicator_name:
                    continue

            return indicator_code

        return None

    def _detect_month_columns(
        self,
        df: pd.DataFrame,
        only_reported_quarter: bool,
    ) -> list[tuple[int, int]]:
        quarters = [self.quarter] if only_reported_quarter and self.quarter else None
        quarter_columns = self._detect_quarter_columns(df, quarters=quarters)
        if quarter_columns:
            return quarter_columns

        detected: list[tuple[int, int]] = []
        for row_idx in range(min(15, len(df))):
            row_detected: list[tuple[int, int]] = []
            for col_idx in range(3, len(df.columns)):
                month = self._parse_month_header(df.iloc[row_idx, col_idx])
                if not month:
                    continue
                if quarters and ((month - 1) // 3 + 1) not in quarters:
                    continue
                row_detected.append((month, col_idx))
            if len(row_detected) >= 3:
                detected = row_detected
                break

        return detected

    def _detect_quarter_columns(
        self,
        df: pd.DataFrame,
        quarters: Optional[list[int]] = None,
    ) -> list[tuple[int, int]]:
        for row_idx in range(min(12, len(df))):
            groups: list[tuple[int, int]] = []
            for col_idx in range(3, len(df.columns)):
                quarter = self._parse_quarter_label(df.iloc[row_idx, col_idx])
                if quarter:
                    groups.append((quarter, col_idx))

            if not groups:
                continue

            columns: list[tuple[int, int]] = []
            for quarter, start_col in groups:
                if quarters and quarter not in quarters:
                    continue
                for offset in range(3):
                    col_idx = start_col + offset
                    if col_idx >= len(df.columns):
                        continue
                    month = (quarter - 1) * 3 + offset + 1
                    columns.append((month, col_idx))
            if columns:
                return columns
        return []

    def _detect_cumulative_columns(self, df: pd.DataFrame) -> list[tuple[str, int]]:
        for row_idx in range(min(8, len(df))):
            columns: list[tuple[str, int]] = []
            for col_idx in range(3, len(df.columns)):
                label = self._normalize_text(df.iloc[row_idx, col_idx])
                if not label:
                    continue
                for key, cum_type in CUMULATIVE_LABELS.items():
                    if key in label:
                        columns.append((cum_type, col_idx))
                        break
            if columns:
                return columns
        return []

    @classmethod
    def _parse_month_header(cls, raw) -> Optional[int]:
        if pd.isna(raw):
            return None

        if isinstance(raw, (datetime, date, pd.Timestamp)):
            return raw.month

        text = cls._normalize_text(raw)
        if not text:
            return None

        if text in MONTH_ALIASES:
            return MONTH_ALIASES[text]

        first_token = re.split(r'[\s/.-]+', text, maxsplit=1)[0]
        if first_token in MONTH_ALIASES:
            return MONTH_ALIASES[first_token]

        try:
            parsed = pd.to_datetime(str(raw), errors='raise')
        except (ValueError, TypeError, OverflowError):
            return None
        return parsed.month

    @classmethod
    def _parse_quarter_label(cls, raw) -> Optional[int]:
        text = cls._normalize_text(raw)
        if not text:
            return None

        match = re.search(r'([1-4])\s*(?:o|º)?\s*trimestre', text)
        if not match:
            return None
        return int(match.group(1))

    @staticmethod
    def _normalize_code(raw) -> str:
        if pd.isna(raw):
            return ''

        if isinstance(raw, float) and raw.is_integer():
            raw = int(raw)

        code = str(raw).replace('\xa0', ' ').strip()
        code = re.sub(r'\s+', '', code)
        while code.endswith('.'):
            code = code[:-1]
        return code.lower()

    @staticmethod
    def _normalize_text(raw) -> str:
        if raw is None or pd.isna(raw):
            return ''

        text = str(raw).replace('\xa0', ' ').strip().lower()
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(ch for ch in text if not unicodedata.combining(ch))
        text = re.sub(r'\s+', ' ', text)
        return text

    @staticmethod
    def _normalize_value_for_indicator(value: Decimal, indicator: Indicator) -> Decimal:
        if indicator.unit == 'fcfa_millions' and abs(value) >= Decimal('1000000'):
            return value / Decimal('1000000')
        return value

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
