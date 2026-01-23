"""User schemas."""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from app.models.user import UserRole
from app.core.sanitizers import validate_email


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    fecha_nacimiento: date
    numero_contacto: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate and normalize email address."""
        return validate_email(v)


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=6)
    role: UserRole
    programa_academico: Optional[str] = None  # For Estudiante
    ciudad_residencia: Optional[str] = None  # For Estudiante
    area_ensenanza: Optional[str] = None  # For Profesor


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    fecha_nacimiento: Optional[date] = None
    numero_contacto: Optional[str] = None
    programa_academico: Optional[str] = None
    ciudad_residencia: Optional[str] = None
    area_ensenanza: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""
    uuid: UUID  # Technical identifier (UUID) - for backend use
    id: int  # User-friendly identifier (Integer) - for easy identification by users
    role: UserRole
    codigo_institucional: str
    edad: Optional[int] = None
    programa_academico: Optional[str] = None
    ciudad_residencia: Optional[str] = None
    area_ensenanza: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

