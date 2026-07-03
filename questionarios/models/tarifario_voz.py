from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from .base import IndicadorBase

class TarifarioVozOrangeIndicador(IndicadorBase):
    """
    Modelo para armazenar os dados de tarifário da operadora Orange.
    """
    # Internet USB Pré-pago
    dongle_3g = models.IntegerField(verbose_name="Dongle 3G")
    dongle_4g = models.IntegerField(verbose_name="Dongle 4G")
    airbox_4g = models.IntegerField(verbose_name="Airbox 4G")
    flybox_4g = models.IntegerField(verbose_name="Flybox 4G")
    flybox_4g_plus = models.IntegerField(verbose_name="Flybox 4G+")
    
    # Internet USB/BOX Residencial
    casa_zen_2mbits_adesao = models.IntegerField(verbose_name="Orange Internet Casa Zen 2 Mbit/s - Adesão")
    casa_conforto_4mbits_adesao = models.IntegerField(verbose_name="Orange Internet Casa Conforto 4 Mbit/s - Adesão")
    casabox_2mbits_adesao = models.IntegerField(verbose_name="Casabox 2 Mbit/s - Adesão")
    casabox_5mbits_adesao = models.IntegerField(verbose_name="Casabox 5 Mbit/s - Adesão")
    
    # Subscrição mensal Residencial
    casa_zen_2mbits_mensal = models.IntegerField(verbose_name="Orange Internet Casa Zen 2 Mbit/s - Mensal")
    casa_conforto_4mbits_mensal = models.IntegerField(verbose_name="Orange Internet Casa Conforto 4 Mbit/s - Mensal")
    casabox_2mbits_mensal = models.IntegerField(verbose_name="Casabox 2 Mbit/s - Mensal")
    casabox_5mbits_mensal = models.IntegerField(verbose_name="Casabox 5 Mbit/s - Mensal")

    # Subscrição mensal por capacidades (Mbit/s)
    pass_ilimite_1h = models.IntegerField(verbose_name="Pass Ilimité 1h")
    pass_ilimite_3h = models.IntegerField(verbose_name="Pass Ilimité 3h")
    pass_ilimite_8h = models.IntegerField(verbose_name="Pass Ilimité 8h")
    pass_ilimite_dimanche = models.IntegerField(verbose_name="Pass Ilimité Dimanche")
    pass_ilimite_nuit = models.IntegerField(verbose_name="Pass Ilimité Nuit")
    pass_jours_ferie = models.IntegerField(verbose_name="Pass Jours Férié")
    pass_30_mo = models.IntegerField(verbose_name="Pass 30 Mo")
    pass_75_mo = models.IntegerField(verbose_name="Pass 75 Mo")
    pass_150_mo = models.IntegerField(verbose_name="Pass 150 Mo")
    pass_250_mo = models.IntegerField(verbose_name="Pass 250 Mo")
    pass_500_mo = models.IntegerField(verbose_name="Pass 500 Mo")
    pass_600_mo = models.IntegerField(verbose_name="Pass 600 Mo")
    pass_1_5_go = models.IntegerField(verbose_name="Pass 1.5 Go")
    pass_3_go = models.IntegerField(verbose_name="Pass 3 Go")
    pass_10_go = models.IntegerField(verbose_name="Pass 10 Go")
    pass_18_go = models.IntegerField(verbose_name="Pass 18 Go")
    pass_35_go = models.IntegerField(verbose_name="Pass 35 Go")
    pass_100_go = models.IntegerField(verbose_name="Pass 100 Go")
    pass_400_mo = models.IntegerField(verbose_name="Pass 400 Mo")
    pass_1_go = models.IntegerField(verbose_name="Pass 1 Go")

    # Serviço de Voz PRÉ-PAGO/PÓS-PAGO
    cartao_sim_adesao = models.IntegerField(verbose_name="Assinatura/Adesão ao serviço/cartão SIM")
    taxa_adesao = models.CharField(verbose_name="Taxa/Imposto incluído", max_length=50)
    
    # Tarifa - Minuto de comunicação On-net
    tarifa_orange_livre_6h_22h = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Orange Livre - 06h-22h")
    tarifa_orange_livre_22h_6h = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Orange Livre - 22h-06h")
    tarifa_orange_jovem_vip_jovem = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Orange Jovem VIP - entre Jovem VIP")
    tarifa_orange_jovem_vip_6h_22h = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Orange Jovem VIP - 06h-22h")
    tarifa_orange_jovem_vip_22h_6h = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Orange Jovem VIP - 22h-06h")
    tarifa_orange_intenso = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Orange Intenso")

    # Tarifa - Minuto de comunicação Off-net (local)
    tarifa_offnet_orange_livre = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Orange Livre")
    tarifa_offnet_orange_jovem_vip = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Orange Jovem VIP")
    tarifa_offnet_orange_intenso = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Orange Intenso")

    # Tarifa - Minuto de comunicação Off-net (Internacional)
    tarifa_zona1 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Zone 1: Côte d'Ivoire, Mali")
    tarifa_zona2 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Zone 2: Cape Vert, Angola, Brasil...")
    tarifa_zona3 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Zone 3: Royaume Uni, Espagne...")
    tarifa_zona4 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Zone 4: Niger, Mauritanie, Reste du monde")
    tarifa_zona5 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Zone 5: Guinée Conakry")
    tarifa_zona6 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Zone 6: Gambie")

    # Linhas Alugadas/Dedicadas
    toll_free = models.IntegerField(verbose_name="Toll Free", null=True, blank=True)
    vpn = models.IntegerField(verbose_name="VPN", null=True, blank=True)

    # Promoções e Impostos
    taxa_imposto = models.CharField(max_length=50, verbose_name="Taxa/Imposto incluído")
    promocoes = models.TextField(verbose_name="Promoções", null=True, blank=True)
    link_plano = models.URLField(verbose_name="Link onde o plano tarifário é publicado", null=True, blank=True)

    # Campos de controle
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tarifario_orange_criado')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tarifario_orange_atualizado')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tarifário Orange - {self.ano}/{self.mes}"

    class Meta:
        verbose_name = "Tarifário Orange"
        verbose_name_plural = "Tarifários Orange"
        unique_together = ('ano', 'mes')


class TarifarioVozMTNIndicador(IndicadorBase):
    """
    Modelo para armazenar os dados de tarifário da operadora TELECEL.
    Herda de IndicadorBase que contém os campos ano e mês.
    """
    # Identificador da operadora
    operadora = models.CharField(default="TELECEL", max_length=50, editable=False)

    # Huawei
    huawei_4g_lte = models.IntegerField(
        verbose_name="Huawei 4G LTE",
        help_text="Huawei 4G LTE - 30,000F",
        validators=[MinValueValidator(0)]
    )
    huawei_mobile_wifi_4g = models.IntegerField(
        verbose_name="Huawei Mobile Wi-Fi 4G",
        help_text="Huawei Mobile Wi-Fi 4G - 20,000F",
        validators=[MinValueValidator(0)]
    )

    # Pacotes Diários (Pacote 1)
    pacote_30mb = models.IntegerField(
        verbose_name="100F - 30MB",
        validators=[MinValueValidator(0)]
    )
    pacote_100mb = models.IntegerField(
        verbose_name="200F - 100MB",
        validators=[MinValueValidator(0)]
    )
    pacote_300mb = models.IntegerField(
        verbose_name="400F - 300MB",
        validators=[MinValueValidator(0)]
    )
    pacote_1gb = models.IntegerField(
        verbose_name="500F - 1GB",
        validators=[MinValueValidator(0)]
    )

    # Pacotes Semanais (Pacote 2)
    pacote_650mb = models.IntegerField(
        verbose_name="1000F - 650MB",
        validators=[MinValueValidator(0)]
    )
    pacote_1000mb = models.IntegerField(
        verbose_name="2000F - 1000MB",
        validators=[MinValueValidator(0)]
    )

    # Pacotes Mensais (Pacote 3)
    pacote_1_5gb = models.IntegerField(
        verbose_name="4000 - 1,5GB",
        validators=[MinValueValidator(0)]
    )
    pacote_10gb = models.IntegerField(
        verbose_name="10,000 - 10GB",
        validators=[MinValueValidator(0)]
    )
    pacote_18gb = models.IntegerField(
        verbose_name="15,000 - 18GB",
        validators=[MinValueValidator(0)]
    )
    pacote_30gb = models.IntegerField(
        verbose_name="21,000 - 30GB",
        validators=[MinValueValidator(0)]
    )
    pacote_50gb = models.IntegerField(
        verbose_name="25,000 - 50GB",
        validators=[MinValueValidator(0)]
    )
    pacote_60gb = models.IntegerField(
        verbose_name="30,000 - 60GB",
        validators=[MinValueValidator(0)]
    )
    pacote_120gb = models.IntegerField(
        verbose_name="50,000 - 120GB",
        validators=[MinValueValidator(0)]
    )

    # Pacote Y'ello Night (Pacote 4)
    pacote_yello_350mb = models.IntegerField(
        verbose_name="200F - 350MB",
        validators=[MinValueValidator(0)]
    )
    pacote_yello_1_5gb = models.IntegerField(
        verbose_name="500F - 1.5GB",
        validators=[MinValueValidator(0)]
    )
    pacote_yello_1_5gb_7dias = models.IntegerField(
        verbose_name="800F - 1.5GB/7dias",
        validators=[MinValueValidator(0)]
    )

    # Pacotes Ilimitados (Pacote 5)
    pacote_1hora = models.IntegerField(
        verbose_name="200F - 1 hora ilimitado",
        validators=[MinValueValidator(0)]
    )
    pacote_3horas = models.IntegerField(
        verbose_name="400F - 3 horas ilimitado",
        validators=[MinValueValidator(0)]
    )
    pacote_9horas = models.IntegerField(
        verbose_name="1000F - 9 horas ilimitado",
        validators=[MinValueValidator(0)]
    )

    # Taxas e Impostos
    taxa_imposto = models.CharField(
        verbose_name="Taxa/Imposto incluído",
        max_length=50,
        default="19%"
    )

    # Link do plano
    link_plano = models.URLField(
        verbose_name="Link onde o plano tarifário é publicado",
        null=True,
        blank=True
    )

    # Campos de controle
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tarifario_telecel_criado'
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tarifario_telecel_atualizado'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tarifário MTN"
        verbose_name_plural = "Tarifários MTN"
        unique_together = ('ano', 'mes')

    def __str__(self):
        return f"Tarifário TELECEL - {self.ano}/{self.mes}"