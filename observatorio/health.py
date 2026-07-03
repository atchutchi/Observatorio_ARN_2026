"""
Health check endpoints para monitoramento da aplicação.
"""

from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import sys
import os


def health_check(request):
    """
    Endpoint básico de health check.
    Retorna status 200 se a aplicação está funcionando.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'observatorio-arn',
        'version': '1.0.0'
    })


def health_check_detailed(request):
    """
    Endpoint detalhado de health check.
    Verifica banco de dados, configurações e dependências.
    """
    health_status = {
        'status': 'healthy',
        'service': 'observatorio-arn',
        'version': '1.0.0',
        'checks': {}
    }
    
    # Check 1: Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['checks']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
    
    # Check 2: Python Version
    health_status['checks']['python'] = {
        'status': 'healthy',
        'version': sys.version.split()[0]
    }
    
    # Check 3: Debug Mode
    health_status['checks']['debug_mode'] = {
        'status': 'info',
        'enabled': settings.DEBUG
    }
    
    # Check 4: Static Files
    static_root = settings.STATIC_ROOT
    health_status['checks']['static_files'] = {
        'status': 'healthy' if os.path.exists(static_root) else 'warning',
        'path': static_root,
        'exists': os.path.exists(static_root)
    }
    
    # Check 5: Supabase Configuration
    supabase_configured = bool(
        hasattr(settings, 'SUPABASE_URL') and 
        settings.SUPABASE_URL and 
        hasattr(settings, 'SUPABASE_KEY') and 
        settings.SUPABASE_KEY
    )
    health_status['checks']['supabase'] = {
        'status': 'healthy' if supabase_configured else 'warning',
        'configured': supabase_configured
    }
    
    # Check 6: Hugging Face Configuration
    hf_configured = bool(
        hasattr(settings, 'HUGGINGFACE_TOKEN') and 
        settings.HUGGINGFACE_TOKEN
    )
    health_status['checks']['huggingface'] = {
        'status': 'healthy' if hf_configured else 'warning',
        'configured': hf_configured
    }
    
    # Status HTTP baseado nos checks
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Endpoint de readiness check para Kubernetes/Docker.
    Verifica se a aplicação está pronta para receber tráfego.
    """
    ready = True
    checks = {}
    
    # Verifica banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks['database'] = 'ready'
    except Exception as e:
        ready = False
        checks['database'] = f'not ready: {str(e)}'
    
    # Verifica migrations
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            ready = False
            checks['migrations'] = 'pending migrations'
        else:
            checks['migrations'] = 'up to date'
    except Exception as e:
        checks['migrations'] = f'error: {str(e)}'
    
    status = 'ready' if ready else 'not ready'
    status_code = 200 if ready else 503
    
    return JsonResponse({
        'status': status,
        'checks': checks
    }, status=status_code)


def liveness_check(request):
    """
    Endpoint de liveness check para Kubernetes/Docker.
    Verifica se a aplicação está viva (não travada).
    """
    return JsonResponse({
        'status': 'alive',
        'service': 'observatorio-arn'
    })

