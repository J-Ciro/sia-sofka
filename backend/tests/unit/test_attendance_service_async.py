"""Async unit tests for AttendanceService async methods.

Tests for async methods that require AsyncSession to increase coverage.
"""

import pytest
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.attendance import (
    ClaseSession,
    Attendance,
    AttendanceStatus,
)
from app.models.user import User, UserRole
from app.models.enrollment import Enrollment
from app.models.subject import Subject
from app.services.attendance_service import AttendanceService
from app.core.exceptions import NotFoundError, ValidationError, UnauthorizedError


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_clase_session_async(async_db_session: AsyncSession):
    """Test creating clase session with async session."""
    from bcrypt import hashpw, gensalt
    
    # Create profesor
    profesor = User(
        email="async_profesor@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Async",
        apellido="Profesor",
        codigo_institucional="PRF888",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    # Create subject
    subject = Subject(
        nombre="Async Test Subject",
        codigo_institucional="ASYNC001",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    # Create student and enrollment
    student = User(
        email="async_student@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.ESTUDIANTE,
        nombre="Async",
        apellido="Student",
        codigo_institucional="EST888",
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(student)
    await async_db_session.commit()
    await async_db_session.refresh(student)
    
    enrollment = Enrollment(
        estudiante_id=student.id,
        subject_id=subject.id,
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    
    # Create service and session
    service = AttendanceService(async_db_session, profesor)
    today = date.today()
    
    clase_session = await service.create_clase_session(
        subject_id=subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        descripcion="Async test session",
    )
    
    assert clase_session.id is not None
    assert clase_session.subject_id == subject.id
    assert clase_session.creado_por == profesor.id
    
    # Verify attendance was created
    result = await async_db_session.execute(
        select(Attendance).where(Attendance.clase_session_id == clase_session.id)
    )
    attendances = result.scalars().all()
    assert len(attendances) == 1
    assert attendances[0].estado == AttendanceStatus.AUSENTE


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_session_statistics_async(async_db_session: AsyncSession):
    """Test getting session statistics with async session."""
    from bcrypt import hashpw, gensalt
    
    profesor = User(
        email="stats_profesor@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Stats",
        apellido="Profesor",
        codigo_institucional="PRF777",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Stats Subject",
        codigo_institucional="STATS001",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    # Create students
    students = []
    for i in range(3):
        student = User(
            email=f"stats_student{i}@test.com",
            password_hash=hashpw(b"password123", gensalt()).decode(),
            role=UserRole.ESTUDIANTE,
            nombre=f"Student{i}",
            apellido="Stats",
            codigo_institucional=f"EST77{i}",
            fecha_nacimiento=date(2000, 1, 1),
        )
        async_db_session.add(student)
        await async_db_session.commit()
        await async_db_session.refresh(student)
        students.append(student)
        
        enrollment = Enrollment(
            estudiante_id=student.id,
            subject_id=subject.id,
        )
        async_db_session.add(enrollment)
        await async_db_session.commit()
    
    # Create session
    today = date.today()
    session = ClaseSession(
        subject_id=subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    # Create attendances: 2 PRESENTE, 1 AUSENTE
    statuses = [AttendanceStatus.PRESENTE, AttendanceStatus.PRESENTE, AttendanceStatus.AUSENTE]
    for student, status in zip(students, statuses):
        attendance = Attendance(
            clase_session_id=session.id,
            estudiante_id=student.id,
            estado=status,
        )
        async_db_session.add(attendance)
    await async_db_session.commit()
    
    # Get statistics
    service = AttendanceService(async_db_session, profesor)
    stats = await service.get_session_statistics(session.id)
    
    assert stats["total"] == 3
    assert stats["presentes"] == 2
    assert stats["ausentes"] == 1
    assert stats["tardanzas"] == 0
    assert stats["porcentaje_asistencia"] == pytest.approx(66.67, rel=0.01)  # 2/3 * 100


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_clase_session_unauthorized(async_db_session: AsyncSession):
    """Test creating session as non-profesor raises error."""
    from bcrypt import hashpw, gensalt
    
    student = User(
        email="unauth_student@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.ESTUDIANTE,
        nombre="Unauth",
        apellido="Student",
        codigo_institucional="EST666",
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(student)
    await async_db_session.commit()
    await async_db_session.refresh(student)
    
    service = AttendanceService(async_db_session, student)
    today = date.today()
    
    with pytest.raises(UnauthorizedError):
        await service.create_clase_session(
            subject_id=1,
            fecha=today,
            hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
            hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_clase_session_duplicate(async_db_session: AsyncSession):
    """Test creating duplicate session raises error."""
    from bcrypt import hashpw, gensalt
    
    profesor = User(
        email="dup_profesor@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Dup",
        apellido="Profesor",
        codigo_institucional="PRF555",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Dup Subject",
        codigo_institucional="DUP001",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    service = AttendanceService(async_db_session, profesor)
    today = date.today()
    
    # Create first session
    await service.create_clase_session(
        subject_id=subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
    )
    
    # Try to create duplicate
    with pytest.raises(ValidationError):
        await service.create_clase_session(
            subject_id=subject.id,
            fecha=today,
            hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
            hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        )
