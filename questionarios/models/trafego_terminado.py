# models/trafego_terminado.py
from django.db import models
from django.conf import settings
from .base import IndicadorBase

class TrafegoTerminadoIndicador(IndicadorBase):
    # COMUNICAÇÕES DE VOZ
    chamadas_outros_op_moveis_nacionais = models.BigIntegerField(help_text="De outros Operadores móveis nacionais (off-net)")
    chamadas_telecel = models.BigIntegerField(help_text="TELECEL")
    chamadas_operador_b = models.BigIntegerField(null=True, blank=True, help_text="Operador B")
    chamadas_outros = models.BigIntegerField(null=True, blank=True, help_text="Outros (favor especificar)")
    chamadas_operador_rede_fixa = models.BigIntegerField(null=True, blank=True, help_text="Operador da rede Fixa")
    
    # Operadores de redes Internacionais
    chamadas_cedeao = models.BigIntegerField(help_text="CEDEAO")
    chamadas_cplp = models.BigIntegerField(help_text="CPLP")
    chamadas_palop = models.BigIntegerField(help_text="PALOP")
    chamadas_resto_africa = models.BigIntegerField(help_text="Resto de Africa")
    chamadas_resto_mundo = models.BigIntegerField(help_text="Resto do mundo")
    
    chamadas_numeros_curtos = models.BigIntegerField(help_text="N.º de chamadas de voz terminadas em números curtos e números não geográficos")

    # MINUTOS DE VOZ
    minutos_outros_op_moveis_nacionais = models.BigIntegerField(help_text="De outros operadores móveis nacionais (off-net)")
    minutos_telecel = models.BigIntegerField(help_text="TELECEL")
    minutos_operador_b = models.BigIntegerField(null=True, blank=True, help_text="Operador móvel B")
    minutos_outros = models.BigIntegerField(null=True, blank=True, help_text="Outros (favor especificar)")
    minutos_operador_rede_fixa = models.BigIntegerField(null=True, blank=True, help_text="Operador da rede Fixa")
    
    # Para operadores de redes internacionais
    minutos_cedeao = models.BigIntegerField(help_text="CEDEAO")
    minutos_cplp = models.BigIntegerField(help_text="CPLP")
    minutos_palop = models.BigIntegerField(help_text="PALOP")
    minutos_resto_africa = models.BigIntegerField(help_text="Resto de Africa")
    minutos_resto_mundo = models.BigIntegerField(help_text="Resto do mundo")
    
    minutos_numeros_curtos = models.BigIntegerField(help_text="N.º de minutos de voz terminadas em números curtos e números não geográficos")

    # TRAFEGO DE MENSAGENS
    sms_outras_redes_moveis_nacionais = models.BigIntegerField(help_text="De outras redes móveis nacionais (off-net)")
    sms_outras_redes_internacionais = models.BigIntegerField(help_text="De outras redes internacionais")
    sms_outros = models.BigIntegerField(null=True, blank=True, help_text="Outros (Ex. serviços de valor acrescentado baseados no envio de mensagens)")

    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='trafego_terminado_criado')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='trafego_terminado_atualizado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tráfego Terminado - {self.ano}/{self.mes}"

    class Meta:
        unique_together = ('ano', 'mes', 'operadora')

    def calcular_total_chamadas(self):
        return (
            self.chamadas_outros_op_moveis_nacionais +
            self.chamadas_telecel +
            (self.chamadas_operador_b or 0) +
            (self.chamadas_outros or 0) +
            (self.chamadas_operador_rede_fixa or 0) +
            self.chamadas_cedeao +
            self.chamadas_cplp +
            self.chamadas_palop +
            self.chamadas_resto_africa +
            self.chamadas_resto_mundo +
            self.chamadas_numeros_curtos
        )

    def calcular_total_minutos(self):
        return (
            self.minutos_outros_op_moveis_nacionais +
            self.minutos_telecel +
            (self.minutos_operador_b or 0) +
            (self.minutos_outros or 0) +
            (self.minutos_operador_rede_fixa or 0) +
            self.minutos_cedeao +
            self.minutos_cplp +
            self.minutos_palop +
            self.minutos_resto_africa +
            self.minutos_resto_mundo +
            self.minutos_numeros_curtos
        )

    def calcular_total_sms(self):
        return (
            self.sms_outras_redes_moveis_nacionais +
            self.sms_outras_redes_internacionais +
            (self.sms_outros or 0)
        )