"""
Pydantic schemas for API validation
"""
from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TestCount(BaseModel):
    """Test code and count"""
    code: str
    name: Optional[str] = None
    count: int


class SpeciesCount(BaseModel):
    """Species name and count"""
    species: str
    count: int


class BreedCount(BaseModel):
    """Breed name and count"""
    breed: str
    species: Optional[str] = None
    count: int


class MetricsSubmission(BaseModel):
    """
    Daily metrics submission from a center

    API key should be provided via X-API-Key header (recommended)
    or in request body (deprecated, for backward compatibility)
    """
    center_code: str
    api_key: Optional[str] = None  # Deprecated: use X-API-Key header instead
    date: date
    total_orders: int = 0
    total_results: int = 0
    total_pets: int = 0
    total_owners: int = 0
    tests: List[TestCount] = []
    species: List[SpeciesCount] = []
    breeds: List[BreedCount] = []

    class Config:
        schema_extra = {
            "example": {
                "center_code": "HVC",
                "date": "2025-11-13",
                "total_orders": 50,
                "total_results": 45,
                "total_pets": 30,
                "total_owners": 25,
                "tests": [
                    {"code": "GLU", "name": "Glucosa", "count": 15},
                    {"code": "BUN", "name": "Nitrogeno Ureico", "count": 12}
                ],
                "species": [
                    {"species": "Canino", "count": 20},
                    {"species": "Felino", "count": 10}
                ],
                "breeds": [
                    {"breed": "Labrador", "species": "Canino", "count": 8},
                    {"breed": "Chihuahua", "species": "Canino", "count": 6}
                ]
            }
        }


class CenterResponse(BaseModel):
    """Center information response"""
    id: int
    code: str
    name: str
    country: Optional[str] = None
    city: Optional[str] = None
    is_active: int  # Database uses Integer (0/1) not Boolean
    registered_at: datetime
    last_sync_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class DailyMetricResponse(BaseModel):
    """Daily metrics response"""
    id: int
    center_id: int
    date: date
    total_orders: int
    total_results: int
    total_pets: int
    total_owners: int
    created_at: datetime

    class Config:
        orm_mode = True


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_centers: int
    active_centers: int
    date_range: Dict[str, str]
    total_orders: int
    total_results: int
    total_pets: int
    centers: List[CenterResponse]


class EventData(BaseModel):
    """Data payload for real-time events"""
    order_id: Optional[int] = None
    result_id: Optional[int] = None
    pet_id: Optional[int] = None
    owner_id: Optional[int] = None
    tests: Optional[List[str]] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    test_count: Optional[int] = None


class EventSubmission(BaseModel):
    """
    Real-time event submission from a center

    API key should be provided via X-API-Key header (recommended)
    or in request body (deprecated, for backward compatibility)
    """
    center_code: str
    api_key: Optional[str] = None  # Deprecated: use X-API-Key header instead
    event_type: str  # order_created, result_created, pet_created, owner_created
    timestamp: datetime
    data: EventData

    class Config:
        schema_extra = {
            "example": {
                "center_code": "HVC",
                "event_type": "order_created",
                "timestamp": "2025-11-17T14:30:45Z",
                "data": {
                    "order_id": 123,
                    "pet_id": 45,
                    "tests": ["GLU", "BUN", "ALT"],
                    "species": "Canino",
                    "breed": "Labrador",
                    "test_count": 3
                }
            }
        }


class CenterMetadataUpdate(BaseModel):
    """
    Center metadata update from main pethospital system

    Sent when center details change in the main system.
    Updates center name, location, and active status in KPI service.
    """
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Hospital Veterinario Central",
                "city": "Santo Domingo",
                "country": "Republica Dominicana",
                "is_active": True
            }
        }


# ============================================================================
# ENHANCED METRICS SCHEMAS (v2.1)
# ============================================================================

class PerformanceMetricData(BaseModel):
    """Performance and efficiency metrics"""
    avg_order_processing_time: Optional[int] = None  # in minutes
    peak_hour: Optional[int] = None  # 0-23
    peak_hour_orders: Optional[int] = None
    completion_rate: Optional[int] = None  # 0-100
    same_day_completion: Optional[int] = None
    morning_orders: int = 0
    afternoon_orders: int = 0
    evening_orders: int = 0
    night_orders: int = 0


class ModuleMetricData(BaseModel):
    """Module usage metric"""
    module_name: str  # laboratorio, consultas, farmacia, etc.
    operations_count: int = 0
    active_users: int = 0
    total_revenue: Optional[int] = None  # in cents
    avg_transaction: Optional[int] = None  # in cents


class SystemUsageMetricData(BaseModel):
    """System usage and access metrics"""
    total_active_users: int = 0
    peak_concurrent_users: int = 0
    avg_session_duration: Optional[int] = None  # in minutes
    web_access_count: int = 0
    mobile_access_count: int = 0
    desktop_access_count: int = 0
    total_workstations: int = 0


class PaymentMethodData(BaseModel):
    """Payment method distribution"""
    payment_method: str  # efectivo, tarjeta, transferencia, seguro
    transaction_count: int = 0
    total_amount: Optional[int] = None  # in cents


class EnhancedMetricsSubmission(BaseModel):
    """
    Enhanced daily metrics submission from a center (v2.1)

    Includes all original metrics plus performance, module usage,
    system usage, and payment method data
    """
    # Original metrics (backward compatible)
    center_code: str
    api_key: Optional[str] = None
    date: date
    total_orders: int = 0
    total_results: int = 0
    total_pets: int = 0
    total_owners: int = 0
    tests: List[TestCount] = []
    species: List[SpeciesCount] = []
    breeds: List[BreedCount] = []

    # Enhanced metrics (v2.1)
    performance: Optional[PerformanceMetricData] = None
    modules: List[ModuleMetricData] = []
    system_usage: Optional[SystemUsageMetricData] = None
    payment_methods: List[PaymentMethodData] = []

    class Config:
        schema_extra = {
            "example": {
                "center_code": "HVC",
                "date": "2025-11-19",
                "total_orders": 50,
                "total_results": 45,
                "total_pets": 30,
                "total_owners": 25,
                "tests": [
                    {"code": "GLU", "name": "Glucosa", "count": 15}
                ],
                "species": [
                    {"species": "Canino", "count": 20}
                ],
                "breeds": [
                    {"breed": "Labrador", "species": "Canino", "count": 8}
                ],
                "performance": {
                    "avg_order_processing_time": 120,
                    "peak_hour": 14,
                    "peak_hour_orders": 12,
                    "completion_rate": 90,
                    "same_day_completion": 40,
                    "morning_orders": 15,
                    "afternoon_orders": 25,
                    "evening_orders": 8,
                    "night_orders": 2
                },
                "modules": [
                    {
                        "module_name": "laboratorio",
                        "operations_count": 50,
                        "active_users": 3,
                        "total_revenue": 15000,
                        "avg_transaction": 300
                    },
                    {
                        "module_name": "consultas",
                        "operations_count": 30,
                        "active_users": 2
                    }
                ],
                "system_usage": {
                    "total_active_users": 5,
                    "peak_concurrent_users": 3,
                    "avg_session_duration": 180,
                    "web_access_count": 100,
                    "mobile_access_count": 20,
                    "desktop_access_count": 50,
                    "total_workstations": 4
                },
                "payment_methods": [
                    {"payment_method": "efectivo", "transaction_count": 20, "total_amount": 8000},
                    {"payment_method": "tarjeta", "transaction_count": 10, "total_amount": 7000}
                ]
            }
        }
