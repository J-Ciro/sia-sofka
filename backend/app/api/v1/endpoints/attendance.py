"""Attendance endpoints for manual attendance tracking system.

REST API endpoints for managing class sessions and attendance records.
Implements role-based access control (Profesor can manage, Estudiante can view).
"""

from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
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
        clase_session = await service.create_clase_session(
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


@router.get("/sessions", response_model=list[ClaseSessionResponse])
async def list_clase_sessions(
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all class sessions.
    
    Profesores see only their sessions.
    Students see sessions from their enrolled subjects.
    """
    from app.repositories.attendance_repository import AttendanceRepository
    repo = AttendanceRepository(db)
    
    if current_user.role == UserRole.PROFESOR:
        # Profesores see their own sessions
        sessions = await repo.get_sessions_by_profesor(current_user.id, subject_id)
    else:
        # Estudiantes see sessions from enrolled subjects
        sessions = await repo.get_sessions_for_student(current_user.id, subject_id)
    
    return [ClaseSessionResponse.model_validate(s) for s in sessions]


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


@router.get("/sessions/{session_id}/attendances", response_model=list[AttendanceResponse])
async def get_session_attendances(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all attendance records for a class session."""
    from app.repositories.attendance_repository import AttendanceRepository
    repo = AttendanceRepository(db)
    
    # Verify session exists
    clase_session = await repo.get_by_id(ClaseSession, session_id)
    if not clase_session:
        raise HTTPException(status_code=404, detail=f"ClaseSession {session_id} not found")
    
    # Get attendances
    attendances = await repo.get_attendances_by_session(session_id)
    
    return [AttendanceResponse.model_validate(a) for a in attendances]


@router.post("/sessions/{session_id}/save", status_code=status.HTTP_200_OK)
async def save_session_attendances(
    session_id: int,
    attendance_updates: list[AttendanceUpdate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save multiple attendance updates for a session.
    
    This endpoint updates all attendance records for a session in a single transaction.
    """
    if current_user.role != UserRole.PROFESOR:
        raise HTTPException(status_code=403, detail="Only professors can save attendance")
    
    from app.repositories.attendance_repository import AttendanceRepository
    from sqlalchemy import select
    
    repo = AttendanceRepository(db)
    
    # Verify session exists
    clase_session = await repo.get_by_id(ClaseSession, session_id)
    if not clase_session:
        raise HTTPException(status_code=404, detail=f"ClaseSession {session_id} not found")
    
    # Update each attendance record
    updated_count = 0
    for update in attendance_updates:
        # Find attendance by session and student
        query = select(Attendance).where(
            Attendance.clase_session_id == session_id,
            Attendance.estudiante_id == update.estudiante_id
        )
        result = await db.execute(query)
        attendance = result.scalar_one_or_none()
        
        if attendance:
            attendance.estado = update.estado
            updated_count += 1
    
    await db.commit()
    
    return {
        "message": f"Successfully updated {updated_count} attendance records",
        "updated_count": updated_count
    }


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
    stats = await service.get_session_statistics(session_id)
    
    return SessionStatisticsResponse(**stats)

