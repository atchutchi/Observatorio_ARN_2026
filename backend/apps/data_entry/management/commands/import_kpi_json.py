"""
Management command to import KPI data from ARN JSON files.

Maps JSON indicator codes from the ARN questionnaires to the database
indicator hierarchy. Handles both monthly and cumulative data.

Usage:
    python manage.py import_kpi_json
    python manage.py import_kpi_json --file orange_kpi_2024.json
    python manage.py import_kpi_json --operator ORANGE --year 2024
    python manage.py import_kpi_json --dry-run
"""
import json
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.operators.models import Operator
from apps.indicators.models import IndicatorCategory, Indicator, Period
from apps.data_entry.models import DataEntry, CumulativeData


MONTH_MAP = {
    'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
}

CUMULATIVE_MAP = {
    't1_acumulado': '3M',
    't2_acumulado': '6M',
    't3_acumulado': '9M',
    't4_acumulado': '12M',
}

CATEGORY_MAP = {
    'estacoes_moveis': 'estacoes_moveis',
    'mobile_money': 'estacoes_moveis',
    'trafego_originado': 'trafego_originado',
    'trafego_terminado': 'trafego_terminado',
    'roaming_internacional': 'trafego_roaming',
    'largura_banda_internacional': 'lbi',
    'internet_fixo': 'internet_fixo',
    'trafego_internet_fixo': 'internet_trafic',
    'receitas': 'receitas',
    'emprego': 'empregos',
    'investimento': 'investimento',
}

INDICATOR_MAP = {
    'estacoes_moveis': {
        'pos_pago': ('1.1.1', 'Estações Pós-Pago', 'number'),
        'pos_pago_uso_efetivo': ('1.2.1', 'Pós-Pago com utilização efetiva', 'number'),
        'pre_pago': ('1.1.2', 'Estações Pré-Pago', 'number'),
        'pre_pago_uso_efetivo': ('1.2.2', 'Pré-Pago com utilização efetiva', 'number'),
        'situacoes_especificas': ('1.1.3', 'Situações Específicas', 'number'),
        'utilizadores_sms': ('4.1', 'Utilizadores de SMS', 'number'),
        'roaming_out_parceiros': ('4.2', 'Utilizadores de Roaming-Out', 'number'),
        'roaming_out': ('4.2', 'Utilizadores de Roaming-Out', 'number'),
        'banda_larga_3g_4g': ('2', 'Assinantes da Banda Larga Móvel', 'number'),
        'utilizadores_3g': ('2.2.1', '3G', 'number'),
        'internet_3g_box': ('2.1.4', 'Box (Router) 3G', 'number'),
        'internet_3g_usb': ('2.1.2', 'Modem USB 3G', 'number'),
        'utilizadores_4g': ('2.2.2', '4G', 'number'),
        'internet_4g_box': ('2.1.4.1', 'Box (Router) 4G', 'number'),
        'internet_4g_usb': ('2.1.2.1', 'Modem USB 4G', 'number'),
    },
    'mobile_money': {
        'mobile_money_utilizadores': ('4.3', 'Utilizadores de Mobile Money', 'number'),
        'mobile_money_mulher': ('4.3.1', 'Mobile Money - Mulher', 'number'),
        'mobile_money_homem': ('4.3.2', 'Mobile Money - Homem', 'number'),
        'mobile_money_carregamentos': ('4.3.3', 'Mobile Money - Carregamentos', 'fcfa'),
        'mobile_money_levantamentos': ('4.3.4', 'Mobile Money - Levantamentos', 'fcfa'),
        'mobile_money_transferencias': ('4.3.5', 'Mobile Money - Transferências', 'fcfa'),
    },
    'trafego_originado': {
        'chamadas_originadas': ('1', 'Chamadas de Voz Originadas', 'calls'),
        'chamadas_on_net': ('1.1', 'Chamadas On-Net', 'calls'),
        'chamadas_off_net': ('1.2', 'Chamadas Off-Net', 'calls'),
        'chamadas_internacional': ('1.3', 'Chamadas Internacionais saída', 'calls'),
        'minutos_originados': ('2', 'Minutos de Voz Originados', 'minutes'),
        'minutos_on_net': ('2.1', 'Minutos On-Net', 'minutes'),
        'minutos_off_net': ('2.2', 'Minutos Off-Net', 'minutes'),
        'minutos_internacional': ('2.3', 'Minutos Internacionais saída', 'minutes'),
        'sms_enviadas': ('3', 'SMS Originados', 'sms'),
        'sms_on_net': ('3.1', 'SMS On-Net', 'sms'),
        'sms_off_net': ('3.2', 'SMS Off-Net', 'sms'),
        'sms_internacional': ('3.3', 'SMS Internacional saída', 'sms'),
        'sessoes_dados_2g': ('4.1', 'Tráfego de dados 2G', 'mbps'),
        'sessoes_dados_3g': ('4.2', 'Tráfego de dados 3G', 'mbps'),
        'sessoes_dados_4g': ('4.3', 'Tráfego de dados 4G', 'mbps'),
        'trafego_dados_2g_mbit': ('4.1.1', 'Volume dados 2G (Mbit)', 'mbps'),
        'trafego_dados_3g_mbit': ('4.2.1', 'Volume dados 3G Internet (Mbit)', 'mbps'),
        'trafego_dados_3g_box_mbit': ('4.5', 'Tráfego Internet Box 3G', 'mbps'),
        'trafego_dados_3g_usb_mbit': ('4.6', 'Tráfego Internet USB 3G', 'mbps'),
        'trafego_dados_4g_mbit': ('4.3.1', 'Volume dados 4G Internet (Mbit)', 'mbps'),
        'trafego_dados_4g_box_mbit': ('4.7', 'Tráfego Internet Box 4G', 'mbps'),
        'trafego_dados_4g_usb_mbit': ('4.8', 'Tráfego Internet USB 4G', 'mbps'),
        'dados_4g_row64': ('4.3', 'Tráfego de dados 4G', 'mbps'),
        'dados_4g_row65': ('4.3.2', 'Acesso Internet banda larga 4G', 'mbps'),
        'dados_4g_row87': ('4.3.1', 'Volume dados 4G Internet (Mbit)', 'mbps'),
        'dados_4g_row88': ('4.3.3', 'Volume Internet banda larga 4G', 'mbps'),
    },
    'trafego_terminado': {
        'chamadas_terminadas': ('1', 'Chamadas de Voz Terminadas', 'calls'),
        'chamadas_term_off_net': ('1.1', 'Off-Net entrada', 'calls'),
        'chamadas_term_internacional': ('1.2', 'Chamadas Internacionais entrada', 'calls'),
        'minutos_terminados': ('2', 'Minutos de Voz Terminados', 'minutes'),
        'minutos_term_off_net': ('2.1', 'Minutos Off-Net entrada', 'minutes'),
        'minutos_term_internacional': ('2.2', 'Minutos Internacionais entrada', 'minutes'),
        'sms_terminadas': ('3', 'SMS Terminados', 'sms'),
        'sms_term_off_net': ('3.1', 'SMS Off-Net entrada', 'sms'),
        'sms_term_internacional': ('3.2', 'SMS Internacional entrada', 'sms'),
    },
    'roaming_internacional': {
        'roaming_in_chamadas_orig': ('1.1.1', 'Chamadas originadas por visitantes', 'calls'),
        'roaming_in_chamadas_term': ('1.1.2', 'Chamadas terminadas a visitantes', 'calls'),
        'roaming_in_minutos_orig': ('1.2.1', 'Minutos originados por visitantes', 'minutes'),
        'roaming_in_minutos_term': ('1.2.2', 'Minutos terminados a visitantes', 'minutes'),
        'roaming_in_sms_enviadas': ('1.3.1', 'SMS enviados por visitantes', 'sms'),
        'roaming_in_sms_recebidas': ('1.3.2', 'SMS recebidos por visitantes', 'sms'),
        'roaming_in_internet_sessoes': ('1.4', 'Dados Roaming-In', 'mb'),
        'roaming_in_internet_volume': ('1.4.1', 'Volume Dados Roaming-In (Mbit)', 'mb'),
        'roaming_out_chamadas_orig': ('2.1.1', 'Chamadas originadas no estrangeiro', 'calls'),
        'roaming_out_chamadas_term': ('2.1.2', 'Chamadas recebidas no estrangeiro', 'calls'),
        'roaming_out_minutos_orig': ('2.2.1', 'Minutos originados no estrangeiro', 'minutes'),
        'roaming_out_minutos_term': ('2.2.2', 'Minutos recebidos no estrangeiro', 'minutes'),
        'roaming_out_sms_enviadas': ('2.3.1', 'SMS enviados no estrangeiro', 'sms'),
        'roaming_out_internet_sessoes': ('2.4', 'Dados Roaming-Out', 'mb'),
        'roaming_out_internet_volume': ('2.4.1', 'Volume Dados Roaming-Out (Mbit)', 'mb'),
        'acordos_roaming': ('2.5', 'Acordos de roaming assinados', 'number'),
    },
    'largura_banda_internacional': {
        'lbi_downlink_disponivel': ('1', 'Largura de Banda Internacional', 'mbps'),
        'lbi_downlink_instalada': ('1.1', 'Capacidade contratada', 'mbps'),
        'lbi_downlink_contratada': ('1.1.1', 'Capacidade contratada downlink', 'mbps'),
        'lbi_downlink_utilizada': ('1.2', 'Capacidade utilizada', 'mbps'),
        'lbi_uplink_disponivel': ('1.3', 'Ligação uplink disponível', 'mbps'),
        'lbi_uplink_utilizada': ('1.3.1', 'Uplink utilizada', 'mbps'),
    },
    'internet_fixo': {
        'assinantes_internet_fixo': ('1', 'Por Tecnologia de Acesso', 'number'),
        'assinantes_box': ('1.1', 'Satélite (VSAT)', 'number'),
        'assinantes_hertziano': ('1.2', 'Feixes Hertzianos (FH)', 'number'),
        'assinantes_proxim': ('1.6', 'Outras tecnologias', 'number'),
        'assinantes_fibra': ('1.3', 'Fibra Óptica (FO)', 'number'),
        'debito_256k_2m': ('2.2', '256 Kbps ≤ Débito < 2 Mbps', 'number'),
        'debito_3_4m': ('2.3', '2 Mbps ≤ Débito < 10 Mbps', 'number'),
        'debito_2_4m': ('2.3', '2 Mbps ≤ Débito < 10 Mbps', 'number'),
        'debito_5_10m': ('2.4', '10 Mbps ≤ Débito < 30 Mbps', 'number'),
        'debito_10m': ('2.4', '10 Mbps ≤ Débito < 30 Mbps', 'number'),
        'debito_outros': ('2.5', '30 Mbps ≤ Débito < 100 Mbps', 'number'),
        'cat_residencial': ('3.1', 'Residencial', 'number'),
        'cat_corporativo': ('3.2', 'Empresas/Corporativo', 'number'),
        'cat_publicas': ('3.3', 'Administração Pública', 'number'),
        'cat_ensino': ('3.5', 'Instituições de Ensino', 'number'),
        'cat_saude': ('3.3.1', 'Instituições de Saúde', 'number'),
        'cat_ong': ('3.6', 'Outros', 'number'),
        'regiao_bissau': ('4.1', 'SAB (Sector Autónomo de Bissau)', 'number'),
        'regiao_bafata': ('4.5', 'Bafatá', 'number'),
        'regiao_biombo': ('4.2', 'Biombo', 'number'),
        'regiao_bolama': ('4.9', 'Bolama/Bijagós', 'number'),
        'regiao_cacheu': ('4.3', 'Cacheu', 'number'),
        'regiao_gabu': ('4.6', 'Gabú', 'number'),
        'regiao_oio': ('4.4', 'Oio', 'number'),
        'regiao_quinara': ('4.8', 'Quinara', 'number'),
        'regiao_tombali': ('4.7', 'Tombali', 'number'),
    },
    'trafego_internet_fixo': {
        'trafego_internet_fixo_total': ('1', 'Por Tecnologia de Acesso', 'gb'),
        'trafego_hertziano_proxim': ('1.2', 'Feixes Hertzianos (FH)', 'gb'),
        'trafego_fibra': ('1.3', 'Fibra Óptica (FO)', 'gb'),
    },
    'receitas': {
        'receita_total': ('8', 'Total de Receitas (Volume de Negócios)', 'fcfa_millions'),
        'receita_voz': ('1', 'Receitas de Serviços de Voz', 'fcfa_millions'),
        'receita_chamadas_on_net': ('1.1', 'Receitas de chamadas On-Net', 'fcfa_millions'),
        'receita_chamadas_off_net': ('1.2', 'Receitas de chamadas Off-Net saída', 'fcfa_millions'),
        'receita_chamadas_off_net_mtn': ('1.2', 'Receitas de chamadas Off-Net saída', 'fcfa_millions'),
        'receita_chamadas_internacional': ('1.3', 'Receitas de chamadas Internacionais saída', 'fcfa_millions'),
        'receita_voz_roaming_out': ('1.4', 'Receitas de Roaming-Out voz', 'fcfa_millions'),
        'receita_terminacao_voz': ('2', 'Receitas de Interconexão', 'fcfa_millions'),
        'receita_term_off_net_mtn': ('2.1', 'Receitas de terminação Off-Net entrada', 'fcfa_millions'),
        'receita_term_off_net_orange': ('2.1', 'Receitas de terminação Off-Net entrada', 'fcfa_millions'),
        'receita_term_internacional': ('2.2', 'Receitas de terminação Internacional entrada', 'fcfa_millions'),
        'receita_mensagens': ('3', 'Receitas de SMS', 'fcfa_millions'),
        'receita_dados_moveis': ('4.1', 'Receitas de Internet móvel', 'fcfa_millions'),
        'receita_internet_fixo': ('4.2', 'Receitas de Internet fixa', 'fcfa_millions'),
    },
    'emprego': {
        'emprego_directo_total': ('1', 'Emprego Directo', 'persons'),
        'emprego_nacionais': ('1.1', 'Nacionais', 'persons'),
        'emprego_homens': ('1.1.1', 'Masculino', 'persons'),
        'emprego_mulheres': ('1.1.2', 'Feminino', 'persons'),
        'emprego_indirecto': ('2', 'Emprego Indirecto', 'persons'),
    },
    'investimento': {
        'investimento_total': ('1', 'Investimento Total', 'fcfa_millions'),
        'investimento_corporeo': ('1.1.1', 'Investimento Corpóreo (Tangível)', 'fcfa_millions'),
        'investimento_telecom': ('1.1', 'Investimento em Telecomunicações', 'fcfa_millions'),
        'investimento_internet': ('1.2', 'Investimento em Serviços Internet', 'fcfa_millions'),
        'investimento_incorporeo': ('1.1.2', 'Investimento Incorpóreo (Intangível)', 'fcfa_millions'),
        'investimento_row15': ('1.1.1.1', 'Equipamentos de Telecomunicações', 'fcfa_millions'),
        'investimento_row17': ('1.1.1.2', 'Equipamentos informáticos', 'fcfa_millions'),
    },
}


class Command(BaseCommand):
    help = 'Importa dados KPI de ficheiros JSON (ARN 2024) para a base de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', type=str, help='Nome do ficheiro JSON específico',
        )
        parser.add_argument(
            '--operator', type=str, help='Código do operador (ORANGE, TELECEL)',
        )
        parser.add_argument(
            '--year', type=int, help='Ano dos dados',
        )
        parser.add_argument(
            '--dry-run', action='store_true', help='Simula sem gravar',
        )
        parser.add_argument(
            '--data-dir', type=str, default='data/kpi_2024',
            help='Directório dos ficheiros JSON',
        )

    def handle(self, *args, **options):
        data_dir = Path(options['data_dir'])
        if not data_dir.is_absolute():
            data_dir = Path(os.path.dirname(os.path.abspath(__file__))).parents[3] / data_dir
        dry_run = options['dry_run']
        target_file = options.get('file')

        json_files = []
        if target_file:
            json_files = [data_dir / target_file]
        else:
            if data_dir.exists():
                json_files = sorted(data_dir.glob('*.json'))

        if not json_files:
            self.stderr.write(self.style.ERROR(f'Nenhum ficheiro JSON em {data_dir}'))
            return

        self.stdout.write(f'Encontrados {len(json_files)} ficheiro(s) JSON')
        total_created = 0
        total_updated = 0

        for json_file in json_files:
            self.stdout.write(f'\n{"="*60}')
            self.stdout.write(self.style.HTTP_INFO(f'Processando: {json_file.name}'))
            created, updated = self._process_file(json_file, dry_run, options)
            total_created += created
            total_updated += updated

        self._compute_root_totals(dry_run)

        self.stdout.write(f'\n{"="*60}')
        prefix = '[DRY-RUN] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f'{prefix}Importação concluída: {total_created} criados, {total_updated} actualizados',
        ))

    def _process_file(self, json_file, dry_run, options):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        operator_name = data.get('operadora', '')
        year = options.get('year') or data.get('ano', 2024)
        operator_code = options.get('operator')

        if not operator_code:
            name_map = {
                'orange': 'ORANGE', 'orange bissau': 'ORANGE',
                'telecel': 'TELECEL', 'mtn': 'TELECEL',
            }
            operator_code = name_map.get(operator_name.lower(), operator_name.upper())

        try:
            operator = Operator.objects.get(code=operator_code)
        except Operator.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Operador {operator_code} não encontrado'))
            return 0, 0

        self.stdout.write(f'  Operador: {operator.name} ({operator.code})')
        self.stdout.write(f'  Ano: {year}')

        created = 0
        updated = 0

        for json_cat in data.get('categorias', []):
            json_cat_id = json_cat['id']
            db_cat_code = CATEGORY_MAP.get(json_cat_id)

            if not db_cat_code:
                self.stdout.write(self.style.WARNING(
                    f'  Categoria ignorada: {json_cat_id} (sem mapeamento)',
                ))
                continue

            try:
                db_category = IndicatorCategory.objects.get(code=db_cat_code)
            except IndicatorCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'  Categoria DB não encontrada: {db_cat_code}',
                ))
                continue

            cat_map = INDICATOR_MAP.get(json_cat_id, {})
            cat_created = 0
            cat_updated = 0

            for json_ind in json_cat.get('indicadores', []):
                json_ind_id = json_ind['id']
                mapping = cat_map.get(json_ind_id)

                if not mapping:
                    self.stdout.write(self.style.WARNING(
                        f'    Indicador ignorado: {json_ind_id} ({json_ind["nome"]})',
                    ))
                    continue

                db_code, db_name, db_unit = mapping
                indicator = self._get_or_create_indicator(
                    db_category, db_code, db_name, db_unit, dry_run,
                )
                if not indicator:
                    continue

                if 'mensal' in json_ind:
                    c, u = self._import_monthly(
                        indicator, operator, year, json_ind['mensal'], dry_run,
                    )
                    cat_created += c
                    cat_updated += u

                if 'acumulado' in json_ind:
                    c, u = self._import_cumulative(
                        indicator, operator, year, json_ind['acumulado'],
                        json_ind.get('unidade', ''), dry_run,
                    )
                    cat_created += c
                    cat_updated += u

            self.stdout.write(
                f'  {json_cat["nome"]}: {cat_created} criados, {cat_updated} actualizados',
            )
            created += cat_created
            updated += cat_updated

        return created, updated

    def _get_or_create_indicator(self, category, code, name, unit, dry_run):
        try:
            return Indicator.objects.get(category=category, code=code)
        except Indicator.DoesNotExist:
            if dry_run:
                self.stdout.write(f'    [DRY-RUN] Criar indicador: {code} - {name}')
                return None

            parent = None
            if '.' in code:
                parent_code = code.rsplit('.', 1)[0]
                parent = Indicator.objects.filter(
                    category=category, code=parent_code,
                ).first()

            level = code.count('.')
            max_order = Indicator.objects.filter(
                category=category,
            ).order_by('-order').values_list('order', flat=True).first() or 0

            indicator = Indicator.objects.create(
                category=category, code=code, name=name, unit=unit,
                level=level, parent=parent, order=max_order + 1,
                is_calculated=False,
            )
            self.stdout.write(f'    Indicador criado: {code} - {name}')
            return indicator

    def _import_monthly(self, indicator, operator, year, monthly_data, dry_run):
        created = 0
        updated = 0

        for month_name, value in monthly_data.items():
            month_num = MONTH_MAP.get(month_name.lower())
            if not month_num:
                continue

            try:
                dec_value = Decimal(str(value))
            except (InvalidOperation, ValueError, TypeError):
                continue

            try:
                period = Period.objects.get(year=year, month=month_num)
            except Period.DoesNotExist:
                continue

            if dry_run:
                continue

            _, was_created = DataEntry.objects.update_or_create(
                indicator=indicator, operator=operator, period=period,
                defaults={
                    'value': dec_value,
                    'source': 'imported',
                    'is_validated': True,
                    'observation': f'Importado JSON ARN {year}',
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        return created, updated

    def _import_cumulative(self, indicator, operator, year, cumulative_data, unidade, dry_run):
        created = 0
        updated = 0

        for cum_key, value in cumulative_data.items():
            cum_type = CUMULATIVE_MAP.get(cum_key)
            if not cum_type:
                continue

            try:
                dec_value = Decimal(str(value))
            except (InvalidOperation, ValueError, TypeError):
                continue

            if unidade in ('milhoes_fcfa',) and indicator.unit == 'fcfa_millions':
                pass
            elif unidade == 'fcfa' and indicator.unit == 'fcfa_millions':
                dec_value = dec_value / Decimal('1000000')

            if dry_run:
                continue

            _, was_created = CumulativeData.objects.update_or_create(
                indicator=indicator, operator=operator,
                year=year, cumulative_type=cum_type,
                defaults={
                    'value': dec_value,
                    'source': 'imported',
                    'is_validated': True,
                    'observation': f'Importado JSON ARN {year}',
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        return created, updated

    def _compute_root_totals(self, dry_run):
        """Compute root-level totals for indicators the dashboard expects."""
        self.stdout.write('\nComputando totais raiz para o dashboard...')

        self._compute_subscribers_total(dry_run)
        self._compute_data_traffic_total(dry_run)

    def _compute_subscribers_total(self, dry_run):
        """estacoes_moveis code '1' = total pre-paid + post-paid."""
        try:
            cat = IndicatorCategory.objects.get(code='estacoes_moveis')
        except IndicatorCategory.DoesNotExist:
            return

        root = Indicator.objects.filter(category=cat, code='1').first()
        if not root:
            return

        pre = Indicator.objects.filter(category=cat, code='1.1.2').first()
        pos = Indicator.objects.filter(category=cat, code='1.1.1').first()
        if not pre or not pos:
            return

        operators = Operator.objects.filter(is_active=True)
        periods = Period.objects.filter(year=2024)
        count = 0

        for period in periods:
            for op in operators:
                pre_entry = DataEntry.objects.filter(
                    indicator=pre, operator=op, period=period,
                ).first()
                pos_entry = DataEntry.objects.filter(
                    indicator=pos, operator=op, period=period,
                ).first()

                total_val = Decimal('0')
                if pre_entry and pre_entry.value:
                    total_val += pre_entry.value
                if pos_entry and pos_entry.value:
                    total_val += pos_entry.value

                if total_val > 0 and not dry_run:
                    _, created = DataEntry.objects.update_or_create(
                        indicator=root, operator=op, period=period,
                        defaults={
                            'value': total_val,
                            'source': 'calculated',
                            'is_validated': True,
                            'observation': 'Total assinantes = Pré + Pós',
                        },
                    )
                    if created:
                        count += 1

        self.stdout.write(f'  Total assinantes (code 1): {count} entradas criadas/actualizadas')

    def _compute_data_traffic_total(self, dry_run):
        """trafego_originado code '4' = sum of data traffic sub-indicators."""
        try:
            cat = IndicatorCategory.objects.get(code='trafego_originado')
        except IndicatorCategory.DoesNotExist:
            return

        root = Indicator.objects.filter(category=cat, code='4').first()
        if not root:
            return

        sub_codes = ['4.1', '4.2', '4.3']
        subs = Indicator.objects.filter(category=cat, code__in=sub_codes)
        if not subs.exists():
            return

        operators = Operator.objects.filter(is_active=True)
        periods = Period.objects.filter(year=2024)
        count = 0

        for period in periods:
            for op in operators:
                total_val = Decimal('0')
                for sub in subs:
                    entry = DataEntry.objects.filter(
                        indicator=sub, operator=op, period=period,
                    ).first()
                    if entry and entry.value:
                        total_val += entry.value

                if total_val > 0 and not dry_run:
                    _, created = DataEntry.objects.update_or_create(
                        indicator=root, operator=op, period=period,
                        defaults={
                            'value': total_val,
                            'source': 'calculated',
                            'is_validated': True,
                            'observation': 'Total dados = 2G + 3G + 4G',
                        },
                    )
                    if created:
                        count += 1

        self.stdout.write(f'  Total dados (code 4): {count} entradas criadas/actualizadas')
