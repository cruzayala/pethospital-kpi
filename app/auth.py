"""
Authentication and security utilities

Provides basic authentication for dashboard and API key validation
"""
import secrets
from typing import Optional
from fastapi import HTTPException, Header, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .config import settings

# HTTP Basic Auth for dashboard
security = HTTPBasic()


def verify_dashboard_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """
    Verify dashboard username and password using HTTP Basic Auth

    Args:
        credentials: HTTP Basic credentials from request

    Returns:
        True if credentials are valid

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Use constant-time comparison to prevent timing attacks
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        settings.DASHBOARD_USERNAME.encode("utf-8")
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        settings.DASHBOARD_PASSWORD.encode("utf-8")
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True


def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """
    Verify API key from request header

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: 401 if API key is missing or invalid format
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Basic validation (length, format)
    if len(x_api_key) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
        )

    return x_api_key


def get_api_key_from_header_or_body(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    body_api_key: Optional[str] = None
) -> str:
    """
    Get API key from header (preferred) or body (deprecated)

    This function supports backward compatibility by accepting API key
    from either header or request body.

    Args:
        x_api_key: API key from X-API-Key header
        body_api_key: API key from request body (deprecated)

    Returns:
        The API key

    Raises:
        HTTPException: 401 if no API key is provided
    """
    # Prefer header
    if x_api_key:
        return x_api_key

    # Fallback to body (with deprecation warning logged)
    if body_api_key:
        from loguru import logger
        logger.warning(
            "API key provided in request body is deprecated. "
            "Please use X-API-Key header instead."
        )
        return body_api_key

    # No API key provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key required. Provide via X-API-Key header or request body.",
        headers={"WWW-Authenticate": "ApiKey"},
    )


# =============================================================================
# JWT AUTHENTICATION (USER/PASSWORD)
# =============================================================================

from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token scheme
jwt_security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Dictionary containing claims (usually {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token (longer expiration)

    Args:
        data: Dictionary containing claims

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and verify JWT token

    Args:
        token: JWT token string

    Returns:
        Dictionary with token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise credentials_exception


async def get_current_user(
    credentials = Depends(jwt_security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    Dependency for FastAPI routes that require authentication
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (convenience dependency)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require superuser permissions"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Superuser required."
        )
    return current_user


class PermissionChecker:
    """
    Dependency class for checking user permissions

    Usage:
        @router.get("/endpoint", dependencies=[Depends(PermissionChecker("view_analytics"))])
    """

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_permission(self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.required_permission}"
            )
        return current_user


class RoleChecker:
    """
    Dependency class for checking user roles

    Usage:
        @router.get("/endpoint", dependencies=[Depends(RoleChecker("admin"))])
    """

    def __init__(self, required_role: str):
        self.required_role = required_role

    async def __call__(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_role(self.required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required role: {self.required_role}"
            )
        return current_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username and password

    Returns:
        User object if authentication successful, None otherwise
    """
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return user
