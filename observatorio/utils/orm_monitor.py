import logging
import functools
import time
import traceback
from django.db import connection, models, IntegrityError, OperationalError, ProgrammingError
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger('observatorio.models')

def log_model_operation(operation_type):
    """
    Decorator for logging model operations (save, delete, etc.)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            model_name = self.__class__.__name__
            model_id = getattr(self, 'pk', None)
            start_time = time.time()
            
            try:
                logger.debug(f"{operation_type} iniciada: {model_name} (ID: {model_id})")
                result = func(self, *args, **kwargs)
                elapsed_time = time.time() - start_time
                logger.debug(f"{operation_type} concluída: {model_name} (ID: {model_id}) em {elapsed_time:.4f}s")
                return result
            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(f"Erro em {operation_type}: {model_name} (ID: {model_id}): {str(e)}")
                logger.error(traceback.format_exc())
                raise
        
        return wrapper
    
    return decorator

# Monitoramento de sinais do Django
@receiver(pre_save)
def log_pre_save(sender, instance, **kwargs):
    if settings.DEBUG and getattr(settings, 'ORM_DEBUG', False):
        model_name = sender.__name__
        model_id = getattr(instance, 'pk', None)
        
        if model_id:
            logger.debug(f"Pré-save: Atualizando {model_name} (ID: {model_id})")
        else:
            logger.debug(f"Pré-save: Criando novo {model_name}")

@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    if settings.DEBUG and getattr(settings, 'ORM_DEBUG', False):
        model_name = sender.__name__
        model_id = instance.pk
        
        if created:
            logger.debug(f"Pós-save: Criado {model_name} (ID: {model_id})")
        else:
            logger.debug(f"Pós-save: Atualizado {model_name} (ID: {model_id})")

@receiver(pre_delete)
def log_pre_delete(sender, instance, **kwargs):
    if settings.DEBUG and getattr(settings, 'ORM_DEBUG', False):
        model_name = sender.__name__
        model_id = instance.pk
        logger.debug(f"Pré-delete: Removendo {model_name} (ID: {model_id})")

@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    if settings.DEBUG and getattr(settings, 'ORM_DEBUG', False):
        model_name = sender.__name__
        model_id = getattr(instance, 'pk', '[Não disponível]')
        logger.debug(f"Pós-delete: Removido {model_name} (ID: {model_id})")

# Classes para monitoramento de consultas
class QueryMonitor:
    """
    Classe para monitorar consultas SQL
    """
    def __init__(self, model=None):
        self.model = model
        self.query_count = 0
        self.start_time = 0
        self.end_time = 0
        self.logger = logging.getLogger('observatorio.db')
    
    def __enter__(self):
        self.start_time = time.time()
        self.query_count = len(connection.queries)
        model_name = self.model.__name__ if self.model else "Desconhecido"
        self.logger.debug(f"Iniciando monitoramento de consultas para {model_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        new_query_count = len(connection.queries)
        queries_executed = new_query_count - self.query_count
        elapsed_time = self.end_time - self.start_time
        model_name = self.model.__name__ if self.model else "Desconhecido"
        
        if exc_type:
            self.logger.error(f"Erro durante consultas para {model_name}: {exc_val}")
            return False
        
        if queries_executed > 0:
            self.logger.debug(f"Modelo {model_name}: {queries_executed} consultas em {elapsed_time:.4f}s")
            
            if settings.DEBUG and getattr(settings, 'DETAILED_DB_LOGGING', False):
                for i, query in enumerate(connection.queries[self.query_count:new_query_count]):
                    self.logger.debug(f"Consulta {i+1}: {query.get('sql', '')} - Tempo: {query.get('time', '0')}s")
        
        return True

# Diagnóstico de modelos
def diagnose_model(model_class):
    """
    Diagnóstico completo de um modelo, identificando problemas comuns
    """
    logger.info(f"Iniciando diagnóstico do modelo {model_class.__name__}")
    
    try:
        # Verificar tabela
        table_name = model_class._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            table_exists = bool(cursor.fetchone())
            
            if not table_exists:
                logger.error(f"A tabela '{table_name}' não existe no banco de dados")
                return False
            
            # Verificar colunas
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {col[1] for col in cursor.fetchall()}
            
            for field in model_class._meta.fields:
                if field.column not in columns:
                    logger.error(f"A coluna '{field.column}' não existe na tabela '{table_name}'")
        
        # Verificar constraints
        meta = model_class._meta
        logger.info(f"Modelo {model_class.__name__} tem {len(meta.constraints)} constraints")
        
        # Verificar índices
        logger.info(f"Modelo {model_class.__name__} tem {len(meta.indexes)} índices")
        
        # Verificar relações
        related_models = []
        for field in meta.fields:
            if isinstance(field, models.ForeignKey):
                related_models.append(field.related_model.__name__)
        
        if related_models:
            logger.info(f"Modelo {model_class.__name__} tem relações com: {', '.join(related_models)}")
        
        # Teste de contagem
        try:
            count = model_class.objects.count()
            logger.info(f"Modelo {model_class.__name__} tem {count} registros")
        except Exception as e:
            logger.error(f"Erro ao contar registros de {model_class.__name__}: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro no diagnóstico do modelo {model_class.__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def diagnose_all_models():
    """
    Executa diagnóstico em todos os modelos do projeto
    """
    from django.apps import apps
    
    logger.info("Iniciando diagnóstico de todos os modelos")
    
    models_with_issues = []
    
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.') or app_config.name.startswith('allauth.'):
            continue
            
        for model in app_config.get_models():
            logger.info(f"Verificando modelo: {model.__name__} (app: {app_config.name})")
            if not diagnose_model(model):
                models_with_issues.append(f"{app_config.name}.{model.__name__}")
    
    if models_with_issues:
        logger.error(f"Modelos com problemas: {', '.join(models_with_issues)}")
    else:
        logger.info("Nenhum problema encontrado nos modelos.")
    
    return models_with_issues 