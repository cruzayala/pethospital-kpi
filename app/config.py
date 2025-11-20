"""
Configuration management for PetHospital KPI Service

Centralizes all environment variables and application settings
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pethospital_kpi")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Application
    APP_TITLE: str = os.getenv("APP_TITLE", "PetHospital KPI Service")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    ENABLE_DOCS: bool = os.getenv("ENABLE_DOCS", "true").lower() in ("true", "1", "yes")

    # Security - CORS
    ALLOWED_ORIGINS_STR: str = os.getenv("ALLOWED_ORIGINS", "*")

    # Dashboard Authentication (Basic Auth for HTML dashboard)
    DASHBOARD_USERNAME: str = os.getenv("DASHBOARD_USERNAME", "admin")
    DASHBOARD_PASSWORD: str = os.getenv("DASHBOARD_PASSWORD", "change-this-secure-password")

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Parse allowed origins from comma-separated string"""
        if self.ALLOWED_ORIGINS_STR == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(",") if origin.strip()]

    # Security - JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Center API Key (for KPI events submission)
    CENTER_API_KEY: str = os.getenv("CENTER_API_KEY", "codex-kpi-master-key-2025")

    # Rate Limiting
    RATE_LIMIT_SUBMIT: str = os.getenv("RATE_LIMIT_SUBMIT", "100/day")
    RATE_LIMIT_EVENTS: str = os.getenv("RATE_LIMIT_EVENTS", "1000/day")
    RATE_LIMIT_DASHBOARD: str = os.getenv("RATE_LIMIT_DASHBOARD", "60/minute")

    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "false").lower() in ("true", "1", "yes")
    CACHE_TTL_DEFAULT: int = int(os.getenv("CACHE_TTL_DEFAULT", "300"))  # 5 minutes

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"

    def validate(self) -> None:
        """Validate critical configuration at startup"""
        errors = []

        # Check database URL
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL is required")

        # Dashboard credentials
        if not self.DASHBOARD_USERNAME:
            errors.append("DASHBOARD_USERNAME is required")
        if not self.DASHBOARD_PASSWORD:
            errors.append("DASHBOARD_PASSWORD is required")

        # Warn about default JWT secret in production
        if self.is_production and self.JWT_SECRET_KEY == "change-this-secret-key-in-production":
            errors.append("JWT_SECRET_KEY must be changed in production")
        if self.is_production and self.DASHBOARD_PASSWORD == "change-this-secure-password":
            errors.append("DASHBOARD_PASSWORD must be changed in production")
        if self.is_production and self.DASHBOARD_USERNAME == "admin":
            errors.append("DASHBOARD_USERNAME should not be 'admin' in production")

        # Warn about open CORS in production
        if self.is_production and "*" in self.ALLOWED_ORIGINS:
            errors.append("ALLOWED_ORIGINS should be restricted in production (not '*')")

        if errors:
            error_msg = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)


# Global settings instance
settings = Settings()
