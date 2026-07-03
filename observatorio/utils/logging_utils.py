import logging
import functools
import time
import traceback
from django.db import connection

logger = logging.getLogger('observatorio')

def log_database_queries(func):
    """
    Decorator to log all database queries executed by a function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        initial_queries = len(connection.queries)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Log queries only if DEBUG is True
            if connection.queries:
                num_queries = len(connection.queries) - initial_queries
                query_time = sum(float(q.get('time', 0)) for q in connection.queries[initial_queries:])
                total_time = time.time() - start_time
                
                logger.debug(f"Function: {func.__name__}")
                logger.debug(f"Executed {num_queries} queries in {query_time:.4f}s (total time: {total_time:.4f}s)")
                
                for i, query in enumerate(connection.queries[initial_queries:]):
                    logger.debug(f"Query {i+1}: {query.get('sql', '')} - Time: {query.get('time', '0')}s")
            
            return result
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    return wrapper

def get_model_logger(model_name):
    """
    Get a logger specifically for a Django model
    """
    return logging.getLogger(f'observatorio.models.{model_name}')

class DatabaseQueryLogger:
    """Context manager for logging database queries in a specific block of code"""
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.logger = logging.getLogger('observatorio.db')
        self.initial_queries = 0
        self.start_time = 0
    
    def __enter__(self):
        self.initial_queries = len(connection.queries)
        self.start_time = time.time()
        self.logger.debug(f"Starting database operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.error(f"Error in database operation {self.operation_name}: {exc_val}")
            return False
        
        num_queries = len(connection.queries) - self.initial_queries
        query_time = sum(float(q.get('time', 0)) for q in connection.queries[self.initial_queries:])
        total_time = time.time() - self.start_time
        
        self.logger.debug(f"Completed {self.operation_name}")
        self.logger.debug(f"Executed {num_queries} queries in {query_time:.4f}s (total time: {total_time:.4f}s)")
        
        if num_queries > 0:
            for i, query in enumerate(connection.queries[self.initial_queries:]):
                self.logger.debug(f"Query {i+1}: {query.get('sql', '')} - Time: {query.get('time', '0')}s")
        
        return True

def log_exception(logger=None):
    """
    Decorator to log exceptions raised by a function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger('observatorio.exceptions')
                
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {str(e)}")
                logger.error(traceback.format_exc())
                raise
        return wrapper
    return decorator 