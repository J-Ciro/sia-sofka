"""Subject model."""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Subject(Base):
    """Subject (Materia) model."""
    
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    codigo_institucional = Column(String, unique=True, index=True, nullable=False)
    numero_creditos = Column(Integer, nullable=False)
    horario = Column(String, nullable=True)
    descripcion = Column(Text, nullable=True)
    
    # Foreign key to profesor
    profesor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    profesor = relationship(
        "User",
        back_populates="subjects",
        foreign_keys=[profesor_id]
    )
    enrollments = relationship(
        "Enrollment",
        back_populates="subject",
        cascade="all, delete-orphan"
    )
    clase_sessions = relationship(
        "ClaseSession",
        back_populates="subject",
        cascade="all, delete-orphan"
    )
    attendance_stats = relationship(
        "AttendanceStats",
        back_populates="subject",
        cascade="all, delete-orphan"
    )
    attendance_alerts = relationship(
        "AttendanceAlert",
        back_populates="subject",
        cascade="all, delete-orphan"
    )
    schedules = relationship(
        "Schedule",
        back_populates="subject",
        cascade="all, delete-orphan",
    )

