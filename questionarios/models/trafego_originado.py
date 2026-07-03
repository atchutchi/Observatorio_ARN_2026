"""
Modelo para Tráfego Originado conforme estrutura KPI ARN.
Seção 5 dos questionários ARN - Tráfego Originado.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import IndicadorBase

class TrafegoOriginadoIndicador(IndicadorBase):
    """
    Modelo para indicadores de Tráfego Originado (Seção 5 KPI ARN).
    Inclui dados de tráfego de dados, mensagens (SMS), voz e chamadas.
    """
    
    # ========== 5.1 TRÁFEGO DE DADOS ==========
    
    # 5.1.1 Tráfego de Dados das redes 2G
    trafego_dados_2g_mbytes = models.BigIntegerField(
        verbose_name="5.1.1 Tráfego de Dados 2G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume em MBytes"
    )
    trafego_dados_2g_sessoes = models.BigIntegerField(
        verbose_name="5.1.1.a Sessões 2G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Número de sessões"
    )
    
    # 5.1.2 Tráfego de Dados das redes 3G e upgrades
    trafego_dados_3g_upgrade_mbytes = models.BigIntegerField(
        verbose_name="5.1.2 Tráfego de Dados 3G e upgrades",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume em MBytes"
    )
    internet_3g_mbytes = models.BigIntegerField(
        verbose_name="5.1.2.1 Internet 3G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume em MBytes"
    )
    internet_3g_placas_modem_mbytes = models.BigIntegerField(
        verbose_name="5.1.2.1.p Placas/Modem 3G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume via Placas/Modem em MBytes"
    )
    internet_3g_modem_usb_mbytes = models.BigIntegerField(
        verbose_name="5.1.2.1.q Modem USB 3G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume via Modem USB em MBytes"
    )
    
    # Sessões 3G
    trafego_dados_3g_upgrade_sessoes = models.BigIntegerField(
        verbose_name="5.1.2.a Sessões 3G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Número de sessões"
    )
    internet_3g_sessoes = models.BigIntegerField(
        verbose_name="5.1.2.1.a Sessões Internet 3G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Número de sessões de Internet"
    )
    internet_3g_placas_modem_sessoes = models.BigIntegerField(
        verbose_name="5.1.2.1.p.a Sessões Placas 3G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Sessões via Placas/Modem"
    )
    internet_3g_modem_usb_sessoes = models.BigIntegerField(
        verbose_name="5.1.2.1.q.a Sessões USB 3G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Sessões via Modem USB"
    )
    
    # 5.1.3 Tráfego de Dados das redes 4G/LTE
    trafego_dados_4g_mbytes = models.BigIntegerField(
        verbose_name="5.1.3 Tráfego de Dados 4G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume em MBytes"
    )
    internet_4g_mbytes = models.BigIntegerField(
        verbose_name="5.1.3.1 Internet 4G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume em MBytes"
    )
    internet_4g_placas_modem_mbytes = models.BigIntegerField(
        verbose_name="5.1.3.1.p Placas/Modem 4G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume via Placas/Modem em MBytes"
    )
    internet_4g_modem_usb_mbytes = models.BigIntegerField(
        verbose_name="5.1.3.1.q Modem USB 4G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume via Modem USB em MBytes"
    )
    
    # Sessões 4G
    trafego_dados_4g_sessoes = models.BigIntegerField(
        verbose_name="5.1.3.a Sessões 4G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Número de sessões"
    )
    internet_4g_sessoes = models.BigIntegerField(
        verbose_name="5.1.3.1.a Sessões Internet 4G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Número de sessões de Internet"
    )
    internet_4g_placas_modem_sessoes = models.BigIntegerField(
        verbose_name="5.1.3.1.p.a Sessões Placas 4G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Sessões via Placas/Modem"
    )
    internet_4g_modem_usb_sessoes = models.BigIntegerField(
        verbose_name="5.1.3.1.q.a Sessões USB 4G",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Sessões via Modem USB"
    )
    
    # ========== 5.2 TRÁFEGO DE MENSAGENS (SMS) ==========
    
    # 5.2.1 Total e divisões nacionais
    sms_total = models.BigIntegerField(
        verbose_name="5.2 Total de SMS",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Número total de mensagens enviadas"
    )
    sms_on_net = models.BigIntegerField(
        verbose_name="5.2.1 SMS On-net",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="SMS dentro da mesma rede"
    )
    sms_off_net_nacional = models.BigIntegerField(
        verbose_name="5.2.2 SMS Off-net Nacional",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="SMS para outras redes nacionais"
    )
    
    # 5.2.3 Internacional (dividido por regiões)
    sms_internacional_total = models.BigIntegerField(
        verbose_name="5.2.3 SMS Internacional Total",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Total de SMS internacionais"
    )
    sms_cedeao = models.BigIntegerField(
        verbose_name="5.2.3.1 SMS CEDEAO",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="SMS para países da CEDEAO"
    )
    sms_palop = models.BigIntegerField(
        verbose_name="5.2.3.2 SMS PALOP",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="SMS para países PALOP"
    )
    sms_cplp = models.BigIntegerField(
        verbose_name="5.2.3.3 SMS CPLP",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="SMS para países CPLP"
    )
    sms_resto_africa = models.BigIntegerField(
        verbose_name="5.2.3.4 SMS Resto de África",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="SMS para outros países africanos"
    )
    sms_resto_mundo = models.BigIntegerField(
        verbose_name="5.2.3.5 SMS Resto do Mundo",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="SMS para resto do mundo"
    )
    
    # ========== 5.3 VOLUME DE TRÁFEGO DE VOZ (MINUTOS) ==========
    
    # 5.3.1 Total e divisões nacionais
    voz_total_minutos = models.BigIntegerField(
        verbose_name="5.3 Total de Minutos de Voz",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Volume total em minutos"
    )
    voz_on_net_minutos = models.BigIntegerField(
        verbose_name="5.3.1 Voz On-net",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Minutos dentro da mesma rede"
    )
    voz_off_net_nacional_minutos = models.BigIntegerField(
        verbose_name="5.3.2 Voz Off-net Nacional",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Minutos para outras redes nacionais"
    )
    voz_rede_fixa_minutos = models.BigIntegerField(
        verbose_name="5.3.2.1 Voz para Rede Fixa",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Minutos para rede fixa"
    )
    voz_outras_redes_moveis_minutos = models.BigIntegerField(
        verbose_name="5.3.2.2 Voz para Outras Redes Móveis",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Minutos para outras operadoras móveis"
    )
    
    # 5.3.3 Internacional (dividido por regiões)
    voz_internacional_total_minutos = models.BigIntegerField(
        verbose_name="5.3.3 Voz Internacional Total",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Total de minutos internacionais"
    )
    voz_cedeao_minutos = models.BigIntegerField(
        verbose_name="5.3.3.1 Voz CEDEAO",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Minutos para países da CEDEAO"
    )
    voz_palop_minutos = models.BigIntegerField(
        verbose_name="5.3.3.2 Voz PALOP",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Minutos para países PALOP"
    )
    voz_cplp_minutos = models.BigIntegerField(
        verbose_name="5.3.3.3 Voz CPLP",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Minutos para países CPLP"
    )
    voz_resto_africa_minutos = models.BigIntegerField(
        verbose_name="5.3.3.4 Voz Resto de África",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Minutos para outros países africanos"
    )
    voz_resto_mundo_minutos = models.BigIntegerField(
        verbose_name="5.3.3.5 Voz Resto do Mundo",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Minutos para resto do mundo"
    )
    
    # ========== 5.4 NÚMERO DE COMUNICAÇÕES DE VOZ (CHAMADAS) ==========
    
    # 5.4.1 Total e divisões nacionais
    chamadas_total = models.BigIntegerField(
        verbose_name="5.4 Total de Chamadas",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Número total de chamadas"
    )
    chamadas_on_net = models.BigIntegerField(
        verbose_name="5.4.1 Chamadas On-net",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Chamadas dentro da mesma rede"
    )
    chamadas_off_net_nacional = models.BigIntegerField(
        verbose_name="5.4.2 Chamadas Off-net Nacional",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Chamadas para outras redes nacionais"
    )
    chamadas_rede_fixa = models.BigIntegerField(
        verbose_name="5.4.2.1 Chamadas para Rede Fixa",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Chamadas para rede fixa"
    )
    chamadas_outras_redes_moveis = models.BigIntegerField(
        verbose_name="5.4.2.2 Chamadas para Outras Redes Móveis",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Chamadas para outras operadoras móveis"
    )
    
    # 5.4.3 Internacional (dividido por regiões)
    chamadas_internacional_total = models.BigIntegerField(
        verbose_name="5.4.3 Chamadas Internacional Total",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Total de chamadas internacionais"
    )
    chamadas_cedeao = models.BigIntegerField(
        verbose_name="5.4.3.1 Chamadas CEDEAO",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Chamadas para países da CEDEAO"
    )
    chamadas_palop = models.BigIntegerField(
        verbose_name="5.4.3.2 Chamadas PALOP",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Chamadas para países PALOP"
    )
    chamadas_cplp = models.BigIntegerField(
        verbose_name="5.4.3.3 Chamadas CPLP",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Chamadas para países CPLP"
    )
    chamadas_resto_africa = models.BigIntegerField(
        verbose_name="5.4.3.4 Chamadas Resto de África",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Chamadas para outros países africanos"
    )
    chamadas_resto_mundo = models.BigIntegerField(
        verbose_name="5.4.3.5 Chamadas Resto do Mundo",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Chamadas para resto do mundo"
    )
    
    # ========== 5.5 OUTROS SERVIÇOS ==========
    numeros_curtos = models.BigIntegerField(
        verbose_name="5.5.1 Números Curtos",
        validators=[MinValueValidator(0)],
        null=True, blank=True,
        default=0,
        help_text="Chamadas/SMS para números curtos"
    )
    
    mms_total = models.BigIntegerField(
        verbose_name="5.5.2 MMS Total",
        validators=[MinValueValidator(0)],
        null=True, blank=True,
        default=0,
        help_text="Total de MMS enviados"
    )
    
    # Campos de auditoria
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='trafego_originado_criado'
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='trafego_originado_atualizado'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    # ========== MÉTODOS DE CÁLCULO ==========
    
    def calcular_total_dados_2g_mb(self):
        """Calcula total de dados 2G em MB"""
        return self.trafego_dados_2g_mbytes
    
    def calcular_total_dados_3g_mb(self):
        """Calcula total de dados 3G em MB"""
        return (
            self.trafego_dados_3g_upgrade_mbytes + 
            self.internet_3g_mbytes + 
            self.internet_3g_placas_modem_mbytes + 
            self.internet_3g_modem_usb_mbytes
        )
    
    def calcular_total_dados_4g_mb(self):
        """Calcula total de dados 4G em MB"""
        return (
            self.trafego_dados_4g_mbytes + 
            self.internet_4g_mbytes + 
            self.internet_4g_placas_modem_mbytes + 
            self.internet_4g_modem_usb_mbytes
        )
    
    def calcular_total_dados_mb(self):
        """Calcula total geral de dados em MB"""
        return (
            self.calcular_total_dados_2g_mb() +
            self.calcular_total_dados_3g_mb() +
            self.calcular_total_dados_4g_mb()
        )
    
    def calcular_total_dados_gb(self):
        """Calcula total de dados em GB"""
        return self.calcular_total_dados_mb() / 1024
    
    def calcular_total_dados_2g_gb(self):
        """Calcula total de dados 2G em GB"""
        return self.calcular_total_dados_2g_mb() / 1024
    
    def calcular_total_dados_3g_gb(self):
        """Calcula total de dados 3G em GB"""
        return self.calcular_total_dados_3g_mb() / 1024
    
    def calcular_total_dados_4g_gb(self):
        """Calcula total de dados 4G em GB"""
        return self.calcular_total_dados_4g_mb() / 1024
    
    def calcular_total_voz_horas(self):
        """Calcula total de voz em horas"""
        return self.calcular_total_voz_minutos() / 60
    
    def calcular_duracao_media_chamada(self):
        """Calcula duração média por chamada em minutos"""
        total_chamadas = self.calcular_total_chamadas()
        if total_chamadas > 0:
            return self.calcular_total_voz_minutos() / total_chamadas
        return 0
    
    def calcular_mb_por_sessao_2g(self):
        """Calcula média de MB por sessão 2G"""
        if self.trafego_dados_2g_sessoes > 0:
            return self.trafego_dados_2g_mbytes / self.trafego_dados_2g_sessoes
        return 0
    
    def calcular_total_voz_dias(self):
        """Calcula total de voz em dias"""
        return self.calcular_total_voz_minutos() / 1440
    
    def calcular_total_sessoes(self):
        """Calcula total de sessões de dados"""
        return (
            self.trafego_dados_2g_sessoes +
            self.trafego_dados_3g_upgrade_sessoes +
            self.internet_3g_sessoes +
            self.internet_3g_placas_modem_sessoes +
            self.internet_3g_modem_usb_sessoes +
            self.trafego_dados_4g_sessoes +
            self.internet_4g_sessoes +
            self.internet_4g_placas_modem_sessoes +
            self.internet_4g_modem_usb_sessoes
        )
    
    def calcular_total_sms_nacional(self):
        """Calcula total de SMS nacionais"""
        return self.sms_on_net + self.sms_off_net_nacional
    
    def calcular_total_sms_internacional(self):
        """Calcula total de SMS internacionais"""
        return (
            self.sms_cedeao + self.sms_palop + self.sms_cplp + 
            self.sms_resto_africa + self.sms_resto_mundo
        )
    
    def calcular_total_sms(self):
        """Calcula total geral de SMS"""
        return self.calcular_total_sms_nacional() + self.calcular_total_sms_internacional()
    
    def calcular_total_voz_nacional_minutos(self):
        """Calcula total de minutos de voz nacional"""
        return (
            self.voz_on_net_minutos + 
            self.voz_off_net_nacional_minutos +
            self.voz_rede_fixa_minutos +
            self.voz_outras_redes_moveis_minutos
        )
    
    def calcular_total_voz_internacional_minutos(self):
        """Calcula total de minutos de voz internacional"""
        return (
            self.voz_cedeao_minutos + self.voz_palop_minutos + 
            self.voz_cplp_minutos + self.voz_resto_africa_minutos + 
            self.voz_resto_mundo_minutos
        )
    
    def calcular_total_voz_minutos(self):
        """Calcula total geral de minutos de voz"""
        return self.calcular_total_voz_nacional_minutos() + self.calcular_total_voz_internacional_minutos()
    
    def calcular_total_chamadas_nacional(self):
        """Calcula total de chamadas nacionais"""
        return (
            self.chamadas_on_net + 
            self.chamadas_off_net_nacional +
            self.chamadas_rede_fixa +
            self.chamadas_outras_redes_moveis
        )
    
    def calcular_total_chamadas_internacional(self):
        """Calcula total de chamadas internacionais"""
        return (
            self.chamadas_cedeao + self.chamadas_palop + 
            self.chamadas_cplp + self.chamadas_resto_africa + 
            self.chamadas_resto_mundo
        )
    
    def calcular_total_chamadas(self):
        """Calcula total geral de chamadas"""
        return self.calcular_total_chamadas_nacional() + self.calcular_total_chamadas_internacional()
    
    def get_percentual_on_net(self):
        """Calcula percentual de tráfego on-net"""
        total_voz = self.calcular_total_voz_minutos()
        if total_voz > 0:
            return (self.voz_on_net_minutos / total_voz) * 100
        return 0
    
    def get_percentual_internacional(self):
        """Calcula percentual de tráfego internacional"""
        total_voz = self.calcular_total_voz_minutos()
        if total_voz > 0:
            return (self.calcular_total_voz_internacional_minutos() / total_voz) * 100
        return 0
    
    def validar_consistencia(self):
        """Valida a consistência dos dados"""
        errors = []
        
        # Validar totais
        if self.sms_total != self.calcular_total_sms():
            errors.append("Total de SMS não coincide com a soma dos componentes")
        
        if self.voz_total_minutos != self.calcular_total_voz_minutos():
            errors.append("Total de minutos de voz não coincide com a soma")
        
        if self.chamadas_total != self.calcular_total_chamadas():
            errors.append("Total de chamadas não coincide com a soma")
        
        # Validar internacional
        if self.sms_internacional_total != self.calcular_total_sms_internacional():
            errors.append("Total SMS internacional não coincide com soma das regiões")
        
        if self.voz_internacional_total_minutos != self.calcular_total_voz_internacional_minutos():
            errors.append("Total voz internacional não coincide com soma das regiões")
        
        if self.chamadas_internacional_total != self.calcular_total_chamadas_internacional():
            errors.append("Total chamadas internacional não coincide com soma das regiões")
        
        return errors
    
    def clean(self):
        """Validação do modelo"""
        from django.core.exceptions import ValidationError
        
        errors = self.validar_consistencia()
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Tráfego Originado - {self.operadora} - {self.ano}/{self.mes:02d}"

    class Meta:
        unique_together = ('ano', 'mes', 'operadora')
        verbose_name = "Indicador de Tráfego Originado"
        verbose_name_plural = "Indicadores de Tráfego Originado"
        ordering = ['-ano', '-mes', 'operadora']