"""
PetHospital KPI Service - Main Application

This service collects and displays KPI metrics from multiple
veterinary centers running Codex Veterinaria.

Version 2.0.0 - Production-Ready
- Enhanced security (CORS, Rate Limiting, Authentication)
- Structured logging
- Error monitoring with Sentry
- Improved health checks
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from .config import settings
from .database import init_db
from .routes import kpi, dashboard, analytics, auth_routes, admin, config
from .exceptions import register_exception_handlers
from .logging_config import setup_logging
from .modules.cache_service import init_cache_service


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events

    Startup:
    - Validate configuration
    - Initialize database
    - Setup logging
    - Initialize Sentry (if configured)

    Shutdown:
    - Cleanup resources
    """
    # Startup
    logger.info(f"Starting {settings.APP_TITLE} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    try:
        # Validate configuration
        settings.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        # Continue startup but log the errors
        logger.warning("Starting with configuration warnings")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    # Initialize cache service
    try:
        cache = init_cache_service(
            redis_url=settings.REDIS_URL,
            enabled=settings.CACHE_ENABLED
        )
        if cache.enabled:
            logger.info(f"Cache service initialized: {settings.REDIS_URL}")
        else:
            logger.info("Cache service disabled (will work without caching)")
    except Exception as e:
        logger.warning(f"Cache initialization warning: {e}")
        logger.info("Continuing without cache")

    # Initialize Sentry for error tracking
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                traces_sample_rate=0.1 if settings.is_production else 1.0,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                ],
                send_default_pii=False,  # Don't send personally identifiable information
            )
            logger.info("Sentry error tracking initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Sentry: {e}")

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_TITLE,
    description="Centralized KPI tracking for Codex Veterinaria installations - Production Ready v2.0",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration (restrictive by default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Register exception handlers
register_exception_handlers(app)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    logger.info(f"{request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")

    try:
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} - Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"{request.method} {request.url.path} - Error: {e}")
        raise


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount uploads directory for logos (must be before routers to avoid conflicts)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth_routes.router)  # Authentication endpoints
app.include_router(kpi.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(admin.router)  # Admin endpoints (user management)
app.include_router(config.router)  # Configuration endpoints (system config & logos)


@app.get("/health")
@limiter.limit("60/minute")
def health_check(request: Request):
    """
    Basic health check endpoint (liveness probe)

    Returns OK if service is running
    """
    return {
        "status": "ok",
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health/ready")
@limiter.limit("60/minute")
def readiness_check(request: Request):
    """
    Readiness check endpoint

    Checks if service is ready to accept requests (database connection, etc.)
    """
    from .database import get_db
    from sqlalchemy import text

    try:
        # Try to query database
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()

        return {
            "status": "ready",
            "service": settings.APP_TITLE,
            "version": settings.APP_VERSION,
            "checks": {
                "database": "ok"
            }
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "service": settings.APP_TITLE,
            "checks": {
                "database": "error"
            }
        }


@app.get("/api/docs-info")
def api_docs_info():
    """API documentation information"""
    docs_info = {
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "submit_metrics": "POST /kpi/submit",
            "submit_events": "POST /kpi/events",
            "list_centers": "GET /kpi/centers",
            "get_metrics": "GET /kpi/centers/{code}/metrics",
            "summary_stats": "GET /kpi/stats/summary",
            "dashboard": "GET /",
            "health": "GET /health",
            "readiness": "GET /health/ready"
        }
    }

    if settings.ENABLE_DOCS:
        docs_info.update({
            "openapi_url": "/openapi.json",
            "docs_url": "/docs",
            "redoc_url": "/redoc",
        })

    return docs_info
