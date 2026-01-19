"""Attendance-related models for manual attendance tracking."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date, time
import enum
from app.core.database import Base


class AttendanceStatus(str, enum.Enum):
    """Attendance status enum."""
    PRESENTE = "Presente"
    AUSENTE = "Ausente"
    TARDANZA = "Tardanza"


class ClaseSession(Base):
    """Class session model - represents a single class session."""
    
    __tablename__ = "clase_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    hora_inicio = Column(DateTime, nullable=False)
    hora_fin = Column(DateTime, nullable=False)
    descripcion = Column(String, nullable=True)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=False)
    
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
    subject = relationship(
        "Subject",
        back_populates="clase_sessions",
        foreign_keys=[subject_id]
    )
    creado_por_user = relationship(
        "User",
        back_populates="clase_sessions_creadas",
        foreign_keys=[creado_por]
    )
    attendances = relationship(
        "Attendance",
        back_populates="clase_session",
        cascade="all, delete-orphan"
    )


class Attendance(Base):
    """Attendance model - represents a student's attendance in a session."""
    
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    clase_session_id = Column(Integer, ForeignKey("clase_sessions.id"), nullable=False, index=True)
    estudiante_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    estado = Column(SQLEnum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENTE)
    
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
    
    # Unique constraint: student can only have one attendance per session
    __table_args__ = (
        __import__('sqlalchemy').UniqueConstraint(
            "clase_session_id", "estudiante_id", 
            name="uq_attendance_per_session"
        ),
    )
    
    # Relationships
    clase_session = relationship(
        "ClaseSession",
        back_populates="attendances",
        foreign_keys=[clase_session_id]
    )
    estudiante = relationship(
        "User",
        back_populates="attendances",
        foreign_keys=[estudiante_id]
    )


class AttendanceStats(Base):
    """Attendance statistics model - aggregated attendance data per student per subject."""
    
    __tablename__ = "attendance_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    total_sesiones = Column(Integer, nullable=False, default=0)
    presentes = Column(Integer, nullable=False, default=0)
    ausentes = Column(Integer, nullable=False, default=0)
    tardanzas = Column(Integer, nullable=False, default=0)
    porcentaje_asistencia = Column(Float, nullable=False, default=0.0)
    
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
    
    # Unique constraint: one stats record per student per subject
    __table_args__ = (
        __import__('sqlalchemy').UniqueConstraint(
            "estudiante_id", "subject_id",
            name="uq_stats_per_student_subject"
        ),
    )
    
    # Relationships
    estudiante = relationship(
        "User",
        back_populates="attendance_stats",
        foreign_keys=[estudiante_id]
    )
    subject = relationship(
        "Subject",
        back_populates="attendance_stats",
        foreign_keys=[subject_id]
    )


class AttendanceAlert(Base):
    """Attendance alert model - alerts for students with low attendance."""
    
    __tablename__ = "attendance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    nivel = Column(String, nullable=False)  # "warning" or "critical"
    porcentaje_asistencia = Column(Float, nullable=False)
    descripcion = Column(String, nullable=True)
    resuelta_en = Column(DateTime, nullable=True)
    
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
    estudiante = relationship(
        "User",
        back_populates="attendance_alerts",
        foreign_keys=[estudiante_id]
    )
    subject = relationship(
        "Subject",
        back_populates="attendance_alerts",
        foreign_keys=[subject_id]
    )
