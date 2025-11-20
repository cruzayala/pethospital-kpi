"""
Global exception handlers for FastAPI

Provides consistent error responses following RFC 7807 Problem Details standard
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from loguru import logger
from .config import settings


def register_exception_handlers(app: FastAPI):
    """
    Register all exception handlers with the FastAPI app

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle Pydantic validation errors

        Returns a structured error response with details about validation failures
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": list(error["loc"]),
                "msg": error["msg"],
                "type": error["type"],
            })

        logger.warning(
            f"Validation error on {request.method} {request.url.path}: {errors}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "type": "validation_error",
                "title": "Validation Error",
                "status": 422,
                "detail": "Request validation failed",
                "errors": errors,
                "instance": str(request.url),
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """
        Handle database integrity errors (unique constraints, foreign keys, etc.)
        """
        logger.error(
            f"Database integrity error on {request.method} {request.url.path}: {exc}"
        )

        # Don't expose internal database details in production
        detail = "Database integrity constraint violated"
        if settings.is_development:
            detail = f"Database error: {str(exc.orig)}"

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "type": "integrity_error",
                "title": "Database Integrity Error",
                "status": 409,
                "detail": detail,
                "instance": str(request.url),
            },
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, exc: OperationalError):
        """
        Handle database operational errors (connection issues, etc.)
        """
        logger.error(
            f"Database operational error on {request.method} {request.url.path}: {exc}"
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "type": "database_error",
                "title": "Database Connection Error",
                "status": 503,
                "detail": "Unable to connect to database. Please try again later.",
                "instance": str(request.url),
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """
        Handle generic SQLAlchemy errors
        """
        logger.error(
            f"Database error on {request.method} {request.url.path}: {exc}"
        )

        detail = "A database error occurred"
        if settings.is_development:
            detail = f"Database error: {str(exc)}"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "database_error",
                "title": "Database Error",
                "status": 500,
                "detail": detail,
                "instance": str(request.url),
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """
        Handle ValueError exceptions (invalid data)
        """
        logger.warning(
            f"Value error on {request.method} {request.url.path}: {exc}"
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "type": "value_error",
                "title": "Invalid Value",
                "status": 400,
                "detail": str(exc),
                "instance": str(request.url),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Catch-all handler for unexpected exceptions

        Logs the error and returns a generic error response
        """
        logger.exception(
            f"Unhandled exception on {request.method} {request.url.path}: {exc}"
        )

        # Don't expose internal error details in production
        detail = "An unexpected error occurred"
        if settings.is_development:
            detail = f"Error: {str(exc)}"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "internal_error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": detail,
                "instance": str(request.url),
            },
        )

    logger.info("Exception handlers registered")
