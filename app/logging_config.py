"""Centralized logging configuration for the backend."""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from app.config import settings


def setup_logging():
    """
    Configure centralized logging for the application.
    
    Logs are written to:
    - Console (stdout) for immediate visibility
    - File (logs/app.log) for persistent storage
    - Error file (logs/errors.log) for errors only
    
    Log format includes timestamp, level, module, and message.
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Log file paths
    app_log_file = os.path.join(log_dir, 'app.log')
    error_log_file = os.path.join(log_dir, 'errors.log')
    
    # Define log format
    log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs (rotating, max 10MB, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (rotating, errors only)
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    # Reduce noise from third-party libraries
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"Application logging initialized")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log directory: {log_dir}")
    logger.info(f"App log file: {app_log_file}")
    logger.info(f"Error log file: {error_log_file}")
    logger.info("=" * 60)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__ from the calling module)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


# Custom exception logger
class ExceptionLogger:
    """Helper class for logging exceptions with full traceback."""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def log_exception(self, exc: Exception, context: str = None):
        """
        Log an exception with full traceback.
        
        Args:
            exc: The exception to log
            context: Additional context about where/why the exception occurred
        """
        import traceback
        
        error_msg = f"Exception occurred"
        if context:
            error_msg += f" in {context}"
        error_msg += f": {type(exc).__name__}: {str(exc)}"
        
        self.logger.error(error_msg)
        self.logger.error(f"Traceback:\n{traceback.format_exc()}")
    
    def log_request_error(self, request_path: str, method: str, exc: Exception, 
                          user_id: str = None, extra_data: dict = None):
        """
        Log a request-related error with context.
        
        Args:
            request_path: The API path that caused the error
            method: HTTP method (GET, POST, etc.)
            exc: The exception that occurred
            user_id: User ID if available
            extra_data: Additional data to include in the log
        """
        import traceback
        
        error_details = {
            "path": request_path,
            "method": method,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "user_id": user_id
        }
        
        if extra_data:
            error_details.update(extra_data)
        
        self.logger.error(f"Request error: {error_details}")
        self.logger.error(f"Traceback:\n{traceback.format_exc()}")


# Email notification for critical errors (optional)
def notify_critical_error(error_msg: str, error_details: dict = None):
    """
    Send notification for critical errors (optional integration).
    
    This is a placeholder for integrating with notification services
    like email, Slack, or PagerDuty for critical error alerts.
    
    Args:
        error_msg: Error message
        error_details: Additional error details
    """
    logger = logging.getLogger(__name__)
    logger.critical(f"CRITICAL ERROR: {error_msg}")
    if error_details:
        logger.critical(f"Error details: {error_details}")
    
    # TODO: Integrate with notification service (email, Slack, etc.)
    # Example:
    # - Send email to admin
    # - Post to Slack channel
    # - Trigger PagerDuty alert
