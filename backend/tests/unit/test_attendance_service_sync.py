"""Unit tests for AttendanceService async methods.

These tests use async_db_session since AttendanceService now requires AsyncSession.
All methods are async after the refactoring.
"""

import pytest
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import (
    ClaseSession,
    Attendance,
    AttendanceStatus,
)
from app.models.user import User, UserRole
from app.models.enrollment import Enrollment
from app.models.subject import Subject
from app.services.attendance_service import AttendanceService
from app.core.exceptions import NotFoundError


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mark_all_present_sync(async_db_session: AsyncSession, async_profesor_user: User, async_subject, async_enrollment):
    """Test mark_all_present with async session."""
    # Create session
    today = date.today()
    session = ClaseSession(
        subject_id=async_subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=async_profesor_user.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    service = AttendanceService(async_db_session, async_profesor_user)
    
    # Mark all present (async method)
    count = await service.mark_all_present(session.id)
    
    assert count >= 1
    
    # Verify attendance was created/updated
    from sqlalchemy import select
    stmt = select(Attendance).where(
        Attendance.clase_session_id == session.id,
        Attendance.estudiante_id == async_enrollment.estudiante_id
    )
    result = await async_db_session.execute(stmt)
    attendance = result.scalar_one_or_none()
    
    assert attendance is not None
    assert attendance.estado == AttendanceStatus.PRESENTE


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mark_all_absent_sync(async_db_session: AsyncSession, async_profesor_user: User, async_subject, async_enrollment):
    """Test mark_all_absent with async session."""
    # Create session
    today = date.today()
    session = ClaseSession(
        subject_id=async_subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=async_profesor_user.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    service = AttendanceService(async_db_session, async_profesor_user)
    
    # Mark all absent (async method)
    count = await service.mark_all_absent(session.id)
    
    assert count >= 1
    
    # Verify attendance was created/updated
    from sqlalchemy import select
    stmt = select(Attendance).where(
        Attendance.clase_session_id == session.id,
        Attendance.estudiante_id == async_enrollment.estudiante_id
    )
    result = await async_db_session.execute(stmt)
    attendance = result.scalar_one_or_none()
    
    assert attendance is not None
    assert attendance.estado == AttendanceStatus.AUSENTE


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mark_all_present_not_found(async_db_session: AsyncSession, async_profesor_user: User):
    """Test mark_all_present with non-existent session."""
    service = AttendanceService(async_db_session, async_profesor_user)
    
    with pytest.raises(NotFoundError):
        await service.mark_all_present(99999)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mark_all_absent_not_found(async_db_session: AsyncSession, async_profesor_user: User):
    """Test mark_all_absent with non-existent session."""
    service = AttendanceService(async_db_session, async_profesor_user)
    
    with pytest.raises(NotFoundError):
        await service.mark_all_absent(99999)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_attendance_sync(async_db_session: AsyncSession, async_profesor_user: User, async_subject, async_enrollment):
    """Test update_attendance with async session."""
    # Create session
    today = date.today()
    session = ClaseSession(
        subject_id=async_subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=async_profesor_user.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    # Create attendance
    attendance = Attendance(
        clase_session_id=session.id,
        estudiante_id=async_enrollment.estudiante_id,
        estado=AttendanceStatus.AUSENTE,
    )
    async_db_session.add(attendance)
    await async_db_session.commit()
    await async_db_session.refresh(attendance)
    
    service = AttendanceService(async_db_session, async_profesor_user)
    
    # Update attendance (async method)
    updated = await service.update_attendance(attendance.id, AttendanceStatus.PRESENTE)
    
    assert updated is not None
    assert updated.estado == AttendanceStatus.PRESENTE


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_attendance_not_found_sync(async_db_session: AsyncSession, async_profesor_user: User):
    """Test update_attendance with non-existent attendance."""
    service = AttendanceService(async_db_session, async_profesor_user)
    
    with pytest.raises(NotFoundError):
        await service.update_attendance(99999, AttendanceStatus.PRESENTE)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_attendance_stats_new(async_db_session: AsyncSession, async_estudiante_user: User, async_subject):
    """Test create_attendance_stats creating new stats (async)."""
    service = AttendanceService(async_db_session, None)
    
    stats = await service.create_attendance_stats(
        estudiante_id=async_estudiante_user.id,
        subject_id=async_subject.id,
        total_sesiones=10,
        presentes=8,
        ausentes=1,
        tardanzas=1,
    )
    
    assert stats.estudiante_id == async_estudiante_user.id
    assert stats.subject_id == async_subject.id
    assert stats.total_sesiones == 10
    assert stats.presentes == 8
    assert stats.ausentes == 1
    assert stats.tardanzas == 1
    assert stats.porcentaje_asistencia == 90.0  # (8+1)/10 * 100


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_attendance_stats_update_existing(
    async_db_session: AsyncSession, async_estudiante_user: User, async_subject
):
    """Test create_attendance_stats updating existing stats (async)."""
    service = AttendanceService(async_db_session, None)
    
    # Create first stats
    stats1 = await service.create_attendance_stats(
        estudiante_id=async_estudiante_user.id,
        subject_id=async_subject.id,
        total_sesiones=10,
        presentes=8,
        ausentes=1,
        tardanzas=1,
    )
    
    # Update stats
    stats2 = await service.create_attendance_stats(
        estudiante_id=async_estudiante_user.id,
        subject_id=async_subject.id,
        total_sesiones=20,
        presentes=16,
        ausentes=2,
        tardanzas=2,
    )
    
    assert stats1.id == stats2.id  # Same record
    assert stats2.total_sesiones == 20
    assert stats2.porcentaje_asistencia == 90.0  # (16+2)/20 * 100
