"""Schedule Repository - capa de acceso a datos para horarios.

TASK-006 a TASK-009. Validación de solapamientos (aula, profesor, estudiante)
y consulta de horario semanal por rol.
"""

from datetime import time
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, joinedload

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
    """Repositorio para Schedule y consultas de solapamiento."""

    def __init__(self, db: Session):
        self.db = db

    def find_classroom_overlaps(
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
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def find_professor_overlaps(
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
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def find_student_overlaps(
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
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_weekly_schedule(
        self,
        user_id: int,
        role: UserRole,
    ) -> List[Schedule]:
        """TASK-009: Horario semanal según rol (Profesor: sus materias; Estudiante: inscripciones)."""
        stmt = select(Schedule).options(
            joinedload(Schedule.subject),
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

        result = self.db.execute(stmt)
        return list(result.scalars().all())
