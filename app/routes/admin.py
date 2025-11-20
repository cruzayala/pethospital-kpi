"""
Admin routes for user management

Protected routes for system administrators to manage users, roles, and permissions
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from loguru import logger

from ..database import get_db
from ..models import User, Role, Permission
from ..auth import get_current_superuser

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")


@router.get("/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Admin page for user management

    **PROTECTED**: Only superusers can access
    """
    logger.info(f"Admin users page accessed by: {current_user.username}")

    # Get all users
    users = db.execute(select(User)).scalars().all()

    # Get all roles
    roles = db.execute(select(Role)).scalars().all()

    # Get all permissions
    permissions = db.execute(select(Permission)).scalars().all()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "current_user": current_user,
        "users": users,
        "roles": roles,
        "permissions": permissions
    })
