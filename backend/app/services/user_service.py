"""User service with business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


class UserService:
    """Service for user business logic."""
    
    def __init__(self, db: AsyncSession):
        """Initialize user service.
        
        Args:
            db: Database session
        """
        self.repository = UserRepository(db)
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with business logic.
        
        Args:
            user_data: User creation data
        
        Returns:
            Created user
        
        Raises:
            ValueError: If email already exists or invalid data
        """
        # Check if email already exists
        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Generate institutional code
        codigo = await generar_codigo_institucional(self.db, user_data.role.value)
        
        # Create user data dict - only include fields that are not None
        user_dict = {
            "email": user_data.email,
            "password_hash": get_password_hash(user_data.password),
            "role": user_data.role,
            "nombre": user_data.nombre,
            "apellido": user_data.apellido,
            "codigo_institucional": codigo,
            "fecha_nacimiento": user_data.fecha_nacimiento,
        }
        
        # Add optional fields only if they are provided
        if user_data.numero_contacto is not None:
            user_dict["numero_contacto"] = user_data.numero_contacto
        
        # Role-specific fields
        from app.models.user import UserRole
        if user_data.role == UserRole.ESTUDIANTE:
            if user_data.programa_academico is not None:
                user_dict["programa_academico"] = user_data.programa_academico
            if user_data.ciudad_residencia is not None:
                user_dict["ciudad_residencia"] = user_data.ciudad_residencia
        elif user_data.role == UserRole.PROFESOR:
            if user_data.area_ensenanza is not None:
                user_dict["area_ensenanza"] = user_data.area_ensenanza
        
        # Create user
        user = await self.repository.create(user_dict)
        
        # Calculate and set age
        calculated_age = user.calcular_edad()
        # Use setattr to avoid mypy Column type issues
        setattr(user, 'edad', calculated_age)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID.
        
        Args:
            user_id: User ID
        
        Returns:
            User or None
        """
        return await self.repository.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email.
        
        Args:
            email: User email
        
        Returns:
            User or None
        """
        return await self.repository.get_by_email(email)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        """Update user with business logic.
        
        Args:
            user_id: User ID
            user_data: User update data
        
        Returns:
            Updated user or None
        """
        # Convert Pydantic model to dict (exclude None values)
        update_dict = user_data.model_dump(exclude_unset=True)
        
        # If fecha_nacimiento is updated, recalculate age
        if "fecha_nacimiento" in update_dict:
            user = await self.repository.get_by_id(user_id)
            if user:
                user.fecha_nacimiento = update_dict["fecha_nacimiento"]
                update_dict["edad"] = user.calcular_edad()
        
        return await self.repository.update(user_id, update_dict)
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user.
        
        Args:
            user_id: User ID
        
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(user_id)
    
    async def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> list[User]:
        """Get users by role.
        
        Args:
            role: User role
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of users
        """
        return await self.repository.get_by_role(role, skip, limit)


