from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from .base import IndicadorBase
import logging

logger = logging.getLogger(__name__)

class InvestimentoIndicador(IndicadorBase):
    # Investimento Corpóreo
    # Serviços de telecomunicações
    servicos_telecomunicacoes = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Serviços de Telecomunicações"
    )
    
    # Serviços de Internet
    servicos_internet = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Serviços de Internet"
    )

    # Investimento Incorpóreo
    # Serviços de telecomunicações
    servicos_telecomunicacoes_incorporeo = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Serviços de Telecomunicações (Incorpóreo)"
    )

    # Serviços de Internet
    servicos_internet_incorporeo = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Serviços de Internet (Incorpóreo)"
    )

    # Campos para rastreamento
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='investimento_criado'
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='investimento_atualizado'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    # Campos adicionais dinâmicos
    outros_investimentos = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        help_text="Campos adicionais de investimentos"
    )

    def calcular_total_corporeo(self):
        try:
            telecomunicacoes = self.servicos_telecomunicacoes or 0
            internet = self.servicos_internet or 0
            return telecomunicacoes + internet
        except Exception as e:
            logger.error(f"Erro ao calcular total corpóreo: {e}")
            return 0

    def calcular_total_incorporeo(self):
        try:
            telecomunicacoes = self.servicos_telecomunicacoes_incorporeo or 0
            internet = self.servicos_internet_incorporeo or 0
            return telecomunicacoes + internet
        except Exception as e:
            logger.error(f"Erro ao calcular total incorpóreo: {e}")
            return 0

    def calcular_total_geral(self):
        try:
            return self.calcular_total_corporeo() + self.calcular_total_incorporeo()
        except Exception as e:
            logger.error(f"Erro ao calcular total geral: {e}")
            return 0

    def calcular_total_outros(self):
        return 0  # Simplificado para evitar parsing de JSON

    def __str__(self):
        operadora_display = self.get_operadora_display() if self.operadora else "Não definida"
        return f"Investimento - {self.ano}/{self.mes} - {operadora_display}"

    class Meta:
        unique_together = ('ano', 'mes', 'operadora')
        verbose_name = "Indicador de Investimento"
        verbose_name_plural = "Indicadores de Investimento"