"""Enrollment endpoints - Refactored to use repository pattern and serializers."""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError, ConflictError, ForbiddenError
from app.core.logging import logger
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse
from app.services.enrollment_service import EnrollmentService
from app.repositories.enrollment_repository import EnrollmentRepository
from app.api.v1.dependencies import require_admin, get_current_active_user
from app.api.v1.serializers.enrollment_serializer import EnrollmentSerializer
from app.models.user import UserRole

router = APIRouter()


@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new enrollment (Admin only)."""
    service = EnrollmentService(db)
    
    try:
        enrollment = await service.create_enrollment(enrollment_data)
        await db.commit()
        await db.refresh(enrollment)
        
        # Load enrollment with relations using repository
        enrollment_repo = EnrollmentRepository(db)
        enrollment_with_relations = await enrollment_repo.get_with_relations(
            enrollment.id,
            relations=['estudiante', 'subject']
        )
        
        if not enrollment_with_relations:
            raise NotFoundError("Enrollment", int(enrollment.id))
        
        # Serialize single enrollment using serializer
        responses = await EnrollmentSerializer.serialize_batch([enrollment_with_relations], db)
        return responses[0] if responses else None  # Helper pattern for single item serialization
    except ValueError as e:
        await db.rollback()
        if "already enrolled" in str(e).lower() or "duplicate" in str(e).lower():
            raise ConflictError(str(e))
        raise ValidationError(str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating enrollment: {str(e)}", exc_info=True)
        raise ValidationError(f"Error creating enrollment: {str(e)}")


@router.get("/me", response_model=List[EnrollmentResponse])
async def get_my_enrollments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obtener las inscripciones del estudiante actual (solo Estudiante). Devuelve enrollments con subject."""
    if current_user.role != UserRole.ESTUDIANTE:
        raise ForbiddenError("Solo los estudiantes pueden consultar sus inscripciones")
    enrollment_repo = EnrollmentRepository(db)
    enrollments = await enrollment_repo.get_many_with_relations(
        estudiante_id=current_user.id,
        relations=['estudiante', 'subject'],
        limit=500,
    )
    return await EnrollmentSerializer.serialize_batch(enrollments, db)


@router.get("", response_model=List[EnrollmentResponse])
async def get_enrollments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all enrollments (Admin only)."""
    # Use repository to load enrollments with relations
    enrollment_repo = EnrollmentRepository(db)
    enrollments = await enrollment_repo.get_many_with_relations(
        relations=['estudiante', 'subject'],
        skip=skip,
        limit=limit
    )
    
    # Serialize enrollments using serializer
    return await EnrollmentSerializer.serialize_batch(enrollments, db)


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get enrollment by ID (Admin only)."""
    # Use repository to load enrollment with relations
    enrollment_repo = EnrollmentRepository(db)
    enrollment = await enrollment_repo.get_with_relations(
        enrollment_id,
        relations=['estudiante', 'subject']
    )
    
    if not enrollment:
        raise NotFoundError("Enrollment", enrollment_id)
    
    # Serialize single enrollment using serializer
    responses = await EnrollmentSerializer.serialize_batch([enrollment], db)
    return responses[0] if responses else None  # Helper pattern for single item serialization


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete enrollment (Admin only)."""
    service = EnrollmentService(db)
    deleted = await service.delete_enrollment(enrollment_id)
    
    if not deleted:
        raise NotFoundError("Enrollment", enrollment_id)

