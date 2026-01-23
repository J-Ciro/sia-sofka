"""Subject endpoints - Refactored to use repository pattern and serializers."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError, ConflictError
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.schemas.user import UserResponse
from app.services.admin_service import AdminService
from app.services.subject_service import SubjectService
from app.services.profesor_service import ProfesorService
from app.services.user_service import UserService
from app.repositories.subject_repository import SubjectRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.api.v1.dependencies import require_admin, get_current_active_user
from app.api.v1.serializers.subject_serializer import SubjectSerializer
from app.api.v1.serializers.enrollment_serializer import EnrollmentSerializer

router = APIRouter()


# ==================== Helper Functions ====================

async def _get_subjects_for_profesor(
    db: AsyncSession, current_user: User
) -> List[SubjectResponse]:
    """Get subjects for profesor role."""
    profesor_service = ProfesorService(db, current_user)
    subjects = await profesor_service.get_assigned_subjects()
    
    # Si hay subjects, cargar relación profesor con eager loading
    if subjects:
        subject_ids = [s.id for s in subjects]
        stmt = (
            select(Subject)
            .where(Subject.id.in_(subject_ids))
            .options(selectinload(Subject.profesor))
        )
        result = await db.execute(stmt)
        subjects = list(result.scalars().all())
    
    return SubjectSerializer.serialize_batch(subjects)


async def _get_subjects_for_admin(
    db: AsyncSession, skip: int, limit: int
) -> List[SubjectResponse]:
    """Get subjects for admin role."""
    # Usar eager loading para cargar relación profesor directamente
    stmt = (
        select(Subject)
        .options(selectinload(Subject.profesor))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    subjects = list(result.scalars().all())
    
    return SubjectSerializer.serialize_batch(subjects)


async def _get_enrollments_for_role(
    db: AsyncSession,
    current_user: User,
    subject_id: int,
    is_profesor: bool
) -> List:
    """Get enrollments for a subject based on user role."""
    enrollment_repo = EnrollmentRepository(db)
    
    if is_profesor:
        # Profesor: verificar que la materia esté asignada
        profesor_service = ProfesorService(db, current_user)
        await profesor_service.get_students_by_subject(subject_id)
    
    enrollments = await enrollment_repo.get_many_with_relations(
        subject_id=subject_id,
        relations=['estudiante', 'subject']
    )
    return await EnrollmentSerializer.serialize_batch(enrollments, db)


async def _get_students_for_role(
    db: AsyncSession,
    current_user: User,
    subject_id: int,
    is_profesor: bool
) -> List[UserResponse]:
    """Get students for a subject based on user role."""
    if is_profesor:
        profesor_service = ProfesorService(db, current_user)
        students = await profesor_service.get_students_by_subject(subject_id)
    else:
        # Admin: obtener estudiantes usando eager loading (evita N+1 queries)
        enrollment_repo = EnrollmentRepository(db)
        enrollments = await enrollment_repo.get_many_with_relations(
            subject_id=subject_id,
            relations=['estudiante']  # Eager load estudiantes
        )
        # Extraer estudiantes de enrollments (ya cargados)
        students = [
            enrollment.estudiante 
            for enrollment in enrollments 
            if hasattr(enrollment, 'estudiante') and enrollment.estudiante
        ]
    
    return [UserResponse.model_validate(student) for student in students]


# ==================== Endpoints ====================

@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new subject (Admin only)."""
    admin_service = AdminService(db, current_user)
    
    try:
        subject = await admin_service.create_subject(subject_data)
        # El repositorio ya hace commit, solo necesitamos cargar la relación profesor
        # Usar eager loading en lugar de refresh manual
        stmt = (
            select(Subject)
            .where(Subject.id == subject.id)
            .options(selectinload(Subject.profesor))
        )
        result = await db.execute(stmt)
        subject_with_profesor = result.scalar_one_or_none()
        
        if not subject_with_profesor:
            raise NotFoundError("Subject", subject.id)
        
        # Serialize using SubjectSerializer
        serialized = SubjectSerializer.serialize_batch([subject_with_profesor])
        return serialized[0] if serialized else None
    except ValueError as e:
        await db.rollback()
        raise ValidationError(str(e))


@router.get("", response_model=List[SubjectResponse])
async def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get subjects.
    
    - Admin: can see all subjects
    - Profesor: can see only their assigned subjects
    """
    if current_user.role == UserRole.PROFESOR:
        return await _get_subjects_for_profesor(db, current_user)
    elif current_user.role == UserRole.ADMIN:
        return await _get_subjects_for_admin(db, skip, limit)
    else:
        raise ForbiddenError("Not enough permissions")


@router.get("/{subject_id}/enrollments")
async def get_subject_enrollments(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get enrollments for a subject.
    
    - Profesor: can see enrollments of their assigned subjects
    - Admin: can see enrollments of any subject
    """
    try:
        if current_user.role == UserRole.PROFESOR:
            return await _get_enrollments_for_role(db, current_user, subject_id, is_profesor=True)
        elif current_user.role == UserRole.ADMIN:
            return await _get_enrollments_for_role(db, current_user, subject_id, is_profesor=False)
        else:
            raise ForbiddenError("Not enough permissions")
    except ValueError as e:
        raise ValidationError(str(e))


@router.get("/{subject_id}/students")
async def get_subject_students(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get students enrolled in a subject.
    
    - Profesor: can see students of their assigned subjects
    - Admin: can see students of any subject
    """
    try:
        if current_user.role == UserRole.PROFESOR:
            return await _get_students_for_role(db, current_user, subject_id, is_profesor=True)
        elif current_user.role == UserRole.ADMIN:
            return await _get_students_for_role(db, current_user, subject_id, is_profesor=False)
        else:
            raise ForbiddenError("Not enough permissions")
    except ValueError as e:
        raise ValidationError(str(e))


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get subject by ID (Admin only)."""
    service = SubjectService(db)
    subject = await service.get_subject_by_id(subject_id)
    
    if not subject:
        raise NotFoundError("Subject", subject_id)
    
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update subject (Admin only)."""
    admin_service = AdminService(db, current_user)
    subject = await admin_service.update_subject(subject_id, subject_data)
    
    if not subject:
        raise NotFoundError("Subject", subject_id)
    
    # Load profesor relationship with eager loading before serialization
    stmt = (
        select(Subject)
        .where(Subject.id == subject_id)
        .options(selectinload(Subject.profesor))
    )
    result = await db.execute(stmt)
    subject_with_profesor = result.scalar_one_or_none()
    
    if not subject_with_profesor:
        raise NotFoundError("Subject", subject_id)
    
    # Use serializer to properly serialize with profesor relationship
    serialized = SubjectSerializer.serialize_batch([subject_with_profesor])
    return serialized[0] if serialized else None


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete subject (Admin only).
    
    Raises ConflictError if subject has historical data that prevents deletion.
    """
    admin_service = AdminService(db, current_user)
    try:
        deleted = await admin_service.delete_subject(subject_id)
        
        if not deleted:
            raise NotFoundError("Subject", subject_id)
    except ConflictError:
        # Re-raise ConflictError as-is (already has proper status code and message)
        raise
    except ValueError as e:
        # Handle business logic validation errors
        raise ValidationError(str(e))

