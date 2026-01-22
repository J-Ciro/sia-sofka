"""Schedule Repository - capa de acceso a datos para horarios.

TASK-006 a TASK-009. Validación de solapamientos (aula, profesor, estudiante)
y consulta de horario semanal por rol. Async para uso en API.
"""

from datetime import time, date
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.schedule import Schedule
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.user import UserRole


def _overlap_condition(hora_inicio: time, hora_fin: time):
    """Intervalos [a,b) y [c,d) solapan si a < d y c < b."""
    return and_(
        Schedule.hora_inicio < hora_fin,
        Schedule.hora_fin > hora_inicio,
    )


class ScheduleRepository:
    """Repositorio para Schedule y consultas de solapamiento (async)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_classroom_overlaps(
        self,
        classroom_id: int,
        dia_semana: int,
        hora_inicio: time,
        hora_fin: time,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[Schedule]:
        """TASK-006: Horarios que solapan con el rango en el mismo aula y día."""
        stmt = (
            select(Schedule)
            .where(
                Schedule.classroom_id == classroom_id,
                Schedule.dia_semana == dia_semana,
                _overlap_condition(hora_inicio, hora_fin),
            )
        )
        if exclude_schedule_id is not None:
            stmt = stmt.where(Schedule.id != exclude_schedule_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_professor_overlaps(
        self,
        profesor_id: int,
        dia_semana: int,
        hora_inicio: time,
        hora_fin: time,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[Schedule]:
        """TASK-007: Horarios de materias del profesor que solapan en día y hora."""
        stmt = (
            select(Schedule)
            .join(Subject, Schedule.subject_id == Subject.id)
            .where(
                Subject.profesor_id == profesor_id,
                Schedule.dia_semana == dia_semana,
                _overlap_condition(hora_inicio, hora_fin),
            )
        )
        if exclude_schedule_id is not None:
            stmt = stmt.where(Schedule.id != exclude_schedule_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_student_overlaps(
        self,
        estudiante_id: int,
        dia_semana: int,
        hora_inicio: time,
        hora_fin: time,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[Schedule]:
        """TASK-008: Horarios de materias inscritas del estudiante que solapan."""
        stmt = (
            select(Schedule)
            .join(Subject, Schedule.subject_id == Subject.id)
            .join(Enrollment, and_(
                Enrollment.subject_id == Subject.id,
                Enrollment.estudiante_id == estudiante_id,
            ))
            .where(
                Schedule.dia_semana == dia_semana,
                _overlap_condition(hora_inicio, hora_fin),
            )
        )
        if exclude_schedule_id is not None:
            stmt = stmt.where(Schedule.id != exclude_schedule_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all_schedules(self) -> List[Schedule]:
        """Todos los horarios (para Admin en calendario)."""
        stmt = (
            select(Schedule)
            .options(
                joinedload(Schedule.subject).joinedload(Subject.profesor),
                joinedload(Schedule.classroom),
            )
            .order_by(Schedule.dia_semana, Schedule.hora_inicio)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_weekly_schedule(
        self,
        user_id: int,
        role: UserRole,
    ) -> List[Schedule]:
        """TASK-009: Horario semanal según rol (Profesor: sus materias; Estudiante: inscripciones)."""
        stmt = select(Schedule).options(
            joinedload(Schedule.subject).joinedload(Subject.profesor),
            joinedload(Schedule.classroom),
        ).order_by(Schedule.dia_semana, Schedule.hora_inicio)

        if role == UserRole.PROFESOR:
            stmt = stmt.join(Subject, Schedule.subject_id == Subject.id).where(
                Subject.profesor_id == user_id
            )
        elif role == UserRole.ESTUDIANTE:
            stmt = (
                stmt.join(Subject, Schedule.subject_id == Subject.id)
                .join(Enrollment, and_(
                    Enrollment.subject_id == Subject.id,
                    Enrollment.estudiante_id == user_id,
                ))
            )
        else:
            return []

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        """Obtener horario por ID con subject y classroom."""
        stmt = (
            select(Schedule)
            .where(Schedule.id == schedule_id)
            .options(
                joinedload(Schedule.subject).joinedload(Subject.profesor),
                joinedload(Schedule.classroom),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_classroom(
        self, classroom_id: int
    ) -> List[Schedule]:
        """TASK-018: Horarios de un aula."""
        stmt = (
            select(Schedule)
            .where(Schedule.classroom_id == classroom_id)
            .options(
                joinedload(Schedule.subject).joinedload(Subject.profesor),
                joinedload(Schedule.classroom),
            )
            .order_by(Schedule.dia_semana, Schedule.hora_inicio)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_classroom_overlaps_by_date(
        self,
        classroom_id: int,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[Schedule]:
        """Find classroom conflicts for a specific date.
        
        Args:
            classroom_id: ID of the classroom to check
            fecha: Specific date to check for conflicts
            hora_inicio: Start time of the schedule
            hora_fin: End time of the schedule
            exclude_schedule_id: Optional schedule ID to exclude from conflict check
            
        Returns:
            List of conflicting schedules for the same classroom on the specific date
        """
        stmt = (
            select(Schedule)
            .where(
                Schedule.classroom_id == classroom_id,
                Schedule.fecha_especifica == fecha,
                _overlap_condition(hora_inicio, hora_fin),
            )
        )
        if exclude_schedule_id is not None:
            stmt = stmt.where(Schedule.id != exclude_schedule_id)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_professor_overlaps_by_date(
        self,
        profesor_id: int,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[Schedule]:
        """Find professor conflicts for a specific date.
        
        Args:
            profesor_id: ID of the professor to check
            fecha: Specific date to check for conflicts
            hora_inicio: Start time of the schedule
            hora_fin: End time of the schedule
            exclude_schedule_id: Optional schedule ID to exclude from conflict check
            
        Returns:
            List of conflicting schedules for the same professor on the specific date
        """
        stmt = (
            select(Schedule)
            .join(Subject, Schedule.subject_id == Subject.id)
            .where(
                Subject.profesor_id == profesor_id,
                Schedule.fecha_especifica == fecha,
                _overlap_condition(hora_inicio, hora_fin),
            )
        )
        if exclude_schedule_id is not None:
            stmt = stmt.where(Schedule.id != exclude_schedule_id)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_schedules_by_date_range(
        self,
        start_date: date,
        end_date: date,
        user_id: Optional[int] = None,
        role: Optional[UserRole] = None,
    ) -> List[Schedule]:
        """Get schedules for a date range, including both weekly and date-specific.
        
        Args:
            start_date: Start date of the range (inclusive)
            end_date: End date of the range (inclusive)
            user_id: Optional user ID for filtering by role
            role: Optional user role for filtering schedules
            
        Returns:
            List of schedules within the date range, including:
            - Date-specific schedules that fall within the range
            - Weekly recurring schedules (without fecha_especifica)
        """
        # Base query for date-specific schedules within the range
        date_query = (
            select(Schedule)
            .where(Schedule.fecha_especifica.between(start_date, end_date))
            .options(
                joinedload(Schedule.subject).joinedload(Subject.profesor),
                joinedload(Schedule.classroom),
            )
        )
        
        # Base query for weekly recurring schedules (no specific date)
        weekly_query = (
            select(Schedule)
            .where(Schedule.fecha_especifica.is_(None))
            .options(
                joinedload(Schedule.subject).joinedload(Subject.profesor),
                joinedload(Schedule.classroom),
            )
        )
        
        # Apply user/role filters if provided
        if user_id is not None and role is not None:
            if role == UserRole.PROFESOR:
                # Filter by professor's subjects
                date_query = date_query.join(Subject).where(Subject.profesor_id == user_id)
                weekly_query = weekly_query.join(Subject).where(Subject.profesor_id == user_id)
            elif role == UserRole.ESTUDIANTE:
                # Filter by student's enrolled subjects
                date_query = (
                    date_query.join(Subject)
                    .join(Enrollment, and_(
                        Enrollment.subject_id == Subject.id,
                        Enrollment.estudiante_id == user_id,
                    ))
                )
                weekly_query = (
                    weekly_query.join(Subject)
                    .join(Enrollment, and_(
                        Enrollment.subject_id == Subject.id,
                        Enrollment.estudiante_id == user_id,
                    ))
                )
        
        # Execute both queries
        date_result = await self.db.execute(date_query)
        weekly_result = await self.db.execute(weekly_query)
        
        # Combine results and return
        date_schedules = list(date_result.scalars().all())
        weekly_schedules = list(weekly_result.scalars().all())
        
        return date_schedules + weekly_schedules
