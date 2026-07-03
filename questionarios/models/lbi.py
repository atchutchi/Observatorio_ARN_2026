from django.db import models
from django.conf import settings
from .base import IndicadorBase

class LBIIndicador(IndicadorBase):
    # Largura de banda de Internet internacional por tecnologia
    satelite = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cabo_fibra_optica = models.DecimalField(max_digits=10, decimal_places=2)
    feixe_hertziano = models.DecimalField(max_digits=10, decimal_places=2)

    # Down link
    disponivel_nominal_down = models.DecimalField(max_digits=10, decimal_places=2)
    instalada_equipada_down = models.DecimalField(max_digits=10, decimal_places=2)
    contratada_down = models.DecimalField(max_digits=10, decimal_places=2)
    utilizada_down = models.DecimalField(max_digits=10, decimal_places=2)

    # Up link
    disponivel_nominal_up = models.DecimalField(max_digits=10, decimal_places=2)
    instalada_equipada_up = models.DecimalField(max_digits=10, decimal_places=2)
    contratada_up = models.DecimalField(max_digits=10, decimal_places=2)
    utilizada_up = models.DecimalField(max_digits=10, decimal_places=2)

    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='lbi_criado')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='lbi_atualizado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LBI - {self.ano}/{self.mes}"

    class Meta:
        unique_together = ('ano', 'mes', 'operadora')

    def calcular_total_tecnologia(self):
        return (self.satelite or 0) + self.cabo_fibra_optica + self.feixe_hertziano

    def calcular_total_down(self):
        return self.utilizada_down

    def calcular_total_up(self):
        return self.utilizada_up