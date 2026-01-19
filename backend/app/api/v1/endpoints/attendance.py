"""Attendance endpoints for manual attendance tracking system.

REST API endpoints for managing class sessions and attendance records.
Implements role-based access control (Profesor can manage, Estudiante can view).
"""

from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db, get_current_user
from app.schemas.attendance import (
    ClaseSessionCreate,
    ClaseSessionResponse,
    AttendanceUpdate,
    AttendanceResponse,
    SessionStatisticsResponse,
)
from app.models.user import User, UserRole
from app.models.attendance import ClaseSession, Attendance
from app.services.attendance_service import AttendanceService
from app.core.exceptions import NotFoundError, UnauthorizedError, ValidationError

router = APIRouter(tags=["attendance"])


@router.post("/sessions", response_model=ClaseSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_clase_session(
    session_data: ClaseSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new class session.
    
    Only Profesores can create class sessions.
    Validates that hora_fin > hora_inicio and fecha is not in the future (beyond current time).
    """
    if current_user.role != UserRole.PROFESOR:
        raise UnauthorizedError("Only professors can create class sessions")
    
    service = AttendanceService(db, current_user)
    
    try:
        clase_session = service.create_clase_session(
            subject_id=session_data.subject_id,
            fecha=session_data.fecha,
            hora_inicio=session_data.hora_inicio,
            hora_fin=session_data.hora_fin,
            descripcion=session_data.descripcion,
        )
        return ClaseSessionResponse.model_validate(clase_session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (NotFoundError, UnauthorizedError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=e.detail if hasattr(e, 'detail') else str(e))


@router.get("/sessions/{session_id}", response_model=ClaseSessionResponse)
async def get_clase_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a class session by ID."""
    from app.repositories.attendance_repository import AttendanceRepository
    repo = AttendanceRepository(db)
    
    clase_session = await repo.get_by_id(ClaseSession, session_id)
    
    if not clase_session:
        raise HTTPException(status_code=404, detail=f"ClaseSession {session_id} not found")
    
    return ClaseSessionResponse.model_validate(clase_session)


@router.patch("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update attendance status.
    
    Only Profesores can update attendance records.
    """
    if current_user.role != UserRole.PROFESOR:
        raise HTTPException(status_code=403, detail="Only professors can update attendance")
    
    service = AttendanceService(db, current_user)
    
    # Get existing attendance
    from app.repositories.attendance_repository import AttendanceRepository
    repo = AttendanceRepository(db)
    
    attendance = await repo.get_by_id(Attendance, attendance_id)
    
    if not attendance:
        raise HTTPException(status_code=404, detail=f"Attendance {attendance_id} not found")
    
    # Update attendance
    updated_attendance = service.update_attendance(
        attendance_id=attendance_id,
        estado=attendance_data.estado,
    )
    
    return AttendanceResponse.model_validate(updated_attendance)


@router.get("/sessions/{session_id}/stats", response_model=SessionStatisticsResponse)
async def get_session_statistics(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get attendance statistics for a class session."""
    service = AttendanceService(db, current_user)
    
    # Verify session exists
    from app.repositories.attendance_repository import AttendanceRepository
    repo = AttendanceRepository(db)
    
    clase_session = await repo.get_by_id(ClaseSession, session_id)
    
    if not clase_session:
        raise HTTPException(status_code=404, detail=f"ClaseSession {session_id} not found")
    
    # Get statistics
    stats = service.get_session_statistics(session_id)
    
    return SessionStatisticsResponse(**stats)

