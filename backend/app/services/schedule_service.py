"""Schedule Service - lógica de negocio para horarios.

TASK-010 a TASK-013. Validación de conflictos (aula, profesor) y
obtención de horario semanal por rol.
"""

from datetime import time
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.schedule import Schedule
from app.models.subject import Subject
from app.models.user import UserRole
from app.repositories.schedule_repository import ScheduleRepository


class ScheduleService:
    """Servicio de horarios con validación de conflictos."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ScheduleRepository(db)

    def validate_schedule_conflicts(
        self,
        subject_id: int,
        classroom_id: int,
        dia_semana: int,
        hora_inicio: time,
        hora_fin: time,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[dict]:
        """TASK-010, TASK-011: Detecta conflictos de aula y de profesor.

        Returns:
            Lista de dicts: [{"type": "classroom"|"professor", "schedules": [...]}]
        """
        result = self.db.execute(select(Subject).where(Subject.id == subject_id))
        subject = result.scalar_one_or_none()
        if not subject:
            raise ValueError("Subject not found")
        profesor_id = subject.profesor_id

        conflicts: List[dict] = []

        co = self.repo.find_classroom_overlaps(
            classroom_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
        )
        if co:
            conflicts.append({"type": "classroom", "schedules": co})

        po = self.repo.find_professor_overlaps(
            profesor_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
        )
        if po:
            conflicts.append({"type": "professor", "schedules": po})

        return conflicts

    def get_professor_schedule(self, profesor_id: int) -> List[Schedule]:
        """TASK-012: Horario semanal del profesor."""
        return self.repo.get_weekly_schedule(profesor_id, UserRole.PROFESOR)

    def get_student_schedule(self, estudiante_id: int) -> List[Schedule]:
        """TASK-013: Horario semanal del estudiante (materias inscritas)."""
        return self.repo.get_weekly_schedule(estudiante_id, UserRole.ESTUDIANTE)
