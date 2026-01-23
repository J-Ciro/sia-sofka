"""API v1 dependencies."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.schemas.token import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get the current authenticated user.
    
    Args:
        token: JWT token from request
        db: Database session
    
    Returns:
        Current user
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        email_raw = payload.get("sub")
        if email_raw is None or not isinstance(email_raw, str):
            raise credentials_exception
        email: str = email_raw
        token_data = TokenData(email=email, role=payload.get("role"))
    except Exception:
        raise credentials_exception
    
    stmt = select(User).where(User.email == token_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to get the current active user.
    
    Args:
        current_user: Current user from get_current_user
    
    Returns:
        Current active user
    """
    # For now, all users are considered active
    # Can add is_active field to User model if needed
    return current_user


def require_role(allowed_roles: list[UserRole]):
    """Dependency factory to require specific roles.
    
    Args:
        allowed_roles: List of allowed roles
    
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user
    
    return role_checker


# Convenience dependencies for each role
require_admin = require_role([UserRole.ADMIN])
require_profesor = require_role([UserRole.PROFESOR])
require_estudiante = require_role([UserRole.ESTUDIANTE])
require_admin_or_profesor = require_role([UserRole.ADMIN, UserRole.PROFESOR])
