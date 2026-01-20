"""Schedule Service - lógica de negocio para horarios.

TASK-010 a TASK-013. Validación de conflictos (aula, profesor) y
obtención de horario semanal por rol. Async para API.
"""

from datetime import time
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ScheduleConflictError
from app.models.schedule import Schedule
from app.models.subject import Subject
from app.models.user import UserRole
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate


def _serialize_conflicts(conflicts: List[dict]) -> List[dict]:
    """Convierte conflictos con Schedule a estructura JSON-serializable."""
    out = []
    for c in conflicts:
        scheds = []
        for s in c["schedules"]:
            scheds.append({
                "id": s.id,
                "codigo": s.codigo,
                "subject_id": s.subject_id,
                "classroom_id": s.classroom_id,
                "dia_semana": s.dia_semana,
                "hora_inicio": s.hora_inicio.strftime("%H:%M") if s.hora_inicio else None,
                "hora_fin": s.hora_fin.strftime("%H:%M") if s.hora_fin else None,
            })
        out.append({"type": c["type"], "schedules": scheds})
    return out


class ScheduleService:
    """Servicio de horarios con validación de conflictos (async)."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ScheduleRepository(db)

    async def validate_schedule_conflicts(
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
        result = await self.db.execute(select(Subject).where(Subject.id == subject_id))
        subject = result.scalar_one_or_none()
        if not subject:
            raise ValueError("Subject not found")
        profesor_id = subject.profesor_id

        conflicts: List[dict] = []

        co = await self.repo.find_classroom_overlaps(
            classroom_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
        )
        if co:
            conflicts.append({"type": "classroom", "schedules": co})

        po = await self.repo.find_professor_overlaps(
            profesor_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
        )
        if po:
            conflicts.append({"type": "professor", "schedules": po})

        return conflicts

    async def get_all_schedules(self) -> List[Schedule]:
        """Todos los horarios (Admin en calendario)."""
        return await self.repo.get_all_schedules()

    async def get_professor_schedule(self, profesor_id: int) -> List[Schedule]:
        """TASK-012: Horario semanal del profesor."""
        return await self.repo.get_weekly_schedule(profesor_id, UserRole.PROFESOR)

    async def get_student_schedule(self, estudiante_id: int) -> List[Schedule]:
        """TASK-013: Horario semanal del estudiante (materias inscritas)."""
        return await self.repo.get_weekly_schedule(estudiante_id, UserRole.ESTUDIANTE)

    async def create_schedule(self, data: ScheduleCreate) -> Schedule:
        """Crear horario tras validar conflictos. TASK-014."""
        conflicts = await self.validate_schedule_conflicts(
            data.subject_id, data.classroom_id, data.dia_semana,
            data.hora_inicio, data.hora_fin,
        )
        if conflicts:
            raise ScheduleConflictError(_serialize_conflicts(conflicts))

        schedule = Schedule(
            subject_id=data.subject_id,
            classroom_id=data.classroom_id,
            dia_semana=data.dia_semana,
            hora_inicio=data.hora_inicio,
            hora_fin=data.hora_fin,
        )
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        # Recargar con relaciones para respuesta
        s = await self.repo.get_by_id(schedule.id)
        return s or schedule

    async def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        """Obtener horario por ID."""
        return await self.repo.get_by_id(schedule_id)

    async def update_schedule(
        self, schedule_id: int, data: ScheduleUpdate
    ) -> Optional[Schedule]:
        """Actualizar horario validando conflictos. TASK-016."""
        s = await self.repo.get_by_id(schedule_id)
        if not s:
            return None

        subject_id = data.subject_id if data.subject_id is not None else s.subject_id
        classroom_id = data.classroom_id if data.classroom_id is not None else s.classroom_id
        dia_semana = data.dia_semana if data.dia_semana is not None else s.dia_semana
        hora_inicio = data.hora_inicio if data.hora_inicio is not None else s.hora_inicio
        hora_fin = data.hora_fin if data.hora_fin is not None else s.hora_fin

        conflicts = await self.validate_schedule_conflicts(
            subject_id, classroom_id, dia_semana, hora_inicio, hora_fin,
            exclude_schedule_id=schedule_id,
        )
        if conflicts:
            raise ScheduleConflictError(_serialize_conflicts(conflicts))

        if data.subject_id is not None:
            s.subject_id = data.subject_id
        if data.classroom_id is not None:
            s.classroom_id = data.classroom_id
        if data.dia_semana is not None:
            s.dia_semana = data.dia_semana
        if data.hora_inicio is not None:
            s.hora_inicio = data.hora_inicio
        if data.hora_fin is not None:
            s.hora_fin = data.hora_fin

        await self.db.commit()
        await self.db.refresh(s)
        return await self.repo.get_by_id(schedule_id)

    async def delete_schedule(self, schedule_id: int) -> bool:
        """Eliminar horario. TASK-017."""
        s = await self.repo.get_by_id(schedule_id)
        if not s:
            return False
        await self.db.delete(s)
        await self.db.commit()
        return True

    async def get_by_classroom(self, classroom_id: int) -> List[Schedule]:
        """TASK-018: Horarios de un aula."""
        return await self.repo.get_by_classroom(classroom_id)
