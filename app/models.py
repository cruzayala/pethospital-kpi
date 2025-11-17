"""
Database models for KPI tracking
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class Center(Base):
    """
    Registered veterinary centers
    """
    __tablename__ = "centers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100))
    city = Column(String(100))
    api_key = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Integer, default=1, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_sync_at = Column(DateTime)

    # Relationships
    daily_metrics = relationship("DailyMetric", back_populates="center")
    test_summaries = relationship("TestSummary", back_populates="center")
    species_summaries = relationship("SpeciesSummary", back_populates="center")


class DailyMetric(Base):
    """
    Aggregated daily metrics per center
    """
    __tablename__ = "daily_metrics"
    __table_args__ = (UniqueConstraint("center_id", "date", name="uq_center_date"),)

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    total_orders = Column(Integer, default=0)
    total_results = Column(Integer, default=0)
    total_pets = Column(Integer, default=0)
    total_owners = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    center = relationship("Center", back_populates="daily_metrics")


class TestSummary(Base):
    """
    Test count summary per center per day
    """
    __tablename__ = "test_summaries"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    test_code = Column(String(50), nullable=False)
    test_name = Column(String(255))
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    center = relationship("Center", back_populates="test_summaries")


class SpeciesSummary(Base):
    """
    Species distribution summary per center per day
    """
    __tablename__ = "species_summaries"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    species_name = Column(String(100), nullable=False)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    center = relationship("Center", back_populates="species_summaries")


class BreedSummary(Base):
    """
    Top breeds summary per center per day
    """
    __tablename__ = "breed_summaries"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    breed_name = Column(String(255), nullable=False)
    species_name = Column(String(100))
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
