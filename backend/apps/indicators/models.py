from django.db import models


class IndicatorCategory(models.Model):
    """As 11 categorias principais de indicadores"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    order = models.IntegerField(verbose_name='Ordem')
    is_cumulative = models.BooleanField(
        default=False, verbose_name='Cumulativo',
        help_text='Dados reportados em formato cumulativo (3M/6M/9M/12M)',
    )

    class Meta:
        verbose_name = 'Categoria de Indicador'
        verbose_name_plural = 'Categorias de Indicadores'
        ordering = ['order']

    def __str__(self):
        return self.name


class Indicator(models.Model):
    """Cada sub-indicador dentro de uma categoria, organizados hierarquicamente"""
    UNIT_CHOICES = [
        ('number', 'Número'),
        ('minutes', 'Minutos'),
        ('calls', 'Chamadas'),
        ('sms', 'Mensagens SMS'),
        ('mbps', 'MBPS'),
        ('gb', 'Gigabytes'),
        ('mb', 'Megabytes'),
        ('fcfa', 'F CFA'),
        ('fcfa_millions', 'Milhões F CFA'),
        ('kbps', 'Kbps'),
        ('gbps', 'Gbps'),
        ('persons', 'Pessoas'),
        ('percentage', 'Percentagem'),
        ('ms', 'Milissegundos'),
        ('text', 'Texto'),
    ]

    FORMULA_CHOICES = [
        ('', 'Sem fórmula'),
        ('sum_children', 'Soma dos filhos'),
        ('sum_operators', 'Soma dos operadores'),
        ('percentage', 'Percentagem'),
        ('growth_rate', 'Taxa de crescimento'),
        ('penetration', 'Taxa de penetração'),
        ('market_share', 'Quota de mercado'),
    ]

    category = models.ForeignKey(
        IndicatorCategory, on_delete=models.CASCADE,
        related_name='indicators', verbose_name='Categoria',
    )
    code = models.CharField(max_length=20, verbose_name='Código')
    name = models.CharField(max_length=300, verbose_name='Nome')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE,
        related_name='children', verbose_name='Indicador pai',
    )
    unit = models.CharField(
        max_length=20, choices=UNIT_CHOICES, default='number', verbose_name='Unidade',
    )
    level = models.IntegerField(default=0, verbose_name='Nível hierárquico')
    is_calculated = models.BooleanField(default=False, verbose_name='Calculado automaticamente')
    formula_type = models.CharField(
        max_length=50, blank=True, default='',
        choices=FORMULA_CHOICES, verbose_name='Tipo de fórmula',
    )
    order = models.IntegerField(verbose_name='Ordem')
    notes = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Indicador'
        verbose_name_plural = 'Indicadores'
        ordering = ['category__order', 'order']
        unique_together = ['category', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class OperatorTypeIndicator(models.Model):
    """Mapeamento: quais indicadores se aplicam a cada tipo de operador"""
    operator_type = models.ForeignKey(
        'operators.OperatorType', on_delete=models.CASCADE,
        related_name='indicator_mappings', verbose_name='Tipo de Operador',
    )
    indicator = models.ForeignKey(
        Indicator, on_delete=models.CASCADE,
        related_name='operator_type_mappings', verbose_name='Indicador',
    )
    is_applicable = models.BooleanField(default=True, verbose_name='Aplicável')
    is_mandatory = models.BooleanField(default=True, verbose_name='Obrigatório')
    notes = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Indicador por Tipo de Operador'
        verbose_name_plural = 'Indicadores por Tipo de Operador'
        unique_together = ['operator_type', 'indicator']

    def __str__(self):
        status = "✓" if self.is_applicable else "✗"
        return f"{status} {self.operator_type.code} → {self.indicator}"


class Period(models.Model):
    """Período de reporte (mensal, dentro de trimestres)"""
    QUARTER_CHOICES = [(1, 'Q1'), (2, 'Q2'), (3, 'Q3'), (4, 'Q4')]
    MONTH_CHOICES = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
        (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
        (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
        (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
    ]

    year = models.IntegerField(verbose_name='Ano')
    quarter = models.IntegerField(choices=QUARTER_CHOICES, verbose_name='Trimestre')
    month = models.IntegerField(choices=MONTH_CHOICES, verbose_name='Mês')
    start_date = models.DateField(verbose_name='Data início')
    end_date = models.DateField(verbose_name='Data fim')
    is_locked = models.BooleanField(default=False, verbose_name='Bloqueado')

    class Meta:
        verbose_name = 'Período'
        verbose_name_plural = 'Períodos'
        unique_together = ['year', 'month']
        ordering = ['-year', '-quarter', '-month']

    def __str__(self):
        return f"{self.get_month_display()} {self.year} (Q{self.quarter})"
