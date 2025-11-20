"""
Pydantic schemas for authentication
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator


# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    center_id: Optional[int] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    center_id: Optional[int] = None


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    roles: List[str] = []


# =============================================================================
# ROLE SCHEMAS
# =============================================================================

class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None


class RoleInDB(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleResponse(RoleInDB):
    permissions: List[str] = []


# =============================================================================
# PERMISSION SCHEMAS
# =============================================================================

class PermissionBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    resource: str = Field(..., min_length=2, max_length=50)
    action: str = Field(..., min_length=2, max_length=50)


class PermissionCreate(PermissionBase):
    pass


class PermissionInDB(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionResponse(PermissionInDB):
    pass


# =============================================================================
# AUTHENTICATION SCHEMAS
# =============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserWithTokenResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# =============================================================================
# USER MANAGEMENT SCHEMAS
# =============================================================================

class UserRoleAssignment(BaseModel):
    user_id: int
    role_ids: List[int]


class RolePermissionAssignment(BaseModel):
    role_id: int
    permission_ids: List[int]


class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]


class RoleListResponse(BaseModel):
    total: int
    roles: List[RoleResponse]


class PermissionListResponse(BaseModel):
    total: int
    permissions: List[PermissionResponse]
