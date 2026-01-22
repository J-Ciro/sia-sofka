"""Enrollment schemas."""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EnrollmentBase(BaseModel):
    """Base enrollment schema."""
    estudiante_id: int
    subject_id: int


class EnrollmentCreate(EnrollmentBase):
    """Schema for creating an enrollment."""
    pass


# Schemas anidados simplificados para las relaciones
class EstudianteInfo(BaseModel):
    """Información básica del estudiante."""
    id: int
    nombre: str
    apellido: str
    codigo_institucional: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)


class SubjectInfo(BaseModel):
    """Información básica de la materia."""
    id: int
    nombre: str
    codigo_institucional: str
    numero_creditos: int
    
    model_config = ConfigDict(from_attributes=True)


class EnrollmentResponse(EnrollmentBase):
    """Schema for enrollment response."""
    id: int
    created_at: Optional[datetime] = None
    
    # Nested models
    estudiante: Optional[EstudianteInfo] = None
    subject: Optional[SubjectInfo] = None
    
    model_config = ConfigDict(from_attributes=True)


