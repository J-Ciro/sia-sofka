"""Authentication endpoints - Refactored to use services."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.api.v1.dependencies import (
    get_current_active_user,
    require_admin,
)

router = APIRouter()


@router.post("/login", response_model=Token)
@rate_limit("10/minute")  # Rate limiting opcional (solo si ENABLE_RATE_LIMITING=true)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login endpoint.
    
    Args:
        form_data: OAuth2 password request form (username=email, password)
        db: Database session
    
    Returns:
        Access token
    
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email using service (username in OAuth2 form)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Register a new user (Admin only).
    
    Args:
        user_data: User creation data
        db: Database session
        current_user: Current admin user (from dependency)
    
    Returns:
        Created user
    
    Raises:
        ConflictError: If email already exists
        ValidationError: If user data is invalid
    """
    user_service = UserService(db)
    
    try:
        # Create user using service (handles code generation, age calculation, and duplicate check)
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        # UserService.create_user raises ValueError for duplicate email
        if "already registered" in str(e).lower() or "email" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user information.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user data
    """
    return current_user


