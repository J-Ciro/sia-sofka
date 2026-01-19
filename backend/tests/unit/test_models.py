"""Unit tests for database models."""

import pytest
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade


@pytest.mark.asyncio
async def test_user_model_creation(async_db_session: AsyncSession):
    """Test User model creation."""
    from app.utils.codigo_generator import generar_codigo_institucional
    from app.models.user import UserRole
    
    codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
    
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.ESTUDIANTE,
        nombre="Juan",
        apellido="Pérez",
        codigo_institucional=codigo,
        fecha_nacimiento=date(2000, 1, 1),
        numero_contacto="1234567890",
        programa_academico="Ingeniería",
        ciudad_residencia="Bogotá",
    )
    
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.ESTUDIANTE
    assert user.nombre == "Juan"
    assert user.apellido == "Pérez"
    assert user.programa_academico == "Ingeniería"
    assert user.codigo_institucional is not None
    assert user.codigo_institucional.startswith("EST-")


@pytest.mark.asyncio
async def test_profesor_model_creation(async_db_session: AsyncSession):
    """Test Profesor model creation."""
    from app.utils.codigo_generator import generar_codigo_institucional
    from app.models.user import UserRole
    
    codigo = await generar_codigo_institucional(async_db_session, "Profesor")
    
    profesor = User(
        email="profesor@example.com",
        password_hash="hashed_password",
        role=UserRole.PROFESOR,
        nombre="María",
        apellido="González",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1980, 5, 15),
        numero_contacto="0987654321",
        area_ensenanza="Matemáticas",
    )
    
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    assert profesor.id is not None
    assert profesor.role == UserRole.PROFESOR
    assert profesor.area_ensenanza == "Matemáticas"
    assert profesor.codigo_institucional.startswith("PROF-")


@pytest.mark.asyncio
async def test_admin_model_creation(async_db_session: AsyncSession):
    """Test Admin model creation."""
    from app.utils.codigo_generator import generar_codigo_institucional
    from app.models.user import UserRole
    
    codigo = await generar_codigo_institucional(async_db_session, "Admin")
    
    admin = User(
        email="admin@example.com",
        password_hash="hashed_password",
        role=UserRole.ADMIN,
        nombre="Carlos",
        apellido="Rodríguez",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1975, 3, 20),
        numero_contacto="5555555555",
    )
    
    async_db_session.add(admin)
    await async_db_session.commit()
    await async_db_session.refresh(admin)
    
    assert admin.id is not None
    assert admin.role == UserRole.ADMIN
    assert admin.codigo_institucional.startswith("ADM-")


@pytest.mark.asyncio
async def test_subject_model_creation(async_db_session: AsyncSession):
    """Test Subject model creation."""
    from app.utils.codigo_generator import generar_codigo_institucional
    from app.models.user import UserRole
    
    codigo = await generar_codigo_institucional(async_db_session, "Profesor")
    
    profesor = User(
        email="profesor@example.com",
        password_hash="hashed",
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1980, 1, 1),
        numero_contacto="123",
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Matemáticas I",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00-10:00",
        descripcion="Curso de matemáticas básicas",
        profesor_id=profesor.id,
    )
    
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    assert subject.id is not None
    assert subject.nombre == "Matemáticas I"
    assert subject.codigo_institucional == "MAT-101"
    assert subject.numero_creditos == 3
    assert subject.profesor_id == profesor.id


@pytest.mark.asyncio
async def test_enrollment_model_creation(async_db_session: AsyncSession):
    """Test Enrollment model creation."""
    from app.utils.codigo_generator import generar_codigo_institucional
    from app.models.user import UserRole
    
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    
    estudiante = User(
        email="estudiante@example.com",
        password_hash="hashed",
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        numero_contacto="123",
    )
    async_db_session.add(estudiante)
    
    profesor = User(
        email="prof@example.com",
        password_hash="hashed",
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
        numero_contacto="123",
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    await async_db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    
    async_db_session.add(enrollment)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment)
    
    assert enrollment.id is not None
    assert enrollment.estudiante_id == estudiante.id
    assert enrollment.subject_id == subject.id


@pytest.mark.asyncio
async def test_grade_model_creation(async_db_session: AsyncSession):
    """Test Grade model creation."""
    from app.utils.codigo_generator import generar_codigo_institucional
    from app.models.user import UserRole
    
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    
    estudiante = User(
        email="est@example.com",
        password_hash="hashed",
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        numero_contacto="123",
    )
    async_db_session.add(estudiante)
    
    profesor = User(
        email="prof@example.com",
        password_hash="hashed",
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
        numero_contacto="123",
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    await async_db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment)
    
    grade = Grade(
        enrollment_id=enrollment.id,
        nota=4.5,
        periodo="2024-1",
        fecha=date.today(),
        observaciones="Buen desempeño",
    )
    
    async_db_session.add(grade)
    await async_db_session.commit()
    await async_db_session.refresh(grade)
    
    assert grade.id is not None
    assert grade.enrollment_id == enrollment.id
    assert grade.nota == 4.5
    assert grade.periodo == "2024-1"


@pytest.mark.asyncio
async def test_user_subject_relationship(async_db_session: AsyncSession):
    """Test relationship between User (profesor) and Subject."""
    from app.utils.codigo_generator import generar_codigo_institucional
    from app.models.user import UserRole
    
    codigo = await generar_codigo_institucional(async_db_session, "Profesor")
    
    profesor = User(
        email="prof@example.com",
        password_hash="hashed",
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1980, 1, 1),
        numero_contacto="123",
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    subject1 = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    subject2 = Subject(
        nombre="Física",
        codigo_institucional="FIS-101",
        numero_creditos=3,
        horario="Martes 8:00",
        profesor_id=profesor.id,
    )
    async_db_session.add_all([subject1, subject2])
    await async_db_session.commit()
    
    # Test relationship - need to load relationship explicitly in async
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    
    result = await async_db_session.execute(
        select(User).options(selectinload(User.subjects)).where(User.id == profesor.id)
    )
    profesor_loaded = result.scalar_one()
    assert len(profesor_loaded.subjects) == 2


@pytest.mark.asyncio
async def test_enrollment_unique_constraint(async_db_session: AsyncSession):
    """Test that enrollment has unique constraint on (estudiante_id, subject_id)."""
    from app.utils.codigo_generator import generar_codigo_institucional
    from app.models.user import UserRole
    from sqlalchemy.exc import IntegrityError
    
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    
    estudiante = User(
        email="est@example.com",
        password_hash="hashed",
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        numero_contacto="123",
    )
    async_db_session.add(estudiante)
    
    profesor = User(
        email="prof@example.com",
        password_hash="hashed",
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
        numero_contacto="123",
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    await async_db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    enrollment1 = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    async_db_session.add(enrollment1)
    await async_db_session.commit()
    
    # Try to create duplicate enrollment
    enrollment2 = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    async_db_session.add(enrollment2)
    
    with pytest.raises(IntegrityError):  # Should raise IntegrityError
        await async_db_session.commit()

