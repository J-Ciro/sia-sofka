"""Enrollment service with business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.user_repository import UserRepository
from app.repositories.subject_repository import SubjectRepository
from app.schemas.enrollment import EnrollmentCreate
from app.models.enrollment import Enrollment
from app.models.user import UserRole


class EnrollmentService:
    """Service for enrollment business logic."""
    
    def __init__(self, db: AsyncSession):
        """Initialize enrollment service.
        
        Args:
            db: Database session
        """
        self.repository = EnrollmentRepository(db)
        self.user_repository = UserRepository(db)
        self.subject_repository = SubjectRepository(db)
        self.db = db
    
    async def create_enrollment(self, enrollment_data: EnrollmentCreate) -> Enrollment:
        """Create a new enrollment with business logic.
        
        Args:
            enrollment_data: Enrollment creation data
        
        Returns:
            Created enrollment
        
        Raises:
            ValueError: If invalid data or duplicate enrollment
        """
        # Verify estudiante exists and is an Estudiante
        estudiante = await self.user_repository.get_by_id(enrollment_data.estudiante_id)
        if not estudiante:
            raise ValueError("Estudiante not found")
        
        if estudiante.role != UserRole.ESTUDIANTE:
            raise ValueError("User is not an Estudiante")
        
        # Verify subject exists
        subject = await self.subject_repository.get_by_id(enrollment_data.subject_id)
        if not subject:
            raise ValueError("Subject not found")
        
        # Check if enrollment already exists
        existing = await self.repository.get_by_estudiante_and_subject(
            enrollment_data.estudiante_id,
            enrollment_data.subject_id,
        )
        if existing:
            raise ValueError("Estudiante is already enrolled in this subject")
        
        # Create enrollment
        enrollment_dict = enrollment_data.model_dump()
        return await self.repository.create(enrollment_dict)
    
    async def get_enrollment_by_id(self, enrollment_id: int) -> Enrollment | None:
        """Get enrollment by ID.
        
        Args:
            enrollment_id: Enrollment ID
        
        Returns:
            Enrollment or None
        """
        return await self.repository.get_by_id(enrollment_id)
    
    async def get_enrollments_by_estudiante(
        self, estudiante_id: int, skip: int = 0, limit: int = 100
    ) -> list[Enrollment]:
        """Get enrollments by estudiante.
        
        Args:
            estudiante_id: Estudiante user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of enrollments
        """
        result = await self.repository.get_by_estudiante(estudiante_id, skip, limit)
        return list(result) if result else []
    
    async def get_enrollments_by_subject(
        self, subject_id: int, skip: int = 0, limit: int = 100
    ) -> list[Enrollment]:
        """Get enrollments by subject.
        
        Args:
            subject_id: Subject ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of enrollments
        """
        result = await self.repository.get_by_subject(subject_id, skip, limit)
        return list(result) if result else []
    
    async def delete_enrollment(self, enrollment_id: int) -> bool:
        """Delete enrollment.
        
        Args:
            enrollment_id: Enrollment ID
        
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(enrollment_id)


