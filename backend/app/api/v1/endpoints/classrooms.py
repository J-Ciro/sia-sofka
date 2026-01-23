"""Classrooms endpoint - CRUD de aulas (Admin). Profesores eligen del banco al crear horarios."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ConflictError
from app.models.schedule import Classroom, Schedule
from app.schemas.schedule import ClassroomCreate, ClassroomUpdate, ClassroomResponse
from app.api.v1.dependencies import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter()


def _generar_codigo_aula() -> str:
    """Genera código único para aula (ej. AULA-A1B2C3D4)."""
    return f"AULA-{uuid.uuid4().hex[:8].upper()}"


@router.get("", response_model=List[ClassroomResponse])
async def list_classrooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Listar todas las aulas (banco de salones). Cualquier autenticado."""
    stmt = select(Classroom).order_by(Classroom.codigo)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [ClassroomResponse.model_validate(c) for c in rows]


@router.get("/{classroom_id}", response_model=ClassroomResponse)
async def get_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obtener un aula por ID."""
    result = await db.execute(select(Classroom).where(Classroom.id == classroom_id))
    row = result.scalar_one_or_none()
    if not row:
        raise NotFoundError("Classroom", classroom_id)
    return ClassroomResponse.model_validate(row)


@router.post("", response_model=ClassroomResponse, status_code=status.HTTP_201_CREATED)
async def create_classroom(
    data: ClassroomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Crear aula (Admin). Código se genera automáticamente. El profesor elige del banco al asignar horarios."""
    codigo = _generar_codigo_aula()
    c = Classroom(
        codigo=codigo,
        nombre=data.nombre,
        capacidad=data.capacidad,
        ubicacion=data.ubicacion,
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return ClassroomResponse.model_validate(c)


@router.put("/{classroom_id}", response_model=ClassroomResponse)
async def update_classroom(
    classroom_id: int,
    data: ClassroomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Actualizar aula (Admin)."""
    r = await db.execute(select(Classroom).where(Classroom.id == classroom_id))
    c = r.scalar_one_or_none()
    if not c:
        raise NotFoundError("Classroom", classroom_id)
    if data.nombre is not None:
        setattr(c, 'nombre', data.nombre)
    if data.capacidad is not None:
        setattr(c, 'capacidad', data.capacidad)
    if data.ubicacion is not None:
        setattr(c, 'ubicacion', data.ubicacion)
    await db.commit()
    await db.refresh(c)
    return ClassroomResponse.model_validate(c)


@router.delete("/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Eliminar aula (Admin). No se puede si tiene horarios asignados."""
    r = await db.execute(select(Classroom).where(Classroom.id == classroom_id))
    c = r.scalar_one_or_none()
    if not c:
        raise NotFoundError("Classroom", classroom_id)
    cnt = await db.execute(select(func.count(Schedule.id)).where(Schedule.classroom_id == classroom_id))
    if (cnt.scalar() or 0) > 0:
        raise ConflictError("No se puede eliminar: tiene horarios asignados")
    await db.delete(c)
    await db.commit()
