"""Unit tests for repositories."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.repositories.user_repository import UserRepository
from app.repositories.subject_repository import SubjectRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.grade_repository import GradeRepository
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_user_repository_create(async_db_session: AsyncSession):
    """Test UserRepository create method."""
    repo = UserRepository(async_db_session)
    
    codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
    user_data = {
        "email": "test@example.com",
        "password_hash": get_password_hash("password123"),
        "role": UserRole.ESTUDIANTE,
        "nombre": "Test",
        "apellido": "User",
        "codigo_institucional": codigo,
        "fecha_nacimiento": date(2000, 1, 1),
    }
    
    user = await repo.create(user_data)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.ESTUDIANTE


@pytest.mark.asyncio
async def test_user_repository_get_by_id(async_db_session: AsyncSession):
    """Test UserRepository get_by_id method."""
    repo = UserRepository(async_db_session)
    
    codigo = await generar_codigo_institucional(async_db_session, "Profesor")
    user = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    found_user = await repo.get_by_id(user.id)
    
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.email == "prof@example.com"


@pytest.mark.asyncio
async def test_user_repository_get_by_email(async_db_session: AsyncSession):
    """Test UserRepository get_by_email method."""
    repo = UserRepository(async_db_session)
    
    codigo = await generar_codigo_institucional(async_db_session, "Admin")
    user = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1975, 1, 1),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    
    found_user = await repo.get_by_email("admin@example.com")
    
    assert found_user is not None
    assert found_user.email == "admin@example.com"


@pytest.mark.asyncio
async def test_user_repository_update(async_db_session: AsyncSession):
    """Test UserRepository update method."""
    repo = UserRepository(async_db_session)
    
    codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
    user = User(
        email="update@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Original",
        apellido="Name",
        codigo_institucional=codigo,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    update_data = {"nombre": "Updated", "apellido": "Name"}
    updated_user = await repo.update(user.id, update_data)
    
    assert updated_user.nombre == "Updated"
    assert updated_user.apellido == "Name"


@pytest.mark.asyncio
async def test_user_repository_delete(async_db_session: AsyncSession):
    """Test UserRepository delete method."""
    repo = UserRepository(async_db_session)
    
    codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
    user = User(
        email="delete@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Delete",
        apellido="Test",
        codigo_institucional=codigo,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    await repo.delete(user.id)
    await async_db_session.commit()
    
    found_user = await repo.get_by_id(user.id)
    assert found_user is None


@pytest.mark.asyncio
async def test_subject_repository_create(async_db_session: AsyncSession):
    """Test SubjectRepository create method."""
    # Create profesor first
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    repo = SubjectRepository(async_db_session)
    subject_data = {
        "nombre": "Matemáticas I",
        "codigo_institucional": "MAT-101",
        "numero_creditos": 3,
        "horario": "Lunes 8:00-10:00",
        "profesor_id": profesor.id,
    }
    
    subject = await repo.create(subject_data)
    
    assert subject.id is not None
    assert subject.nombre == "Matemáticas I"
    assert subject.profesor_id == profesor.id


@pytest.mark.asyncio
async def test_enrollment_repository_create(async_db_session: AsyncSession):
    """Test EnrollmentRepository create method."""
    # Create estudiante and subject
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante)
    
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
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
    
    repo = EnrollmentRepository(async_db_session)
    enrollment_data = {
        "estudiante_id": estudiante.id,
        "subject_id": subject.id,
    }
    
    enrollment = await repo.create(enrollment_data)
    
    assert enrollment.id is not None
    assert enrollment.estudiante_id == estudiante.id
    assert enrollment.subject_id == subject.id


@pytest.mark.asyncio
async def test_grade_repository_create(async_db_session: AsyncSession):
    """Test GradeRepository create method."""
    # Setup: create estudiante, profesor, subject, enrollment
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante)
    
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
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
    
    repo = GradeRepository(async_db_session)
    grade_data = {
        "enrollment_id": enrollment.id,
        "nota": 4.5,
        "periodo": "2024-1",
        "fecha": date.today(),
    }
    
    grade = await repo.create(grade_data)
    
    assert grade.id is not None
    assert grade.nota == 4.5
    assert grade.periodo == "2024-1"


