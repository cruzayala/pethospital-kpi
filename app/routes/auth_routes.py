"""
Authentication endpoints
"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from ..database import get_db
from ..models import User, Role, Permission
from ..schemas_auth import (
    LoginRequest,
    UserCreate,
    UserResponse,
    UserWithTokenResponse,
    TokenResponse,
    TokenRefreshRequest,
    UserListResponse,
    UserChangePassword,
    RoleResponse,
    PermissionResponse
)
from ..auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    get_current_user,
    get_current_superuser,
    decode_token
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=UserWithTokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with username and password

    Returns JWT access token and refresh token
    """
    # Authenticate user
    user = authenticate_user(db, login_data.username, login_data.password)

    if not user:
        logger.warning(f"Failed login attempt for username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    # Get user roles
    role_names = [role.name for role in user.roles]

    logger.info(f"User {user.username} logged in successfully")

    # Manually construct user dict to avoid ORM roles serialization issues
    user_response = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "email_verified": user.email_verified,
        "center_id": user.center_id,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login_at": user.last_login_at,
        "roles": role_names
    }

    return {
        "user": user_response,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Verify user still exists and is active
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        access_token = create_access_token(data={"sub": username})

        logger.info(f"Token refreshed for user: {username}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_data.refresh_token,  # Return same refresh token
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    user_dict = UserResponse.from_orm(current_user).dict(exclude={"roles"})
    user_dict["roles"] = [role.name for role in current_user.roles]
    return user_dict


@router.post("/change-password")
async def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Hash and update new password
    current_user.hashed_password = hash_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()

    logger.info(f"Password changed for user: {current_user.username}")

    return {"message": "Password changed successfully"}


# =============================================================================
# USER MANAGEMENT (Admin only)
# =============================================================================

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Create a new user (superuser only)
    """
    # Check if username or email already exists
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        center_id=user_data.center_id,
        is_active=True,
        is_superuser=False,
        email_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User created: {new_user.username} by {current_user.username}")

    user_dict = UserResponse.from_orm(new_user).dict(exclude={"roles"})
    user_dict["roles"] = [role.name for role in new_user.roles]
    return user_dict


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    List all users (superuser only)
    """
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()

    users_response = []
    for user in users:
        role_names = [role.name for role in user.roles]
        users_response.append({
            **UserResponse.from_orm(user).dict(),
            "roles": role_names
        })

    return {
        "total": total,
        "users": users_response
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (superuser only)
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    role_names = [role.name for role in user.roles]

    return {
        **UserResponse.from_orm(user).dict(),
        "roles": role_names
    }


@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Assign a role to a user (superuser only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role not in user.roles:
        user.roles.append(role)
        db.commit()

    logger.info(f"Role {role.name} assigned to user {user.username} by {current_user.username}")

    return {"message": f"Role {role.name} assigned to user {user.username}"}


@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Remove a role from a user (superuser only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role in user.roles:
        user.roles.remove(role)
        db.commit()

    logger.info(f"Role {role.name} removed from user {user.username} by {current_user.username}")

    return {"message": f"Role {role.name} removed from user {user.username}"}


# =============================================================================
# ROLES AND PERMISSIONS
# =============================================================================

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all roles
    """
    roles = db.query(Role).all()

    roles_response = []
    for role in roles:
        perm_names = [perm.name for perm in role.permissions]
        roles_response.append({
            **RoleResponse.from_orm(role).dict(),
            "permissions": perm_names
        })

    return roles_response


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all permissions
    """
    permissions = db.query(Permission).all()
    return [PermissionResponse.from_orm(perm) for perm in permissions]
