"""Repository protocols for Dependency Inversion Principle.

These protocols define the interfaces that repositories must implement,
allowing services to depend on abstractions rather than concrete implementations.
This makes the code more testable and maintainable.
"""

from typing import Protocol, TypeVar, Generic, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")
CreateSchemaType = TypeVar("CreateSchemaType", contravariant=True)
UpdateSchemaType = TypeVar("UpdateSchemaType", contravariant=True)


class BaseRepositoryProtocol(Protocol, Generic[T, CreateSchemaType, UpdateSchemaType]):
    """Protocol for base repository operations."""

    db: AsyncSession

    async def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        ...

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        ...

    async def create(self, data: CreateSchemaType) -> T:
        """Create a new entity."""
        ...

    async def update(self, entity: T, data: UpdateSchemaType) -> T:
        """Update an existing entity."""
        ...

    async def delete(self, entity: T) -> None:
        """Delete an entity."""
        ...


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""

    db: AsyncSession

    async def get_by_id(self, user_id: int) -> Optional[Any]:
        """Get user by ID."""
        ...

    async def get_by_email(self, email: str) -> Optional[Any]:
        """Get user by email."""
        ...

    async def get_by_codigo(self, codigo: str) -> Optional[Any]:
        """Get user by institutional code."""
        ...

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all users."""
        ...

    async def create(self, data: Any) -> Any:
        """Create a new user."""
        ...

    async def update(self, user: Any, data: Any) -> Any:
        """Update a user."""
        ...

    async def delete(self, user: Any) -> None:
        """Delete a user."""
        ...


class SubjectRepositoryProtocol(Protocol):
    """Protocol for subject repository operations."""

    db: AsyncSession

    async def get_by_id(self, subject_id: int) -> Optional[Any]:
        """Get subject by ID."""
        ...

    async def get_by_codigo(self, codigo: str) -> Optional[Any]:
        """Get subject by institutional code."""
        ...

    async def get_by_profesor(self, profesor_id: int) -> List[Any]:
        """Get all subjects for a professor."""
        ...

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all subjects."""
        ...

    async def create(self, data: Any) -> Any:
        """Create a new subject."""
        ...

    async def update(self, subject: Any, data: Any) -> Any:
        """Update a subject."""
        ...

    async def delete(self, subject: Any) -> None:
        """Delete a subject."""
        ...


class EnrollmentRepositoryProtocol(Protocol):
    """Protocol for enrollment repository operations."""

    db: AsyncSession

    async def get_by_id(self, enrollment_id: int) -> Optional[Any]:
        """Get enrollment by ID."""
        ...

    async def get_by_estudiante(self, estudiante_id: int) -> List[Any]:
        """Get all enrollments for a student."""
        ...

    async def get_by_subject(self, subject_id: int) -> List[Any]:
        """Get all enrollments for a subject."""
        ...

    async def get_by_estudiante_and_subject(
        self, estudiante_id: int, subject_id: int
    ) -> Optional[Any]:
        """Get enrollment by student and subject."""
        ...

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all enrollments."""
        ...

    async def create(self, data: Any) -> Any:
        """Create a new enrollment."""
        ...

    async def delete(self, enrollment: Any) -> None:
        """Delete an enrollment."""
        ...

    async def get_with_relations(
        self, enrollment_id: int, relations: Optional[List[str]] = None
    ) -> Optional[Any]:
        """Get enrollment with eager-loaded relationships.
        
        Args:
            enrollment_id: The enrollment ID
            relations: List of relation names to load (e.g., ['estudiante', 'subject'])
        
        Returns:
            Enrollment with loaded relationships or None
        """
        ...


class GradeRepositoryProtocol(Protocol):
    """Protocol for grade repository operations."""

    db: AsyncSession

    async def get_by_id(self, grade_id: int) -> Optional[Any]:
        """Get grade by ID."""
        ...

    async def get_by_enrollment(self, enrollment_id: int) -> List[Any]:
        """Get all grades for an enrollment."""
        ...

    async def get_by_subject(self, subject_id: int) -> List[Any]:
        """Get all grades for a subject."""
        ...

    async def get_by_estudiante(self, estudiante_id: int) -> List[Any]:
        """Get all grades for a student."""
        ...

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all grades."""
        ...

    async def create(self, data: Any) -> Any:
        """Create a new grade."""
        ...

    async def update(self, grade: Any, data: Any) -> Any:
        """Update a grade."""
        ...

    async def delete(self, grade: Any) -> None:
        """Delete a grade."""
        ...

    async def get_with_relations(
        self, 
        grade_id: int, 
        relations: Optional[List[str]] = None
    ) -> Optional[Any]:
        """Get grade with eager-loaded relationships.
        
        Args:
            grade_id: The grade ID
            relations: List of relation names to load (e.g., ['enrollment', 'enrollment.estudiante'])
        
        Returns:
            Grade with loaded relationships or None
        """
        ...

    async def get_many_with_relations(
        self,
        grade_ids: Optional[List[int]] = None,
        enrollment_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        relations: Optional[List[str]] = None,
    ) -> List[Any]:
        """Get multiple grades with eager-loaded relationships.
        
        Args:
            grade_ids: Optional list of grade IDs to filter
            enrollment_id: Optional enrollment ID to filter
            subject_id: Optional subject ID to filter
            relations: List of relation names to load
        
        Returns:
            List of grades with loaded relationships
        """
        ...


__all__ = [
    "BaseRepositoryProtocol",
    "UserRepositoryProtocol",
    "SubjectRepositoryProtocol",
    "EnrollmentRepositoryProtocol",
    "GradeRepositoryProtocol",
]
