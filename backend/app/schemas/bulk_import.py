"""Schemas for bulk import/export of students via Excel."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# Required Excel columns per plan (CON-001: only Estudiante)
REQUIRED_EXCEL_COLUMNS = [
    "email",
    "password",
    "nombre",
    "apellido",
    "rol",
    "fecha_nacimiento",
    "numero_contacto",
    "programa_academico",
    "ciudad_residencia",
]


class EstudianteImportRow(BaseModel):
    """Schema for one row of student import from Excel."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    rol: str = Field(..., description="Must be 'Estudiante'")
    fecha_nacimiento: date
    numero_contacto: str = Field(..., min_length=10, max_length=20)
    programa_academico: str = Field(..., min_length=1, max_length=200)
    ciudad_residencia: str = Field(..., min_length=1, max_length=100)

    @field_validator("rol")
    @classmethod
    def rol_must_be_estudiante(cls, v: str) -> str:
        if v != "Estudiante":
            raise ValueError("Solo se permite rol 'Estudiante' en importación masiva")
        return v

    @field_validator("fecha_nacimiento")
    @classmethod
    def fecha_no_futura(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        return v


class BulkImportError(BaseModel):
    """Detail of an error for a specific row."""

    row: int
    field: str
    message: str
    value: Optional[str] = None


class BulkImportResult(BaseModel):
    """Result of a bulk import: created, updated, errors."""

    created: int = 0
    updated: int = 0
    errors: list[BulkImportError] = Field(default_factory=list)
