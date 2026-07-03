from django.db import models
from django.conf import settings
from .base import IndicadorBase

class TrafegoInternetIndicador(IndicadorBase):
    # Tráfego de Serviços de Internet fixo via rádio
    trafego_total = models.DecimalField(max_digits=15, decimal_places=2, help_text="Mbit/s")
    por_via_satelite = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    por_sistema_hertziano_fixo_terra = models.DecimalField(max_digits=15, decimal_places=2)
    fibra_otica = models.DecimalField(max_digits=15, decimal_places=2)

    # Tráfego por débito
    banda_estreita_256kbps = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    kbps_64_128 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    kbps_128_256 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    banda_estreita_outros = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Banda Larga ≥ 256 Kbps
    banda_larga_total = models.DecimalField(max_digits=15, decimal_places=2)
    kbits_256_2mbits = models.DecimalField(max_digits=15, decimal_places=2)
    mbits_2_4 = models.DecimalField(max_digits=15, decimal_places=2)
    mbits_10 = models.DecimalField(max_digits=15, decimal_places=2)
    banda_larga_outros = models.DecimalField(max_digits=15, decimal_places=2)

    # Tráfego por categoria
    residencial = models.DecimalField(max_digits=15, decimal_places=2)
    corporativo_empresarial = models.DecimalField(max_digits=15, decimal_places=2)
    instituicoes_publicas = models.DecimalField(max_digits=15, decimal_places=2)
    instituicoes_ensino = models.DecimalField(max_digits=15, decimal_places=2)
    instituicoes_saude = models.DecimalField(max_digits=15, decimal_places=2)
    ong_outros = models.DecimalField(max_digits=15, decimal_places=2)

    # Tráfego por Região
    cidade_bissau = models.DecimalField(max_digits=15, decimal_places=2)
    bafata = models.DecimalField(max_digits=15, decimal_places=2)
    biombo = models.DecimalField(max_digits=15, decimal_places=2)
    bolama_bijagos = models.DecimalField(max_digits=15, decimal_places=2)
    cacheu = models.DecimalField(max_digits=15, decimal_places=2)
    gabu = models.DecimalField(max_digits=15, decimal_places=2)
    oio = models.DecimalField(max_digits=15, decimal_places=2)
    quinara = models.DecimalField(max_digits=15, decimal_places=2)
    tombali = models.DecimalField(max_digits=15, decimal_places=2)

    # Tráfego por acesso público via rádio (PWLAN)
    acesso_livre = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    acesso_condicionado = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='trafego_internet_criado')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='trafego_internet_atualizado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tráfego de Internet - {self.ano}/{self.mes}"

    class Meta:
        unique_together = ('ano', 'mes', 'operadora')

    def calcular_total_trafego(self):
        return self.trafego_total

    def calcular_total_banda_larga(self):
        return self.banda_larga_total

    def calcular_total_categoria(self):
        return (self.residencial + self.corporativo_empresarial + self.instituicoes_publicas +
                self.instituicoes_ensino + self.instituicoes_saude + self.ong_outros)

    def calcular_total_regiao(self):
        return (self.cidade_bissau + self.bafata + self.biombo + self.bolama_bijagos +
                self.cacheu + self.gabu + self.oio + self.quinara + self.tombali)