from .base import IndicadorBase
from .estacoes_moveis import EstacoesMoveisIndicador
from .trafego_originado import TrafegoOriginadoIndicador
from .trafego_terminado import TrafegoTerminadoIndicador
from .trafego_roaming_internacional import TrafegoRoamingInternacionalIndicador
from .lbi import LBIIndicador
from .trafego_internet import TrafegoInternetIndicador
from .internet_fixo import InternetFixoIndicador
from .receitas import ReceitasIndicador
from .emprego import EmpregoIndicador
from .investimento import InvestimentoIndicador
from .tarifario_voz import TarifarioVozOrangeIndicador, TarifarioVozMTNIndicador
from .tarifario_voz_telecel import TarifarioVozTelecelIndicador

# Import RegistroQuestionario and AssinantesIndicador if they exist
try:
    from .registro_questionario import RegistroQuestionario
except ImportError:
    # Create a placeholder class if the model doesn't exist yet
    from django.db import models
    class RegistroQuestionario(models.Model):
        class Meta:
            app_label = 'questionarios'
            managed = False

try:
    from .assinantes import AssinantesIndicador
except ImportError:
    # Create a placeholder class if the model doesn't exist yet
    from django.db import models
    class AssinantesIndicador(models.Model):
        class Meta:
            app_label = 'questionarios'
            managed = False

__all__ = [
    'IndicadorBase',
    'EstacoesMoveisIndicador',
    'TrafegoOriginadoIndicador',
    'TrafegoTerminadoIndicador',
    'TrafegoRoamingInternacionalIndicador',
    'LBIIndicador',
    'TrafegoInternetIndicador',
    'InternetFixoIndicador',
    'TarifarioVozOrangeIndicador',
    'TarifarioVozMTNIndicador',
    'TarifarioVozTelecelIndicador',
    'ReceitasIndicador',
    'EmpregoIndicador',
    'InvestimentoIndicador',
    'RegistroQuestionario',
    'AssinantesIndicador',
]