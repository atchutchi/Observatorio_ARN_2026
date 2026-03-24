"""
Mapeamento de sheets Excel para categorias de indicadores
e mapeamento de colunas para cada tipo de ficheiro.
"""

SHEET_TO_CATEGORY = {
    'Estações móveis': 'estacoes_moveis',
    'Estacoes moveis': 'estacoes_moveis',
    'estacoes_moveis': 'estacoes_moveis',
    'Trafego_originado': 'trafego_originado',
    'Tráfego Originado': 'trafego_originado',
    'trafego_originado': 'trafego_originado',
    'Trafego_Terminado': 'trafego_terminado',
    'Tráfego Terminado': 'trafego_terminado',
    'trafego_terminado': 'trafego_terminado',
    'Trafego_Roaming_Internacional': 'trafego_roaming',
    'Tráfego Roaming Internacional': 'trafego_roaming',
    'trafego_roaming': 'trafego_roaming',
    'LBI': 'lbi',
    'lbi': 'lbi',
    'Internet_Fixo': 'internet_fixo',
    'Internet Fixo': 'internet_fixo',
    'internet_fixo': 'internet_fixo',
    'Internet_Trafic': 'internet_trafic',
    'Internet Trafic': 'internet_trafic',
    'internet_trafic': 'internet_trafic',
    'tarifario_voz': 'tarifario_voz',
    'Tarifário de Voz': 'tarifario_voz',
    'tarifario_voz 1': 'tarifario_voz',
    'RECEITAS': 'receitas',
    'Receitas': 'receitas',
    'receitas': 'receitas',
    'Empregos': 'empregos',
    'empregos': 'empregos',
    'Investimento': 'investimento',
    'investimento': 'investimento',
}

OPERATOR_NAME_MAPPING = {
    'MTN': 'TELECEL',
    'mtn': 'TELECEL',
    'Spacetel': 'TELECEL',
    'Spacetel Guiné-Bissau': 'TELECEL',
    'Spacetel Guiné-Bissau SA': 'TELECEL',
    'TELECEL': 'TELECEL',
    'Telecel': 'TELECEL',
    'Orange': 'ORANGE',
    'ORANGE': 'ORANGE',
    'Orange Bissau': 'ORANGE',
    'Orange Bissau SA': 'ORANGE',
    'Starlink': 'STARLINK',
    'STARLINK': 'STARLINK',
}

MONTHLY_COLUMN_LAYOUT = {
    'indicator_code_col': 0,
    'indicator_name_col': 1,
    'unit_col': 2,
    'data_start_col': 3,
    'months_per_quarter': 3,
    'quarters': {
        1: {'start_col': 3, 'months': [1, 2, 3]},
        2: {'start_col': 6, 'months': [4, 5, 6]},
        3: {'start_col': 9, 'months': [7, 8, 9]},
        4: {'start_col': 12, 'months': [10, 11, 12]},
    },
}

CUMULATIVE_COLUMN_LAYOUT = {
    'indicator_code_col': 0,
    'indicator_name_col': 1,
    'unit_col': 2,
    'year_col': 3,
    'periods': {
        '3M': 4,
        '6M': 5,
        '9M': 6,
        '12M': 7,
    },
    'observation_col': 8,
}

CUMULATIVE_CATEGORIES = {'receitas', 'investimento'}
