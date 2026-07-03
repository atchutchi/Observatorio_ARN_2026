import pandas as pd
import re
import logging
from decimal import Decimal, InvalidOperation
from django.contrib.auth.models import User # To set user
# Import FieldDoesNotExist
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction # Import transaction
from datetime import datetime

# Import all relevant models from questionarios
from questionarios.models import (
    TrafegoInternetIndicador, ReceitasIndicador, EmpregoIndicador,
    EstacoesMoveisIndicador, AssinantesIndicador, TrafegoOriginadoIndicador,
    TrafegoTerminadoIndicador, TrafegoRoamingInternacionalIndicador,
    LBIIndicador, InternetFixoIndicador, InvestimentoIndicador,
    TarifarioVozOrangeIndicador, TarifarioVozMTNIndicador, TarifarioVozTelecelIndicador
    # Ensure RegistroQuestionario is not needed here unless processed from Excel
)

logger = logging.getLogger(__name__)

# Mapping from Excel INDICADOR names (or Cod.) to Model field names
# Adjust based on exact Excel names and your model field names
INDICATOR_FIELD_MAPPING = {
    # Cod. | INDICADOR
    1.1: 'por_via_satelite',
    1.2: 'por_sistema_hertziano_fixo_terra',
    1.3: 'fibra_otica',
    # 2.1 - Banda Estreita - Not directly in TrafegoInternetIndicador model?
    2.11: 'kbps_64_128', # Check if Cod. are 2.1.1 or 2.11
    2.12: 'kbps_128_256',
    2.13: 'banda_estreita_outros',
    # 2.2 - Banda Larga
    2.21: 'kbits_256_2mbits',
    2.22: 'mbits_2_4',
    2.23: 'mbits_10', # Assuming 10 Mbit/s matches 2.2.3
    2.24: 'banda_larga_outros',
    # 3 - Tráfego por categoria
    3.1: 'residencial',
    3.2: 'corporativo_empresarial',
    3.31: 'instituicoes_publicas',
    3.32: 'instituicoes_ensino',
    3.33: 'instituicoes_saude',
    4: 'ong_outros',
    # 5 - Tráfego por Região
    5.1: 'cidade_bissau',
    5.2: 'bafata',
    5.3: 'biombo',
    5.4: 'bolama_bijagos',
    5.5: 'cacheu',
    5.6: 'gabu',
    5.7: 'oio',
    5.8: 'quinara',
    5.9: 'tombali', # Assuming Tombali is 5.9 based on pattern
    # 6 - Tráfego por acesso público via rádio (PWLAN) 
    # Need corresponding model fields if these exist
    # 6.1: 'acesso_livre', 
    # 6.2: 'acesso_condicionado',
    
    # Mapping by Name if Cod. is unreliable
    "Por via Satélite": "por_via_satelite",
    "Por Sistema Hertziano Fixo de Terra (FH) + PROXIM": "por_sistema_hertziano_fixo_terra",
    "Fibra Ótica": "fibra_otica",
    "64 - 128 Kbps": "kbps_64_128",
    "128 - 256 Kbps": "kbps_128_256",
    "Outros (Especificar)": "banda_estreita_outros", # Might need specific handling
    "256 Kbit/s - 2 Mbit/s": "kbits_256_2mbits",
    "2 - 4 Mbit/s": "mbits_2_4", 
    "10 Mbit/s": "mbits_10",
    # "Outros (Especificar)" again - needs context or better label
    "Residencial": "residencial",
    "Corporativo / empresarial": "corporativo_empresarial",
    "Instituições Públicas": "instituicoes_publicas",
    "Instituições de Ensino": "instituicoes_ensino",
    "Instituições de Saúde": "instituicoes_saude",
    "ONG e outros (especificar)": "ong_outros",
    "Cidade de Bissau": "cidade_bissau",
    "Bafatá": "bafata",
    "Biombo": "biombo",
    "Bolama Bijagós": "bolama_bijagos",
    "Cacheu": "cacheu",
    "Gabú": "gabu",
    "Oio": "oio",
    "Quinara": "quinara",
    "Tombali": "tombali",
    
    # Add other mappings...
}

MONTH_MAPPING = {
    'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4,
    'MAIO': 5, 'JUNHO': 6, 'JULHO': 7, 'AGOSTO': 8,
    'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
}

def clean_value(value):
    """Cleans monetary/number values from Excel."""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float, Decimal)):
        # Handle potential floats coming from pandas/excel
        try:
            return Decimal(value)
        except InvalidOperation:
             # Handle cases like infinity or NaN if they occur
             logger.warning(f"Could not convert float value '{value}' to Decimal.")
             return None
            
    text = str(value).strip()
    if text.upper() == 'NA' or text == '-' or text == '':
        return None
        
    text = text.replace('.', '').replace(',', '.')
    try:
        return Decimal(text)
    except InvalidOperation:
        logger.warning(f"Could not convert text value '{value}' to Decimal.")
        return None

def parse_internet_traffic(df, year, operadora_code, user):
    """Parses the TrafegoInternetIndicador data from the DataFrame."""
    processed_count = 0
    error_count = 0
    errors = []

    # Ensure Cod. column is suitable for matching (e.g., float or text)
    # df['Cod.'] = df['Cod.'].astype(str) # Example: if matching by string code

    for excel_code, model_field in INDICATOR_FIELD_MAPPING.items():
        # Find the row matching the code or indicator name
        row = None
        try:
            if isinstance(excel_code, (float, int)):
                 # Try matching by numeric code first
                 numeric_code = float(excel_code)
                 if 'Cod.' in df.columns:
                     # Ensure comparison is between floats after handling potential NaNs
                     df_codes_float = pd.to_numeric(df['Cod.'], errors='coerce')
                     row = df[df_codes_float == numeric_code]
            if row is None or row.empty:
                 # Try matching by indicator name if code fails or isn't numeric
                 if 'INDICADOR' in df.columns:
                     row = df[df['INDICADOR'].astype(str).str.strip() == str(excel_code)]

            if row is None or row.empty:
                logger.warning(f"Could not find row for indicator code/name: {excel_code}")
                errors.append(f"Indicador não encontrado no Excel: {excel_code}")
                error_count += 1
                continue
            
            row_data = row.iloc[0] # Get the first matching row

            for month_name, month_num in MONTH_MAPPING.items():
                if month_name in row_data:
                    value = clean_value(row_data[month_name])
                    
                    # Check if field exists in model before trying to update
                    try:
                         TrafegoInternetIndicador._meta.get_field(model_field)
                    except FieldDoesNotExist:
                        logger.warning(f"Model field '{model_field}' mapped from Excel '{excel_code}' does not exist in TrafegoInternetIndicador.")
                        # errors.append(f"Campo do modelo '{model_field}' não existe.") # Option: report as error
                        # error_count += 1
                        continue # Skip this field
                        
                    try:
                        obj, created = TrafegoInternetIndicador.objects.update_or_create(
                            operadora=operadora_code,
                            ano=year,
                            mes=month_num,
                            defaults={model_field: value, 'atualizado_por': user}
                        )
                        if created:
                            obj.criado_por = user
                            obj.save()
                        # Only count as processed if update_or_create succeeded
                        processed_count += 1 
                    except Exception as e:
                        logger.error(f"Error updating/creating TrafegoInternet for {year}-{month_num}, Op:{operadora_code}, Field:{model_field}: {e}")
                        errors.append(f"Erro BD ({year}-{month_num}, {model_field}): {e}")
                        error_count += 1
                else:
                    logger.warning(f"Month column '{month_name}' not found in DataFrame for indicator {excel_code}.")
                    # Optionally report missing month column as an error
                    # errors.append(f"Coluna do mês '{month_name}' não encontrada.")
                    # error_count += 1

        except Exception as e:
            logger.error(f"Error processing indicator {excel_code} ({model_field}): {e}")
            errors.append(f"Erro ao processar indicador {excel_code}: {e}")
            error_count += 1
            
    # Recalculate processed count based only on successful updates/creates if needed
    # This count might be slightly off if update_or_create fails mid-loop for a row
    # A more accurate count would increment inside the inner try block

    return processed_count, error_count, errors

def process_excel_file(uploaded_file, user, operadora_code=None, year=None, indicator_type=None):
    """Main function to process the uploaded Excel file.
    
    Args:
        uploaded_file: The uploaded Excel file
        user: The user uploading the file
        operadora_code: The operadora code (orange, telecel, telecel)
        year: The year for the data (integer)
        indicator_type: Type of indicator to process ('trafego_internet', 'receitas', etc.)
    """
    results = {
        'processed': 0,
        'errors': 0,
        'error_details': []
    }
    
    # Define mapping of indicator types to sheet names and parser functions
    indicator_processors = {
        'trafego_internet': {
            'sheet_name': 'Internet_Trafico',
            'parser_function': parse_internet_traffic,
            'header_row': 3
        },
        # Add other indicator types as needed
        # 'receitas': {
        #    'sheet_name': 'RECEITAS',
        #    'parser_function': parse_receitas,
        #    'header_row': 3
        # },
    }
    
    # If no specific indicator type provided, try to process all known types
    if not indicator_type:
        processor_list = indicator_processors.values()
    else:
        if indicator_type not in indicator_processors:
            results['error_details'].append(f"Tipo de indicador '{indicator_type}' não reconhecido.")
            results['errors'] += 1
            return results
        
        processor_list = [indicator_processors[indicator_type]]
    
    for processor in processor_list:
        sheet_name = processor['sheet_name']
        parser_function = processor['parser_function']
        header_row_index = processor['header_row']
        
        try:
            # Load the sheet
            excel_data = pd.read_excel(
                uploaded_file, 
                sheet_name=sheet_name, 
                header=header_row_index
            )
            
            # Determine Year if not provided 
            sheet_year = year
            if not sheet_year:
                try:
                    # Attempt to extract year from header cell like 'I TRIMESTRE 2023'
                    # Combine column headers into a single string to search
                    header_text = " ".join(map(str, excel_data.columns))
                    match = re.search(r'\b(20\d{2})\b', header_text)
                    if match:
                        sheet_year = int(match.group(1))
                except Exception as e:
                    logger.warning(f"Could not automatically detect year from headers/cells: {e}")
            
            if not sheet_year:
                current_year = datetime.now().year
                sheet_year = current_year  # Use current year as fallback
                results['error_details'].append(f"Aviso: Ano não especificado para aba '{sheet_name}'. Usando ano atual: {current_year}.")
            
            # Use provided operadora or fallback
            sheet_operadora = operadora_code
            if not sheet_operadora:
                # Try to extract from filename or sheet
                # For now, default to requesting user to specify
                results['error_details'].append(f"Aviso: Operadora não especificada para aba '{sheet_name}'. Por favor, selecione a operadora no formulário.")
                results['errors'] += 1
                continue  # Skip this processor if operadora not specified
            
            logger.info(f"Processing sheet '{sheet_name}' for Year: {sheet_year}, Operadora: {sheet_operadora}")
            
            # Parse the sheet with the appropriate function
            p_count, e_count, errors = parser_function(excel_data, sheet_year, sheet_operadora, user)
            results['processed'] += p_count
            results['errors'] += e_count
            results['error_details'].extend(errors)
            
            if p_count > 0 or e_count > 0:
                results['error_details'].insert(0, f"Planilha '{sheet_name}': {p_count} processados, {e_count} erros.")
                
        except ValueError as ve:
            # Specific error for sheet not found
            if f"Worksheet named '{sheet_name}' not found" in str(ve):
                logger.warning(f"Planilha '{sheet_name}' não encontrada no arquivo.")
                results['error_details'].append(f"Aviso: Planilha '{sheet_name}' não encontrada ou nome incorreto. Pulando esta planilha.")
            else:
                # Re-raise other ValueErrors or handle them
                logger.error(f"Erro de valor ao ler planilha '{sheet_name}': {ve}", exc_info=True)
                results['errors'] += 1
                results['error_details'].append(f"Erro de valor ao ler planilha '{sheet_name}': {ve}")
        except Exception as e:
            logger.error(f"Erro ao processar planilha '{sheet_name}': {e}", exc_info=True)
            results['errors'] += 1
            results['error_details'].append(f"Erro geral ao processar planilha '{sheet_name}': {e}")
    
    return results 