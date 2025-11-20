"""
Configuration Routes
API endpoints for system configuration and logo management
"""
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from loguru import logger

from ..database import get_db
from ..auth import get_current_user, get_current_superuser, PermissionChecker
from ..models import User, SystemConfig, CompanyLogo
from ..modules.config_service import config_service


router = APIRouter(prefix="/api/config", tags=["Configuration"])


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================

class SystemConfigResponse(BaseModel):
    """System configuration response"""
    id: int
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    company_email: Optional[str] = None
    timezone: str
    language: str
    theme: str
    reports_email: Optional[str] = None

    class Config:
        from_attributes = True


class SystemConfigUpdate(BaseModel):
    """System configuration update request"""
    company_name: Optional[str] = Field(None, max_length=255)
    company_address: Optional[str] = Field(None, max_length=500)
    company_phone: Optional[str] = Field(None, max_length=50)
    company_email: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    theme: Optional[str] = Field(None, max_length=20)
    reports_email: Optional[str] = Field(None, max_length=255)


class CompanyLogoResponse(BaseModel):
    """Company logo response"""
    id: int
    center_id: Optional[int] = None
    filename: str
    mime_type: str
    file_size: int
    uploaded_at: str
    is_active: bool

    class Config:
        from_attributes = True


class UploadLogoResponse(BaseModel):
    """Logo upload response"""
    success: bool
    message: str
    logo: CompanyLogoResponse


class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool
    message: str


# =============================================================================
# SYSTEM CONFIGURATION ENDPOINTS
# =============================================================================

@router.get("/system", response_model=SystemConfigResponse)
async def get_system_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current system configuration

    **Authentication**: Required (any authenticated user)
    """
    config = config_service.get_system_config(db)

    if not config:
        # Create default if doesn't exist
        config = config_service.update_system_config(db, {
            "company_name": "PetHospital KPI",
            "timezone": "America/Santo_Domingo",
            "language": "es",
            "theme": "light"
        })

    logger.info(f"System config retrieved by user: {current_user.username}")
    return config


@router.put("/system", response_model=SystemConfigResponse)
async def update_system_configuration(
    config_data: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only superusers can modify
):
    """
    Update system configuration

    **Authentication**: Superuser required
    **Permissions**: Only superusers can modify system configuration
    """
    # Convert Pydantic model to dict, excluding None values
    update_data = {k: v for k, v in config_data.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )

    config = config_service.update_system_config(db, update_data)

    logger.info(f"System config updated by {current_user.username}: {list(update_data.keys())}")
    return config


# =============================================================================
# LOGO MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/logo/upload", response_model=UploadLogoResponse)
async def upload_company_logo(
    file: UploadFile = File(...),
    center_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only superusers
):
    """
    Upload a new company logo

    **Authentication**: Superuser required
    **File Requirements**:
    - Max size: 5MB
    - Allowed formats: PNG, JPG, JPEG, GIF, SVG
    - Images will be automatically resized to max 800x400px

    **Args**:
    - file: Image file to upload
    - center_id: Optional center ID (None for global logo)
    """
    try:
        logo = config_service.upload_logo(db, file, center_id)

        return UploadLogoResponse(
            success=True,
            message="Logo uploaded successfully",
            logo=CompanyLogoResponse(
                id=logo.id,
                center_id=logo.center_id,
                filename=logo.filename,
                mime_type=logo.mime_type,
                file_size=logo.file_size,
                uploaded_at=logo.uploaded_at.isoformat(),
                is_active=logo.is_active
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading logo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading logo: {str(e)}"
        )


@router.get("/logo/active", response_model=Optional[CompanyLogoResponse])
async def get_active_logo(
    center_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the currently active logo

    **Authentication**: Required (any authenticated user)

    **Args**:
    - center_id: Optional center ID (None for global logo)

    **Returns**:
    - Logo metadata or null if no active logo
    """
    logo = config_service.get_active_logo(db, center_id)

    if not logo:
        return None

    return CompanyLogoResponse(
        id=logo.id,
        center_id=logo.center_id,
        filename=logo.filename,
        mime_type=logo.mime_type,
        file_size=logo.file_size,
        uploaded_at=logo.uploaded_at.isoformat(),
        is_active=logo.is_active
    )


@router.get("/logo/file/{logo_id}")
async def get_logo_file(
    logo_id: int,
    db: Session = Depends(get_db)
):
    """
    Get logo file by ID

    **Authentication**: Public (no authentication required for displaying logos)

    Returns the actual image file for display
    """
    logo = db.get(CompanyLogo, logo_id)

    if not logo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logo not found"
        )

    from pathlib import Path
    file_path = Path(logo.file_path)

    if not file_path.exists():
        logger.error(f"Logo file not found: {file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logo file not found on disk"
        )

    return FileResponse(
        path=str(file_path),
        media_type=logo.mime_type,
        filename=logo.filename
    )


@router.get("/logo/all", response_model=list[CompanyLogoResponse])
async def get_all_logos(
    center_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only superusers
):
    """
    Get all logos (active and inactive) for a center

    **Authentication**: Superuser required

    **Args**:
    - center_id: Optional center ID (None for global logos)
    """
    logos = config_service.get_all_logos(db, center_id)

    return [
        CompanyLogoResponse(
            id=logo.id,
            center_id=logo.center_id,
            filename=logo.filename,
            mime_type=logo.mime_type,
            file_size=logo.file_size,
            uploaded_at=logo.uploaded_at.isoformat(),
            is_active=logo.is_active
        )
        for logo in logos
    ]


@router.delete("/logo/{logo_id}", response_model=MessageResponse)
async def delete_logo(
    logo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only superusers
):
    """
    Delete a logo and its file

    **Authentication**: Superuser required
    **Warning**: This action cannot be undone
    """
    success = config_service.delete_logo(db, logo_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logo not found"
        )

    logger.info(f"Logo deleted by {current_user.username}: ID={logo_id}")

    return MessageResponse(
        success=True,
        message="Logo deleted successfully"
    )


# =============================================================================
# HEALTH CHECK
# =============================================================================

@router.get("/health")
async def config_health_check():
    """
    Health check endpoint for configuration module

    **Authentication**: Public
    """
    return {
        "status": "healthy",
        "module": "configuration",
        "upload_dir_exists": config_service.UPLOAD_DIR.exists()
    }
