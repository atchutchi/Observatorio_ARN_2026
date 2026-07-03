from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from .base import IndicadorBase

class InternetFixoIndicador(IndicadorBase):
    # Número de assinantes de Internet fixo via rádio
    cidade_bissau = models.IntegerField(validators=[MinValueValidator(0)])
    bafata = models.IntegerField(validators=[MinValueValidator(0)])
    biombo = models.IntegerField(validators=[MinValueValidator(0)])
    bolama_bijagos = models.IntegerField(validators=[MinValueValidator(0)])
    cacheu = models.IntegerField(validators=[MinValueValidator(0)])
    gabu = models.IntegerField(validators=[MinValueValidator(0)])
    oio = models.IntegerField(validators=[MinValueValidator(0)])
    quinara = models.IntegerField(validators=[MinValueValidator(0)])
    tombali = models.IntegerField(validators=[MinValueValidator(0)])

    # Número de assinantes activos de Internet Fixo via Rádio
    airbox = models.IntegerField(validators=[MinValueValidator(0)])
    sistema_hertziano_fixo_terra = models.IntegerField(validators=[MinValueValidator(0)])
    outros_proxim = models.IntegerField(validators=[MinValueValidator(0)])
    fibra_otica = models.IntegerField(validators=[MinValueValidator(0)])

    # Número de assinantes de Serviços de Internet por débito
    banda_larga_256kbits_2mbits = models.IntegerField(validators=[MinValueValidator(0)])
    banda_larga_2_4mbits = models.IntegerField(validators=[MinValueValidator(0)])
    banda_larga_5_10mbits = models.IntegerField(validators=[MinValueValidator(0)])
    banda_larga_outros = models.IntegerField(validators=[MinValueValidator(0)])

    # Número de assinantes de Internet por categoria
    residencial = models.IntegerField(validators=[MinValueValidator(0)])
    corporativo_empresarial = models.IntegerField(validators=[MinValueValidator(0)])
    instituicoes_publicas = models.IntegerField(validators=[MinValueValidator(0)])
    instituicoes_ensino = models.IntegerField(validators=[MinValueValidator(0)])
    instituicoes_saude = models.IntegerField(validators=[MinValueValidator(0)])
    ong_outros = models.IntegerField(validators=[MinValueValidator(0)])

    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='internet_fixo_criado')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='internet_fixo_atualizado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def calcular_total_assinantes_radio(self):
        return (self.cidade_bissau + self.bafata + self.biombo + 
                self.bolama_bijagos + self.cacheu + self.gabu + 
                self.oio + self.quinara + self.tombali)

    def calcular_total_assinantes_ativos(self):
        return (self.airbox + self.sistema_hertziano_fixo_terra + 
                self.outros_proxim + self.fibra_otica)

    def calcular_total_banda_larga(self):
        return (self.banda_larga_256kbits_2mbits + self.banda_larga_2_4mbits + 
                self.banda_larga_5_10mbits + self.banda_larga_outros)

    def calcular_total_assinantes_categoria(self):
        return (self.residencial + self.corporativo_empresarial + 
                self.instituicoes_publicas + self.instituicoes_ensino + 
                self.instituicoes_saude + self.ong_outros)

    def __str__(self):
        return f"Internet Fixo - {self.ano}/{self.mes}"

    class Meta:
        unique_together = ('ano', 'mes', 'operadora')
        verbose_name = "Indicador de Internet Fixo"
        verbose_name_plural = "Indicadores de Internet Fixo"