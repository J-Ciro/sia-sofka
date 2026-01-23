"""User model."""

from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date, datetime
import enum
import uuid
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles enum."""
    ADMIN = "Admin"
    PROFESOR = "Profesor"
    ESTUDIANTE = "Estudiante"


class User(Base):
    """User model for all roles (Admin, Profesor, Estudiante)."""
    
    __tablename__ = "users"
    
    # Technical identifier (UUID) - for backend use
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=False,
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False
    )
    
    # User-friendly identifier (Integer) - for easy identification by users
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    
    # Personal information
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    codigo_institucional = Column(String, unique=True, index=True, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    edad = Column(Integer, nullable=True)  # Can be calculated or stored
    numero_contacto = Column(String, nullable=True)
    
    # Fields specific to Estudiante
    programa_academico = Column(String, nullable=True)
    ciudad_residencia = Column(String, nullable=True)
    
    # Fields specific to Profesor
    area_ensenanza = Column(String, nullable=True)
    
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
    subjects = relationship(
        "Subject",
        back_populates="profesor",
        foreign_keys="Subject.profesor_id"
    )
    enrollments = relationship(
        "Enrollment",
        back_populates="estudiante",
        foreign_keys="Enrollment.estudiante_id"
    )
    clase_sessions_creadas = relationship(
        "ClaseSession",
        back_populates="creado_por_user",
        foreign_keys="ClaseSession.creado_por"
    )
    attendances = relationship(
        "Attendance",
        back_populates="estudiante",
        foreign_keys="Attendance.estudiante_id"
    )
    attendance_stats = relationship(
        "AttendanceStats",
        back_populates="estudiante",
        foreign_keys="AttendanceStats.estudiante_id"
    )
    attendance_alerts = relationship(
        "AttendanceAlert",
        back_populates="estudiante",
        foreign_keys="AttendanceAlert.estudiante_id"
    )
    
    def calcular_edad(self) -> int:
        """Calculate age from fecha_nacimiento."""
        if not self.fecha_nacimiento:
            return 0
        today = date.today()
        age = today.year - self.fecha_nacimiento.year
        if (today.month, today.day) < (
            self.fecha_nacimiento.month,
            self.fecha_nacimiento.day,
        ):
            age -= 1
        return age

