"""Attendance Service - Business logic for attendance operations."""

from typing import Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.attendance import (
    ClaseSession,
    Attendance,
    AttendanceStatus,
    AttendanceStats,
    AttendanceAlert,
)
from app.repositories.attendance_repository import AttendanceRepository
from app.core.exceptions import NotFoundError, ValidationError, UnauthorizedError


class AttendanceService:
    """Service for attendance-related business logic."""
    
    def __init__(self, db: Union[Session, AsyncSession], usuario_autenticado: Optional[User] = None):
        """Initialize attendance service.
        
        Args:
            db: Database session
            usuario_autenticado: Authenticated user making the request
        """
        self.db = db
        self.usuario_autenticado = usuario_autenticado
        self.attendance_repo = AttendanceRepository(db)
    
    def create_clase_session(
        self,
        subject_id: int,
        fecha: date,
        hora_inicio: datetime,
        hora_fin: datetime,
        descripcion: Optional[str] = None,
    ) -> ClaseSession:
        """Create a new clase session.
        
        Args:
            subject_id: Subject ID
            fecha: Date of the class
            hora_inicio: Start time
            hora_fin: End time
            descripcion: Optional description
        
        Returns:
            Created ClaseSession instance
        
        Raises:
            ValidationError: If validation fails
            UnauthorizedError: If user is not authorized
        """
        # Validate that user is a professor
        if self.usuario_autenticado.role != "Profesor":
            raise UnauthorizedError("Solo profesores pueden crear sesiones de clase")
        
        # Validate date is not in the future
        if fecha > date.today():
            raise ValidationError("No se puede crear asistencia para fechas futuras")
        
        # Validate time ordering
        if hora_fin <= hora_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la hora de inicio")
        
        # Create session
        clase_session = ClaseSession(
            subject_id=subject_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            descripcion=descripcion,
            creado_por=self.usuario_autenticado.id,
        )
        
        self.db.add(clase_session)
        self.db.commit()
        self.db.refresh(clase_session)
        
        return clase_session
    
    def mark_all_present(self, clase_session_id: int) -> int:
        """Mark all enrolled students in a session as present.
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Number of students marked
        """
        clase_session = self.db.query(ClaseSession).filter(
            ClaseSession.id == clase_session_id
        ).first()
        
        if not clase_session:
            raise NotFoundError("ClaseSession", clase_session_id)
        
        # Get all enrolled students for the subject
        from app.models.enrollment import Enrollment
        enrollments = self.db.query(Enrollment).filter(
            Enrollment.subject_id == clase_session.subject_id
        ).all()
        
        count = 0
        for enrollment in enrollments:
            # Check if attendance already exists
            existing = self.attendance_repo.get_by_session_and_student(
                clase_session_id,
                enrollment.estudiante_id,
            )
            
            if existing:
                # Update existing
                self.attendance_repo.update(
                    existing.id,
                    estado=AttendanceStatus.PRESENTE,
                )
            else:
                # Create new
                self.attendance_repo.create(
                    clase_session_id=clase_session_id,
                    estudiante_id=enrollment.estudiante_id,
                    estado=AttendanceStatus.PRESENTE,
                )
            count += 1
        
        return count
    
    def mark_all_absent(self, clase_session_id: int) -> int:
        """Mark all enrolled students in a session as absent.
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Number of students marked
        """
        clase_session = self.db.query(ClaseSession).filter(
            ClaseSession.id == clase_session_id
        ).first()
        
        if not clase_session:
            raise NotFoundError("ClaseSession", clase_session_id)
        
        # Get all enrolled students
        from app.models.enrollment import Enrollment
        enrollments = self.db.query(Enrollment).filter(
            Enrollment.subject_id == clase_session.subject_id
        ).all()
        
        count = 0
        for enrollment in enrollments:
            existing = self.attendance_repo.get_by_session_and_student(
                clase_session_id,
                enrollment.estudiante_id,
            )
            
            if existing:
                self.attendance_repo.update(
                    existing.id,
                    estado=AttendanceStatus.AUSENTE,
                )
            else:
                self.attendance_repo.create(
                    clase_session_id=clase_session_id,
                    estudiante_id=enrollment.estudiante_id,
                    estado=AttendanceStatus.AUSENTE,
                )
            count += 1
        
        return count
    
    def update_attendance(
        self,
        attendance_id: int,
        estado: AttendanceStatus,
    ) -> Attendance:
        """Update attendance status.
        
        Args:
            attendance_id: Attendance ID
            estado: New status
        
        Returns:
            Updated Attendance instance
        
        Raises:
            NotFoundError: If attendance not found
        """
        attendance = self.attendance_repo.get_by_id(attendance_id)
        
        if not attendance:
            raise NotFoundError("Attendance", attendance_id)
        
        return self.attendance_repo.update(attendance_id, estado=estado)
    
    def get_session_statistics(self, clase_session_id: int) -> Dict[str, Any]:
        """Get attendance statistics for a session.
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Dictionary with statistics
        """
        counts = self.attendance_repo.count_by_status(clase_session_id)
        percentage = self.attendance_repo.calculate_attendance_percentage(clase_session_id)
        
        total = sum(counts.values())
        
        return {
            "total": total,
            "presentes": counts.get(AttendanceStatus.PRESENTE, 0),
            "tardanzas": counts.get(AttendanceStatus.TARDANZA, 0),
            "ausentes": counts.get(AttendanceStatus.AUSENTE, 0),
            "porcentaje_asistencia": percentage,
        }
    
    def create_attendance_stats(
        self,
        estudiante_id: int,
        subject_id: int,
        total_sesiones: int,
        presentes: int,
        ausentes: int,
        tardanzas: int,
    ) -> AttendanceStats:
        """Create or update attendance statistics.
        
        Args:
            estudiante_id: Student ID
            subject_id: Subject ID
            total_sesiones: Total sessions
            presentes: Present count
            ausentes: Absent count
            tardanzas: Late count
        
        Returns:
            AttendanceStats instance
        """
        # Calculate percentage
        valid_attendance = presentes + tardanzas
        porcentaje = (valid_attendance / total_sesiones * 100) if total_sesiones > 0 else 0.0
        
        # Check if stats already exist
        existing = self.db.query(AttendanceStats).filter(
            AttendanceStats.estudiante_id == estudiante_id,
            AttendanceStats.subject_id == subject_id,
        ).first()
        
        if existing:
            # Update existing
            existing.total_sesiones = total_sesiones
            existing.presentes = presentes
            existing.ausentes = ausentes
            existing.tardanzas = tardanzas
            existing.porcentaje_asistencia = porcentaje
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new
            stats = AttendanceStats(
                estudiante_id=estudiante_id,
                subject_id=subject_id,
                total_sesiones=total_sesiones,
                presentes=presentes,
                ausentes=ausentes,
                tardanzas=tardanzas,
                porcentaje_asistencia=porcentaje,
            )
            self.db.add(stats)
            self.db.commit()
            self.db.refresh(stats)
            return stats
