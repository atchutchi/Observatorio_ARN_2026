from django.db import models
from django.conf import settings


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('quarterly', 'Relatório Trimestral'),
        ('annual', 'Relatório Anual'),
        ('custom', 'Relatório Personalizado'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('generating', 'Em Geração'),
        ('ready', 'Pronto'),
        ('published', 'Publicado'),
        ('error', 'Erro'),
    ]

    title = models.CharField(max_length=300, verbose_name='Título')
    report_type = models.CharField(
        max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name='Tipo',
    )
    year = models.IntegerField(verbose_name='Ano')
    quarter = models.IntegerField(null=True, blank=True, verbose_name='Trimestre')
    pdf_file = models.FileField(
        upload_to='reports/pdf/%Y/', blank=True, verbose_name='Ficheiro PDF',
    )
    excel_file = models.FileField(
        upload_to='reports/excel/%Y/', blank=True, verbose_name='Ficheiro Excel',
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='Gerado por',
    )
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de geração')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Estado',
    )
    executive_summary = models.TextField(blank=True, verbose_name='Resumo executivo')
    sections = models.JSONField(default=dict, blank=True, verbose_name='Secções')
    error_log = models.TextField(blank=True, verbose_name='Log de erros')

    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ReportTemplate(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nome')
    report_type = models.CharField(max_length=20, verbose_name='Tipo')
    description = models.TextField(blank=True, verbose_name='Descrição')
    sections = models.JSONField(default=list, verbose_name='Secções')
    is_default = models.BooleanField(default=False, verbose_name='Padrão')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Template de Relatório'
        verbose_name_plural = 'Templates de Relatório'

    def __str__(self):
        return self.name
