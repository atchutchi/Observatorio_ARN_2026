import calendar
from datetime import date
from django.core.management.base import BaseCommand
from apps.operators.models import OperatorType, Operator
from apps.indicators.models import IndicatorCategory, Indicator, OperatorTypeIndicator, Period


OPERATOR_TYPES = [
    {'code': 'terrestrial_full', 'name': 'Operador Terrestre Completo',
     'description': 'Operador com rede terrestre completa (2G/3G/4G), voz, SMS, dados, Mobile Money'},
    {'code': 'satellite_isp', 'name': 'Operador Satélite / ISP',
     'description': 'Operador de internet por satélite sem infraestrutura terrestre'},
]

OPERATORS = [
    {
        'name': 'Telecel', 'legal_name': 'Spacetel Guiné-Bissau SA',
        'code': 'TELECEL', 'operator_type': 'terrestrial_full',
        'brand_color': '#E30613',
        'historical_names': ['MTN', 'Spacetel', 'Spacetel Guiné-Bissau SA', 'mtn'],
    },
    {
        'name': 'Orange Bissau', 'legal_name': 'Orange Bissau SA',
        'code': 'ORANGE', 'operator_type': 'terrestrial_full',
        'brand_color': '#FF6600',
        'historical_names': ['Orange', 'Orange Bissau'],
    },
    {
        'name': 'Starlink', 'legal_name': 'Starlink Internet Services (SpaceX)',
        'code': 'STARLINK', 'operator_type': 'satellite_isp',
        'brand_color': '#000000',
        'historical_names': [],
    },
]

CATEGORIES = [
    {'code': 'estacoes_moveis', 'name': 'Estações Móveis (Parque de Assinantes)', 'order': 1, 'is_cumulative': False},
    {'code': 'trafego_originado', 'name': 'Tráfego Originado', 'order': 2, 'is_cumulative': False},
    {'code': 'trafego_terminado', 'name': 'Tráfego Terminado', 'order': 3, 'is_cumulative': False},
    {'code': 'trafego_roaming', 'name': 'Tráfego Roaming Internacional', 'order': 4, 'is_cumulative': False},
    {'code': 'lbi', 'name': 'LBI (Largura de Banda Internacional)', 'order': 5, 'is_cumulative': False},
    {'code': 'internet_fixo', 'name': 'Internet Fixo (Assinantes)', 'order': 6, 'is_cumulative': False},
    {'code': 'internet_trafic', 'name': 'Internet Traffic (Volume)', 'order': 7, 'is_cumulative': False},
    {'code': 'tarifario_voz', 'name': 'Tarifário de Voz', 'order': 8, 'is_cumulative': False},
    {'code': 'receitas', 'name': 'Receitas', 'order': 9, 'is_cumulative': True},
    {'code': 'empregos', 'name': 'Empregos', 'order': 10, 'is_cumulative': False},
    {'code': 'investimento', 'name': 'Investimento', 'order': 11, 'is_cumulative': True},
]

# (code, name, unit, level, parent_code_or_None, is_calculated, formula_type)
# 'T' = terrestrial_full applicable, 'S' = satellite_isp applicable, 'B' = both
INDICATORS = {
    'estacoes_moveis': [
        ('1', 'Parque de Assinantes', 'number', 0, None, True, 'sum_children', 'T'),
        ('1.1', 'Estações móveis em utilização efetiva', 'number', 1, '1', True, 'sum_children', 'T'),
        ('1.1.1', 'Pós-Pago', 'number', 2, '1.1', False, '', 'T'),
        ('1.1.2', 'Pré-Pago', 'number', 2, '1.1', False, '', 'T'),
        ('1.2', 'Estações com utilização efetiva - Voz', 'number', 1, '1', True, 'sum_children', 'T'),
        ('1.2.1', 'Pós-Pago', 'number', 2, '1.2', False, '', 'T'),
        ('1.2.2', 'Pré-Pago', 'number', 2, '1.2', False, '', 'T'),
        ('1.3', 'Estações com utilização efetiva - dados celulares', 'number', 1, '1', True, 'sum_children', 'T'),
        ('1.3.1', '2G', 'number', 2, '1.3', False, '', 'T'),
        ('1.3.2', '3G', 'number', 2, '1.3', False, '', 'T'),
        ('1.3.3', '4G', 'number', 2, '1.3', False, '', 'T'),
        ('1.3.4', '5G', 'number', 2, '1.3', False, '', 'T'),
        ('1.4', 'Estações com utilização efetiva - SMS', 'number', 1, '1', True, 'sum_children', 'T'),
        ('1.4.1', 'Pós-Pago', 'number', 2, '1.4', False, '', 'T'),
        ('1.4.2', 'Pré-Pago', 'number', 2, '1.4', False, '', 'T'),
        ('2', 'Assinantes da Banda Larga Móvel', 'number', 0, None, True, 'sum_children', 'T'),
        ('2.1', 'Por tipo de terminal', 'number', 1, '2', True, 'sum_children', 'T'),
        ('2.1.1', 'Smartphone', 'number', 2, '2.1', False, '', 'T'),
        ('2.1.2', 'Modem USB', 'number', 2, '2.1', False, '', 'T'),
        ('2.1.3', 'Tablet', 'number', 2, '2.1', False, '', 'T'),
        ('2.1.4', 'Box (Router)', 'number', 2, '2.1', False, '', 'T'),
        ('2.1.5', 'Outros', 'number', 2, '2.1', False, '', 'T'),
        ('2.2', 'Por tecnologia', 'number', 1, '2', True, 'sum_children', 'T'),
        ('2.2.1', '3G', 'number', 2, '2.2', False, '', 'T'),
        ('2.2.2', '4G', 'number', 2, '2.2', False, '', 'T'),
        ('2.2.3', '5G', 'number', 2, '2.2', False, '', 'T'),
        ('3', 'Assinantes Rede Fixa Sem Fio - Banda Larga', 'number', 0, None, True, 'sum_children', 'T'),
        ('3.1', 'Débito < 256 Kbps', 'number', 1, '3', False, '', 'T'),
        ('3.2', '256 Kbps ≤ Débito < 2 Mbps', 'number', 1, '3', False, '', 'T'),
        ('3.3', '2 Mbps ≤ Débito < 10 Mbps', 'number', 1, '3', False, '', 'T'),
        ('3.4', '10 Mbps ≤ Débito < 30 Mbps', 'number', 1, '3', False, '', 'T'),
        ('3.5', '30 Mbps ≤ Débito < 100 Mbps', 'number', 1, '3', False, '', 'T'),
        ('3.6', 'Débito ≥ 100 Mbps', 'number', 1, '3', False, '', 'T'),
        ('4', 'Utilizadores de Serviços', 'number', 0, None, False, '', 'T'),
        ('4.1', 'Utilizadores de serviço SMS', 'number', 1, '4', False, '', 'T'),
        ('4.2', 'Utilizadores de serviço de Roaming-Out', 'number', 1, '4', False, '', 'T'),
        ('4.3', 'Utilizadores de Mobile Money', 'number', 1, '4', False, '', 'T'),
        ('4.4', 'Utilizadores de Internet', 'number', 1, '4', False, '', 'T'),
        ('4.5', 'Utilizadores USSD', 'number', 1, '4', False, '', 'T'),
        ('4.6', 'Utilizadores de serviços a Valor Acrescentado (VAS)', 'number', 1, '4', False, '', 'T'),
        ('4.7', 'Utilizadores de Mobile TV', 'number', 1, '4', False, '', 'T'),
        ('4.8', 'Utilizadores de M-Learning', 'number', 1, '4', False, '', 'T'),
        ('4.9', 'Utilizadores de M-Health', 'number', 1, '4', False, '', 'T'),
        ('4.10', 'Utilizadores de M-Agriculture', 'number', 1, '4', False, '', 'T'),
        ('4.11', 'Utilizadores de M-Banking', 'number', 1, '4', False, '', 'T'),
    ],
    'trafego_originado': [
        ('1', 'Chamadas de Voz Originadas', 'calls', 0, None, True, 'sum_children', 'T'),
        ('1.1', 'Chamadas On-Net', 'calls', 1, '1', True, 'sum_children', 'T'),
        ('1.1.1', 'On-Net locais', 'calls', 2, '1.1', False, '', 'T'),
        ('1.1.2', 'On-Net nacionais inter-urbanas', 'calls', 2, '1.1', False, '', 'T'),
        ('1.1.3', 'On-Net p/ Correio de voz', 'calls', 2, '1.1', False, '', 'T'),
        ('1.2', 'Chamadas Off-Net', 'calls', 1, '1', True, 'sum_children', 'T'),
        ('1.2.1', 'Off-Net locais', 'calls', 2, '1.2', False, '', 'T'),
        ('1.2.2', 'Off-Net nacionais inter-urbanas', 'calls', 2, '1.2', False, '', 'T'),
        ('1.2.3', 'Chamadas para rede fixa', 'calls', 2, '1.2', False, '', 'T'),
        ('1.3', 'Chamadas Internacionais saída', 'calls', 1, '1', True, 'sum_children', 'T'),
        ('1.3.1', 'Sub-Região CEDEAO', 'calls', 2, '1.3', False, '', 'T'),
        ('1.3.2', 'Resto de África', 'calls', 2, '1.3', False, '', 'T'),
        ('1.3.3', 'Europa', 'calls', 2, '1.3', False, '', 'T'),
        ('1.3.4', 'Resto do Mundo', 'calls', 2, '1.3', False, '', 'T'),
        ('1.4', 'Chamadas de Vídeo originadas', 'calls', 1, '1', False, '', 'T'),
        ('2', 'Minutos de Voz Originados', 'minutes', 0, None, True, 'sum_children', 'T'),
        ('2.1', 'Minutos On-Net', 'minutes', 1, '2', True, 'sum_children', 'T'),
        ('2.1.1', 'On-Net locais', 'minutes', 2, '2.1', False, '', 'T'),
        ('2.1.2', 'On-Net nacionais inter-urbanos', 'minutes', 2, '2.1', False, '', 'T'),
        ('2.1.3', 'On-Net p/ Correio de voz', 'minutes', 2, '2.1', False, '', 'T'),
        ('2.2', 'Minutos Off-Net', 'minutes', 1, '2', True, 'sum_children', 'T'),
        ('2.2.1', 'Off-Net locais', 'minutes', 2, '2.2', False, '', 'T'),
        ('2.2.2', 'Off-Net nacionais inter-urbanos', 'minutes', 2, '2.2', False, '', 'T'),
        ('2.2.3', 'Minutos para rede fixa', 'minutes', 2, '2.2', False, '', 'T'),
        ('2.3', 'Minutos Internacionais saída', 'minutes', 1, '2', True, 'sum_children', 'T'),
        ('2.3.1', 'Sub-Região CEDEAO', 'minutes', 2, '2.3', False, '', 'T'),
        ('2.3.2', 'Resto de África', 'minutes', 2, '2.3', False, '', 'T'),
        ('2.3.3', 'Europa', 'minutes', 2, '2.3', False, '', 'T'),
        ('2.3.4', 'Resto do Mundo', 'minutes', 2, '2.3', False, '', 'T'),
        ('2.4', 'Minutos de Vídeo originados', 'minutes', 1, '2', False, '', 'T'),
        ('3', 'SMS Originados', 'sms', 0, None, True, 'sum_children', 'T'),
        ('3.1', 'SMS On-Net', 'sms', 1, '3', False, '', 'T'),
        ('3.2', 'SMS Off-Net', 'sms', 1, '3', False, '', 'T'),
        ('3.3', 'SMS Internacional saída', 'sms', 1, '3', False, '', 'T'),
        ('4', 'Tráfego de Dados Originado', 'mbps', 0, None, True, 'sum_children', 'B'),
        ('4.1', 'Tráfego de dados 2G', 'mbps', 1, '4', False, '', 'T'),
        ('4.2', 'Tráfego de dados 3G', 'mbps', 1, '4', False, '', 'T'),
        ('4.3', 'Tráfego de dados 4G', 'mbps', 1, '4', False, '', 'T'),
        ('4.4', 'Tráfego de dados 5G', 'mbps', 1, '4', False, '', 'T'),
        ('4.5', 'Tráfego Internet Box 3G', 'mbps', 1, '4', False, '', 'T'),
        ('4.6', 'Tráfego Internet USB 3G', 'mbps', 1, '4', False, '', 'T'),
        ('4.7', 'Tráfego Internet Box 4G', 'mbps', 1, '4', False, '', 'T'),
        ('4.8', 'Tráfego Internet USB 4G', 'mbps', 1, '4', False, '', 'T'),
        ('4.9', 'Tráfego Satélite LEO', 'mbps', 1, '4', False, '', 'S'),
    ],
    'trafego_terminado': [
        ('1', 'Chamadas de Voz Terminadas', 'calls', 0, None, True, 'sum_children', 'T'),
        ('1.1', 'Off-Net entrada', 'calls', 1, '1', True, 'sum_children', 'T'),
        ('1.1.1', 'Off-Net locais entrada', 'calls', 2, '1.1', False, '', 'T'),
        ('1.1.2', 'Off-Net nacionais inter-urbanas entrada', 'calls', 2, '1.1', False, '', 'T'),
        ('1.1.3', 'De rede fixa', 'calls', 2, '1.1', False, '', 'T'),
        ('1.2', 'Chamadas Internacionais entrada', 'calls', 1, '1', True, 'sum_children', 'T'),
        ('1.2.1', 'Sub-Região CEDEAO', 'calls', 2, '1.2', False, '', 'T'),
        ('1.2.2', 'Resto de África', 'calls', 2, '1.2', False, '', 'T'),
        ('1.2.3', 'Europa', 'calls', 2, '1.2', False, '', 'T'),
        ('1.2.4', 'Resto do Mundo', 'calls', 2, '1.2', False, '', 'T'),
        ('1.3', 'Chamadas de Vídeo terminadas', 'calls', 1, '1', False, '', 'T'),
        ('2', 'Minutos de Voz Terminados', 'minutes', 0, None, True, 'sum_children', 'T'),
        ('2.1', 'Minutos Off-Net entrada', 'minutes', 1, '2', True, 'sum_children', 'T'),
        ('2.1.1', 'Off-Net locais entrada', 'minutes', 2, '2.1', False, '', 'T'),
        ('2.1.2', 'Off-Net nacionais inter-urbanos entrada', 'minutes', 2, '2.1', False, '', 'T'),
        ('2.1.3', 'De rede fixa', 'minutes', 2, '2.1', False, '', 'T'),
        ('2.2', 'Minutos Internacionais entrada', 'minutes', 1, '2', True, 'sum_children', 'T'),
        ('2.2.1', 'Sub-Região CEDEAO', 'minutes', 2, '2.2', False, '', 'T'),
        ('2.2.2', 'Resto de África', 'minutes', 2, '2.2', False, '', 'T'),
        ('2.2.3', 'Europa', 'minutes', 2, '2.2', False, '', 'T'),
        ('2.2.4', 'Resto do Mundo', 'minutes', 2, '2.2', False, '', 'T'),
        ('2.3', 'Minutos de Vídeo terminados', 'minutes', 1, '2', False, '', 'T'),
        ('3', 'SMS Terminados', 'sms', 0, None, True, 'sum_children', 'T'),
        ('3.1', 'SMS Off-Net entrada', 'sms', 1, '3', False, '', 'T'),
        ('3.2', 'SMS Internacional entrada', 'sms', 1, '3', False, '', 'T'),
    ],
    'trafego_roaming': [
        ('1', 'Roaming-In', 'number', 0, None, False, '', 'T'),
        ('1.1', 'Chamadas Roaming-In', 'calls', 1, '1', True, 'sum_children', 'T'),
        ('1.1.1', 'Chamadas originadas por visitantes', 'calls', 2, '1.1', False, '', 'T'),
        ('1.1.2', 'Chamadas terminadas a visitantes', 'calls', 2, '1.1', False, '', 'T'),
        ('1.2', 'Minutos Roaming-In', 'minutes', 1, '1', True, 'sum_children', 'T'),
        ('1.2.1', 'Minutos originados por visitantes', 'minutes', 2, '1.2', False, '', 'T'),
        ('1.2.2', 'Minutos terminados a visitantes', 'minutes', 2, '1.2', False, '', 'T'),
        ('1.3', 'SMS Roaming-In', 'sms', 1, '1', True, 'sum_children', 'T'),
        ('1.3.1', 'SMS enviados por visitantes', 'sms', 2, '1.3', False, '', 'T'),
        ('1.3.2', 'SMS recebidos por visitantes', 'sms', 2, '1.3', False, '', 'T'),
        ('1.4', 'Dados Roaming-In', 'mb', 1, '1', False, '', 'T'),
        ('2', 'Roaming-Out', 'number', 0, None, False, '', 'T'),
        ('2.1', 'Chamadas Roaming-Out', 'calls', 1, '2', True, 'sum_children', 'T'),
        ('2.1.1', 'Chamadas originadas no estrangeiro', 'calls', 2, '2.1', False, '', 'T'),
        ('2.1.2', 'Chamadas recebidas no estrangeiro', 'calls', 2, '2.1', False, '', 'T'),
        ('2.2', 'Minutos Roaming-Out', 'minutes', 1, '2', True, 'sum_children', 'T'),
        ('2.2.1', 'Minutos originados no estrangeiro', 'minutes', 2, '2.2', False, '', 'T'),
        ('2.2.2', 'Minutos recebidos no estrangeiro', 'minutes', 2, '2.2', False, '', 'T'),
        ('2.3', 'SMS Roaming-Out', 'sms', 1, '2', True, 'sum_children', 'T'),
        ('2.3.1', 'SMS enviados no estrangeiro', 'sms', 2, '2.3', False, '', 'T'),
        ('2.3.2', 'SMS recebidos no estrangeiro', 'sms', 2, '2.3', False, '', 'T'),
        ('2.4', 'Dados Roaming-Out', 'mb', 1, '2', False, '', 'T'),
    ],
    'lbi': [
        ('1', 'Largura de Banda Internacional', 'mbps', 0, None, False, '', 'B'),
        ('1.1', 'Capacidade contratada', 'mbps', 1, '1', False, '', 'B'),
        ('1.2', 'Capacidade utilizada', 'mbps', 1, '1', False, '', 'B'),
        ('1.3', 'Ligação Satélite (VSAT)', 'mbps', 1, '1', False, '', 'T'),
        ('1.4', 'Ligação Fibra óptica submarina', 'mbps', 1, '1', False, '', 'T'),
        ('1.5', 'Ligação Feixes hertzianos', 'mbps', 1, '1', False, '', 'T'),
        ('1.6', 'Capacidade Satélite LEO', 'mbps', 1, '1', False, '', 'S'),
        ('1.7', 'Latência média', 'ms', 1, '1', False, '', 'S'),
        ('1.8', 'Capacidade de peering nacional', 'mbps', 1, '1', False, '', 'B'),
    ],
    'internet_fixo': [
        ('1', 'Por Tecnologia de Acesso', 'number', 0, None, True, 'sum_children', 'B'),
        ('1.1', 'Satélite (VSAT)', 'number', 1, '1', False, '', 'T'),
        ('1.2', 'Feixes Hertzianos (FH)', 'number', 1, '1', False, '', 'T'),
        ('1.3', 'Fibra Óptica (FO)', 'number', 1, '1', False, '', 'T'),
        ('1.4', 'xDSL', 'number', 1, '1', False, '', 'T'),
        ('1.5', 'Satélite LEO', 'number', 1, '1', False, '', 'S'),
        ('1.6', 'Outras tecnologias', 'number', 1, '1', False, '', 'B'),
        ('2', 'Por Velocidade (Débito)', 'number', 0, None, True, 'sum_children', 'B'),
        ('2.1', 'Banda Estreita (< 256 Kbps)', 'number', 1, '2', False, '', 'B'),
        ('2.2', '256 Kbps ≤ Débito < 2 Mbps', 'number', 1, '2', False, '', 'B'),
        ('2.3', '2 Mbps ≤ Débito < 10 Mbps', 'number', 1, '2', False, '', 'B'),
        ('2.4', '10 Mbps ≤ Débito < 30 Mbps', 'number', 1, '2', False, '', 'B'),
        ('2.5', '30 Mbps ≤ Débito < 100 Mbps', 'number', 1, '2', False, '', 'B'),
        ('2.6', 'Débito ≥ 100 Mbps', 'number', 1, '2', False, '', 'B'),
        ('3', 'Por Tipo de Cliente', 'number', 0, None, True, 'sum_children', 'B'),
        ('3.1', 'Residencial', 'number', 1, '3', False, '', 'B'),
        ('3.2', 'Empresas/Corporativo', 'number', 1, '3', False, '', 'B'),
        ('3.3', 'Administração Pública', 'number', 1, '3', False, '', 'B'),
        ('3.4', 'Cibercafés', 'number', 1, '3', False, '', 'B'),
        ('3.5', 'Instituições de Ensino', 'number', 1, '3', False, '', 'B'),
        ('3.6', 'Outros', 'number', 1, '3', False, '', 'B'),
        ('4', 'Por Região/Distrito', 'number', 0, None, True, 'sum_children', 'B'),
        ('4.1', 'SAB (Sector Autónomo de Bissau)', 'number', 1, '4', False, '', 'B'),
        ('4.2', 'Biombo', 'number', 1, '4', False, '', 'B'),
        ('4.3', 'Cacheu', 'number', 1, '4', False, '', 'B'),
        ('4.4', 'Oio', 'number', 1, '4', False, '', 'B'),
        ('4.5', 'Bafatá', 'number', 1, '4', False, '', 'B'),
        ('4.6', 'Gabú', 'number', 1, '4', False, '', 'B'),
        ('4.7', 'Tombali', 'number', 1, '4', False, '', 'B'),
        ('4.8', 'Quinara', 'number', 1, '4', False, '', 'B'),
        ('4.9', 'Bolama/Bijagós', 'number', 1, '4', False, '', 'B'),
    ],
    'internet_trafic': [
        ('1', 'Por Tecnologia de Acesso', 'gb', 0, None, True, 'sum_children', 'B'),
        ('1.1', 'Satélite (VSAT)', 'gb', 1, '1', False, '', 'T'),
        ('1.2', 'Feixes Hertzianos (FH)', 'gb', 1, '1', False, '', 'T'),
        ('1.3', 'Fibra Óptica (FO)', 'gb', 1, '1', False, '', 'T'),
        ('1.4', 'xDSL', 'gb', 1, '1', False, '', 'T'),
        ('1.5', 'Satélite LEO', 'gb', 1, '1', False, '', 'S'),
        ('1.6', 'Outras tecnologias', 'gb', 1, '1', False, '', 'B'),
        ('2', 'Por Velocidade (Débito)', 'gb', 0, None, True, 'sum_children', 'B'),
        ('2.1', 'Banda Estreita (< 256 Kbps)', 'gb', 1, '2', False, '', 'B'),
        ('2.2', '256 Kbps ≤ Débito < 2 Mbps', 'gb', 1, '2', False, '', 'B'),
        ('2.3', '2 Mbps ≤ Débito < 10 Mbps', 'gb', 1, '2', False, '', 'B'),
        ('2.4', '10 Mbps ≤ Débito < 30 Mbps', 'gb', 1, '2', False, '', 'B'),
        ('2.5', '30 Mbps ≤ Débito < 100 Mbps', 'gb', 1, '2', False, '', 'B'),
        ('2.6', 'Débito ≥ 100 Mbps', 'gb', 1, '2', False, '', 'B'),
        ('3', 'Por Tipo de Acesso', 'gb', 0, None, True, 'sum_children', 'B'),
        ('3.1', 'Dedicado', 'gb', 1, '3', False, '', 'B'),
        ('3.2', 'Partilhado', 'gb', 1, '3', False, '', 'B'),
        ('4', 'Métricas Específicas Satélite', 'number', 0, None, False, '', 'S'),
        ('4.1', 'Volume total download', 'gb', 1, '4', False, '', 'S'),
        ('4.2', 'Volume total upload', 'gb', 1, '4', False, '', 'S'),
        ('4.3', 'Latência média', 'ms', 1, '4', False, '', 'S'),
        ('4.4', 'Taxa de disponibilidade do serviço', 'percentage', 1, '4', False, '', 'S'),
        ('4.5', 'Velocidade média de download', 'mbps', 1, '4', False, '', 'S'),
        ('4.6', 'Velocidade média de upload', 'mbps', 1, '4', False, '', 'S'),
    ],
    'tarifario_voz': [
        ('1', 'Planos Tarifários', 'text', 0, None, False, '', 'T'),
        ('1.1', 'Nome do plano', 'text', 1, '1', False, '', 'T'),
        ('1.2', 'Tipo (Pós-Pago / Pré-Pago)', 'text', 1, '1', False, '', 'T'),
        ('1.3', 'Custo de activação', 'fcfa', 1, '1', False, '', 'T'),
        ('1.4', 'Assinatura mensal', 'fcfa', 1, '1', False, '', 'T'),
        ('2', 'Tarifas por Destino e Horário', 'fcfa', 0, None, False, '', 'T'),
        ('2.1', 'Chamadas On-Net - Ponta', 'fcfa', 1, '2', False, '', 'T'),
        ('2.2', 'Chamadas On-Net - Normal', 'fcfa', 1, '2', False, '', 'T'),
        ('2.3', 'Chamadas On-Net - Noite/Fim-de-semana', 'fcfa', 1, '2', False, '', 'T'),
        ('2.4', 'Chamadas Off-Net - Ponta', 'fcfa', 1, '2', False, '', 'T'),
        ('2.5', 'Chamadas Off-Net - Normal', 'fcfa', 1, '2', False, '', 'T'),
        ('2.6', 'Chamadas Off-Net - Noite/Fim-de-semana', 'fcfa', 1, '2', False, '', 'T'),
        ('2.7', 'Internacionais - CEDEAO', 'fcfa', 1, '2', False, '', 'T'),
        ('2.8', 'Internacionais - Resto de África', 'fcfa', 1, '2', False, '', 'T'),
        ('2.9', 'Internacionais - Europa', 'fcfa', 1, '2', False, '', 'T'),
        ('2.10', 'Internacionais - Resto do Mundo', 'fcfa', 1, '2', False, '', 'T'),
        ('2.11', 'SMS Nacional', 'fcfa', 1, '2', False, '', 'T'),
        ('2.12', 'SMS Internacional', 'fcfa', 1, '2', False, '', 'T'),
        ('2.13', 'Dados móveis (preço por MB)', 'fcfa', 1, '2', False, '', 'T'),
    ],
    'receitas': [
        ('1', 'Receitas de Serviços de Voz', 'fcfa_millions', 0, None, True, 'sum_children', 'T'),
        ('1.1', 'Receitas de chamadas On-Net', 'fcfa_millions', 1, '1', False, '', 'T'),
        ('1.2', 'Receitas de chamadas Off-Net saída', 'fcfa_millions', 1, '1', False, '', 'T'),
        ('1.3', 'Receitas de chamadas Internacionais saída', 'fcfa_millions', 1, '1', False, '', 'T'),
        ('1.4', 'Receitas de Roaming-Out voz', 'fcfa_millions', 1, '1', False, '', 'T'),
        ('1.5', 'Receitas de chamadas de Vídeo', 'fcfa_millions', 1, '1', False, '', 'T'),
        ('2', 'Receitas de Interconexão', 'fcfa_millions', 0, None, True, 'sum_children', 'T'),
        ('2.1', 'Receitas de terminação Off-Net entrada', 'fcfa_millions', 1, '2', False, '', 'T'),
        ('2.2', 'Receitas de terminação Internacional entrada', 'fcfa_millions', 1, '2', False, '', 'T'),
        ('2.3', 'Receitas de Roaming-In', 'fcfa_millions', 1, '2', False, '', 'T'),
        ('3', 'Receitas de SMS', 'fcfa_millions', 0, None, True, 'sum_children', 'T'),
        ('3.1', 'Receitas SMS On-Net', 'fcfa_millions', 1, '3', False, '', 'T'),
        ('3.2', 'Receitas SMS Off-Net', 'fcfa_millions', 1, '3', False, '', 'T'),
        ('3.3', 'Receitas SMS Internacional saída', 'fcfa_millions', 1, '3', False, '', 'T'),
        ('3.4', 'Receitas SMS terminação entrada', 'fcfa_millions', 1, '3', False, '', 'T'),
        ('3.5', 'Receitas SMS Roaming', 'fcfa_millions', 1, '3', False, '', 'T'),
        ('4', 'Receitas de Dados/Internet', 'fcfa_millions', 0, None, True, 'sum_children', 'B'),
        ('4.1', 'Receitas de Internet móvel', 'fcfa_millions', 1, '4', False, '', 'T'),
        ('4.2', 'Receitas de Internet fixa', 'fcfa_millions', 1, '4', False, '', 'B'),
        ('4.3', 'Receitas de serviços dados corporativos', 'fcfa_millions', 1, '4', False, '', 'B'),
        ('5', 'Receitas de Serviços Financeiros Móveis', 'fcfa_millions', 0, None, True, 'sum_children', 'T'),
        ('5.1', 'Receitas Mobile Money', 'fcfa_millions', 1, '5', False, '', 'T'),
        ('5.2', 'Comissões de transferências', 'fcfa_millions', 1, '5', False, '', 'T'),
        ('5.3', 'Receitas de levantamentos', 'fcfa_millions', 1, '5', False, '', 'T'),
        ('6', 'Receitas de VAS', 'fcfa_millions', 0, None, True, 'sum_children', 'T'),
        ('6.1', 'Receitas de conteúdos digitais', 'fcfa_millions', 1, '6', False, '', 'T'),
        ('6.2', 'Receitas USSD', 'fcfa_millions', 1, '6', False, '', 'T'),
        ('6.3', 'Outras receitas VAS', 'fcfa_millions', 1, '6', False, '', 'T'),
        ('7', 'Outras Receitas', 'fcfa_millions', 0, None, True, 'sum_children', 'B'),
        ('7.1', 'Receitas de venda de equipamentos', 'fcfa_millions', 1, '7', False, '', 'B'),
        ('7.2', 'Receitas de publicidade', 'fcfa_millions', 1, '7', False, '', 'B'),
        ('7.3', 'Receitas de instalação', 'fcfa_millions', 1, '7', False, '', 'B'),
        ('7.4', 'Outras receitas diversas', 'fcfa_millions', 1, '7', False, '', 'B'),
        ('8', 'Total de Receitas (Volume de Negócios)', 'fcfa_millions', 0, None, True, 'sum_children', 'B'),
    ],
    'empregos': [
        ('1', 'Emprego Directo', 'persons', 0, None, True, 'sum_children', 'B'),
        ('1.1', 'Nacionais', 'persons', 1, '1', True, 'sum_children', 'B'),
        ('1.1.1', 'Masculino', 'persons', 2, '1.1', False, '', 'B'),
        ('1.1.2', 'Feminino', 'persons', 2, '1.1', False, '', 'B'),
        ('1.2', 'Expatriados', 'persons', 1, '1', True, 'sum_children', 'B'),
        ('1.2.1', 'Masculino', 'persons', 2, '1.2', False, '', 'B'),
        ('1.2.2', 'Feminino', 'persons', 2, '1.2', False, '', 'B'),
        ('2', 'Emprego Indirecto', 'persons', 0, None, True, 'sum_children', 'B'),
        ('2.1', 'Agentes comerciais', 'persons', 1, '2', False, '', 'B'),
        ('2.2', 'Distribuidores', 'persons', 1, '2', False, '', 'B'),
        ('2.3', 'Técnicos subcontratados', 'persons', 1, '2', False, '', 'B'),
        ('2.4', 'Outros', 'persons', 1, '2', False, '', 'B'),
    ],
    'investimento': [
        ('1', 'Investimento Total', 'fcfa_millions', 0, None, True, 'sum_children', 'B'),
        ('1.1', 'Investimento em Telecomunicações', 'fcfa_millions', 1, '1', True, 'sum_children', 'T'),
        ('1.1.1', 'Investimento Corpóreo (Tangível)', 'fcfa_millions', 2, '1.1', True, 'sum_children', 'T'),
        ('1.1.1.1', 'Rede de acesso', 'fcfa_millions', 3, '1.1.1', False, '', 'T'),
        ('1.1.1.2', 'Rede core', 'fcfa_millions', 3, '1.1.1', False, '', 'T'),
        ('1.1.1.3', 'Plataformas de serviços', 'fcfa_millions', 3, '1.1.1', False, '', 'T'),
        ('1.1.1.4', 'Edifícios e instalações', 'fcfa_millions', 3, '1.1.1', False, '', 'T'),
        ('1.1.1.5', 'Outros corpóreos', 'fcfa_millions', 3, '1.1.1', False, '', 'T'),
        ('1.1.2', 'Investimento Incorpóreo (Intangível)', 'fcfa_millions', 2, '1.1', True, 'sum_children', 'T'),
        ('1.1.2.1', 'Licenças de software', 'fcfa_millions', 3, '1.1.2', False, '', 'T'),
        ('1.1.2.2', 'Licenças de espectro', 'fcfa_millions', 3, '1.1.2', False, '', 'T'),
        ('1.1.2.3', 'Outros incorpóreos', 'fcfa_millions', 3, '1.1.2', False, '', 'T'),
        ('1.2', 'Investimento em Serviços Internet', 'fcfa_millions', 1, '1', True, 'sum_children', 'T'),
        ('1.2.1', 'Corpóreo', 'fcfa_millions', 2, '1.2', False, '', 'T'),
        ('1.2.2', 'Incorpóreo', 'fcfa_millions', 2, '1.2', False, '', 'T'),
        ('1.3', 'Investimento Infraestrutura Satélite Local', 'fcfa_millions', 1, '1', True, 'sum_children', 'S'),
        ('1.3.1', 'Estações gateway terrestres', 'fcfa_millions', 2, '1.3', False, '', 'S'),
        ('1.3.2', 'Equipamento de distribuição', 'fcfa_millions', 2, '1.3', False, '', 'S'),
        ('1.3.3', 'Stock de kits para clientes', 'fcfa_millions', 2, '1.3', False, '', 'S'),
        ('1.3.4', 'Edifícios e instalações', 'fcfa_millions', 2, '1.3', False, '', 'S'),
        ('1.4', 'Investimento Incorpóreo Satélite', 'fcfa_millions', 1, '1', True, 'sum_children', 'S'),
        ('1.4.1', 'Licenças e autorizações regulatórias', 'fcfa_millions', 2, '1.4', False, '', 'S'),
        ('1.4.2', 'Software e sistemas', 'fcfa_millions', 2, '1.4', False, '', 'S'),
        ('1.4.3', 'Outros incorpóreos', 'fcfa_millions', 2, '1.4', False, '', 'S'),
    ],
}


class Command(BaseCommand):
    help = 'Popula a base de dados com operadores, indicadores e períodos iniciais'

    def handle(self, *args, **options):
        self.seed_operator_types()
        self.seed_operators()
        self.seed_categories_and_indicators()
        self.seed_periods()
        self.stdout.write(self.style.SUCCESS('Seed data criado com sucesso!'))

    def seed_operator_types(self):
        for ot_data in OPERATOR_TYPES:
            obj, created = OperatorType.objects.update_or_create(
                code=ot_data['code'], defaults=ot_data,
            )
            status = 'criado' if created else 'actualizado'
            self.stdout.write(f"  OperatorType: {obj.name} ({status})")

    def seed_operators(self):
        for op_data in OPERATORS:
            ot = OperatorType.objects.get(code=op_data.pop('operator_type'))
            obj, created = Operator.objects.update_or_create(
                code=op_data['code'], defaults={**op_data, 'operator_type': ot},
            )
            status = 'criado' if created else 'actualizado'
            self.stdout.write(f"  Operator: {obj.name} ({status})")

    def seed_categories_and_indicators(self):
        terrestrial = OperatorType.objects.get(code='terrestrial_full')
        satellite = OperatorType.objects.get(code='satellite_isp')

        for cat_data in CATEGORIES:
            cat, created = IndicatorCategory.objects.update_or_create(
                code=cat_data['code'], defaults=cat_data,
            )
            status = 'criado' if created else 'actualizado'
            self.stdout.write(f"  Category: {cat.name} ({status})")

            indicators_data = INDICATORS.get(cat_data['code'], [])
            indicator_map = {}
            for i, ind_tuple in enumerate(indicators_data):
                code, name, unit, level, parent_code, is_calc, formula, applicability = ind_tuple
                parent = indicator_map.get(parent_code) if parent_code else None

                ind, ind_created = Indicator.objects.update_or_create(
                    category=cat, code=code,
                    defaults={
                        'name': name, 'unit': unit, 'level': level,
                        'parent': parent, 'is_calculated': is_calc,
                        'formula_type': formula, 'order': i + 1,
                    },
                )
                indicator_map[code] = ind

                if applicability == 'T':
                    OperatorTypeIndicator.objects.update_or_create(
                        operator_type=terrestrial, indicator=ind,
                        defaults={'is_applicable': True, 'is_mandatory': True},
                    )
                    OperatorTypeIndicator.objects.update_or_create(
                        operator_type=satellite, indicator=ind,
                        defaults={'is_applicable': False, 'is_mandatory': False,
                                  'notes': 'Não aplicável a operadores satélite'},
                    )
                elif applicability == 'S':
                    OperatorTypeIndicator.objects.update_or_create(
                        operator_type=terrestrial, indicator=ind,
                        defaults={'is_applicable': False, 'is_mandatory': False,
                                  'notes': 'Específico para operadores satélite'},
                    )
                    OperatorTypeIndicator.objects.update_or_create(
                        operator_type=satellite, indicator=ind,
                        defaults={'is_applicable': True, 'is_mandatory': True},
                    )
                else:  # 'B' = both
                    OperatorTypeIndicator.objects.update_or_create(
                        operator_type=terrestrial, indicator=ind,
                        defaults={'is_applicable': True, 'is_mandatory': True},
                    )
                    OperatorTypeIndicator.objects.update_or_create(
                        operator_type=satellite, indicator=ind,
                        defaults={'is_applicable': True, 'is_mandatory': True},
                    )

            self.stdout.write(f"    → {len(indicators_data)} indicadores criados")

    def seed_periods(self):
        quarter_months = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
        count = 0
        for year in range(2018, 2027):
            for quarter, months in quarter_months.items():
                for month in months:
                    last_day = calendar.monthrange(year, month)[1]
                    Period.objects.update_or_create(
                        year=year, month=month,
                        defaults={
                            'quarter': quarter,
                            'start_date': date(year, month, 1),
                            'end_date': date(year, month, last_day),
                        },
                    )
                    count += 1
        self.stdout.write(f"  Períodos: {count} meses criados (2018-2026)")
