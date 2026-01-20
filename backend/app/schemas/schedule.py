"""Schedule and Classroom schemas - horarios-calendario."""

from datetime import time
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


# --- Horas límite (CON-001, CON-002) ---
HORA_MIN = time(6, 0)   # 6:00 AM
HORA_MAX = time(22, 0)  # 10:00 PM
DURACION_MIN_MINUTOS = 60   # 1 hora
DURACION_MAX_MINUTOS = 240  # 4 horas


def _time_to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


class ScheduleBase(BaseModel):
    """Base schedule schema."""
    subject_id: int = Field(..., gt=0)
    classroom_id: int = Field(..., gt=0)
    dia_semana: int = Field(..., ge=1, le=6, description="1=Lunes..6=Sábado")
    hora_inicio: time
    hora_fin: time

    @field_validator("hora_fin")
    @classmethod
    def hora_fin_after_inicio(cls, v: time, info):
        if "hora_inicio" in info.data and v <= info.data["hora_inicio"]:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        return v

    @field_validator("hora_inicio", "hora_fin")
    @classmethod
    def hora_en_rango(cls, v: time):
        m = _time_to_minutes(v)
        if m < _time_to_minutes(HORA_MIN) or m > _time_to_minutes(HORA_MAX):
            raise ValueError("Las horas deben estar entre 6:00 y 22:00")
        return v

    @field_validator("hora_fin", mode="after")
    @classmethod
    def duracion_valida(cls, v: time, info):
        if "hora_inicio" not in info.data:
            return v
        hi = info.data["hora_inicio"]
        dur = _time_to_minutes(v) - _time_to_minutes(hi)
        if dur < DURACION_MIN_MINUTOS:
            raise ValueError("La clase debe durar al menos 1 hora")
        if dur > DURACION_MAX_MINUTOS:
            raise ValueError("La clase no puede durar más de 4 horas")
        return v


class ScheduleCreate(ScheduleBase):
    """Schema for creating a schedule."""


class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule."""
    subject_id: Optional[int] = Field(None, gt=0)
    classroom_id: Optional[int] = Field(None, gt=0)
    dia_semana: Optional[int] = Field(None, ge=1, le=6)
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None


# --- Anidados para respuesta ---
class SubjectNested(BaseModel):
    id: int
    nombre: str
    codigo_institucional: str
    profesor_id: int
    model_config = ConfigDict(from_attributes=True)


class ClassroomNested(BaseModel):
    id: int
    codigo: str
    nombre: str
    capacidad: int
    ubicacion: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""
    id: int
    codigo: str
    subject_id: int
    classroom_id: int
    dia_semana: int
    hora_inicio: time
    hora_fin: time
    subject: Optional[SubjectNested] = None
    classroom: Optional[ClassroomNested] = None
    model_config = ConfigDict(from_attributes=True)


# --- Classroom (para listados y formularios) ---
class ClassroomCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=200)
    capacidad: int = Field(..., gt=0, le=500)
    ubicacion: Optional[str] = None


class ClassroomResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    capacidad: int
    ubicacion: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
