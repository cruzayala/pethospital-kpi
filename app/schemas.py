"""
Pydantic schemas for API validation
"""
from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


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
    """
    center_code: str = Field(..., description="Unique center code")
    api_key: str = Field(..., description="API key for authentication")
    date: date = Field(..., description="Date of metrics")
    total_orders: int = Field(default=0, ge=0)
    total_results: int = Field(default=0, ge=0)
    total_pets: int = Field(default=0, ge=0)
    total_owners: int = Field(default=0, ge=0)
    tests: List[TestCount] = Field(default_factory=list)
    species: List[SpeciesCount] = Field(default_factory=list)
    breeds: List[BreedCount] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "center_code": "HVC",
                "api_key": "your-api-key-here",
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
    )


class CenterResponse(BaseModel):
    """Center information response"""
    id: int
    code: str
    name: str
    country: Optional[str] = None
    city: Optional[str] = None
    is_active: bool
    registered_at: datetime
    last_sync_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_centers: int
    active_centers: int
    date_range: Dict[str, str]
    total_orders: int
    total_results: int
    total_pets: int
    centers: List[CenterResponse]
