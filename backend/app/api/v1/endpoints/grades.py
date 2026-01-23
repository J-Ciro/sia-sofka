"""Grade endpoints - Refactored to use repository pattern and serializers."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse
from app.services.grade_service import GradeService
from app.services.profesor_service import ProfesorService
from app.services.estudiante_service import EstudianteService
from app.repositories.grade_repository import GradeRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.api.v1.dependencies import (
    get_current_active_user,
    require_admin_or_profesor,
)
from app.api.v1.serializers.grade_serializer import GradeSerializer
from app.api.v1.validators.grade_validator import GradeValidator

router = APIRouter()


# ==================== Endpoints ====================


@router.post("", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
async def create_grade(
    grade_data: GradeCreate,
    subject_id: int = Query(..., description="Subject ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Create a new grade (Profesor or Admin only).
    
    Profesores can only create grades for their assigned subjects.
    """
    try:
        if current_user.role == UserRole.PROFESOR:
            profesor_service = ProfesorService(db, current_user)
            grade = await profesor_service.create_grade(grade_data, subject_id)
        else:
            # Admin can create grades for any subject
            service = GradeService(db)
            grade = await service.create_grade(grade_data)
        
        # Load grade with enrollment using repository
        grade_repo = GradeRepository(db)
        grade_with_enrollment = await grade_repo.get_with_relations(grade.id)
        
        if not grade_with_enrollment:
            raise NotFoundError("Grade", int(grade.id))
        
        # Serialize single grade using serializer
        responses = await GradeSerializer.serialize_batch([grade_with_enrollment], db)
        return responses[0] if responses else None
    except ValueError as e:
        if current_user.role == UserRole.PROFESOR:
            raise ForbiddenError(str(e))
        else:
            raise NotFoundError("Grade", str(e))


async def _get_grades_with_filters(
    db: AsyncSession,
    current_user: Optional[User] = None,
    subject_id: Optional[int] = None,
    enrollment_id: Optional[int] = None,
    is_estudiante: bool = False,
    is_profesor: bool = False,
) -> List[GradeResponse]:
    """Get grades with filters based on user role.
    
    Args:
        db: Database session
        current_user: Current user (required for estudiante/profesor)
        subject_id: Optional subject ID filter
        enrollment_id: Optional enrollment ID filter
        is_estudiante: If True, get grades for estudiante
        is_profesor: If True, verify profesor permissions
    
    Returns:
        List of grade responses
    """
    grade_repo = GradeRepository(db)
    
    if is_estudiante and current_user:
        # Estudiante: get grades through service first
        estudiante_service = EstudianteService(db, current_user)
        if subject_id is None:
            raise HTTPException(status_code=400, detail="subject_id is required")
        grades = await estudiante_service.get_grades_by_subject(subject_id)
        grade_ids = [int(grade.id) for grade in grades]
        grades_with_enrollment = await grade_repo.get_many_with_relations(
            grade_ids=grade_ids,
            relations=['enrollment']
        )
        return await GradeSerializer.serialize_batch(grades_with_enrollment, db)
    
    if is_profesor and current_user:
        # Profesor: verify access first
        if subject_id is None:
            raise HTTPException(status_code=400, detail="subject_id is required")
        await GradeValidator.verify_profesor_can_access_subject(db, current_user, subject_id)
    
    # Admin or Profesor: use repository directly
    grades = await grade_repo.get_many_with_relations(
        enrollment_id=enrollment_id,
        subject_id=subject_id,
        relations=['enrollment']
    )
    return await GradeSerializer.serialize_batch(grades, db)


@router.get("", response_model=List[GradeResponse])
async def get_grades(
    subject_id: int = Query(None, description="Filter by subject ID"),
    enrollment_id: int = Query(None, description="Filter by enrollment ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get grades.
    
    - Estudiante: can only see their own grades
    - Profesor: can see grades for their assigned subjects
    - Admin: can see all grades
    """
    if current_user.role == UserRole.ESTUDIANTE:
        if not subject_id:
            raise ForbiddenError("Subject ID is required for estudiantes")
        try:
            return await _get_grades_with_filters(
                db, current_user, subject_id, enrollment_id, is_estudiante=True
            )
        except ValueError as e:
            raise ForbiddenError(str(e))
    
    elif current_user.role == UserRole.PROFESOR:
        if not subject_id:
            raise ForbiddenError("Subject ID is required for profesores")
        return await _get_grades_with_filters(
            db, current_user, subject_id, enrollment_id, is_profesor=True
        )
    
    else:  # Admin
        return await _get_grades_with_filters(db, None, subject_id, enrollment_id)


@router.get("/{grade_id}", response_model=GradeResponse)
async def get_grade(
    grade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get grade by ID."""
    grade_repo = GradeRepository(db)
    grade = await grade_repo.get_with_relations(grade_id)
    
    if not grade:
        raise NotFoundError("Grade", grade_id)
    
    # Verify permissions
    if current_user.role == UserRole.ESTUDIANTE:
        enrollment_repo = EnrollmentRepository(db)
        enrollment = await enrollment_repo.get_by_id(grade.enrollment_id)
        if enrollment and enrollment.estudiante_id != current_user.id:
            raise ForbiddenError("Cannot access other student's grades")
    
    # Serialize single grade using serializer
    responses = await GradeSerializer.serialize_batch([grade], db)
    return responses[0] if responses else None


@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Update grade (Profesor or Admin only)."""
    grade_repo = GradeRepository(db)
    
    # Get existing grade to verify permissions
    existing_grade = await grade_repo.get_by_id(grade_id)
    if not existing_grade:
        raise NotFoundError("Grade", grade_id)
    
    # Verify profesor permissions
    if current_user.role == UserRole.PROFESOR:
        await GradeValidator.verify_profesor_subject_permission(
            db, current_user, int(existing_grade.enrollment_id)
        )
    
    # Update grade using service (business logic)
    service = GradeService(db)
    await service.update_grade(grade_id, grade_data)
    
    # Load updated grade with enrollment relationship
    grade = await grade_repo.get_with_relations(grade_id)
    if not grade:
        raise NotFoundError("Grade", grade_id)
    
    # Serialize single grade using serializer
    responses = await GradeSerializer.serialize_batch([grade], db)
    return responses[0] if responses else None


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grade(
    grade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Delete grade (Profesor or Admin only)."""
    grade_repo = GradeRepository(db)
    
    # Get existing grade to verify permissions
    existing_grade = await grade_repo.get_by_id(grade_id)
    if not existing_grade:
        raise NotFoundError("Grade", grade_id)
    
    # Verify profesor permissions
    if current_user.role == UserRole.PROFESOR:
        await GradeValidator.verify_profesor_subject_permission(
            db, current_user, int(existing_grade.enrollment_id)
        )
    
    # Delete grade using service (business logic)
    service = GradeService(db)
    deleted = await service.delete_grade(grade_id)
    if not deleted:
        raise NotFoundError("Grade", grade_id)


