"""Attendance Repository - Data access layer for attendance operations."""

from datetime import date, datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.models.attendance import (
    Attendance,
    AttendanceStatus,
    ClaseSession,
)
from app.repositories.base import AbstractRepository
from app.repositories.mixins import EagerLoadMixin, PaginationMixin
from app.core.decorators import handle_repository_errors


class AttendanceRepository(AbstractRepository[Attendance], EagerLoadMixin, PaginationMixin):
    """Repository for Attendance model operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize attendance repository.
        
        Args:
            db: Database session (async only)
        """
        super().__init__(db, Attendance)
    
    # CRUD methods (create, get_by_id, update, delete) come from AbstractRepository
    
    @handle_repository_errors
    async def get_by_session_and_student(
        self,
        clase_session_id: int,
        estudiante_id: int,
    ) -> Optional[Attendance]:
        """Get attendance for a specific student in a specific session.
        
        Args:
            clase_session_id: ID of the clase session
            estudiante_id: ID of the student
        
        Returns:
            Attendance instance or None
        """
        return await self._get_one_with_relations(
            Attendance,
            and_(
                Attendance.clase_session_id == clase_session_id,
                Attendance.estudiante_id == estudiante_id,
            ),
            use_joined=['clase_session', 'estudiante']
        )
    
    @handle_repository_errors
    async def get_all_by_session(
        self, 
        clase_session_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[Attendance]:
        """Get all attendance records for a specific session.
        
        Args:
            clase_session_id: ID of the clase session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Attendance instances
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        return await self._get_many_with_relations(
            Attendance,
            Attendance.clase_session_id == clase_session_id,
            use_joined=['clase_session', 'estudiante'],
            skip=skip,
            limit=limit
        )
    
    @handle_repository_errors
    async def get_by_student_and_subject(
        self,
        estudiante_id: int,
        subject_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Attendance]:
        """Get all attendance records for a student in a specific subject.
        
        Args:
            estudiante_id: ID of the student
            subject_id: ID of the subject
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Attendance instances
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        from sqlalchemy.orm import joinedload
        
        # Use direct query with join since we need to join ClaseSession
        stmt = (
            select(Attendance)
            .join(ClaseSession, Attendance.clase_session_id == ClaseSession.id)
            .where(
                Attendance.estudiante_id == estudiante_id,
                ClaseSession.subject_id == subject_id,
            )
            .options(
                joinedload(Attendance.clase_session),
                joinedload(Attendance.estudiante)
            )
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    # Async methods for FastAPI endpoints
    
    @handle_repository_errors
    async def get_sessions_by_profesor(
        self,
        profesor_id: int,
        subject_id: Optional[int] = None,
    ) -> list[ClaseSession]:
        """Get all clase sessions created by a profesor.
        
        Args:
            profesor_id: Profesor user ID
            subject_id: Optional subject ID filter
        
        Returns:
            List of ClaseSession instances
        """
        query = select(ClaseSession).where(ClaseSession.creado_por == profesor_id)
        
        if subject_id:
            query = query.where(ClaseSession.subject_id == subject_id)
        
        query = query.order_by(ClaseSession.fecha.desc(), ClaseSession.hora_inicio.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    @handle_repository_errors
    async def get_sessions_for_student(
        self,
        estudiante_id: int,
        subject_id: Optional[int] = None,
    ) -> list[ClaseSession]:
        """Get all clase sessions for a student's enrolled subjects.
        
        Args:
            estudiante_id: Student user ID
            subject_id: Optional subject ID filter
        
        Returns:
            List of ClaseSession instances
        """
        from app.models.enrollment import Enrollment
        
        # Get enrolled subject IDs
        enrollment_query = select(Enrollment.subject_id).where(
            Enrollment.estudiante_id == estudiante_id
        )
        
        if subject_id:
            enrollment_query = enrollment_query.where(Enrollment.subject_id == subject_id)
        
        result = await self.db.execute(enrollment_query)
        enrolled_subject_ids = [row[0] for row in result.all()]
        
        if not enrolled_subject_ids:
            return []
        
        # Get sessions for enrolled subjects
        query = select(ClaseSession).where(
            ClaseSession.subject_id.in_(enrolled_subject_ids)  # type: ignore[arg-type]
        ).order_by(ClaseSession.fecha.desc(), ClaseSession.hora_inicio.desc())
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        return list(sessions)
    
    @handle_repository_errors
    async def get_attendances_by_session(
        self, 
        clase_session_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[Attendance]:
        """Get all attendance records for a session (async version).
        
        Args:
            clase_session_id: ClaseSession ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Attendance instances
        """
        skip, limit = self._validate_pagination(skip, limit)
        
        return await self._get_many_with_relations(
            Attendance,
            Attendance.clase_session_id == clase_session_id,
            use_joined=['clase_session', 'estudiante'],
            skip=skip,
            limit=limit
        )
    
    @handle_repository_errors
    async def count_by_status_async(self, clase_session_id: int) -> Dict[AttendanceStatus, int]:
        """Count attendance records by status for a session (async version).
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Dictionary with counts by status
        """
        attendances = await self.get_attendances_by_session(clase_session_id)
        
        counts = {
            AttendanceStatus.PRESENTE: 0,
            AttendanceStatus.AUSENTE: 0,
            AttendanceStatus.TARDANZA: 0,
        }
        
        for attendance in attendances:
            counts[attendance.estado] += 1
        
        return counts
    
    @handle_repository_errors
    async def calculate_attendance_percentage_async(self, clase_session_id: int) -> float:
        """Calculate attendance percentage for a session (async version).
        
        Attendance percentage = (PRESENTE + TARDANZA) / TOTAL * 100
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Attendance percentage (0-100)
        """
        attendances = await self.get_attendances_by_session(clase_session_id)
        
        if not attendances:
            return 0.0
        
        present_or_late = sum(
            1 for a in attendances
            if a.estado in (AttendanceStatus.PRESENTE, AttendanceStatus.TARDANZA)
        )
        
        return (present_or_late / len(attendances)) * 100
    
    @handle_repository_errors
    async def get_student_history_by_subject(
        self,
        estudiante_id: int,
        subject_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Attendance]:
        """Asistencia del estudiante en una materia, con ClaseSession. Orden: sesión más reciente primero."""
        skip, limit = self._validate_pagination(skip, limit)
        
        condition = and_(
            Attendance.estudiante_id == estudiante_id,
            ClaseSession.subject_id == subject_id,
        )
        
        from sqlalchemy.orm import joinedload
        
        # Use direct query with join and order by
        stmt = (
            select(Attendance)
            .join(ClaseSession, Attendance.clase_session_id == ClaseSession.id)
            .where(
                Attendance.estudiante_id == estudiante_id,
                ClaseSession.subject_id == subject_id,
            )
            .options(
                joinedload(Attendance.clase_session)
            )
            .order_by(desc(ClaseSession.fecha), desc(ClaseSession.hora_inicio))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    @handle_repository_errors
    async def get_session_by_subject_and_date(
        self,
        subject_id: int,
        fecha: date,
    ) -> Optional[ClaseSession]:
        """Check if session exists for subject on given date.
        
        Args:
            subject_id: Subject ID
            fecha: Date to check
        
        Returns:
            ClaseSession if exists, None otherwise
        """
        query = select(ClaseSession).where(
            ClaseSession.subject_id == subject_id,
            ClaseSession.fecha == fecha
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    @handle_repository_errors
    async def find_overlapping_sessions(
        self,
        subject_id: int,
        fecha: date,
        hora_inicio: datetime,
        hora_fin: datetime,
    ) -> list[ClaseSession]:
        """Sesiones de la misma materia en la misma fecha cuyo horario solapa con [hora_inicio, hora_fin].
        [a,b) y [c,d) solapan si a < d y c < b.
        """
        stmt = select(ClaseSession).where(
            ClaseSession.subject_id == subject_id,
            ClaseSession.fecha == fecha,
            ClaseSession.hora_inicio < hora_fin,
            ClaseSession.hora_fin > hora_inicio,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
