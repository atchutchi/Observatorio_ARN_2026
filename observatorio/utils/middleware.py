import logging
import time
import traceback
from django.db import connection
from django.conf import settings

logger = logging.getLogger('observatorio.middleware')
db_logger = logging.getLogger('observatorio.db')

class DatabaseLoggingMiddleware:
    """
    Middleware to log all database queries for each request
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before the view
        start_time = time.time()
        initial_queries = len(connection.queries)
        
        # Process the request
        response = self.get_response(request)
        
        # Only log if DEBUG is True (otherwise connection.queries will be empty)
        if settings.DEBUG:
            # Calculate query statistics
            total_time = time.time() - start_time
            num_queries = len(connection.queries) - initial_queries
            
            if num_queries > 0:
                query_time = sum(float(q.get('time', 0)) for q in connection.queries[initial_queries:])
                
                # Log basic query information
                db_logger.debug(f"Request: {request.method} {request.path}")
                db_logger.debug(f"Executed {num_queries} queries in {query_time:.4f}s (total request time: {total_time:.4f}s)")
                
                # Log detailed queries
                if settings.DETAILED_DB_LOGGING:
                    for i, query in enumerate(connection.queries[initial_queries:]):
                        db_logger.debug(f"Query {i+1}: {query.get('sql', '')} - Time: {query.get('time', '0')}s")
        
        return response

class RequestLoggingMiddleware:
    """
    Middleware to log all requests and responses
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('observatorio.requests')

    def __call__(self, request):
        # Get request information
        start_time = time.time()
        request_method = request.method
        request_path = request.path
        
        self.logger.info(f"Request started: {request_method} {request_path}")
        
        # Process the request
        try:
            response = self.get_response(request)
            
            # Log the response
            duration = time.time() - start_time
            status_code = response.status_code
            
            if 200 <= status_code < 400:
                self.logger.info(f"Request finished: {request_method} {request_path} - {status_code} in {duration:.4f}s")
            else:
                self.logger.warning(f"Request error: {request_method} {request_path} - {status_code} in {duration:.4f}s")
                
            return response
            
        except Exception as e:
            # Log exceptions
            duration = time.time() - start_time
            self.logger.error(f"Request exception: {request_method} {request_path} - {str(e)} in {duration:.4f}s")
            self.logger.error(traceback.format_exc())
            raise

class SQLDebugMiddleware:
    """
    Middleware to print all SQL queries to the console (for development only)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only print if DEBUG is True and SQL_DEBUG is enabled
        if settings.DEBUG and getattr(settings, 'SQL_DEBUG', False):
            for i, query in enumerate(connection.queries):
                print(f"\n[SQL Query {i+1}] {query.get('sql', '')}")
                print(f"Time: {query.get('time', '0')}s\n")
                
        return response


class PlatformAuthMiddleware:
    """
    Middleware que força autenticação para toda a plataforma
    Redireciona usuários não autenticados para login
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Páginas que não precisam de autenticação
        self.whitelist = [
            '/accounts/login/',
            '/accounts/signup/',
            '/accounts/password/reset/',
            '/accounts/password/reset/done/',
            '/accounts/password/reset/key/',
            '/accounts/confirm-email/',
            '/admin/',  # Para o Django admin
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        # Verificar se é uma página na whitelist
        if any(request.path.startswith(path) for path in self.whitelist):
            return self.get_response(request)
        
        # Se usuário não está autenticado, redirecionar para login
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            from django.urls import reverse
            return redirect(reverse('account_login'))
            
        return self.get_response(request)