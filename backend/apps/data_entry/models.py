from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


class DataEntry(models.Model):
    """Valor individual de um indicador por operador e período"""
    SOURCE_CHOICES = [
        ('manual', 'Entrada Manual'),
        ('upload', 'Upload Excel'),
        ('calculated', 'Calculado Automaticamente'),
        ('imported', 'Importado'),
    ]

    indicator = models.ForeignKey(
        'indicators.Indicator', on_delete=models.CASCADE,
        related_name='entries', verbose_name='Indicador',
    )
    operator = models.ForeignKey(
        'operators.Operator', on_delete=models.CASCADE,
        related_name='data_entries', verbose_name='Operador',
    )
    period = models.ForeignKey(
        'indicators.Period', on_delete=models.CASCADE,
        related_name='entries', verbose_name='Período',
    )
    value = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True, verbose_name='Valor',
    )
    observation = models.TextField(blank=True, verbose_name='Observação')
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='Submetido por',
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de submissão')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualização')
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, default='manual', verbose_name='Fonte',
    )
    is_validated = models.BooleanField(default=False, verbose_name='Validado')
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='validated_entries', verbose_name='Validado por',
    )
    validated_at = models.DateTimeField(null=True, blank=True, verbose_name='Data de validação')

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Entrada de Dados'
        verbose_name_plural = 'Entradas de Dados'
        unique_together = ['indicator', 'operator', 'period']
        indexes = [
            models.Index(fields=['operator', 'period']),
            models.Index(fields=['indicator', 'period']),
            models.Index(fields=['operator', 'indicator']),
        ]

    def __str__(self):
        return f"{self.indicator.code} | {self.operator.code} | {self.period} = {self.value}"


class CumulativeData(models.Model):
    """Para indicadores cumulativos (RECEITAS, INVESTIMENTO) — dados 3M, 6M, 9M, 12M"""
    CUMULATIVE_CHOICES = [
        ('3M', '3 Meses (Jan-Mar)'),
        ('6M', '6 Meses (Jan-Jun)'),
        ('9M', '9 Meses (Jan-Set)'),
        ('12M', '12 Meses (Jan-Dez)'),
    ]

    indicator = models.ForeignKey(
        'indicators.Indicator', on_delete=models.CASCADE,
        related_name='cumulative_entries', verbose_name='Indicador',
    )
    operator = models.ForeignKey(
        'operators.Operator', on_delete=models.CASCADE,
        related_name='cumulative_entries', verbose_name='Operador',
    )
    year = models.IntegerField(verbose_name='Ano')
    cumulative_type = models.CharField(
        max_length=5, choices=CUMULATIVE_CHOICES, verbose_name='Período cumulativo',
    )
    value = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True, verbose_name='Valor',
    )
    observation = models.TextField(blank=True, verbose_name='Observação')
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='Submetido por',
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de submissão')
    updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(
        max_length=20, choices=DataEntry.SOURCE_CHOICES,
        default='manual', verbose_name='Fonte',
    )
    is_validated = models.BooleanField(default=False, verbose_name='Validado')

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Dados Cumulativos'
        verbose_name_plural = 'Dados Cumulativos'
        unique_together = ['indicator', 'operator', 'year', 'cumulative_type']

    def __str__(self):
        return f"{self.indicator.code} | {self.operator.code} | {self.year}-{self.cumulative_type} = {self.value}"


class FileUpload(models.Model):
    """Registo de uploads de ficheiros Excel"""
    FILE_TYPE_CHOICES = [
        ('questionnaire_telecel', 'Questionário Telecel'),
        ('questionnaire_orange', 'Questionário Orange'),
        ('questionnaire_starlink', 'Questionário Starlink'),
        ('kpi_orange', 'KPI Orange'),
        ('statistics', 'Dados Estatísticos Consolidados'),
        ('other', 'Outro'),
    ]

    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Em Processamento'),
        ('processed', 'Processado'),
        ('error', 'Erro'),
        ('validated', 'Validado'),
    ]

    operator = models.ForeignKey(
        'operators.Operator', on_delete=models.CASCADE,
        related_name='uploads', verbose_name='Operador',
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='Carregado por',
    )
    received_document = models.ForeignKey(
        'data_entry.ReceivedDocument',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='imports',
        verbose_name='Documento recebido',
    )
    file = models.FileField(upload_to='uploads/%Y/%m/', verbose_name='Ficheiro')
    original_filename = models.CharField(max_length=255, verbose_name='Nome do ficheiro')
    file_type = models.CharField(
        max_length=30, choices=FILE_TYPE_CHOICES, default='other', verbose_name='Tipo',
    )
    year = models.IntegerField(verbose_name='Ano')
    quarter = models.IntegerField(null=True, blank=True, verbose_name='Trimestre')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='uploaded', verbose_name='Estado',
    )
    processing_log = models.TextField(blank=True, verbose_name='Log de processamento')
    records_imported = models.IntegerField(default=0, verbose_name='Registos importados')
    records_errors = models.IntegerField(default=0, verbose_name='Erros')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de upload')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Data de processamento')

    class Meta:
        verbose_name = 'Upload de Ficheiro'
        verbose_name_plural = 'Uploads de Ficheiros'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_filename} ({self.get_status_display()})"


class ReceivedDocument(models.Model):
    """Documento recebido de um operador antes do tratamento e importação de KPIs"""

    DOCUMENT_TYPE_CHOICES = [
        ('questionnaire', 'Questionário preenchido'),
        ('kpi_summary', 'Resumo KPI'),
        ('supporting_document', 'Documento de suporte'),
        ('correspondence', 'Correspondência'),
        ('other', 'Outro'),
    ]

    STATUS_CHOICES = [
        ('received', 'Recebido'),
        ('classifying', 'Em classificação'),
        ('extracting', 'Em extracção'),
        ('reviewing', 'Em revisão'),
        ('validated', 'Validado'),
        ('imported', 'Importado'),
        ('archived', 'Arquivado'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
    ]

    operator = models.ForeignKey(
        'operators.Operator', on_delete=models.CASCADE,
        related_name='received_documents', verbose_name='Operador',
    )
    file = models.FileField(upload_to='received_documents/%Y/%m/', verbose_name='Ficheiro')
    original_filename = models.CharField(max_length=255, verbose_name='Nome original')
    document_type = models.CharField(
        max_length=30, choices=DOCUMENT_TYPE_CHOICES, default='questionnaire',
        verbose_name='Tipo de documento',
    )
    year = models.IntegerField(verbose_name='Ano')
    quarter = models.IntegerField(null=True, blank=True, verbose_name='Trimestre')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='received', verbose_name='Estado',
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='Prioridade',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='assigned_documents', verbose_name='Responsável',
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='received_documents', verbose_name='Recebido por',
    )
    due_date = models.DateField(null=True, blank=True, verbose_name='Prazo interno')
    notes = models.TextField(blank=True, verbose_name='Notas internas')
    checklist = models.JSONField(default=dict, blank=True, verbose_name='Checklist')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de registo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualização')

    class Meta:
        verbose_name = 'Documento Recebido'
        verbose_name_plural = 'Documentos Recebidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['operator', 'year']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"{self.operator.code} | {self.year} | {self.original_filename}"


class DataValidationRule(models.Model):
    """Regras de validação para dados"""
    RULE_TYPE_CHOICES = [
        ('min_value', 'Valor Mínimo'),
        ('max_value', 'Valor Máximo'),
        ('not_null', 'Não pode ser nulo'),
        ('growth_limit', 'Limite de crescimento (%)'),
        ('consistency', 'Consistência com outros indicadores'),
    ]

    indicator = models.ForeignKey(
        'indicators.Indicator', on_delete=models.CASCADE,
        related_name='validation_rules', verbose_name='Indicador',
    )
    rule_type = models.CharField(
        max_length=30, choices=RULE_TYPE_CHOICES, verbose_name='Tipo de regra',
    )
    value = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True, verbose_name='Valor',
    )
    related_indicator = models.ForeignKey(
        'indicators.Indicator', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='related_rules',
        verbose_name='Indicador relacionado',
    )
    error_message = models.CharField(max_length=500, verbose_name='Mensagem de erro')

    class Meta:
        verbose_name = 'Regra de Validação'
        verbose_name_plural = 'Regras de Validação'

    def __str__(self):
        return f"{self.indicator.code}: {self.get_rule_type_display()}"
