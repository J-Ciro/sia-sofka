"""Grade repository with eager loading support."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from app.repositories.base import AbstractRepository
from app.repositories.mixins import EagerLoadMixin, PaginationMixin
from app.core.decorators import handle_repository_errors


class GradeRepository(AbstractRepository[Grade], EagerLoadMixin, PaginationMixin):
    """Repository for Grade model with eager loading capabilities."""
    
    def __init__(self, db: AsyncSession):
        """Initialize grade repository.
        
        Args:
            db: Database session
        """
        super().__init__(db, Grade)
    
    @handle_repository_errors
    async def get_by_enrollment(
        self, enrollment_id: int, skip: int = 0, limit: int = 100
    ) -> List[Grade]:
        """Get grades by enrollment.
        
        Args:
            enrollment_id: Enrollment ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of grades
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        stmt = (
            select(Grade)
            .where(Grade.enrollment_id == enrollment_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    @handle_repository_errors
    async def get_by_subject(
        self, subject_id: int, skip: int = 0, limit: int = 100
    ) -> List[Grade]:
        """Get all grades for a subject.
        
        Args:
            subject_id: Subject ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of grades for the subject
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        # First get enrollments for this subject
        enrollment_stmt = select(Enrollment.id).where(Enrollment.subject_id == subject_id)
        enrollment_result = await self.db.execute(enrollment_stmt)
        enrollment_ids = [row[0] for row in enrollment_result.all()]
        
        if not enrollment_ids:
            return []
        
        # Then get grades for those enrollments
        stmt = (
            select(Grade)
            .where(Grade.enrollment_id.in_(enrollment_ids))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    @handle_repository_errors
    async def get_by_estudiante(
        self, estudiante_id: int, skip: int = 0, limit: int = 100
    ) -> List[Grade]:
        """Get all grades for a student.
        
        Args:
            estudiante_id: Student ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of grades for the student
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        # Get enrollments for this student
        enrollment_stmt = select(Enrollment.id).where(Enrollment.estudiante_id == estudiante_id)
        enrollment_result = await self.db.execute(enrollment_stmt)
        enrollment_ids = [row[0] for row in enrollment_result.all()]
        
        if not enrollment_ids:
            return []
        
        # Get grades for those enrollments
        stmt = (
            select(Grade)
            .where(Grade.enrollment_id.in_(enrollment_ids))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    @handle_repository_errors
    async def get_with_relations(
        self, 
        grade_id: int, 
        relations: Optional[List[str]] = None
    ) -> Optional[Grade]:
        """Get grade with eager-loaded relationships including nested ones.
        
        Args:
            grade_id: The grade ID
            relations: List of relation names to load
                      Default: ['enrollment'] with nested estudiante and subject
        
        Returns:
            Grade with loaded relationships or None
        """
        if relations is None:
            relations = ['enrollment']
        
        # Use selectinload for enrollment, joinedload for nested relationships
        use_joined = ['enrollment.estudiante', 'enrollment.subject'] if 'enrollment' in relations else []
        
        return await self._get_one_with_relations(
            Grade, 
            Grade.id == grade_id,
            relations=relations,
            use_joined=use_joined
        )
    
    @handle_repository_errors
    async def get_many_with_relations(
        self,
        grade_ids: Optional[List[int]] = None,
        enrollment_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        relations: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Grade]:
        """Get multiple grades with eager-loaded relationships.
        
        Args:
            grade_ids: Optional list of grade IDs to filter
            enrollment_id: Optional enrollment ID to filter
            subject_id: Optional subject ID to filter
            relations: List of relation names to load
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of grades with loaded relationships
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        if relations is None:
            relations = ['enrollment']
        
        # Build condition
        from sqlalchemy import or_
        condition = None
        if grade_ids:
            condition = Grade.id.in_(grade_ids)  # type: ignore[assignment]
        elif enrollment_id:
            condition = Grade.enrollment_id == enrollment_id  # type: ignore[assignment]
        elif subject_id:
            # Get enrollments for this subject first
            enrollment_stmt = select(Enrollment.id).where(Enrollment.subject_id == subject_id)
            enrollment_result = await self.db.execute(enrollment_stmt)
            enrollment_ids = [row[0] for row in enrollment_result.all()]
            
            if not enrollment_ids:
                return []
            
            condition = Grade.enrollment_id.in_(enrollment_ids)
        
        # Use joinedload for nested many-to-one relationships
        # When using joinedload for nested relations, we need to include 'enrollment' in use_joined
        # and exclude it from relations to avoid conflicts
        use_joined = []
        filtered_relations = relations.copy() if relations else []
        
        if 'enrollment' in filtered_relations:
            # Use joinedload for enrollment and nested relationships
            use_joined = ['enrollment', 'enrollment.estudiante', 'enrollment.subject']
            # Remove 'enrollment' from relations to avoid conflict
            filtered_relations = [r for r in filtered_relations if r != 'enrollment']
        
        return await self._get_many_with_relations(
            Grade,
            condition=condition,
            relations=filtered_relations if filtered_relations else None,
            use_joined=use_joined,
            skip=skip,
            limit=limit
        )
    
    @handle_repository_errors
    async def get_average_by_enrollment(self, enrollment_id: int) -> Optional[float]:
        """Get average grade for an enrollment.
        
        Args:
            enrollment_id: Enrollment ID
        
        Returns:
            Average grade or None if no grades exist
        """
        stmt = select(func.avg(Grade.nota)).where(
            Grade.enrollment_id == enrollment_id
        )
        result = await self.db.execute(stmt)
        avg = result.scalar()
        return float(avg) if avg is not None else None



