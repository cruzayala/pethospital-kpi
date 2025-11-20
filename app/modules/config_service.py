"""
Configuration Service
Handles system configuration and logo management
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from loguru import logger

from ..models import SystemConfig, CompanyLogo, Center


class ConfigService:
    """Service for managing system configuration and logos"""

    UPLOAD_DIR = Path("uploads/logos")
    ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    LOGO_MAX_WIDTH = 800
    LOGO_MAX_HEIGHT = 400

    def __init__(self):
        # Ensure upload directory exists
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # =============================================================================
    # SYSTEM CONFIGURATION
    # =============================================================================

    def get_system_config(self, db: Session) -> Optional[SystemConfig]:
        """Get system configuration (single row)"""
        # Use .first() as fallback to handle legacy duplicate rows
        result = db.execute(select(SystemConfig).limit(1)).scalar_one_or_none()
        return result

    def update_system_config(self, db: Session, config_data: Dict[str, Any]) -> SystemConfig:
        """Update or create system configuration"""
        config = self.get_system_config(db)

        if config:
            # Update existing
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            config.updated_at = datetime.utcnow()
        else:
            # Create new
            config = SystemConfig(**config_data)
            db.add(config)

        db.commit()
        db.refresh(config)
        logger.info(f"System config updated: {config_data.keys()}")
        return config

    # =============================================================================
    # LOGO MANAGEMENT
    # =============================================================================

    def validate_logo_file(self, file: UploadFile) -> None:
        """Validate uploaded logo file"""
        # Check extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        # Check file size (read in chunks to avoid memory issues)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {self.MAX_FILE_SIZE / 1024 / 1024}MB"
            )

    def resize_logo_image(self, input_path: Path, output_path: Path) -> None:
        """Resize logo to maximum dimensions while maintaining aspect ratio"""
        try:
            with Image.open(input_path) as img:
                # Convert RGBA to RGB if necessary (for JPEG)
                if img.mode == 'RGBA' and output_path.suffix.lower() in ['.jpg', '.jpeg']:
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = background

                # Calculate new size maintaining aspect ratio
                img.thumbnail((self.LOGO_MAX_WIDTH, self.LOGO_MAX_HEIGHT), Image.Resampling.LANCZOS)

                # Save optimized image
                img.save(output_path, optimize=True, quality=85)
                logger.info(f"Logo resized: {input_path} -> {output_path} ({img.size})")

        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    def upload_logo(
        self,
        db: Session,
        file: UploadFile,
        center_id: Optional[int] = None
    ) -> CompanyLogo:
        """
        Upload and process a new logo

        Args:
            db: Database session
            file: Uploaded file
            center_id: Optional center ID (None for global logo)

        Returns:
            CompanyLogo: Created logo record
        """
        # Validate file
        self.validate_logo_file(file)

        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(file.filename).suffix.lower()
        safe_filename = f"logo_{center_id or 'global'}_{timestamp}{file_ext}"
        file_path = self.UPLOAD_DIR / safe_filename

        # Save uploaded file temporarily
        temp_path = file_path.with_suffix(f"{file_ext}.tmp")
        try:
            # Write file
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Resize and optimize (skip for SVG)
            if file_ext != '.svg':
                self.resize_logo_image(temp_path, file_path)
                temp_path.unlink()  # Remove temp file
            else:
                temp_path.rename(file_path)  # Just rename for SVG

            # Get file size
            file_size = file_path.stat().st_size

            # Deactivate previous logo for this center
            if center_id:
                db.execute(
                    select(CompanyLogo)
                    .where(CompanyLogo.center_id == center_id)
                    .where(CompanyLogo.is_active == True)
                ).scalars().all()

                for old_logo in db.execute(
                    select(CompanyLogo)
                    .where(CompanyLogo.center_id == center_id)
                    .where(CompanyLogo.is_active == True)
                ).scalars():
                    old_logo.is_active = False
            else:
                # Deactivate global logos
                for old_logo in db.execute(
                    select(CompanyLogo)
                    .where(CompanyLogo.center_id == None)
                    .where(CompanyLogo.is_active == True)
                ).scalars():
                    old_logo.is_active = False

            # Create logo record
            logo = CompanyLogo(
                center_id=center_id,
                filename=safe_filename,
                file_path=str(file_path),
                mime_type=file.content_type,
                file_size=file_size,
                is_active=True
            )

            db.add(logo)
            db.commit()
            db.refresh(logo)

            logger.info(f"Logo uploaded: {safe_filename} (center_id={center_id})")
            return logo

        except Exception as e:
            # Cleanup on error
            if temp_path.exists():
                temp_path.unlink()
            if file_path.exists():
                file_path.unlink()

            logger.error(f"Error uploading logo: {e}")
            raise HTTPException(status_code=500, detail=f"Error uploading logo: {str(e)}")

    def get_active_logo(self, db: Session, center_id: Optional[int] = None) -> Optional[CompanyLogo]:
        """
        Get active logo for a center (or global logo)

        Args:
            db: Database session
            center_id: Optional center ID (None for global logo)

        Returns:
            CompanyLogo or None
        """
        query = select(CompanyLogo).where(CompanyLogo.is_active == True)

        if center_id:
            query = query.where(CompanyLogo.center_id == center_id)
        else:
            query = query.where(CompanyLogo.center_id == None)

        return db.execute(query).scalar_one_or_none()

    def delete_logo(self, db: Session, logo_id: int) -> bool:
        """
        Delete a logo and its file

        Args:
            db: Database session
            logo_id: Logo ID to delete

        Returns:
            bool: True if deleted, False if not found
        """
        logo = db.get(CompanyLogo, logo_id)
        if not logo:
            return False

        # Delete file
        file_path = Path(logo.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Logo file deleted: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting logo file: {e}")

        # Delete record
        db.delete(logo)
        db.commit()

        logger.info(f"Logo deleted: ID={logo_id}")
        return True

    def get_all_logos(self, db: Session, center_id: Optional[int] = None) -> list[CompanyLogo]:
        """
        Get all logos (active and inactive) for a center

        Args:
            db: Database session
            center_id: Optional center ID (None for global logos)

        Returns:
            List of CompanyLogo objects
        """
        query = select(CompanyLogo).order_by(CompanyLogo.uploaded_at.desc())

        if center_id is not None:
            query = query.where(CompanyLogo.center_id == center_id)

        return db.execute(query).scalars().all()


# Singleton instance
config_service = ConfigService()
