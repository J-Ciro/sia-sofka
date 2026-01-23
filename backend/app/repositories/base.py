"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar, Type, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class AbstractRepository(Generic[ModelType]):
    """Abstract base repository with common CRUD operations."""
    
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        """Initialize repository.
        
        Args:
            db: Database session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model
    
    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new record.
        
        Args:
            data: Dictionary with model attributes
        
        Returns:
            Created model instance
        """
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get record by ID.
        
        Args:
            id: Record ID
        
        Returns:
            Model instance or None
        """
        stmt = select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of model instances
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record.
        
        Args:
            id: Record ID
            data: Dictionary with attributes to update
        
        Returns:
            Updated model instance or None
        """
        stmt = (
            update(self.model)
            .where(self.model.id == id)  # type: ignore[attr-defined]
            .values(**data)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_by_id(id)
    
    async def delete(self, id: int) -> bool:
        """Delete a record.
        
        Args:
            id: Record ID
        
        Returns:
            True if deleted, False if not found
        """
        stmt = delete(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0


