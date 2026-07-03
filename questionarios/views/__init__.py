from . import (
    estacoes_moveis, 
    trafego_originado, 
    trafego_terminado, 
    trafego_roaming_internacional, 
    lbi, 
    trafego_internet, 
    internet_fixo, 
    tarifario_voz, 
    tarifario_voz_telecel,
    receitas, 
    emprego, 
    investimento, 
    analise_mercado,
    assinantes,
    upload,
    public,
    base_views
)

__all__ = [
    'estacoes_moveis',
    'trafego_originado',
    'trafego_terminado',
    'trafego_roaming_internacional',
    'lbi',
    'trafego_internet',
    'internet_fixo',
    'tarifario_voz',
    'tarifario_voz_telecel',
    'receitas',
    'emprego',
    'investimento',
    'analise_mercado',
    'assinantes',
    'upload',
    'public',
    'base_views'
]

from .emprego import (
    EmpregoCreateView,
    EmpregoListView,
    EmpregoUpdateView,
    EmpregoDeleteView,
    EmpregoDetailView,
    EmpregoResumoView,
)

# Nova view de gestão de dados
from .public import data_management_view