"""Schedule Service - lógica de negocio para horarios.

TASK-010 a TASK-013. Validación de conflictos (aula, profesor) y
obtención de horario semanal por rol. Async para API.

Enhanced for date-specific schedules (Task 4.1):
- Enhanced conflict validation supporting both weekly and date-specific schedules
- New calendar display method that expands weekly schedules to specific dates
- Maintains full backward compatibility with existing methods
"""

from datetime import time, date, timedelta
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
    """Convierte conflictos con Schedule a estructura JSON-serializable.
    
    Enhanced for Task 4.1: Includes date-specific information in conflict details.
    """
    out = []
    for c in conflicts:
        scheds = []
        for s in c["schedules"]:
            conflict_data = {
                "id": s.id,
                "codigo": s.codigo,
                "subject_id": s.subject_id,
                "classroom_id": s.classroom_id,
                "dia_semana": s.dia_semana,
                "hora_inicio": s.hora_inicio.strftime("%H:%M") if s.hora_inicio else None,
                "hora_fin": s.hora_fin.strftime("%H:%M") if s.hora_fin else None,
            }
            # Add date-specific information if available
            if hasattr(s, 'fecha_especifica') and s.fecha_especifica:
                conflict_data["fecha_especifica"] = s.fecha_especifica.strftime("%Y-%m-%d")
                conflict_data["es_fecha_especifica"] = True
            else:
                conflict_data["fecha_especifica"] = None
                conflict_data["es_fecha_especifica"] = False
            
            scheds.append(conflict_data)
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
        fecha_especifica: Optional[date] = None,
        exclude_schedule_id: Optional[int] = None,
    ) -> List[dict]:
        """Enhanced conflict validation supporting both weekly and date-specific schedules.
        
        TASK-010, TASK-011: Detecta conflictos de aula y de profesor.
        Enhanced for Task 4.1: Supports date-specific schedule conflict detection.

        Args:
            subject_id: ID of the subject
            classroom_id: ID of the classroom
            dia_semana: Day of week (1=Monday..6=Saturday)
            hora_inicio: Start time
            hora_fin: End time
            fecha_especifica: Optional specific date for date-specific schedules
            exclude_schedule_id: Optional schedule ID to exclude from conflict check

        Returns:
            Lista de dicts: [{"type": "classroom"|"professor"|"classroom_weekly"|"professor_weekly", "schedules": [...]}]
        """
        result = await self.db.execute(select(Subject).where(Subject.id == subject_id))
        subject = result.scalar_one_or_none()
        if not subject:
            raise ValueError("Subject not found")
        profesor_id = subject.profesor_id

        conflicts: List[dict] = []

        if fecha_especifica:
            # Check conflicts for specific date
            classroom_conflicts = await self.repo.find_classroom_overlaps_by_date(
                classroom_id, fecha_especifica, hora_inicio, hora_fin, exclude_schedule_id
            )
            if classroom_conflicts:
                conflicts.append({"type": "classroom", "schedules": classroom_conflicts})

            professor_conflicts = await self.repo.find_professor_overlaps_by_date(
                profesor_id, fecha_especifica, hora_inicio, hora_fin, exclude_schedule_id
            )
            if professor_conflicts:
                conflicts.append({"type": "professor", "schedules": professor_conflicts})
            
            # Also check against weekly recurring schedules for the same day
            weekly_classroom_conflicts = await self.repo.find_classroom_overlaps(
                classroom_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
            )
            weekly_professor_conflicts = await self.repo.find_professor_overlaps(
                profesor_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id
            )
            
            # Filter weekly conflicts to only those without fecha_especifica (recurring schedules)
            weekly_classroom_conflicts = [s for s in weekly_classroom_conflicts if s.fecha_especifica is None]
            weekly_professor_conflicts = [s for s in weekly_professor_conflicts if s.fecha_especifica is None]
            
            if weekly_classroom_conflicts:
                conflicts.append({"type": "classroom_weekly", "schedules": weekly_classroom_conflicts})
            if weekly_professor_conflicts:
                conflicts.append({"type": "professor_weekly", "schedules": weekly_professor_conflicts})
        else:
            # Use existing weekly conflict validation for backward compatibility
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

    async def get_schedules_for_calendar(
        self,
        start_date: date,
        end_date: date,
        user_id: Optional[int] = None,
        role: Optional[UserRole] = None,
    ) -> List[Schedule]:
        """Get schedules for calendar display, expanding weekly schedules to specific dates.
        
        This method is designed for calendar components that need to display schedules
        as events on specific dates. It handles both date-specific schedules and 
        weekly recurring schedules by expanding the weekly ones to specific dates
        within the requested range.
        
        Args:
            start_date: Start date of the range (inclusive)
            end_date: End date of the range (inclusive)
            user_id: Optional user ID for filtering by role
            role: Optional user role for filtering schedules
            
        Returns:
            List of schedules where each schedule has a specific date for display.
            Weekly recurring schedules are expanded to create virtual schedule instances
            for each occurrence within the date range.
        """
        # Get all schedules within the date range (both date-specific and weekly)
        schedules = await self.repo.get_schedules_by_date_range(
            start_date, end_date, user_id, role
        )
        
        # Separate date-specific and weekly schedules
        date_specific_schedules = [s for s in schedules if s.fecha_especifica is not None]
        weekly_schedules = [s for s in schedules if s.fecha_especifica is None]
        
        # Start with date-specific schedules (they already have their dates)
        expanded_schedules = list(date_specific_schedules)  # Make a copy of the list
        
        # Expand weekly schedules to specific dates within the range
        current_date = start_date
        while current_date <= end_date:
            # Convert Python weekday (0=Monday) to our system (1=Monday, 6=Saturday)
            day_of_week = current_date.weekday() + 1
            if day_of_week == 7:  # Handle Sunday if needed (though our system uses 1-6)
                day_of_week = 7
            
            # Find weekly schedules for this day of week
            for schedule in weekly_schedules:
                if schedule.dia_semana == day_of_week:
                    # Check if there's already a date-specific schedule for this date/subject/time
                    # to avoid duplicates when a date-specific schedule overrides a weekly one
                    has_date_specific_override = any(
                        ds.fecha_especifica == current_date and
                        ds.subject_id == schedule.subject_id and
                        ds.hora_inicio == schedule.hora_inicio
                        for ds in date_specific_schedules
                    )
                    
                    if not has_date_specific_override:
                        # Create a virtual schedule instance for this specific date
                        # Use a simple class to avoid SQLAlchemy issues
                        class VirtualSchedule:
                            """Simple class to hold schedule data for virtual instances."""
                            def __init__(self, schedule, fecha_especifica):
                                self.id = schedule.id
                                self.codigo = schedule.codigo
                                self.subject_id = schedule.subject_id
                                self.classroom_id = schedule.classroom_id
                                self.dia_semana = schedule.dia_semana
                                self.hora_inicio = schedule.hora_inicio
                                self.hora_fin = schedule.hora_fin
                                self.fecha_especifica = fecha_especifica
                                self.created_at = schedule.created_at
                                self.updated_at = schedule.updated_at
                                # Copy relationships if they exist
                                if hasattr(schedule, 'subject') and schedule.subject is not None:
                                    self.subject = schedule.subject
                                if hasattr(schedule, 'classroom') and schedule.classroom is not None:
                                    self.classroom = schedule.classroom
                                # Mark as virtual for _to_response
                                self._sa_instance_state = None
                        
                        virtual_schedule = VirtualSchedule(schedule, current_date)
                        expanded_schedules.append(virtual_schedule)
            
            current_date += timedelta(days=1)
        
        return expanded_schedules

    async def get_all_schedules(self) -> List[Schedule]:
        """Todos los horarios (Admin en calendario)."""
        result = await self.repo.get_all_schedules()
        return list(result) if result else []

    async def get_professor_schedule(self, profesor_id: int) -> List[Schedule]:
        """TASK-012: Horario semanal del profesor."""
        result = await self.repo.get_weekly_schedule(profesor_id, UserRole.PROFESOR)
        return list(result) if result else []

    async def get_student_schedule(self, estudiante_id: int) -> List[Schedule]:
        """TASK-013: Horario semanal del estudiante (materias inscritas)."""
        result = await self.repo.get_weekly_schedule(estudiante_id, UserRole.ESTUDIANTE)
        return list(result) if result else []

    async def create_schedule(self, data: ScheduleCreate) -> Schedule:
        """Crear horario tras validar conflictos. TASK-014.
        
        Enhanced for Task 4.1: Supports date-specific schedule creation.
        """
        # Extract fecha_especifica from data if available
        fecha_especifica = getattr(data, 'fecha_especifica', None)
        
        conflicts = await self.validate_schedule_conflicts(
            data.subject_id, data.classroom_id, data.dia_semana,
            data.hora_inicio, data.hora_fin, fecha_especifica,
        )
        if conflicts:
            raise ScheduleConflictError(_serialize_conflicts(conflicts))

        schedule = Schedule(
            subject_id=data.subject_id,
            classroom_id=data.classroom_id,
            dia_semana=data.dia_semana,
            hora_inicio=data.hora_inicio,
            hora_fin=data.hora_fin,
            fecha_especifica=fecha_especifica,
        )
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        # Recargar con relaciones para respuesta
        s = await self.repo.get_by_id(schedule.id)
        return s or schedule

    async def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        """Obtener horario por ID."""
        result = await self.repo.get_by_id(schedule_id)
        return result if result else None

    async def update_schedule(
        self, schedule_id: int, data: ScheduleUpdate
    ) -> Optional[Schedule]:
        """Actualizar horario validando conflictos. TASK-016.
        
        Enhanced for Task 4.1: Supports updating date-specific schedules.
        """
        s = await self.repo.get_by_id(schedule_id)
        if not s:
            return None

        subject_id = data.subject_id if data.subject_id is not None else s.subject_id
        classroom_id = data.classroom_id if data.classroom_id is not None else s.classroom_id
        dia_semana = data.dia_semana if data.dia_semana is not None else s.dia_semana
        hora_inicio = data.hora_inicio if data.hora_inicio is not None else s.hora_inicio
        hora_fin = data.hora_fin if data.hora_fin is not None else s.hora_fin
        
        # Handle fecha_especifica update
        fecha_especifica = s.fecha_especifica  # Keep existing value by default
        if hasattr(data, 'fecha_especifica') and data.fecha_especifica is not None:
            fecha_especifica = data.fecha_especifica

        conflicts = await self.validate_schedule_conflicts(
            subject_id, classroom_id, dia_semana, hora_inicio, hora_fin,
            fecha_especifica, exclude_schedule_id=schedule_id,
        )
        if conflicts:
            raise ScheduleConflictError(_serialize_conflicts(conflicts))

        if data.subject_id is not None:
            setattr(s, 'subject_id', data.subject_id)
        if data.classroom_id is not None:
            setattr(s, 'classroom_id', data.classroom_id)
        if data.dia_semana is not None:
            setattr(s, 'dia_semana', data.dia_semana)
        if data.hora_inicio is not None:
            setattr(s, 'hora_inicio', data.hora_inicio)
        if data.hora_fin is not None:
            setattr(s, 'hora_fin', data.hora_fin)
        if hasattr(data, 'fecha_especifica') and data.fecha_especifica is not None:
            setattr(s, 'fecha_especifica', data.fecha_especifica)

        await self.db.commit()
        await self.db.refresh(s)
        result = await self.repo.get_by_id(schedule_id)
        return result if result else None

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
        result = await self.repo.get_by_classroom(classroom_id)
        return list(result) if result else []
