"""Unit tests for ProfesorService."""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.services.profesor_service import ProfesorService
from app.schemas.grade import GradeCreate
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_profesor_service_get_assigned_subjects(async_db_session: AsyncSession):
    """Test ProfesorService can get assigned subjects."""
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
    
    # Create subjects for this profesor
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
        numero_creditos=4,
        horario="Martes 8:00",
        profesor_id=profesor.id,
    )
    async_db_session.add_all([subject1, subject2])
    await async_db_session.commit()
    
    service = ProfesorService(async_db_session, profesor)
    subjects = await service.get_assigned_subjects()
    
    assert len(subjects) == 2
    assert all(sub.profesor_id == profesor.id for sub in subjects)


@pytest.mark.asyncio
async def test_profesor_service_get_students_by_subject(async_db_session: AsyncSession):
    """Test ProfesorService can get students enrolled in a subject."""
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
    
    # Create estudiantes
    estudiantes = []
    for i in range(3):
        codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
        est = User(
            email=f"est{i}@example.com",
            password_hash=get_password_hash("pass"),
            role=UserRole.ESTUDIANTE,
            nombre=f"Est{i}",
            apellido="Test",
            codigo_institucional=codigo,
            fecha_nacimiento=date(2000, 1, 1),
        )
        estudiantes.append(est)
        async_db_session.add(est)
    
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    for est in estudiantes:
        await async_db_session.refresh(est)
    
    # Create subject
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
    
    # Enroll estudiantes
    for est in estudiantes:
        enrollment = Enrollment(
            estudiante_id=est.id,
            subject_id=subject.id,
        )
        async_db_session.add(enrollment)
    await async_db_session.commit()
    
    service = ProfesorService(async_db_session, profesor)
    students = await service.get_students_by_subject(subject.id)
    
    assert len(students) == 3
    assert all(est.role == UserRole.ESTUDIANTE for est in students)


@pytest.mark.asyncio
async def test_profesor_service_create_grade(async_db_session: AsyncSession):
    """Test ProfesorService can create grade for student in assigned subject."""
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
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    await async_db_session.refresh(estudiante)
    
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
    
    service = ProfesorService(async_db_session, profesor)
    
    grade_data = GradeCreate(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
        observaciones="Buen trabajo",
    )
    
    grade = await service.create_grade(grade_data, subject.id)
    
    assert grade.id is not None
    assert grade.nota == Decimal("4.5")
    assert grade.observaciones == "Buen trabajo"


@pytest.mark.asyncio
async def test_profesor_service_cannot_create_grade_for_unassigned_subject(async_db_session: AsyncSession):
    """Test ProfesorService cannot create grade for unassigned subject."""
    codigo_prof1 = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor1 = User(
        email="prof1@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof1",
        apellido="Test",
        codigo_institucional=codigo_prof1,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor1)
    
    codigo_prof2 = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor2 = User(
        email="prof2@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof2",
        apellido="Test",
        codigo_institucional=codigo_prof2,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor2)
    
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
    await async_db_session.commit()
    await async_db_session.refresh(profesor1)
    await async_db_session.refresh(profesor2)
    await async_db_session.refresh(estudiante)
    
    # Subject assigned to profesor2
    subject = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor2.id,
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
    
    service = ProfesorService(async_db_session, profesor1)  # profesor1 trying to grade
    
    grade_data = GradeCreate(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    
    # Should fail because profesor1 is not assigned to this subject
    with pytest.raises(ValueError):
        await service.create_grade(grade_data, subject.id)


@pytest.mark.asyncio
async def test_profesor_service_update_profile(async_db_session: AsyncSession):
    """Test ProfesorService can update own profile."""
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Original",
        apellido="Name",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
        area_ensenanza="Matemáticas",
        numero_contacto="1234567890",
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    service = ProfesorService(async_db_session, profesor)
    
    from app.schemas.user import UserUpdate
    update_data = UserUpdate(
        nombre="Updated",
        area_ensenanza="Física",
        numero_contacto="0987654321",
    )
    
    updated = await service.update_profile(update_data)
    
    assert updated.nombre == "Updated"
    assert updated.area_ensenanza == "Física"
    assert updated.numero_contacto == "0987654321"


