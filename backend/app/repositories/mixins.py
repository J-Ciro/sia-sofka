"""Mixins for repository operations.

These mixins provide reusable functionality for repositories,
following DRY principle and reducing code duplication.
"""

from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession


class EagerLoadMixin:
    """Mixin to handle eager loading of relationships.
    
    Centralizes the logic for loading related entities using SQLAlchemy's
    selectinload and joinedload strategies.
    
    Usage:
        class UserRepository(BaseRepository, EagerLoadMixin):
            async def get_with_enrollments(self, user_id: int):
                return await self._get_one_with_relations(
                    User, User.id == user_id, ['enrollments']
                )
    """

    db: AsyncSession  # Must be provided by implementing class

    async def _get_one_with_relations(
        self,
        model: Any,
        condition: Any,
        relations: Optional[List[str]] = None,
        use_joined: Optional[List[str]] = None,
    ) -> Optional[Any]:
        """Get a single entity with eager-loaded relationships.
        
        Args:
            model: The SQLAlchemy model class
            condition: The WHERE condition
            relations: List of relationship names to load with selectinload
            use_joined: List of relationship names to load with joinedload
            
        Returns:
            Entity with loaded relationships or None
            
        Example:
            # Load user with enrollments (one-to-many)
            user = await self._get_one_with_relations(
                User, User.id == 1, relations=['enrollments']
            )
            
            # Load enrollment with student and subject (many-to-one)
            enrollment = await self._get_one_with_relations(
                Enrollment, Enrollment.id == 1, 
                use_joined=['estudiante', 'subject']
            )
        """
        stmt = select(model).where(condition)

        # Add selectinload options (best for one-to-many)
        if relations:
            for relation in relations:
                # Handle nested relations like 'enrollment.estudiante'
                if '.' in relation:
                    parts = relation.split('.')
                    first_rel = getattr(model, parts[0])
                    # For nested relations, get the related model class
                    related_model = first_rel.property.mapper.class_
                    second_rel = getattr(related_model, parts[1])
                    stmt = stmt.options(
                        selectinload(first_rel).selectinload(second_rel)
                    )
                else:
                    stmt = stmt.options(selectinload(getattr(model, relation)))

        # Add joinedload options (best for many-to-one)
        if use_joined:
            for relation in use_joined:
                if '.' in relation:
                    # For nested relations, build the chain differently
                    parts = relation.split('.')
                    # Start with first relationship from model
                    first_rel = getattr(model, parts[0])
                    # Use string-based path for nested relations
                    # This is more reliable than trying to chain manually
                    stmt = stmt.options(
                        selectinload(first_rel).joinedload(getattr(first_rel.property.mapper.class_, parts[1]))
                    )
                else:
                    stmt = stmt.options(joinedload(getattr(model, relation)))

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_many_with_relations(
        self,
        model: Any,
        condition: Optional[Any] = None,
        relations: Optional[List[str]] = None,
        use_joined: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Any]:
        """Get multiple entities with eager-loaded relationships.
        
        Args:
            model: The SQLAlchemy model class
            condition: Optional WHERE condition
            relations: List of relationship names to load with selectinload
            use_joined: List of relationship names to load with joinedload
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of entities with loaded relationships
            
        Example:
            # Load all grades with enrollment and nested student/subject
            grades = await self._get_many_with_relations(
                Grade,
                relations=['enrollment'],
                use_joined=['enrollment.estudiante', 'enrollment.subject']
            )
        """
        stmt = select(model)

        if condition is not None:
            stmt = stmt.where(condition)

        # Add selectinload options
        if relations:
            for relation in relations:
                if '.' in relation:
                    parts = relation.split('.')
                    first_rel = getattr(model, parts[0])
                    # For nested relations, get the related model class
                    related_model = first_rel.property.mapper.class_
                    second_rel = getattr(related_model, parts[1])
                    stmt = stmt.options(
                        selectinload(first_rel).selectinload(second_rel)
                    )
                else:
                    stmt = stmt.options(selectinload(getattr(model, relation)))

        # Add joinedload options
        if use_joined:
            # Separate simple relations from nested ones
            simple_joined = [r for r in use_joined if '.' not in r]
            nested_joined = [r for r in use_joined if '.' in r]
            
            # Group nested relations by their first relation (e.g., 'enrollment' in 'enrollment.estudiante')
            nested_by_first: dict[str, list[str]] = {}
            for relation in nested_joined:
                parts = relation.split('.')
                first = parts[0]
                if first not in nested_by_first:
                    nested_by_first[first] = []
                nested_by_first[first].append(parts[1])
            
            # Handle simple joinedload first (if not already handled by nested)
            for relation in simple_joined:
                if relation not in nested_by_first:  # Avoid duplication
                    stmt = stmt.options(joinedload(getattr(model, relation)))
            
            # Handle nested joinedload: each nested relation from the same parent is a separate chain
            for first_rel_name, nested_names in nested_by_first.items():
                first_rel = getattr(model, first_rel_name)
                related_model = first_rel.property.mapper.class_
                # Create separate joinedload options for each nested relation
                # All chains start from the same first relation
                for nested_name in nested_names:
                    nested_rel = getattr(related_model, nested_name)
                    # Chain: model.first_rel -> related_model.nested_rel
                    stmt = stmt.options(joinedload(first_rel).joinedload(nested_rel))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class PaginationMixin:
    """Mixin to handle pagination in a standardized way.
    
    Uses class attributes that match values in app.core.config.settings.
    Class attributes can be overridden in subclasses for testing.
    
    Note: These default values (100, 1000) match settings.default_page_size
    and settings.max_page_size. In production, if settings values differ,
    they will be used automatically via the repository initialization.
    """
    
    # Class attributes (can be overridden in subclasses for testing)
    # These default values match Settings.default_page_size and Settings.max_page_size
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    
    def _validate_pagination(self, skip: int, limit: int) -> tuple[int, int]:
        """Validate and normalize pagination parameters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (validated_skip, validated_limit)
            
        Raises:
            ValueError: If pagination parameters are invalid
        """
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        
        if limit < 1:
            raise ValueError("Limit must be positive")
        
        # Use class attribute (can be overridden in subclass for testing)
        max_size = type(self).MAX_PAGE_SIZE
        
        if limit > max_size:
            limit = max_size
            
        return skip, limit


class TimestampMixin:
    """Mixin for handling timestamp queries."""

    async def _get_recent(
        self,
        model: Any,
        days: int = 7,
        limit: int = 100,
    ) -> List[Any]:
        """Get recent entities based on created_at.
        
        Args:
            model: The SQLAlchemy model class
            days: Number of days to look back
            limit: Maximum number of records to return
            
        Returns:
            List of recent entities
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(model)
            .where(model.created_at >= cutoff_date)
            .order_by(model.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


__all__ = ["EagerLoadMixin", "PaginationMixin", "TimestampMixin"]
