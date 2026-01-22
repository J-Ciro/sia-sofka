"""Schedule and Classroom models for class scheduling.

Implements TASK-001 (Classroom), TASK-002 (Schedule), TASK-003 (unique constraint),
TASK-004 (indexes). Feature: horarios-calendario.
"""

import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Time,
    Date,
    DateTime,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


def _generar_codigo_horario() -> str:
    """Genera código único para horario (HU-01)."""
    return f"HOR-{uuid.uuid4().hex[:8].upper()}"


class Classroom(Base):
    """Classroom (aula) model - TASK-001.

    Capacidad y ubicación para validación de conflictos de salón (HU-02).
    """

    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    capacidad = Column(Integer, nullable=False)
    ubicacion = Column(String, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    schedules = relationship(
        "Schedule",
        back_populates="classroom",
        cascade="all, delete-orphan",
    )


class Schedule(Base):
    """Schedule model - TASK-002.

    Horario de clase con asignatura, aula, día de semana y rango de hora.
    Profesor se obtiene vía Subject.profesor_id (REQ-001, REQ-002, REQ-003).
    """

    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        default=_generar_codigo_horario,
    )
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    dia_semana = Column(Integer, nullable=False, index=True)  # 1=Lunes .. 6=Sábado
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    
    # New field for specific date scheduling (nullable for backward compatibility)
    fecha_especifica = Column(Date, nullable=True, index=True)

    # Timestamps
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # TASK-003: unique (asignatura_id, dia_semana, hora_inicio) - only for weekly schedules
    # New constraint for date-specific schedules
    __table_args__ = (
        UniqueConstraint(
            "subject_id",
            "dia_semana", 
            "hora_inicio",
            name="uq_schedule_subject_dia_hora",
        ),
        UniqueConstraint(
            "subject_id",
            "fecha_especifica",
            "hora_inicio", 
            name="uq_schedule_subject_fecha_hora",
        ),
        # TASK-004: índice para consultas de solapamiento por aula
        Index("ix_schedule_classroom_dia_hora", "classroom_id", "dia_semana", "hora_inicio"),
        # New index for date-specific queries
        Index("ix_schedule_classroom_fecha_hora", "classroom_id", "fecha_especifica", "hora_inicio"),
    )

    # Relationships
    subject = relationship(
        "Subject",
        back_populates="schedules",
        foreign_keys=[subject_id],
    )
    classroom = relationship(
        "Classroom",
        back_populates="schedules",
        foreign_keys=[classroom_id],
    )
