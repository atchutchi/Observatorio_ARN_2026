from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from .base import IndicadorBase

# Model specific to Telecel tariffs, mirroring TELECEL structure
class TarifarioVozTelecelIndicador(IndicadorBase):
    operadora = models.CharField(max_length=10, choices=IndicadorBase.OPERADORAS_CHOICES, default='telecel', editable=False)
    
    # Equipamentos (Mirroring TELECEL fields)
    huawei_4g_lte = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name="Huawei 4G LTE (Preço)")
    huawei_mobile_wifi_4g = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name="Huawei Mobile Wi-Fi 4G (Preço)")
    
    # Pacotes Diários (Mirroring TELECEL fields)
    pacote_30mb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_100mb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_300mb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_1gb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    # Pacotes Semanais (Mirroring TELECEL fields)
    pacote_650mb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_1000mb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    # Pacotes Mensais (Mirroring TELECEL fields)
    pacote_1_5gb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_10gb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_18gb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_30gb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_50gb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_60gb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_120gb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    # Pacote Y'ello Night (Mirroring TELECEL fields, maybe rename later?)
    pacote_yello_350mb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_yello_1_5gb = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_yello_1_5gb_7dias = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    # Pacotes Ilimitados (Mirroring TELECEL fields)
    pacote_1hora = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_3horas = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    pacote_9horas = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)

    # Metadata fields
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='telecel_criado')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='telecel_atualizado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    taxa_imposto = models.DecimalField(max_digits=5, decimal_places=2, default=0.15, verbose_name="Taxa de Imposto Aplicável")
    link_plano = models.URLField(max_length=200, blank=True, null=True, verbose_name="Link para o Plano Tarifário Oficial")

    class Meta:
        verbose_name = "Indicador de Tarifário Voz TELECEL"
        verbose_name_plural = "Indicadores de Tarifário Voz TELECEL"
        unique_together = ('ano', 'mes') # Only one record per month/year for Telecel

    def __str__(self):
        return f"Tarifário TELECEL - {self.ano}/{self.mes}" 