"""
Logging configuration using Loguru

Provides structured logging with rotation, JSON formatting for production,
and integration with FastAPI request context.
"""
import sys
from loguru import logger
from .config import settings


def setup_logging():
    """
    Configure loguru logger with appropriate settings for the environment
    """
    # Remove default handler
    logger.remove()

    # Console logging format
    if settings.is_production:
        # JSON format for production (better for log aggregation)
        log_format = (
            "{"
            '"timestamp": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
            '"level": "{level}", '
            '"module": "{module}", '
            '"function": "{function}", '
            '"line": {line}, '
            '"message": "{message}"'
            "}"
        )
    else:
        # Human-readable format for development
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=not settings.is_production,
        serialize=settings.is_production,  # JSON output in production
    )

    # Add file logging with rotation
    logger.add(
        "logs/kpi-service_{time:YYYY-MM-DD}.log",
        format=log_format,
        level=settings.LOG_LEVEL,
        rotation="00:00",  # Rotate daily at midnight
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress old logs
        serialize=settings.is_production,
        encoding="utf-8",
    )

    # Add error-only file
    logger.add(
        "logs/errors_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="ERROR",
        rotation="00:00",
        retention="90 days",  # Keep error logs longer
        compression="zip",
        serialize=True,  # Always JSON for errors
        encoding="utf-8",
    )

    logger.info(
        f"Logging initialized - Level: {settings.LOG_LEVEL}, Environment: {settings.ENVIRONMENT}"
    )

    return logger


def log_request(request, response_status: int = None):
    """
    Log HTTP request details

    Args:
        request: FastAPI request object
        response_status: HTTP response status code
    """
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }

    if response_status:
        log_data["status"] = response_status

    if response_status and response_status >= 400:
        logger.warning(f"Request completed with error: {log_data}")
    else:
        logger.info(f"Request completed: {log_data}")


def log_database_operation(operation: str, table: str, details: dict = None):
    """
    Log database operation

    Args:
        operation: Type of operation (INSERT, UPDATE, DELETE, SELECT)
        table: Table name
        details: Additional details about the operation
    """
    log_data = {
        "operation": operation,
        "table": table,
    }

    if details:
        log_data.update(details)

    logger.debug(f"Database operation: {log_data}")


# Initialize logging on module import
setup_logging()
