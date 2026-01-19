"""Unit tests for AdminService."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.services.admin_service import AdminService
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.subject import SubjectCreate
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash
from decimal import Decimal


@pytest.mark.asyncio
async def test_admin_service_create_estudiante(async_db_session: AsyncSession):
    """Test AdminService can create estudiante."""
    # Create admin first
    codigo_admin = await generar_codigo_institucional(async_db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    async_db_session.add(admin)
    await async_db_session.commit()
    
    service = AdminService(async_db_session, admin)
    
    user_data = UserCreate(
        email="newestudiante@example.com",
        password="password123",
        nombre="Nuevo",
        apellido="Estudiante",
        role=UserRole.ESTUDIANTE,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería",
    )
    
    user = await service.create_estudiante(user_data)
    
    assert user.id is not None
    assert user.role == UserRole.ESTUDIANTE
    assert user.programa_academico == "Ingeniería"


@pytest.mark.asyncio
async def test_admin_service_create_profesor(async_db_session: AsyncSession):
    """Test AdminService can create profesor."""
    codigo_admin = await generar_codigo_institucional(async_db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    async_db_session.add(admin)
    await async_db_session.commit()
    
    service = AdminService(async_db_session, admin)
    
    user_data = UserCreate(
        email="newprofesor@example.com",
        password="password123",
        nombre="Nuevo",
        apellido="Profesor",
        role=UserRole.PROFESOR,
        fecha_nacimiento=date(1980, 1, 1),
        area_ensenanza="Matemáticas",
    )
    
    user = await service.create_profesor(user_data)
    
    assert user.id is not None
    assert user.role == UserRole.PROFESOR
    assert user.area_ensenanza == "Matemáticas"


@pytest.mark.asyncio
async def test_admin_service_create_subject(async_db_session: AsyncSession):
    """Test AdminService can create subject."""
    codigo_admin = await generar_codigo_institucional(async_db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    async_db_session.add(admin)
    
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
    
    service = AdminService(async_db_session, admin)
    
    subject_data = SubjectCreate(
        nombre="Nueva Materia",
        codigo_institucional="NUE-101",
        numero_creditos=3,
        horario="Lunes 8:00-10:00",
        profesor_id=profesor.id,
    )
    
    subject = await service.create_subject(subject_data)
    
    assert subject.id is not None
    assert subject.nombre == "Nueva Materia"


@pytest.mark.asyncio
async def test_admin_service_generate_average(async_db_session: AsyncSession):
    """Test AdminService can generate average for estudiante and subject."""
    # Setup
    codigo_admin = await generar_codigo_institucional(async_db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    async_db_session.add(admin)
    
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
    
    # Create grades
    grade1 = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.0"),
        periodo="2024-1",
        fecha=date.today(),
    )
    grade2 = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    grade3 = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("5.0"),
        periodo="2024-1",
        fecha=date.today(),
    )
    async_db_session.add_all([grade1, grade2, grade3])
    await async_db_session.commit()
    
    service = AdminService(async_db_session, admin)
    
    average = await service.generate_average(estudiante.id, subject.id)
    
    # Average should be (4.0 + 4.5 + 5.0) / 3 = 4.5
    assert average == Decimal("4.5")


@pytest.mark.asyncio
async def test_admin_service_get_all_estudiantes(async_db_session: AsyncSession):
    """Test AdminService can get all estudiantes."""
    codigo_admin = await generar_codigo_institucional(async_db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    async_db_session.add(admin)
    
    # Create multiple estudiantes
    for i in range(3):
        codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
        estudiante = User(
            email=f"est{i}@example.com",
            password_hash=get_password_hash("pass"),
            role=UserRole.ESTUDIANTE,
            nombre=f"Est{i}",
            apellido="Test",
            codigo_institucional=codigo,
            fecha_nacimiento=date(2000, 1, 1),
        )
        async_db_session.add(estudiante)
    
    await async_db_session.commit()
    
    service = AdminService(async_db_session, admin)
    estudiantes = await service.get_all_estudiantes()
    
    assert len(estudiantes) == 3
    assert all(est.role == UserRole.ESTUDIANTE for est in estudiantes)


@pytest.mark.asyncio
async def test_admin_service_get_all_profesores(async_db_session: AsyncSession):
    """Test AdminService can get all profesores."""
    codigo_admin = await generar_codigo_institucional(async_db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    async_db_session.add(admin)
    
    # Create multiple profesores
    for i in range(2):
        codigo = await generar_codigo_institucional(async_db_session, "Profesor")
        profesor = User(
            email=f"prof{i}@example.com",
            password_hash=get_password_hash("pass"),
            role=UserRole.PROFESOR,
            nombre=f"Prof{i}",
            apellido="Test",
            codigo_institucional=codigo,
            fecha_nacimiento=date(1980, 1, 1),
        )
        async_db_session.add(profesor)
    
    await async_db_session.commit()
    
    service = AdminService(async_db_session, admin)
    profesores = await service.get_all_profesores()
    
    assert len(profesores) == 2
    assert all(prof.role == UserRole.PROFESOR for prof in profesores)


