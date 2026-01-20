"""Async unit tests for AttendanceRepository async methods.

Tests for async repository methods to increase coverage.
"""

import pytest
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.attendance import ClaseSession, Attendance, AttendanceStatus
from app.models.user import User, UserRole
from app.models.enrollment import Enrollment
from app.models.subject import Subject
from app.repositories.attendance_repository import AttendanceRepository


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_sessions_by_profesor_async(async_db_session: AsyncSession):
    """Test getting sessions by profesor (async)."""
    from bcrypt import hashpw, gensalt
    
    profesor = User(
        email="repo_profesor@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Repo",
        apellido="Profesor",
        codigo_institucional="PRF444",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Repo Subject",
        codigo_institucional="REPO001",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    # Create sessions
    today = date.today()
    for i in range(2):
        session = ClaseSession(
            subject_id=subject.id,
            fecha=date(today.year, today.month, today.day - i),
            hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
            hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
            creado_por=profesor.id,
        )
        async_db_session.add(session)
    await async_db_session.commit()
    
    repo = AttendanceRepository(async_db_session)
    sessions = await repo.get_sessions_by_profesor(profesor.id)
    
    assert len(sessions) >= 2
    
    # Test with subject filter
    sessions_filtered = await repo.get_sessions_by_profesor(profesor.id, subject.id)
    assert len(sessions_filtered) >= 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_sessions_for_student_async(async_db_session: AsyncSession):
    """Test getting sessions for student (async)."""
    from bcrypt import hashpw, gensalt
    
    profesor = User(
        email="student_sess_prof@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Student",
        apellido="Prof",
        codigo_institucional="PRF333",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    student = User(
        email="student_sess_student@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.ESTUDIANTE,
        nombre="Student",
        apellido="Sess",
        codigo_institucional="EST333",
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(student)
    await async_db_session.commit()
    await async_db_session.refresh(student)
    
    subject = Subject(
        nombre="Student Sess Subject",
        codigo_institucional="STUSESS001",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    # Enroll student
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
    
    repo = AttendanceRepository(async_db_session)
    sessions = await repo.get_sessions_for_student(student.id)
    
    assert len(sessions) >= 1
    
    # Test with subject filter
    sessions_filtered = await repo.get_sessions_for_student(student.id, subject.id)
    assert len(sessions_filtered) >= 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_attendances_by_session_async(async_db_session: AsyncSession):
    """Test getting attendances by session (async)."""
    from bcrypt import hashpw, gensalt
    
    profesor = User(
        email="att_sess_prof@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Att",
        apellido="Prof",
        codigo_institucional="PRF222",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    student = User(
        email="att_sess_student@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.ESTUDIANTE,
        nombre="Att",
        apellido="Student",
        codigo_institucional="EST222",
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(student)
    await async_db_session.commit()
    await async_db_session.refresh(student)
    
    subject = Subject(
        nombre="Att Sess Subject",
        codigo_institucional="ATTSESS001",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
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
    
    # Create attendance (only one per student per session)
    attendance = Attendance(
        clase_session_id=session.id,
        estudiante_id=student.id,
        estado=AttendanceStatus.PRESENTE,
    )
    async_db_session.add(attendance)
    await async_db_session.commit()
    
    repo = AttendanceRepository(async_db_session)
    attendances = await repo.get_attendances_by_session(session.id)
    
    assert len(attendances) >= 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_count_by_status_async(async_db_session: AsyncSession):
    """Test counting by status (async)."""
    from bcrypt import hashpw, gensalt
    
    profesor = User(
        email="count_prof@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Count",
        apellido="Prof",
        codigo_institucional="PRF111",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    students = []
    for i in range(3):
        student = User(
            email=f"count_student{i}@test.com",
            password_hash=hashpw(b"password123", gensalt()).decode(),
            role=UserRole.ESTUDIANTE,
            nombre=f"Student{i}",
            apellido="Count",
            codigo_institucional=f"EST11{i}",
            fecha_nacimiento=date(2000, 1, 1),
        )
        async_db_session.add(student)
        await async_db_session.commit()
        await async_db_session.refresh(student)
        students.append(student)
    
    subject = Subject(
        nombre="Count Subject",
        codigo_institucional="COUNT001",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
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
    
    repo = AttendanceRepository(async_db_session)
    counts = await repo.count_by_status_async(session.id)
    
    assert counts[AttendanceStatus.PRESENTE] == 2
    assert counts[AttendanceStatus.AUSENTE] == 1
    assert counts[AttendanceStatus.TARDANZA] == 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_calculate_attendance_percentage_async(async_db_session: AsyncSession):
    """Test calculating attendance percentage (async)."""
    from bcrypt import hashpw, gensalt
    
    profesor = User(
        email="perc_prof@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Perc",
        apellido="Prof",
        codigo_institucional="PRF000",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    students = []
    for i in range(5):
        student = User(
            email=f"perc_student{i}@test.com",
            password_hash=hashpw(b"password123", gensalt()).decode(),
            role=UserRole.ESTUDIANTE,
            nombre=f"Student{i}",
            apellido="Perc",
            codigo_institucional=f"EST00{i}",
            fecha_nacimiento=date(2000, 1, 1),
        )
        async_db_session.add(student)
        await async_db_session.commit()
        await async_db_session.refresh(student)
        students.append(student)
    
    subject = Subject(
        nombre="Perc Subject",
        codigo_institucional="PERC001",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
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
    
    # Create attendances: 3 PRESENTE, 1 TARDANZA, 1 AUSENTE = 80% (4/5)
    statuses = [
        AttendanceStatus.PRESENTE,
        AttendanceStatus.PRESENTE,
        AttendanceStatus.PRESENTE,
        AttendanceStatus.TARDANZA,
        AttendanceStatus.AUSENTE,
    ]
    for student, status in zip(students, statuses):
        attendance = Attendance(
            clase_session_id=session.id,
            estudiante_id=student.id,
            estado=status,
        )
        async_db_session.add(attendance)
    await async_db_session.commit()
    
    repo = AttendanceRepository(async_db_session)
    percentage = await repo.calculate_attendance_percentage_async(session.id)
    
    assert percentage == 80.0  # (3 + 1) / 5 * 100


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_session_by_subject_and_date_async(async_db_session: AsyncSession):
    """Test getting session by subject and date (async)."""
    from bcrypt import hashpw, gensalt
    
    profesor = User(
        email="date_prof@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Date",
        apellido="Prof",
        codigo_institucional="PRF999",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Date Subject",
        codigo_institucional="DATE001",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
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
    
    repo = AttendanceRepository(async_db_session)
    found_session = await repo.get_session_by_subject_and_date(subject.id, today)
    
    assert found_session is not None
    assert found_session.id == session.id
    
    # Test non-existent
    yesterday = date(today.year, today.month, today.day - 1)
    not_found = await repo.get_session_by_subject_and_date(subject.id, yesterday)
    assert not_found is None
