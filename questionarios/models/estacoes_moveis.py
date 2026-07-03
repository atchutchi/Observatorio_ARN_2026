from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import IndicadorBase

class EstacoesMoveisIndicador(IndicadorBase):
    """
    Modelo para indicadores de Estações Móveis conforme KPI ARN.
    Baseado na estrutura Excel: ARN_KPI_ORANGE_2024_Resumo.xlsx
    """
    
    # ========== 1. ESTAÇÕES MÓVEIS ATIVAS (Seção A.1) ==========
    # 1.1 Planos Pós-pagos
    afectos_planos_pos_pagos = models.IntegerField(
        verbose_name="1.1 Afectos a planos Pós-pagos",
        validators=[MinValueValidator(0)],
        default=0
    )
    afectos_planos_pos_pagos_utilizacao = models.IntegerField(
        verbose_name="1.1.a Com utilização efectiva (Pós-pagos)",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    # 1.2 Planos Pré-pagos (valores grandes - milhões)
    afectos_planos_pre_pagos = models.BigIntegerField(
        verbose_name="1.2 Afectos a planos Pré-pagos",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Valores em milhões de estações"
    )
    afectos_planos_pre_pagos_utilizacao = models.BigIntegerField(
        verbose_name="1.2.a Com utilização efectiva (Pré-pagos)",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    # 1.3 e 1.4 Situações específicas
    associados_situacoes_especificas = models.IntegerField(
        verbose_name="1.3 Associados a situações específicas",
        null=True, blank=True,
        help_text="NA se não aplicável"
    )
    outros_residuais = models.IntegerField(
        verbose_name="1.4 Outros (residuais)",
        null=True, blank=True,
        help_text="NA se não aplicável"
    )

    # ========== 2. UTILIZADORES DE SERVIÇOS (Seção 2) ==========
    # 2.1.1 SMS
    sms = models.BigIntegerField(
        verbose_name="2.1.1 SMS",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    # 2.1.2 MMS
    mms = models.IntegerField(
        verbose_name="2.1.2 MMS",
        null=True, blank=True,
        help_text="NA se não aplicável"
    )
    
    # 2.1.3 Mobile TV
    mobile_tv = models.IntegerField(
        verbose_name="2.1.3 Mobile TV",
        null=True, blank=True,
        help_text="NA se não aplicável"
    )
    
    # 2.1.4 Roaming Internacional
    roaming_internacional_out_parc_roaming_out = models.BigIntegerField(
        verbose_name="2.1.4 Roaming Internacional - OUT - PARC ROAMING OUT",
        validators=[MinValueValidator(0)],
        default=0
    )

    # ========== 2.1.5 BANDA LARGA (3G + 4G) ==========
    # 2.1.5.1 Tecnologia 3G
    utilizadores_servico_3g_upgrades = models.BigIntegerField(
        verbose_name="2.1.5.1 Utilizadores de serviço de 3G e upgrades",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    utilizadores_acesso_internet_3g = models.IntegerField(
        verbose_name="2.1.5.1.1 Utilizadores de acesso à Internet banda larga (3G)",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    utilizadores_3g_placas_box = models.IntegerField(
        verbose_name="2.1.5.1.1.p Placas (Box) 3G",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    utilizadores_3g_placas_usb = models.IntegerField(
        verbose_name="2.1.5.1.1.q Placas (USB) 3G",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    # 2.1.5.2 Tecnologia 4G
    utilizadores_servico_4g = models.BigIntegerField(
        verbose_name="2.1.5.2 Utilizadores de serviço de 4G",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    utilizadores_acesso_internet_4g = models.IntegerField(
        verbose_name="2.1.5.2.1 Utilizadores de acesso à Internet banda larga (4G)",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    utilizadores_4g_placas_box = models.IntegerField(
        verbose_name="2.1.5.2.1.p Placas (Box) 4G",
        validators=[MinValueValidator(0)],
        default=0
    )
    
    utilizadores_4g_placas_usb = models.IntegerField(
        verbose_name="2.1.5.2.1.q Placas (USB) 4G",
        validators=[MinValueValidator(0)],
        default=0
    )

    # ========== 3. MOBILE MONEY (Seção 3) ==========
    # 3.1 Número de utilizadores
    numero_utilizadores = models.BigIntegerField(
        verbose_name="3.1 Número de utilizadores Mobile Money",
        validators=[MinValueValidator(0)],
        default=0
    )
    numero_utilizadores_mulher = models.BigIntegerField(
        verbose_name="3.1.1 Utilizadores Mulher",
        validators=[MinValueValidator(0)],
        default=0
    )
    numero_utilizadores_homem = models.BigIntegerField(
        verbose_name="3.1.2 Utilizadores Homem",
        validators=[MinValueValidator(0)],
        default=0
    )

    # 3.2 Total de carregamentos (valores em bilhões)
    total_carregamentos = models.DecimalField(
        verbose_name="3.2 Total de carregamentos efectuados",
        max_digits=25, decimal_places=2,  # Aumentado para suportar bilhões
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text="Valor monetário total dos carregamentos"
    )
    total_carregamentos_mulher = models.DecimalField(
        verbose_name="3.2.1 Carregamentos Mulher",
        max_digits=25, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    total_carregamentos_homem = models.DecimalField(
        verbose_name="3.2.2 Carregamentos Homem",
        max_digits=25, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )

    # 3.3 Total de levantamentos (valores em bilhões)
    total_levantamentos = models.DecimalField(
        verbose_name="3.3 Total de levantamentos efectuados",
        max_digits=25, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text="Valor monetário total dos levantamentos"
    )
    total_levantamentos_mulher = models.DecimalField(
        verbose_name="3.3.1 Levantamentos Mulher",
        max_digits=25, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    total_levantamentos_homem = models.DecimalField(
        verbose_name="3.3.2 Levantamentos Homem",
        max_digits=25, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )

    # 3.4 Total de transferências (valores em bilhões)
    total_transferencias = models.DecimalField(
        verbose_name="3.4 Total de Transferências",
        max_digits=25, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text="Valor monetário total das transferências"
    )
    total_transferencias_mulher = models.DecimalField(
        verbose_name="3.4.1 Transferências Mulher",
        max_digits=25, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    total_transferencias_homem = models.DecimalField(
        verbose_name="3.4.2 Transferências Homem",
        max_digits=25, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )

    # ========== 4. LINHAS ALUGADAS (Seção 4 - NOVO) ==========
    linhas_64kbit = models.IntegerField(
        verbose_name="4.1.1 Linhas 64 Kbit",
        validators=[MinValueValidator(0)],
        default=0,
        blank=True
    )
    linhas_128kbit = models.IntegerField(
        verbose_name="4.1.2 Linhas 128 Kbit/s",
        validators=[MinValueValidator(0)],
        default=0,
        blank=True
    )
    linhas_256kbit = models.IntegerField(
        verbose_name="4.1.3 Linhas 256 Kbit/s",
        validators=[MinValueValidator(0)],
        default=0,
        blank=True
    )
    linhas_512kbit = models.IntegerField(
        verbose_name="4.1.4 Linhas 512 Kbit/s",
        validators=[MinValueValidator(0)],
        default=0,
        blank=True
    )
    linhas_1mbit = models.IntegerField(
        verbose_name="4.1.5 Linhas 1 Mbit/s",
        validators=[MinValueValidator(0)],
        default=0,
        blank=True
    )
    linhas_maior_2mbit = models.IntegerField(
        verbose_name="4.1.6 Linhas > 2 Mbit/s",
        validators=[MinValueValidator(0)],
        default=0,
        blank=True
    )

    # Campos de auditoria
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='estacoes_moveis_criadas'
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='estacoes_moveis_atualizadas'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    # ========== MÉTODOS DE CÁLCULO ==========
    def calcular_total_estacoes_moveis(self):
        """Calcula total de estações móveis ativas"""
        return (
            self.afectos_planos_pos_pagos + 
            self.afectos_planos_pre_pagos + 
            (self.associados_situacoes_especificas or 0) + 
            (self.outros_residuais or 0)
        )
    
    def calcular_total_estacoes_com_utilizacao(self):
        """Calcula total de estações com utilização efectiva"""
        return (
            self.afectos_planos_pos_pagos_utilizacao + 
            self.afectos_planos_pre_pagos_utilizacao
        )

    def calcular_total_3g(self):
        """Total de utilizadores 3G (serviço + internet)"""
        return self.utilizadores_servico_3g_upgrades + self.utilizadores_acesso_internet_3g

    def calcular_total_4g(self):
        """Total de utilizadores 4G (serviço + internet)"""
        return self.utilizadores_servico_4g + self.utilizadores_acesso_internet_4g

    def calcular_total_banda_larga(self):
        """Total de utilizadores banda larga (3G + 4G)"""
        # Nota: Um número pode usar 3G e 4G no mesmo mês (conforme nota no Excel)
        return max(
            self.utilizadores_servico_3g_upgrades + self.utilizadores_servico_4g,
            self.utilizadores_acesso_internet_3g + self.utilizadores_acesso_internet_4g
        )

    def calcular_total_linhas_alugadas(self):
        """Total de linhas alugadas/dedicadas"""
        return (
            self.linhas_64kbit + self.linhas_128kbit + 
            self.linhas_256kbit + self.linhas_512kbit + 
            self.linhas_1mbit + self.linhas_maior_2mbit
        )

    def validar_mobile_money(self):
        """Valida consistência dos dados de Mobile Money"""
        errors = []
        
        # Validar soma de gêneros
        if self.numero_utilizadores_mulher + self.numero_utilizadores_homem > self.numero_utilizadores:
            errors.append("Soma de utilizadores por gênero excede o total")
        
        # Validar carregamentos
        soma_carregamentos = self.total_carregamentos_mulher + self.total_carregamentos_homem
        if abs(soma_carregamentos - self.total_carregamentos) > Decimal('0.01'):
            errors.append("Soma de carregamentos por gênero não coincide com total")
        
        # Validar levantamentos
        soma_levantamentos = self.total_levantamentos_mulher + self.total_levantamentos_homem
        if abs(soma_levantamentos - self.total_levantamentos) > Decimal('0.01'):
            errors.append("Soma de levantamentos por gênero não coincide com total")
        
        # Validar transferências
        soma_transferencias = self.total_transferencias_mulher + self.total_transferencias_homem
        if abs(soma_transferencias - self.total_transferencias) > Decimal('0.01'):
            errors.append("Soma de transferências por gênero não coincide com total")
        
        return errors

    def clean(self):
        """Validação do modelo"""
        from django.core.exceptions import ValidationError
        
        errors = self.validar_mobile_money()
        if errors:
            raise ValidationError(errors)
        
        # Validar placas 3G
        if self.utilizadores_3g_placas_box + self.utilizadores_3g_placas_usb > self.utilizadores_acesso_internet_3g:
            raise ValidationError("Total de placas 3G não pode exceder utilizadores de internet 3G")
        
        # Validar placas 4G
        if self.utilizadores_4g_placas_box + self.utilizadores_4g_placas_usb > self.utilizadores_acesso_internet_4g:
            raise ValidationError("Total de placas 4G não pode exceder utilizadores de internet 4G")

    def __str__(self):
        return f"Estações Móveis - {self.operadora} - {self.ano}/{self.mes:02d}"

    class Meta:
        unique_together = ('ano', 'mes', 'operadora')
        verbose_name = "Indicador de Estações Móveis"
        verbose_name_plural = "Indicadores de Estações Móveis"
        ordering = ['-ano', '-mes', 'operadora']