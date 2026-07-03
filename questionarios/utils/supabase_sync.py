import os
import json
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Cliente para interagir com a API do Supabase."""
    
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def sync_table(self, django_table, supabase_table):
        """
        Sincroniza uma tabela do Django com o Supabase.
        
        Args:
            django_table: Nome do modelo Django
            supabase_table: Nome da tabela no Supabase
        """
        try:
            logger.info(f"Iniciando sincronização entre Django ({django_table}) e Supabase ({supabase_table})")
            
            # Importar o modelo dinamicamente
            from django.apps import apps
            model = apps.get_model('questionarios', django_table)
            
            # Obter todos os registros do Django
            django_records = model.objects.all()
            
            # Obter todos os registros do Supabase
            supabase_records = self.get_all_records(supabase_table)
            
            # Mapear registros do Supabase por ID para fácil acesso
            supabase_map = {str(record.get('id', '')): record for record in supabase_records}
            
            # Sincronizar cada registro do Django com o Supabase
            for django_record in django_records:
                record_data = self._prepare_record_data(django_record)
                
                if str(django_record.id) in supabase_map:
                    # Atualizar registro existente
                    self.update_record(supabase_table, django_record.id, record_data)
                    logger.debug(f"Atualizado registro ID {django_record.id} em {supabase_table}")
                else:
                    # Criar novo registro
                    self.insert_record(supabase_table, record_data)
                    logger.debug(f"Criado novo registro em {supabase_table}")
            
            logger.info(f"Sincronização concluída para {django_table} -> {supabase_table}")
            
            return True
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            return False
    
    def _prepare_record_data(self, django_record):
        """
        Prepara os dados de um registro Django para o formato do Supabase.
        """
        data = {}
        
        # Obter todos os campos do modelo
        fields = django_record._meta.fields
        
        for field in fields:
            field_name = field.name
            field_value = getattr(django_record, field_name)
            
            # Tratar campos especiais
            if field_name == 'id':
                data[field_name] = str(field_value)
            elif field_name in ['criado_por', 'atualizado_por'] and field_value is not None:
                data[field_name] = str(field_value.id)
            elif field_name in ['data_criacao', 'data_atualizacao'] and field_value is not None:
                data[field_name] = field_value.isoformat()
            elif field_value is not None:
                data[field_name] = field_value
        
        return data
    
    def get_all_records(self, table):
        """Obtém todos os registros de uma tabela do Supabase."""
        try:
            url = f"{self.supabase_url}/rest/v1/{table}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter registros da tabela {table}: {e}")
            return []
    
    def insert_record(self, table, data):
        """Insere um novo registro no Supabase."""
        try:
            url = f"{self.supabase_url}/rest/v1/{table}"
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao inserir registro na tabela {table}: {e}")
            return None
    
    def update_record(self, table, record_id, data):
        """Atualiza um registro existente no Supabase."""
        try:
            url = f"{self.supabase_url}/rest/v1/{table}?id=eq.{record_id}"
            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao atualizar registro ID {record_id} na tabela {table}: {e}")
            return None

def sync_all_tables():
    """Sincroniza todas as tabelas relevantes com o Supabase."""
    client = SupabaseClient()
    
    # Mapeamento entre modelos Django e tabelas Supabase
    table_mapping = {
        'EstacoesMoveisIndicador': 'estacoes_moveis',
        'TrafegoOriginadoIndicador': 'trafego_originado',
        'TrafegoTerminadoIndicador': 'trafego_terminado',
        'ReceitasIndicador': 'receitas',
        'EmpregoIndicador': 'emprego',
        'InvestimentoIndicador': 'investimento'
    }
    
    success = True
    for django_table, supabase_table in table_mapping.items():
        if not client.sync_table(django_table, supabase_table):
            success = False
    
    return success 