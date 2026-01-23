"""Enrollment repository with eager loading support."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.enrollment import Enrollment
from app.repositories.base import AbstractRepository
from app.repositories.mixins import EagerLoadMixin, PaginationMixin
from app.core.decorators import handle_repository_errors


class EnrollmentRepository(AbstractRepository[Enrollment], EagerLoadMixin, PaginationMixin):
    """Repository for Enrollment model with eager loading capabilities."""
    
    def __init__(self, db: AsyncSession):
        """Initialize enrollment repository.
        
        Args:
            db: Database session
        """
        super().__init__(db, Enrollment)
    
    @handle_repository_errors
    async def get_by_estudiante(
        self, estudiante_id: int, skip: int = 0, limit: int = 100
    ) -> List[Enrollment]:
        """Get enrollments by estudiante.
        
        Args:
            estudiante_id: Estudiante user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of enrollments
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        stmt = (
            select(Enrollment)
            .where(Enrollment.estudiante_id == estudiante_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    @handle_repository_errors
    async def get_by_subject(
        self, subject_id: int, skip: int = 0, limit: int = 100
    ) -> List[Enrollment]:
        """Get enrollments by subject.
        
        Args:
            subject_id: Subject ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of enrollments
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        stmt = (
            select(Enrollment)
            .where(Enrollment.subject_id == subject_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    @handle_repository_errors
    async def get_by_estudiante_and_subject(
        self, estudiante_id: int, subject_id: int
    ) -> Optional[Enrollment]:
        """Get enrollment by estudiante and subject.
        
        Args:
            estudiante_id: Estudiante user ID
            subject_id: Subject ID
        
        Returns:
            Enrollment instance or None
        """
        stmt = select(Enrollment).where(
            Enrollment.estudiante_id == estudiante_id,
            Enrollment.subject_id == subject_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    @handle_repository_errors
    async def get_with_relations(
        self, 
        enrollment_id: int, 
        relations: Optional[List[str]] = None
    ) -> Optional[Enrollment]:
        """Get enrollment with eager-loaded relationships.
        
        Args:
            enrollment_id: The enrollment ID
            relations: List of relation names to load
                      Default: ['estudiante', 'subject']
        
        Returns:
            Enrollment with loaded relationships or None
            
        Example:
            # Load enrollment with student and subject
            enrollment = await repo.get_with_relations(1)
            
            # Load with grades too
            enrollment = await repo.get_with_relations(
                1, relations=['estudiante', 'subject', 'grades']
            )
        """
        if relations is None:
            relations = []
        
        # Use joinedload for many-to-one relationships (estudiante, subject)
        # Use selectinload for one-to-many relationships (grades)
        use_joined = [r for r in relations if r in ['estudiante', 'subject']]
        select_relations = [r for r in relations if r == 'grades']
        
        return await self._get_one_with_relations(
            Enrollment, 
            Enrollment.id == enrollment_id,
            relations=select_relations,
            use_joined=use_joined
        )
    
    @handle_repository_errors
    async def get_many_with_relations(
        self,
        estudiante_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        relations: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Enrollment]:
        """Get multiple enrollments with eager-loaded relationships.
        
        Args:
            estudiante_id: Optional student ID to filter
            subject_id: Optional subject ID to filter
            relations: List of relation names to load
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of enrollments with loaded relationships, ordered by most recent first
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        if relations is None:
            relations = []
        
        # Build condition
        condition = None
        if estudiante_id and subject_id:
            condition = (Enrollment.estudiante_id == estudiante_id) & (Enrollment.subject_id == subject_id)  # type: ignore[assignment]
        elif estudiante_id:
            condition = Enrollment.estudiante_id == estudiante_id  # type: ignore[assignment]
        elif subject_id:
            condition = Enrollment.subject_id == subject_id  # type: ignore[assignment]
        
        # Separate joinedload and selectinload
        use_joined = [r for r in relations if r in ['estudiante', 'subject']]
        select_relations = [r for r in relations if r == 'grades']
        
        # Build query directly to ensure ordering happens BEFORE pagination
        from sqlalchemy import select, desc
        from sqlalchemy.orm import selectinload, joinedload
        
        stmt = select(Enrollment)
        
        if condition is not None:
            stmt = stmt.where(condition)
        
        # Add eager loading options
        if select_relations:
            for relation in select_relations:
                stmt = stmt.options(selectinload(getattr(Enrollment, relation)))
        
        if use_joined:
            for relation in use_joined:
                stmt = stmt.options(joinedload(getattr(Enrollment, relation)))
        
        # Order by id descending (most recent first) BEFORE pagination
        stmt = stmt.order_by(desc(Enrollment.id))
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())



