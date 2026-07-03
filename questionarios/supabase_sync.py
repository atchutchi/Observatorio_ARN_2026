"""
Arquivo para sincronização com o Supabase.
Configura signals do Django para sincronizar automaticamente os modelos com o Supabase.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# Lista de modelos a serem sincronizados com o Supabase
SUPABASE_MODELS = [
    'TarifarioVozOrangeIndicador',
    'TarifarioVozMTNIndicador',
    'EstacoesMoveisIndicador',
    'TrafegoOriginadoIndicador',
    'TrafegoTerminadoIndicador',
    'TrafegoRoamingInternacionalIndicador',
    'LBIIndicador',
    'TrafegoInternetIndicador',
    'InternetFixoIndicador',
    'ReceitasIndicador',
    'EmpregoIndicador',
    'InvestimentoIndicador',
]

@receiver(post_save)
def sync_to_supabase(sender, instance, created, **kwargs):
    """
    Signal para sincronizar dados com o Supabase após salvar.
    """
    sender_name = sender.__name__
    
    # Verifica se o modelo está na lista de modelos a serem sincronizados
    if sender_name in SUPABASE_MODELS:
        try:
            # Obtém o nome da tabela no Supabase (converte CamelCase para snake_case)
            import re
            table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', sender_name).lower()
            
            # Tenta sincronizar com o Supabase
            if hasattr(instance, 'save_to_supabase'):
                instance.save_to_supabase(table_name)
                logger.info(f"Dados sincronizados com Supabase: {sender_name} (ID: {instance.id})")
            else:
                logger.warning(f"Modelo {sender_name} não possui método save_to_supabase")
        except Exception as e:
            # Em caso de erro, apenas loga o erro, não interrompe a operação
            logger.error(f"Erro ao sincronizar com Supabase: {str(e)}")

@receiver(post_delete)
def delete_from_supabase(sender, instance, **kwargs):
    """
    Signal para excluir dados do Supabase após exclusão.
    """
    sender_name = sender.__name__
    
    # Verifica se o modelo está na lista de modelos a serem sincronizados
    if sender_name in SUPABASE_MODELS:
        try:
            # Obtém o nome da tabela no Supabase (converte CamelCase para snake_case)
            import re
            table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', sender_name).lower()
            
            # Tenta excluir do Supabase
            if hasattr(instance, 'delete_from_supabase'):
                instance.delete_from_supabase(table_name)
                logger.info(f"Dados removidos do Supabase: {sender_name} (ID: {instance.id})")
            else:
                logger.warning(f"Modelo {sender_name} não possui método delete_from_supabase")
        except Exception as e:
            # Em caso de erro, apenas loga o erro, não interrompe a operação
            logger.error(f"Erro ao excluir do Supabase: {str(e)}") 