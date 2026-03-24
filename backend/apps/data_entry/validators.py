from decimal import Decimal
from typing import Optional
from dataclasses import dataclass, field

from apps.indicators.models import Indicator, OperatorTypeIndicator
from .models import DataEntry, CumulativeData


@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_non_negative(value: Optional[Decimal], indicator: Indicator) -> ValidationResult:
    """Valores não podem ser negativos (excepto taxas de crescimento)"""
    result = ValidationResult()
    if value is not None and value < 0:
        if indicator.unit not in ('percentage',):
            result.is_valid = False
            result.errors.append(
                f"{indicator.code} ({indicator.name}): valor negativo ({value}) não permitido"
            )
    return result


def validate_operator_applicability(operator, indicator: Indicator) -> ValidationResult:
    """Verificar se o indicador é aplicável ao tipo de operador"""
    result = ValidationResult()
    applicable = OperatorTypeIndicator.objects.filter(
        operator_type=operator.operator_type,
        indicator=indicator,
        is_applicable=True,
    ).exists()
    if not applicable:
        result.is_valid = False
        result.errors.append(
            f"Indicador '{indicator.code} - {indicator.name}' não é aplicável a {operator.name} "
            f"(tipo: {operator.operator_type.name})"
        )
    return result


def validate_children_sum(
    indicator: Indicator, operator, period, expected_total: Decimal
) -> ValidationResult:
    """Total deve igualar a soma dos sub-indicadores"""
    result = ValidationResult()
    if not indicator.is_calculated or indicator.formula_type != 'sum_children':
        return result

    children = indicator.children.all()
    if not children.exists():
        return result

    children_sum = Decimal('0')
    for child in children:
        entry = DataEntry.objects.filter(
            indicator=child, operator=operator, period=period,
        ).first()
        if entry and entry.value is not None:
            children_sum += entry.value

    if children_sum > 0 and expected_total is not None:
        diff = abs(expected_total - children_sum)
        tolerance = max(Decimal('1'), children_sum * Decimal('0.001'))
        if diff > tolerance:
            result.warnings.append(
                f"{indicator.code}: total ({expected_total}) difere da soma "
                f"dos sub-indicadores ({children_sum}), diferença: {diff}"
            )
    return result


def validate_growth_rate(
    indicator: Indicator, operator, period, value: Decimal
) -> ValidationResult:
    """Alertar se crescimento superior a 100% ou inferior a -50%"""
    result = ValidationResult()
    if value is None or value == 0:
        return result

    previous_entries = DataEntry.objects.filter(
        indicator=indicator, operator=operator,
        period__year=period.year - 1 if period.month == period.month else period.year,
    ).order_by('-period__year', '-period__month').first()

    if not previous_entries or previous_entries.value is None or previous_entries.value == 0:
        return result

    prev = previous_entries.value
    growth = ((value - prev) / abs(prev)) * 100

    if growth > 200:
        result.warnings.append(
            f"{indicator.code}: crescimento de {growth:.1f}% face ao período anterior "
            f"(de {prev} para {value}) — verificar anomalia"
        )
    elif growth < -50:
        result.warnings.append(
            f"{indicator.code}: queda de {abs(growth):.1f}% face ao período anterior "
            f"(de {prev} para {value}) — verificar anomalia"
        )
    return result


def validate_outlier(
    indicator: Indicator, operator, period, value: Decimal
) -> ValidationResult:
    """Detectar outliers comparando com o período anterior"""
    result = ValidationResult()
    if value is None:
        return result

    prev = DataEntry.objects.filter(
        indicator=indicator, operator=operator,
        period__year__lte=period.year,
    ).exclude(period=period).order_by('-period__year', '-period__month').first()

    if not prev or prev.value is None or prev.value == 0:
        return result

    ratio = value / prev.value
    if ratio > 3:
        result.warnings.append(
            f"{indicator.code}: valor ({value}) é {ratio:.1f}x o período anterior ({prev.value})"
        )
    elif ratio < Decimal('0.33'):
        result.warnings.append(
            f"{indicator.code}: valor ({value}) é apenas {ratio:.1%} do anterior ({prev.value})"
        )
    return result


def validate_cumulative_ascending(
    indicator: Indicator, operator, year: int,
    val_3m: Optional[Decimal], val_6m: Optional[Decimal],
    val_9m: Optional[Decimal], val_12m: Optional[Decimal],
) -> ValidationResult:
    """Dados cumulativos devem ser crescentes: 3M ≤ 6M ≤ 9M ≤ 12M"""
    result = ValidationResult()
    vals = [('3M', val_3m), ('6M', val_6m), ('9M', val_9m), ('12M', val_12m)]
    non_null = [(label, v) for label, v in vals if v is not None]

    for i in range(1, len(non_null)):
        prev_label, prev_val = non_null[i - 1]
        curr_label, curr_val = non_null[i]
        if curr_val < prev_val:
            result.is_valid = False
            result.errors.append(
                f"{indicator.code}: dados cumulativos não crescentes — "
                f"{curr_label} ({curr_val}) < {prev_label} ({prev_val})"
            )
    return result


def validate_data_entry(entry_data: dict, operator) -> ValidationResult:
    """Executa todas as validações para uma entrada de dados"""
    combined = ValidationResult()
    indicator = entry_data['indicator']
    value = entry_data.get('value')

    checks = [
        validate_operator_applicability(operator, indicator),
        validate_non_negative(value, indicator),
    ]

    period = entry_data.get('period')
    if period and value is not None:
        checks.append(validate_growth_rate(indicator, operator, period, value))
        checks.append(validate_outlier(indicator, operator, period, value))
        checks.append(validate_children_sum(indicator, operator, period, value))

    for check in checks:
        combined.errors.extend(check.errors)
        combined.warnings.extend(check.warnings)
        if not check.is_valid:
            combined.is_valid = False

    return combined
