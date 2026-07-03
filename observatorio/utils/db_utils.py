import logging
import traceback
from django.db import connection, OperationalError, ProgrammingError, IntegrityError
from django.conf import settings
import functools

db_logger = logging.getLogger('observatorio.db')
migration_logger = logging.getLogger('observatorio.migrations')

def log_db_error(error, operation=None, model=None, details=None):
    """
    Log a database error with detailed information
    
    Args:
        error: The exception object
        operation: The database operation being performed (e.g., 'SELECT', 'UPDATE')
        model: The model being accessed
        details: Additional details about the operation
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    # Build a descriptive message
    message_parts = []
    if model:
        message_parts.append(f"Model: {model}")
    if operation:
        message_parts.append(f"Operation: {operation}")
    if details:
        message_parts.append(f"Details: {details}")
    
    message = f"Database Error ({error_type}): {error_message}"
    if message_parts:
        message += f" | {' | '.join(message_parts)}"
    
    # Include traceback for more severe errors
    if isinstance(error, (OperationalError, ProgrammingError)):
        db_logger.error(message)
        db_logger.error(f"Traceback: {traceback.format_exc()}")
    else:
        db_logger.warning(message)
    
    # Log the last executed query if available
    if connection.queries and settings.DEBUG:
        last_query = connection.queries[-1].get('sql', 'No SQL available')
        db_logger.debug(f"Last executed query: {last_query}")

def safe_db_operation(operation_name=None):
    """
    Decorator to safely execute a database operation with logging
    
    Args:
        operation_name: Optional name for the operation
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = operation_name or func.__name__
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Extract model name if available
                model_name = None
                if args and hasattr(args[0], '__class__'):
                    model_name = args[0].__class__.__name__
                
                # Log the error
                log_db_error(
                    error=e,
                    operation=func_name,
                    model=model_name,
                    details=f"Args: {args}, Kwargs: {kwargs}"
                )
                
                # Re-raise for handling by the caller
                raise
        return wrapper
    return decorator

def check_table_exists(table_name):
    """
    Check if a table exists in the database
    
    Args:
        table_name: The name of the table to check
    
    Returns:
        bool: True if the table exists, False otherwise
    """
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'sqlite':
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=%s;",
                    [table_name]
                )
            elif connection.vendor == 'postgresql':
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s);",
                    [table_name]
                )
            elif connection.vendor == 'mysql':
                cursor.execute(
                    "SHOW TABLES LIKE %s;",
                    [table_name]
                )
            else:
                db_logger.warning(f"Unsupported database vendor: {connection.vendor}")
                return False
                
            result = cursor.fetchone()
            exists = bool(result)
            
            if not exists:
                db_logger.warning(f"Table '{table_name}' does not exist in the database")
            else:
                db_logger.debug(f"Table '{table_name}' exists in the database")
                
            return exists
    except Exception as e:
        log_db_error(e, "check_table_exists", details=f"Table: {table_name}")
        return False

def check_column_exists(table_name, column_name):
    """
    Check if a column exists in a table
    
    Args:
        table_name: The name of the table
        column_name: The name of the column
    
    Returns:
        bool: True if the column exists, False otherwise
    """
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'sqlite':
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [column[1] for column in cursor.fetchall()]
                exists = column_name in columns
            elif connection.vendor == 'postgresql':
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name=%s);",
                    [table_name, column_name]
                )
                exists = cursor.fetchone()[0]
            elif connection.vendor == 'mysql':
                cursor.execute(
                    "SHOW COLUMNS FROM %s LIKE %s;",
                    [table_name, column_name]
                )
                exists = bool(cursor.fetchone())
            else:
                db_logger.warning(f"Unsupported database vendor: {connection.vendor}")
                return False
                
            if not exists:
                db_logger.warning(f"Column '{column_name}' does not exist in table '{table_name}'")
            else:
                db_logger.debug(f"Column '{column_name}' exists in table '{table_name}'")
                
            return exists
    except Exception as e:
        log_db_error(e, "check_column_exists", details=f"Table: {table_name}, Column: {column_name}")
        return False

def log_missing_tables_and_columns():
    """
    Scan models and log any missing tables or columns
    """
    from django.apps import apps
    
    for app_config in apps.get_app_configs():
        app_name = app_config.name
        migration_logger.info(f"Checking database integrity for app: {app_name}")
        
        for model in app_config.get_models():
            model_name = model._meta.model_name
            table_name = model._meta.db_table
            
            # Check if table exists
            table_exists = check_table_exists(table_name)
            
            if table_exists:
                # Check columns
                for field in model._meta.fields:
                    column_name = field.column
                    if not check_column_exists(table_name, column_name):
                        migration_logger.error(f"Missing column: {column_name} in table {table_name} (model {model_name})")
            else:
                migration_logger.error(f"Missing table: {table_name} (model {model_name})")
    
    migration_logger.info("Database integrity check completed") 