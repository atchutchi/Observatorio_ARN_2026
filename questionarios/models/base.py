from django.db import models
from django.conf import settings
import os
import json
import requests
import logging
import decimal

logger = logging.getLogger(__name__)

class IndicadorBase(models.Model):
    """Classe base para todos os indicadores."""
    
    OPERADORAS_CHOICES = [
        ('orange', 'Orange'),
        ('telecel', 'TELECEL'),
    ]
    
    operadora = models.CharField(max_length=10, choices=OPERADORAS_CHOICES, null=True, blank=True, verbose_name="Operadora")
    ano = models.IntegerField(default=2025)  # Valor padrão para o ano atual
    mes = models.IntegerField(default=1)     # Valor padrão para janeiro
    
    class Meta:
        abstract = True
    
    def save_to_supabase(self, table_name):
        """
        Salva os dados do indicador no Supabase.
        
        Args:
            table_name (str): Nome da tabela no Supabase
        """
        try:
            # Verifica se as configurações do Supabase existem
            if not hasattr(settings, 'SUPABASE_URL') or not hasattr(settings, 'SUPABASE_KEY'):
                logger.warning("Configurações do Supabase não encontradas. Ignorando sincronização.")
                return False
                
            supabase_url = settings.SUPABASE_URL
            supabase_key = settings.SUPABASE_KEY
            
            # Preparar dados para envio
            data = self._prepare_data_for_supabase()
            
            # Definir cabeçalhos para requisição
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            # Verificar se o registro já existe
            check_url = f"{supabase_url}/rest/v1/{table_name}?id=eq.{self.id}"
            check_response = requests.get(check_url, headers=headers)
            
            if check_response.status_code == 200 and len(check_response.json()) > 0:
                # Atualizar registro existente
                update_url = f"{supabase_url}/rest/v1/{table_name}?id=eq.{self.id}"
                response = requests.patch(update_url, headers=headers, json=data)
            else:
                # Inserir novo registro
                insert_url = f"{supabase_url}/rest/v1/{table_name}"
                response = requests.post(insert_url, headers=headers, json=data)
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Dados salvos com sucesso no Supabase: {table_name}, ID: {self.id}")
                return True
            else:
                logger.error(f"Erro ao salvar no Supabase: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao salvar no Supabase: {e}")
            return False
    
    def delete_from_supabase(self, table_name):
        """
        Remove os dados do indicador do Supabase.
        
        Args:
            table_name (str): Nome da tabela no Supabase
        """
        try:
            # Verifica se as configurações do Supabase existem
            if not hasattr(settings, 'SUPABASE_URL') or not hasattr(settings, 'SUPABASE_KEY'):
                logger.warning("Configurações do Supabase não encontradas. Ignorando deleção.")
                return False
                
            supabase_url = settings.SUPABASE_URL
            supabase_key = settings.SUPABASE_KEY
            
            # Definir cabeçalhos para requisição
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Remover registro do Supabase
            delete_url = f"{supabase_url}/rest/v1/{table_name}?id=eq.{self.id}"
            response = requests.delete(delete_url, headers=headers)
            
            if response.status_code in [200, 204]:
                logger.info(f"Dados removidos com sucesso do Supabase: {table_name}, ID: {self.id}")
                return True
            else:
                logger.error(f"Erro ao remover do Supabase: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao remover do Supabase: {e}")
            return False
    
    def _prepare_data_for_supabase(self):
        """
        Prepara os dados para envio ao Supabase.
        
        Returns:
            dict: Dados formatados para o Supabase
        """
        data = {
            'id': str(self.id) if self.id else None,
            'operadora': self.operadora,
            'ano': self.ano,
            'mes': self.mes
        }
        
        # Adicionar campos específicos de cada modelo
        for field in self._meta.fields:
            field_name = field.name
            # Evitar duplicar campos já adicionados
            if field_name not in ['id', 'operadora', 'ano', 'mes']:
                try:
                    value = getattr(self, field_name)
                    
                    # Tratar campos especiais
                    if field_name in ['criado_por', 'atualizado_por'] and value is not None:
                        data[field_name] = str(value.id)
                    elif field_name in ['data_criacao', 'data_atualizacao'] and value is not None:
                        data[field_name] = value.isoformat()
                    elif value is not None:
                        # Handle Decimal objects by converting to strings
                        if isinstance(value, decimal.Decimal):
                            data[field_name] = str(value)
                        else:
                            data[field_name] = value
                except (AttributeError, TypeError) as e:
                    logger.warning(f"Erro ao preparar campo {field_name} para Supabase: {e}")
        
        return data

    def __str__(self):
        # Add a safe string representation for all derived models
        operadora_display = self.get_operadora_display() if self.operadora else "Não definida"
        return f"{self.__class__.__name__} - {self.ano}/{self.mes} - {operadora_display}"
