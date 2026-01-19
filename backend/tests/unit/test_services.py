"""Unit tests for services."""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.services.user_service import UserService
from app.services.subject_service import SubjectService
from app.services.enrollment_service import EnrollmentService
from app.services.grade_service import GradeService
from app.schemas.user import UserCreate
from app.schemas.subject import SubjectCreate
from app.schemas.enrollment import EnrollmentCreate
from app.schemas.grade import GradeCreate
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_user_service_create_estudiante(async_db_session: AsyncSession):
    """Test UserService create estudiante."""
    service = UserService(async_db_session)
    
    user_data = UserCreate(
        email="estudiante@example.com",
        password="password123",
        nombre="Estudiante",
        apellido="Test",
        role=UserRole.ESTUDIANTE,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería",
        ciudad_residencia="Bogotá",
    )
    
    user = await service.create_user(user_data)
    
    assert user.id is not None
    assert user.email == "estudiante@example.com"
    assert user.role == UserRole.ESTUDIANTE
    assert user.programa_academico == "Ingeniería"
    assert user.codigo_institucional.startswith("EST-")
    assert user.edad is not None


@pytest.mark.asyncio
async def test_user_service_create_profesor(async_db_session: AsyncSession):
    """Test UserService create profesor."""
    service = UserService(async_db_session)
    
    user_data = UserCreate(
        email="profesor@example.com",
        password="password123",
        nombre="Profesor",
        apellido="Test",
        role=UserRole.PROFESOR,
        fecha_nacimiento=date(1980, 5, 15),
        area_ensenanza="Matemáticas",
    )
    
    user = await service.create_user(user_data)
    
    assert user.id is not None
    assert user.role == UserRole.PROFESOR
    assert user.area_ensenanza == "Matemáticas"
    assert user.codigo_institucional.startswith("PROF-")


@pytest.mark.asyncio
async def test_user_service_calculate_age(async_db_session: AsyncSession):
    """Test UserService age calculation."""
    service = UserService(async_db_session)
    
    user_data = UserCreate(
        email="age@example.com",
        password="password123",
        nombre="Age",
        apellido="Test",
        role=UserRole.ESTUDIANTE,
        fecha_nacimiento=date(2000, 1, 1),
    )
    
    user = await service.create_user(user_data)
    
    # Age should be calculated (approximately 24 years in 2024)
    assert user.edad is not None
    assert user.edad > 20
    assert user.edad < 30


@pytest.mark.asyncio
async def test_subject_service_create(async_db_session: AsyncSession):
    """Test SubjectService create."""
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
    
    service = SubjectService(async_db_session)
    subject_data = SubjectCreate(
        nombre="Física I",
        codigo_institucional="FIS-101",
        numero_creditos=4,
        horario="Martes 10:00-12:00",
        descripcion="Curso de física básica",
        profesor_id=profesor.id,
    )
    
    subject = await service.create_subject(subject_data)
    
    assert subject.id is not None
    assert subject.nombre == "Física I"
    assert subject.numero_creditos == 4


@pytest.mark.asyncio
async def test_subject_service_validate_credits(async_db_session: AsyncSession):
    """Test SubjectService credit validation."""
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
    
    service = SubjectService(async_db_session)
    
    # Should fail with invalid credits (negative)
    with pytest.raises(ValueError):
        subject_data = SubjectCreate(
            nombre="Invalid",
            codigo_institucional="INV-101",
            numero_creditos=-1,
            profesor_id=profesor.id,
        )
        await service.create_subject(subject_data)
    
    # Should fail with credits > 10
    with pytest.raises(ValueError):
        subject_data = SubjectCreate(
            nombre="Invalid",
            codigo_institucional="INV-102",
            numero_creditos=11,
            profesor_id=profesor.id,
        )
        await service.create_subject(subject_data)


@pytest.mark.asyncio
async def test_enrollment_service_create(async_db_session: AsyncSession):
    """Test EnrollmentService create."""
    # Setup
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
    
    service = EnrollmentService(async_db_session)
    enrollment_data = EnrollmentCreate(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    
    enrollment = await service.create_enrollment(enrollment_data)
    
    assert enrollment.id is not None
    assert enrollment.estudiante_id == estudiante.id


@pytest.mark.asyncio
async def test_enrollment_service_duplicate_prevention(async_db_session: AsyncSession):
    """Test EnrollmentService prevents duplicate enrollments."""
    # Setup
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
    
    service = EnrollmentService(async_db_session)
    enrollment_data = EnrollmentCreate(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    
    # Create first enrollment
    await service.create_enrollment(enrollment_data)
    
    # Try to create duplicate (should fail)
    with pytest.raises(ValueError):
        await service.create_enrollment(enrollment_data)


@pytest.mark.asyncio
async def test_grade_service_create(async_db_session: AsyncSession):
    """Test GradeService create."""
    # Setup
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
    
    service = GradeService(async_db_session)
    grade_data = GradeCreate(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
        observaciones="Buen desempeño",
    )
    
    grade = await service.create_grade(grade_data)
    
    assert grade.id is not None
    assert grade.nota == Decimal("4.5")
    assert grade.periodo == "2024-1"


@pytest.mark.asyncio
async def test_grade_service_validate_range(async_db_session: AsyncSession):
    """Test GradeService validates note range."""
    # Setup enrollment
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
    
    service = GradeService(async_db_session)
    
    # Should fail with note < 0
    with pytest.raises(ValueError):
        grade_data = GradeCreate(
            enrollment_id=enrollment.id,
            nota=Decimal("-0.5"),
            periodo="2024-1",
            fecha=date.today(),
        )
        await service.create_grade(grade_data)
    
    # Should fail with note > 5
    with pytest.raises(ValueError):
        grade_data = GradeCreate(
            enrollment_id=enrollment.id,
            nota=Decimal("5.5"),
            periodo="2024-1",
            fecha=date.today(),
        )
        await service.create_grade(grade_data)


@pytest.mark.asyncio
async def test_grade_service_calculate_average(async_db_session: AsyncSession):
    """Test GradeService calculates average."""
    # Setup enrollment
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
    
    service = GradeService(async_db_session)
    
    # Create multiple grades
    grade1 = GradeCreate(
        enrollment_id=enrollment.id,
        nota=Decimal("4.0"),
        periodo="2024-1",
        fecha=date.today(),
    )
    await service.create_grade(grade1)
    
    grade2 = GradeCreate(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    await service.create_grade(grade2)
    
    grade3 = GradeCreate(
        enrollment_id=enrollment.id,
        nota=Decimal("5.0"),
        periodo="2024-1",
        fecha=date.today(),
    )
    await service.create_grade(grade3)
    
    # Calculate average
    average = await service.calculate_average(enrollment.id)
    
    # Average should be (4.0 + 4.5 + 5.0) / 3 = 4.5
    assert average == Decimal("4.5")


