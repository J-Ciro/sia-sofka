"""Profile endpoints - Refactored to improve error handling."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.services.profesor_service import ProfesorService
from app.services.estudiante_service import EstudianteService
from app.services.user_service import UserService
from app.api.v1.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's profile."""
    return current_user


@router.put("", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's profile.
    
    Args:
        user_data: User update data
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated user
    
    Raises:
        ValidationError: If update fails
        NotFoundError: If user not found after update
    """
    try:
        if current_user.role == UserRole.PROFESOR:
            service = ProfesorService(db, current_user)
            updated_user = await service.update_profile(user_data)
        elif current_user.role == UserRole.ESTUDIANTE:
            estudiante_service = EstudianteService(db, current_user)
            updated_user = await estudiante_service.update_profile(user_data)
        else:
            # Admin can also update their profile
            user_service = UserService(db)
            updated_user = await user_service.update_user(int(current_user.id), user_data)
        
        if not updated_user:
            raise NotFoundError("User", int(current_user.id))
        
        return updated_user
    except ValueError as e:
        raise ValidationError(str(e))

