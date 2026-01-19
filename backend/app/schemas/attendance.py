"""Pydantic schemas for Attendance feature.

Schemas for request validation and response serialization
for the manual attendance tracking system.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.models.attendance import AttendanceStatus


class ClaseSessionCreate(BaseModel):
    """Schema for creating a new class session."""
    
    subject_id: int = Field(..., description="ID of the subject")
    fecha: date = Field(..., description="Date of the class session")
    hora_inicio: datetime = Field(..., description="Start time of the class")
    hora_fin: datetime = Field(..., description="End time of the class")
    descripcion: Optional[str] = Field(None, description="Optional description or topic")
    
    model_config = {"from_attributes": True}


class ClaseSessionResponse(BaseModel):
    """Schema for class session response."""
    
    id: int
    subject_id: int
    fecha: date
    hora_inicio: datetime
    hora_fin: datetime
    descripcion: Optional[str]
    creado_por: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class AttendanceCreate(BaseModel):
    """Schema for creating attendance record."""
    
    clase_session_id: int = Field(..., description="ID of the class session")
    estudiante_id: int = Field(..., description="ID of the student")
    estado: AttendanceStatus = Field(
        default=AttendanceStatus.PRESENTE,
        description="Attendance status"
    )
    
    model_config = {"from_attributes": True}


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance status."""
    
    estudiante_id: int = Field(..., description="Student ID")
    estado: AttendanceStatus = Field(..., description="New attendance status")
    
    model_config = {"from_attributes": True}


class AttendanceResponse(BaseModel):
    """Schema for attendance response."""
    
    id: int
    clase_session_id: int
    estudiante_id: int
    estado: AttendanceStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class SessionStatisticsResponse(BaseModel):
    """Schema for session statistics response."""
    
    total: int = Field(..., description="Total number of students")
    presentes: int = Field(..., description="Number of present students")
    tardanzas: int = Field(..., description="Number of late students")
    ausentes: int = Field(..., description="Number of absent students")
    porcentaje_asistencia: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Attendance percentage (0-100)"
    )
    
    model_config = {"from_attributes": True}


class AttendanceStatsResponse(BaseModel):
    """Schema for attendance statistics response."""
    
    id: int
    estudiante_id: int
    subject_id: int
    total_sesiones: int = Field(..., description="Total class sessions")
    presentes: int = Field(..., description="Number of times present")
    ausentes: int = Field(..., description="Number of times absent")
    tardanzas: int = Field(..., description="Number of times late")
    porcentaje_asistencia: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Attendance percentage (0-100)"
    )
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
