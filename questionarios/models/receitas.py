# models/receitas.py
from django.db import models
from django.conf import settings
from .base import IndicadorBase

class ReceitasIndicador(IndicadorBase):
    # Receitas de serviços a clientes retalhistas
    receitas_mensalidades = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de Mensalidades")
    
    # Receitas de serviços de voz
    receitas_chamadas_on_net = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de chamadas On-net")
    receitas_chamadas_off_net = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de chamadas para outros STM nacionais")
    receitas_chamadas_telecel = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Para o operador da rede móvel TELECEL")
    receitas_chamadas_rede_movel_b = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Para o operador da rede móvel B")
    receitas_chamadas_outros = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Outros", null=True, blank=True)
    receitas_servico_telefonico_fixo = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de chamadas para serviço telefónico fixo")
    
    # Receitas de chamadas internacionais
    receitas_chamadas_cedeao = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="CEDEAO")
    receitas_chamadas_cplp = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="CPLP")
    receitas_chamadas_palop = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="PALOP")
    receitas_chamadas_resto_africa = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Resto de África")
    receitas_chamadas_resto_mundo = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Resto do mundo")

    # Receitas de Roaming
    receitas_voz_roaming_out = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de serviços de voz em Roaming-out")
    
    # Receitas de Mensagens
    receitas_mensagens = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de serviços de mensagens")
    receitas_mms = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de MMS", null=True, blank=True)

    # Receitas de Dados Móveis
    receitas_dados_moveis = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de serviços de dados móveis")
    receitas_internet_banda_larga = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de acesso à Internet em banda larga")
    receitas_videochamadas = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de videochamadas", null=True, blank=True)
    receitas_mobile_tv = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de Mobile TV", null=True, blank=True)
    receitas_outros_servicos_dados = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de outros serviços de dados", null=True, blank=True)

    # Receitas de Roaming-out (excluindo voz)
    receitas_roaming_out_dados = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de Roaming-out excluindo comunicações de voz", null=True, blank=True)
    receitas_internet_roaming_out = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de acesso à Internet em banda larga em roaming-out", null=True, blank=True)

    # Outras Receitas
    outras_receitas_retalhistas = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Outras receitas retalhistas")
    
    # Receitas de serviços a clientes grossistas
    receitas_terminacao_voz = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de terminação de voz")
    receitas_terminacao_dados = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de terminação de dados", null=True, blank=True)
    receitas_originacao_trafego = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas de originação de tráfego para serviços especiais", null=True, blank=True)
    receitas_servicos_especiais = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Receitas do serviço de facturação e cobrança pela originação de chamadas para serviços especiais", null=True, blank=True)
    outras_receitas_grossistas = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Outras receitas grossistas")

    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='receitas_criado')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='receitas_atualizado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Receitas - {self.ano}/{self.mes}"

    class Meta:
        verbose_name = "Receitas"
        verbose_name_plural = "Receitas"
        unique_together = ('ano', 'mes', 'operadora')

    def calcular_total_receitas_voz(self):
        return (
            self.receitas_chamadas_on_net +
            self.receitas_chamadas_off_net +
            self.receitas_chamadas_telecel +
            self.receitas_chamadas_rede_movel_b +
            (self.receitas_chamadas_outros or 0) +
            self.receitas_servico_telefonico_fixo +
            self.receitas_chamadas_cedeao +
            self.receitas_chamadas_cplp +
            self.receitas_chamadas_palop +
            self.receitas_chamadas_resto_africa +
            self.receitas_chamadas_resto_mundo
        )

    def calcular_total_receitas_internacional(self):
        return (
            self.receitas_chamadas_cedeao +
            self.receitas_chamadas_cplp +
            self.receitas_chamadas_palop +
            self.receitas_chamadas_resto_africa +
            self.receitas_chamadas_resto_mundo
        )

    def calcular_total_receitas_dados(self):
        return (
            self.receitas_dados_moveis +
            self.receitas_internet_banda_larga +
            (self.receitas_videochamadas or 0) +
            (self.receitas_mobile_tv or 0) +
            (self.receitas_outros_servicos_dados or 0)
        )

    def calcular_total_receitas_retalhistas(self):
        return (
            self.receitas_mensalidades +
            self.calcular_total_receitas_voz() +
            self.receitas_voz_roaming_out +
            self.receitas_mensagens +
            self.calcular_total_receitas_dados() +
            (self.receitas_roaming_out_dados or 0) +
            self.outras_receitas_retalhistas
        )

    def calcular_total_receitas_grossistas(self):
        return (
            self.receitas_terminacao_voz +
            (self.receitas_terminacao_dados or 0) +
            (self.receitas_originacao_trafego or 0) +
            (self.receitas_servicos_especiais or 0) +
            self.outras_receitas_grossistas
        )

    def calcular_total_receitas(self):
        return self.calcular_total_receitas_retalhistas() + self.calcular_total_receitas_grossistas()