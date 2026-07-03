# models/emprego.py
from django.db import models
from django.conf import settings
from .base import IndicadorBase

class EmpregoIndicador(IndicadorBase):
    # Emprego Direto
    emprego_direto_total = models.IntegerField(verbose_name="Total do emprego directo")
    
    # Nacionais
    nacionais_total = models.IntegerField(verbose_name="Nacionais - Total")
    nacionais_homem = models.IntegerField(verbose_name="Nacionais - Homem")
    nacionais_mulher = models.IntegerField(verbose_name="Nacionais - Mulher")
    
    # Emprego Indireto
    emprego_indireto = models.IntegerField(verbose_name="Total do emprego indirecto (Agentes, distribuidores, etc.)")

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='emprego_criado'
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='emprego_atualizado'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Emprego - {self.ano}/{self.mes}"

    class Meta:
        verbose_name = "Emprego"
        verbose_name_plural = "Empregos"
        unique_together = ('ano', 'mes', 'operadora')

    def calcular_total_emprego_direto(self):
        return self.emprego_direto_total

    def calcular_total_nacionais(self):
        return self.nacionais_total

    def calcular_total_nacionais_genero(self):
        return self.nacionais_homem + self.nacionais_mulher

    def calcular_percentual_homens(self):
        if self.nacionais_total > 0:
            return (self.nacionais_homem / self.nacionais_total) * 100
        return 0

    def calcular_percentual_mulheres(self):
        if self.nacionais_total > 0:
            return (self.nacionais_mulher / self.nacionais_total) * 100
        return 0

    def calcular_total_emprego_indireto(self):
        return self.emprego_indireto

    def calcular_total_geral(self):
        return self.emprego_direto_total + self.emprego_indireto

    def validar_totais(self):
        # Validar se o total de nacionais por gênero bate com o total de nacionais
        return self.nacionais_homem + self.nacionais_mulher == self.nacionais_total

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.validar_totais():
            raise ValidationError({
                'nacionais_total': 'O total de nacionais deve ser igual à soma de homens e mulheres',
                'nacionais_homem': 'A soma de homens e mulheres deve ser igual ao total de nacionais',
                'nacionais_mulher': 'A soma de homens e mulheres deve ser igual ao total de nacionais'
            })