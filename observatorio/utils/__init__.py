# Utils package for the Observatorio project

from .logging_utils import (
    log_database_queries, 
    get_model_logger,
    DatabaseQueryLogger,
    log_exception
)

from .db_utils import (
    log_db_error,
    safe_db_operation,
    check_table_exists,
    check_column_exists,
    log_missing_tables_and_columns
)

# Make middleware available for direct import
from .middleware import (
    DatabaseLoggingMiddleware,
    RequestLoggingMiddleware,
    SQLDebugMiddleware
)

# ORM monitoring utilities
from .orm_monitor import (
    log_model_operation,
    QueryMonitor,
    diagnose_model,
    diagnose_all_models
) 