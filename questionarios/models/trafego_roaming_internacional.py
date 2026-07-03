from django.db import models
from django.conf import settings
from .base import IndicadorBase

class TrafegoRoamingInternacionalIndicador(IndicadorBase):
    # Chamadas de Roaming internacional - IN
    chamadas_originadas_rede = models.IntegerField()
    chamadas_terminadas_rede = models.IntegerField()
    
    # Minutos de Roaming internacional - IN
    minutos_originados_rede = models.IntegerField()
    minutos_terminados_rede = models.IntegerField()
    
    # Tráfego de dados em ROAMING internacional - IN
    mensagens_escritas_enviadas = models.IntegerField()
    mensagens_escritas_recebidas = models.IntegerField()
    sessoes_acesso_internet = models.IntegerField()
    volume_acesso_internet = models.BigIntegerField(help_text="Em Mbit")
    
    # Chamadas de Roaming Internacional - OUT
    chamadas_originadas_operador_roaming = models.IntegerField()
    chamadas_terminadas_operador_roaming = models.IntegerField()
    
    # Minutos de Roaming Internacional - OUT
    minutos_originados_operador_roaming = models.IntegerField()
    minutos_terminados_operador_roaming = models.IntegerField()
    
    # Tráfego de dados em Roaming Internacional - OUT
    mensagens_escritas_enviadas_out = models.IntegerField()
    sessoes_acesso_internet_out = models.IntegerField()
    volume_acesso_internet_out = models.BigIntegerField(help_text="Em Mbit")
    
    # Acordos de Roaming Internacional
    acordos_roaming_internacional = models.IntegerField(help_text="Número de países")

    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='trafego_roaming_internacional_criado')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='trafego_roaming_internacional_atualizado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tráfego de Roaming Internacional - {self.ano}/{self.mes}"

    class Meta:
        unique_together = ('ano', 'mes', 'operadora')