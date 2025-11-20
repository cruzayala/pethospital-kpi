"""
Database models for KPI tracking and authentication
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, JSON, UniqueConstraint, Boolean, Table
from sqlalchemy.orm import relationship
from .database import Base


# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)


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
    api_key = Column(String(100), nullable=False, index=True)  # Removed unique=True for universal master key
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


class PerformanceMetric(Base):
    """
    Performance and efficiency metrics per center per day
    Tracks operational efficiency without storing sensitive data
    """
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Time-based metrics (in hours, aggregated)
    avg_order_processing_time = Column(Integer)  # Average time from order to result (in minutes)
    peak_hour = Column(Integer)  # Hour of day with most activity (0-23)
    peak_hour_orders = Column(Integer)  # Number of orders in peak hour

    # Efficiency metrics
    completion_rate = Column(Integer)  # Percentage of orders completed (0-100)
    same_day_completion = Column(Integer)  # Number of orders completed same day

    # Workload distribution
    morning_orders = Column(Integer, default=0)  # 6am-12pm
    afternoon_orders = Column(Integer, default=0)  # 12pm-6pm
    evening_orders = Column(Integer, default=0)  # 6pm-12am
    night_orders = Column(Integer, default=0)  # 12am-6am

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ModuleMetric(Base):
    """
    Module usage metrics per center per day
    Tracks which system modules are being used (lab, pharmacy, consultation, etc.)
    """
    __tablename__ = "module_metrics"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Module name (laboratorio, consultas, farmacia, vacunacion, hospitalizacion, etc.)
    module_name = Column(String(100), nullable=False, index=True)

    # Usage metrics
    operations_count = Column(Integer, default=0)  # Total operations in this module
    active_users = Column(Integer, default=0)  # Number of different users who used the module

    # Revenue (optional, aggregated)
    total_revenue = Column(Integer)  # Total revenue generated (in cents to avoid decimals)
    avg_transaction = Column(Integer)  # Average transaction value (in cents)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SystemUsageMetric(Base):
    """
    System usage and technical metrics per center per day
    Tracks concurrent users, workstations, and access patterns
    """
    __tablename__ = "system_usage_metrics"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # User metrics (aggregated, no names)
    total_active_users = Column(Integer, default=0)
    peak_concurrent_users = Column(Integer, default=0)
    avg_session_duration = Column(Integer)  # Average session in minutes

    # Access type distribution
    web_access_count = Column(Integer, default=0)
    mobile_access_count = Column(Integer, default=0)
    desktop_access_count = Column(Integer, default=0)

    # Workstation metrics
    total_workstations = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PaymentMethodMetric(Base):
    """
    Payment methods distribution per center per day
    Tracks how customers are paying (cash, card, insurance, etc.)
    """
    __tablename__ = "payment_method_metrics"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    payment_method = Column(String(50), nullable=False)  # efectivo, tarjeta, transferencia, seguro, etc.
    transaction_count = Column(Integer, default=0)
    total_amount = Column(Integer)  # In cents

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# =============================================================================
# AUTHENTICATION MODELS
# =============================================================================

class User(Base):
    """
    User accounts for dashboard access
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

    # Optional center association (users can belong to specific centers)
    center_id = Column(Integer, ForeignKey("centers.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime)

    # Relationships
    center = relationship("Center", foreign_keys=[center_id])
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission"""
        if self.is_superuser:
            return True
        for role in self.roles:
            if any(p.name == permission_name for p in role.permissions):
                return True
        return False

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        if self.is_superuser:
            return True
        return any(r.name == role_name for r in self.roles)


class Role(Base):
    """
    Roles for grouping permissions
    Examples: admin, analyst, viewer, center_manager
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """
    Granular permissions for actions
    Examples: view_dashboard, view_analytics, export_data, manage_users, manage_centers
    """
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255))
    resource = Column(String(50), nullable=False)  # dashboard, analytics, users, centers, kpi
    action = Column(String(50), nullable=False)  # view, create, update, delete, export

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class SystemConfig(Base):
    """
    Global system configuration settings
    Single row table - only one configuration per system
    """
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255))
    company_address = Column(String(500))
    company_phone = Column(String(50))
    company_email = Column(String(255))
    timezone = Column(String(50), default="America/Santo_Domingo")
    language = Column(String(10), default="es")
    theme = Column(String(20), default="light")
    reports_email = Column(String(255))  # Email for automatic report sending

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CompanyLogo(Base):
    """
    Company logos uploaded by centers
    One active logo per center (or global if center_id is null)
    """
    __tablename__ = "company_logos"

    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(Integer, ForeignKey("centers.id", ondelete="CASCADE"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(50), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationship
    center = relationship("Center")


class ReportTemplate(Base):
    """
    Saved report configurations for quick generation
    Users can save their favorite report configurations
    """
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    filters = Column(JSON)  # Saved filter configuration (dates, centers, etc)
    metrics = Column(JSON)  # Selected metrics to include
    format = Column(String(10), default="pdf")  # pdf, csv, excel

    # Owner tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    creator = relationship("User")


class GeneratedReport(Base):
    """
    History of generated reports with metadata
    Stores information about reports generated for audit and redownload
    """
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id", ondelete="SET NULL"), nullable=True)
    report_name = Column(String(255), nullable=False)
    file_path = Column(String(500))  # Path to generated file
    file_size = Column(Integer)  # Size in bytes
    format = Column(String(10))  # pdf, csv, excel
    filters_used = Column(JSON)  # Filters applied when generating

    # Owner tracking
    generated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime)  # Optional: for automatic cleanup of old reports

    # Relationships
    template = relationship("ReportTemplate")
    generator = relationship("User")
