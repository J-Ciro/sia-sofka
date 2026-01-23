"""Grade service with business logic."""

from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.grade_repository import GradeRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.schemas.grade import GradeCreate, GradeUpdate
from app.models.grade import Grade


class GradeService:
    """Service for grade business logic."""
    
    def __init__(self, db: AsyncSession):
        """Initialize grade service.
        
        Args:
            db: Database session
        """
        self.repository = GradeRepository(db)
        self.enrollment_repository = EnrollmentRepository(db)
        self.db = db
    
    async def create_grade(self, grade_data: GradeCreate) -> Grade:
        """Create a new grade with business logic.
        
        Args:
            grade_data: Grade creation data
        
        Returns:
            Created grade
        
        Raises:
            ValueError: If invalid data or enrollment not found
        """
        # Validate note range (0.0 to 5.0)
        if grade_data.nota < Decimal("0.0") or grade_data.nota > Decimal("5.0"):
            raise ValueError("Note must be between 0.0 and 5.0")
        
        # Verify enrollment exists
        enrollment = await self.enrollment_repository.get_by_id(grade_data.enrollment_id)
        if not enrollment:
            raise ValueError("Enrollment not found")
        
        # Create grade
        grade_dict = grade_data.model_dump()
        # Keep as Decimal for Numeric column
        return await self.repository.create(grade_dict)
    
    async def get_grade_by_id(self, grade_id: int) -> Grade | None:
        """Get grade by ID.
        
        Args:
            grade_id: Grade ID
        
        Returns:
            Grade or None
        """
        return await self.repository.get_by_id(grade_id)
    
    async def update_grade(
        self, grade_id: int, grade_data: GradeUpdate
    ) -> Grade | None:
        """Update grade with business logic.
        
        Args:
            grade_id: Grade ID
            grade_data: Grade update data
        
        Returns:
            Updated grade or None
        
        Raises:
            ValueError: If invalid data
        """
        # Validate note range if provided
        if grade_data.nota is not None:
            if grade_data.nota < Decimal("0.0") or grade_data.nota > Decimal("5.0"):
                raise ValueError("Note must be between 0.0 and 5.0")
        
        update_dict = grade_data.model_dump(exclude_unset=True)
        # Keep as Decimal for Numeric column
        return await self.repository.update(grade_id, update_dict)
    
    async def delete_grade(self, grade_id: int) -> bool:
        """Delete grade.
        
        Args:
            grade_id: Grade ID
        
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(grade_id)
    
    async def get_grades_by_enrollment(
        self, enrollment_id: int, skip: int = 0, limit: int = 100
    ) -> list[Grade]:
        """Get grades by enrollment.
        
        Args:
            enrollment_id: Enrollment ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of grades
        """
        result = await self.repository.get_by_enrollment(enrollment_id, skip, limit)
        return list(result) if result else []
    
    async def calculate_average(self, enrollment_id: int) -> Decimal:
        """Calculate average grade for an enrollment.
        
        Args:
            enrollment_id: Enrollment ID
        
        Returns:
            Average grade as Decimal
        
        Raises:
            ValueError: If no grades found
        """
        average = await self.repository.get_average_by_enrollment(enrollment_id)
        if average is None:
            raise ValueError("No grades found for this enrollment")
        # Round to 2 decimal places
        return Decimal(str(round(average, 2)))

