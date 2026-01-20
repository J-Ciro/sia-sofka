"""Schedule endpoints - TASK-014 a TASK-018. Horarios y calendario."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.services.schedule_service import ScheduleService
from app.api.v1.dependencies import get_current_active_user, require_admin, require_admin_or_profesor

router = APIRouter()


def _to_response(s) -> ScheduleResponse:
    return ScheduleResponse.model_validate(s)


# POST /api/v1/schedules - TASK-014
@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Crear horario (Admin o Profesor). Profesor solo para sus materias; elige aula del banco. Valida conflictos."""
    if current_user.role == UserRole.PROFESOR:
        r = await db.execute(select(Subject).where(Subject.id == data.subject_id))
        sub = r.scalar_one_or_none()
        if not sub or sub.profesor_id != current_user.id:
            raise ForbiddenError("Solo puedes asignar horarios a tus propias materias")
    service = ScheduleService(db)
    try:
        schedule = await service.create_schedule(data)
        return _to_response(schedule)
    except ValueError as e:
        if str(e) == "Subject not found":
            raise ValidationError("Subject not found")
        raise


# GET /api/v1/schedules/weekly - TASK-015
@router.get("/weekly", response_model=List[ScheduleResponse])
async def get_weekly_schedules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_id: Optional[int] = Query(None, description="Admin: ver otro usuario"),
    role: Optional[UserRole] = Query(None, description="Admin: rol al ver otro usuario"),
):
    """Horario semanal. Profesor/Estudiante: el propio. Admin: todos; o user_id+role para filtrar."""
    service = ScheduleService(db)
    uid = current_user.id
    r = current_user.role

    if current_user.role == UserRole.ADMIN and user_id is not None:
        uid = user_id
        r = role if role is not None else current_user.role

    if r == UserRole.PROFESOR:
        rows = await service.get_professor_schedule(uid)
    elif r == UserRole.ESTUDIANTE:
        rows = await service.get_student_schedule(uid)
    elif r == UserRole.ADMIN and user_id is not None and role is not None:
        if role == UserRole.PROFESOR:
            rows = await service.get_professor_schedule(uid)
        elif role == UserRole.ESTUDIANTE:
            rows = await service.get_student_schedule(uid)
        else:
            rows = []
    elif current_user.role == UserRole.ADMIN and user_id is None:
        rows = await service.get_all_schedules()
    else:
        rows = []

    return [_to_response(s) for s in rows]


# PUT /api/v1/schedules/{schedule_id} - TASK-016
@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Actualizar horario (Admin). Valida conflictos."""
    service = ScheduleService(db)
    try:
        s = await service.update_schedule(schedule_id, data)
        if not s:
            raise NotFoundError("Schedule", schedule_id)
        return _to_response(s)
    except ValueError:
        raise


# DELETE /api/v1/schedules/{schedule_id} - TASK-017
@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Eliminar horario (Admin)."""
    service = ScheduleService(db)
    ok = await service.delete_schedule(schedule_id)
    if not ok:
        raise NotFoundError("Schedule", schedule_id)


# GET /api/v1/schedules/classroom/{classroom_id} - TASK-018
@router.get("/classroom/{classroom_id}", response_model=List[ScheduleResponse])
async def get_schedules_by_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Horarios de un aula."""
    service = ScheduleService(db)
    rows = await service.get_by_classroom(classroom_id)
    return [_to_response(s) for s in rows]
