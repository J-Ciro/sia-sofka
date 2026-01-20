"""Classrooms endpoint - listado de aulas para formularios (horarios, etc.)."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schedule import Classroom
from app.schemas.schedule import ClassroomResponse
from app.api.v1.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[ClassroomResponse])
async def list_classrooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Listar todas las aulas. Requiere autenticación."""
    stmt = select(Classroom).order_by(Classroom.codigo)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [ClassroomResponse.model_validate(c) for c in rows]
