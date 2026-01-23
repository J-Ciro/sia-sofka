"""Attendance Service - Business logic for attendance operations."""

from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta
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
from app.utils.attendance_validators import SessionValidator, AttendanceCalculator


class AttendanceService:
    """Service for attendance-related business logic."""
    
    def __init__(self, db: AsyncSession, usuario_autenticado: Optional[User] = None):
        """Initialize attendance service.
        
        Args:
            db: Database session (async only)
            usuario_autenticado: Authenticated user making the request
        """
        self.db = db
        self.usuario_autenticado = usuario_autenticado
        self.attendance_repo = AttendanceRepository(db)
    
    async def create_clase_session(
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
        
        # Use validators (SOLID - Single Responsibility)
        SessionValidator.validate_date(fecha)
        SessionValidator.validate_time_range(hora_inicio, hora_fin)
        
        # Evitar sesiones que se solapen en hora para la misma materia y fecha.
        # El profesor SÍ puede crear varias sesiones al día (varias materias o misma materia
        # en horarios no solapados); si quiere cambiar una existente, debe editarla.
        overlapping = await self.attendance_repo.find_overlapping_sessions(
            subject_id, fecha, hora_inicio, hora_fin
        )
        SessionValidator.validate_no_overlapping_session(
            overlapping, subject_id, fecha, hora_inicio, hora_fin
        )
        
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
        await self.db.flush()  # Flush to get ID without committing yet
        
        # Create attendance records for all enrolled students
        from app.models.enrollment import Enrollment
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(Enrollment).where(Enrollment.subject_id == subject_id)
        )
        enrollments = result.scalars().all()
        
        # Create attendance records with default state AUSENTE
        for enrollment in enrollments:
            attendance = Attendance(
                clase_session_id=clase_session.id,
                estudiante_id=enrollment.estudiante_id,
                estado=AttendanceStatus.AUSENTE
            )
            self.db.add(attendance)
        
        await self.db.commit()
        await self.db.refresh(clase_session)
        
        return clase_session
    
    async def mark_all_present(self, clase_session_id: int) -> int:
        """Mark all enrolled students in a session as present.
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Number of students marked
        """
        from sqlalchemy import select
        from app.models.enrollment import Enrollment
        
        stmt = select(ClaseSession).where(ClaseSession.id == clase_session_id)
        result = await self.db.execute(stmt)
        clase_session = result.scalar_one_or_none()
        
        if not clase_session:
            raise NotFoundError("ClaseSession", clase_session_id)
        
        # Get all enrolled students for the subject
        enrollment_stmt = select(Enrollment).where(
            Enrollment.subject_id == clase_session.subject_id
        )
        enrollment_result = await self.db.execute(enrollment_stmt)
        enrollments = enrollment_result.scalars().all()
        
        count = 0
        for enrollment in enrollments:
            # Check if attendance already exists
            existing = await self.attendance_repo.get_by_session_and_student(
                clase_session_id,
                enrollment.estudiante_id,
            )
            
            if existing:
                # Update existing using AbstractRepository.update
                await self.attendance_repo.update(
                    existing.id,
                    {"estado": AttendanceStatus.PRESENTE}
                )
            else:
                # Create new using AbstractRepository.create
                await self.attendance_repo.create({
                    "clase_session_id": clase_session_id,
                    "estudiante_id": enrollment.estudiante_id,
                    "estado": AttendanceStatus.PRESENTE,
                })
            count += 1
        
        return count
    
    async def mark_all_absent(self, clase_session_id: int) -> int:
        """Mark all enrolled students in a session as absent.
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Number of students marked
        """
        from sqlalchemy import select
        from app.models.enrollment import Enrollment
        
        stmt = select(ClaseSession).where(ClaseSession.id == clase_session_id)
        result = await self.db.execute(stmt)
        clase_session = result.scalar_one_or_none()
        
        if not clase_session:
            raise NotFoundError("ClaseSession", clase_session_id)
        
        # Get all enrolled students
        enrollment_stmt = select(Enrollment).where(
            Enrollment.subject_id == clase_session.subject_id
        )
        enrollment_result = await self.db.execute(enrollment_stmt)
        enrollments = enrollment_result.scalars().all()
        
        count = 0
        for enrollment in enrollments:
            existing = await self.attendance_repo.get_by_session_and_student(
                clase_session_id,
                enrollment.estudiante_id,
            )
            
            if existing:
                await self.attendance_repo.update(
                    existing.id,
                    {"estado": AttendanceStatus.AUSENTE}
                )
            else:
                await self.attendance_repo.create({
                    "clase_session_id": clase_session_id,
                    "estudiante_id": enrollment.estudiante_id,
                    "estado": AttendanceStatus.AUSENTE,
                })
            count += 1
        
        return count
    
    async def update_attendance(
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
        attendance = await self.attendance_repo.get_by_id(attendance_id)
        
        if not attendance:
            raise NotFoundError("Attendance", attendance_id)
        
        return await self.attendance_repo.update(attendance_id, {"estado": estado})
    
    async def get_session_statistics(self, clase_session_id: int) -> Dict[str, Any]:
        """Get attendance statistics for a session.
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Dictionary with statistics
        """
        counts = await self.attendance_repo.count_by_status_async(clase_session_id)
        percentage = await self.attendance_repo.calculate_attendance_percentage_async(clase_session_id)
        
        total = sum(counts.values())
        
        return {
            "total": total,
            "presentes": counts.get(AttendanceStatus.PRESENTE, 0),
            "tardanzas": counts.get(AttendanceStatus.TARDANZA, 0),
            "ausentes": counts.get(AttendanceStatus.AUSENTE, 0),
            "porcentaje_asistencia": percentage,
        }
    
    async def create_attendance_stats(
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
        from sqlalchemy import select
        
        # Calculate percentage
        valid_attendance = presentes + tardanzas
        porcentaje = (valid_attendance / total_sesiones * 100) if total_sesiones > 0 else 0.0
        
        # Check if stats already exist
        stmt = select(AttendanceStats).where(
            AttendanceStats.estudiante_id == estudiante_id,
            AttendanceStats.subject_id == subject_id,
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing
            existing.total_sesiones = total_sesiones
            existing.presentes = presentes
            existing.ausentes = ausentes
            existing.tardanzas = tardanzas
            existing.porcentaje_asistencia = porcentaje
            await self.db.commit()
            await self.db.refresh(existing)
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
            await self.db.commit()
            await self.db.refresh(stats)
            return stats
