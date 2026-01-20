"""Unit tests for AttendanceService sync methods.

Tests for methods that work with Session (not AsyncSession).
Note: These methods are marked as async but use sync code internally.
"""

import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session

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
async def test_mark_all_present_sync(db_session: Session, profesor_user: User, subject, enrollment):
    """Test mark_all_present with sync session."""
    # Create session
    today = date.today()
    session = ClaseSession(
        subject_id=subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=profesor_user.id,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    service = AttendanceService(db_session, profesor_user)
    
    # Mark all present (async method but uses sync code)
    count = await service.mark_all_present(session.id)
    
    assert count >= 1
    
    # Verify attendance was created/updated
    attendance = db_session.query(Attendance).filter(
        Attendance.clase_session_id == session.id,
        Attendance.estudiante_id == enrollment.estudiante_id
    ).first()
    
    assert attendance is not None
    assert attendance.estado == AttendanceStatus.PRESENTE


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mark_all_absent_sync(db_session: Session, profesor_user: User, subject, enrollment):
    """Test mark_all_absent with sync session."""
    # Create session
    today = date.today()
    session = ClaseSession(
        subject_id=subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=profesor_user.id,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    service = AttendanceService(db_session, profesor_user)
    
    # Mark all absent (async method but uses sync code)
    count = await service.mark_all_absent(session.id)
    
    assert count >= 1
    
    # Verify attendance was created/updated
    attendance = db_session.query(Attendance).filter(
        Attendance.clase_session_id == session.id,
        Attendance.estudiante_id == enrollment.estudiante_id
    ).first()
    
    assert attendance is not None
    assert attendance.estado == AttendanceStatus.AUSENTE


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mark_all_present_not_found(db_session: Session, profesor_user: User):
    """Test mark_all_present with non-existent session."""
    service = AttendanceService(db_session, profesor_user)
    
    with pytest.raises(NotFoundError):
        await service.mark_all_present(99999)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mark_all_absent_not_found(db_session: Session, profesor_user: User):
    """Test mark_all_absent with non-existent session."""
    service = AttendanceService(db_session, profesor_user)
    
    with pytest.raises(NotFoundError):
        await service.mark_all_absent(99999)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_attendance_sync(db_session: Session, profesor_user: User, subject, enrollment):
    """Test update_attendance with sync session."""
    # Create session
    today = date.today()
    session = ClaseSession(
        subject_id=subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=profesor_user.id,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    # Create attendance
    attendance = Attendance(
        clase_session_id=session.id,
        estudiante_id=enrollment.estudiante_id,
        estado=AttendanceStatus.AUSENTE,
    )
    db_session.add(attendance)
    db_session.commit()
    db_session.refresh(attendance)
    
    service = AttendanceService(db_session, profesor_user)
    
    # Update attendance (async method but uses sync code)
    updated = await service.update_attendance(attendance.id, AttendanceStatus.PRESENTE)
    
    assert updated.estado == AttendanceStatus.PRESENTE


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_attendance_not_found_sync(db_session: Session, profesor_user: User):
    """Test update_attendance with non-existent attendance."""
    service = AttendanceService(db_session, profesor_user)
    
    with pytest.raises(NotFoundError):
        await service.update_attendance(99999, AttendanceStatus.PRESENTE)


@pytest.mark.unit
def test_create_attendance_stats_new(db_session: Session, estudiante_user: User, subject):
    """Test create_attendance_stats creating new stats."""
    service = AttendanceService(db_session, None)
    
    stats = service.create_attendance_stats(
        estudiante_id=estudiante_user.id,
        subject_id=subject.id,
        total_sesiones=10,
        presentes=8,
        ausentes=1,
        tardanzas=1,
    )
    
    assert stats.estudiante_id == estudiante_user.id
    assert stats.subject_id == subject.id
    assert stats.total_sesiones == 10
    assert stats.presentes == 8
    assert stats.ausentes == 1
    assert stats.tardanzas == 1
    assert stats.porcentaje_asistencia == 90.0  # (8+1)/10 * 100


@pytest.mark.unit
def test_create_attendance_stats_update_existing(
    db_session: Session, estudiante_user: User, subject
):
    """Test create_attendance_stats updating existing stats."""
    service = AttendanceService(db_session, None)
    
    # Create first stats
    stats1 = service.create_attendance_stats(
        estudiante_id=estudiante_user.id,
        subject_id=subject.id,
        total_sesiones=10,
        presentes=8,
        ausentes=1,
        tardanzas=1,
    )
    
    # Update stats
    stats2 = service.create_attendance_stats(
        estudiante_id=estudiante_user.id,
        subject_id=subject.id,
        total_sesiones=20,
        presentes=16,
        ausentes=2,
        tardanzas=2,
    )
    
    assert stats1.id == stats2.id  # Same record
    assert stats2.total_sesiones == 20
    assert stats2.porcentaje_asistencia == 90.0  # (16+2)/20 * 100
