"""Grade validators for permission checks."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.exceptions import NotFoundError, ForbiddenError
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.subject_repository import SubjectRepository
from app.services.profesor_service import ProfesorService


class GradeValidator:
    """Validator for grade-related permissions."""

    @staticmethod
    async def verify_profesor_subject_permission(
        db: AsyncSession, current_user: User, enrollment_id: int
    ) -> None:
        """Verify that a profesor has permission to access a subject via enrollment.
        
        Args:
            db: Database session
            current_user: Current profesor user
            enrollment_id: Enrollment ID to check
            
        Raises:
            NotFoundError: If enrollment not found
            ForbiddenError: If subject is not assigned to profesor
        """
        enrollment_repo = EnrollmentRepository(db)
        enrollment = await enrollment_repo.get_by_id(enrollment_id)

        if not enrollment:
            raise NotFoundError("Enrollment", enrollment_id)

        subject_repo = SubjectRepository(db)
        subject = await subject_repo.get_by_id(int(enrollment.subject_id))

        if not subject or int(subject.profesor_id) != int(current_user.id):
            raise ForbiddenError("Cannot access grade for unassigned subject")

    @staticmethod
    async def verify_profesor_can_access_subject(
        db: AsyncSession, current_user: User, subject_id: int
    ) -> None:
        """Verify that a profesor has access to a subject.
        
        Args:
            db: Database session
            current_user: Current profesor user
            subject_id: Subject ID to check
            
        Raises:
            ForbiddenError: If subject is not assigned to profesor
        """
        profesor_service = ProfesorService(db, current_user)
        subjects = await profesor_service.get_assigned_subjects()
        subject_ids = [s.id for s in subjects]

        if subject_id not in subject_ids:
            raise ForbiddenError("Subject is not assigned to this profesor")

