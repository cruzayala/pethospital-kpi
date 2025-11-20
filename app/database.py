"""
Database configuration for KPI service
Uses Railway PostgreSQL in production
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment (Railway provides DATABASE_URL automatically)
DATABASE_URL = os.getenv("DATABASE_URL")

# Railway uses postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fallback to local dev if no DATABASE_URL
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/pethospital_kpi"

# Create engine with connection pool settings optimized for Railway
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using
    pool_size=5,             # Connections in pool
    max_overflow=10,         # Extra connections allowed
    pool_recycle=3600,       # Recycle connections every hour
    echo=False               # Don't log SQL queries
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Dependency for database sessions
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    """
    Base.metadata.create_all(bind=engine)
