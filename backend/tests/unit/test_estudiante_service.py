"""Unit tests for EstudianteService."""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.services.estudiante_service import EstudianteService
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_estudiante_service_get_grades_by_subject(async_db_session: AsyncSession):
    """Test EstudianteService can get grades by subject."""
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
    async_db_session.add_all([grade1, grade2])
    await async_db_session.commit()
    
    service = EstudianteService(async_db_session, estudiante)
    grades = await service.get_grades_by_subject(subject.id)
    
    assert len(grades) == 2
    assert all(grade.enrollment_id == enrollment.id for grade in grades)


@pytest.mark.asyncio
async def test_estudiante_service_get_all_enrollments(async_db_session: AsyncSession):
    """Test EstudianteService can get all enrollments."""
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
    
    # Create multiple subjects
    subjects = []
    for i in range(3):
        subject = Subject(
            nombre=f"Materia {i}",
            codigo_institucional=f"MAT-{i}01",
            numero_creditos=3,
            horario=f"Día {i} 8:00",
            profesor_id=profesor.id,
        )
        subjects.append(subject)
        async_db_session.add(subject)
    await async_db_session.commit()
    for sub in subjects:
        await async_db_session.refresh(sub)
    
    # Enroll in all subjects
    for subject in subjects:
        enrollment = Enrollment(
            estudiante_id=estudiante.id,
            subject_id=subject.id,
        )
        async_db_session.add(enrollment)
    await async_db_session.commit()
    
    service = EstudianteService(async_db_session, estudiante)
    enrollments = await service.get_all_enrollments()
    
    assert len(enrollments) == 3
    assert all(enroll["enrollment"].estudiante_id == estudiante.id for enroll in enrollments)


@pytest.mark.asyncio
async def test_estudiante_service_get_subject_status(async_db_session: AsyncSession):
    """Test EstudianteService can get subject status with grades."""
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
    async_db_session.add_all([grade1, grade2])
    await async_db_session.commit()
    
    service = EstudianteService(async_db_session, estudiante)
    status = await service.get_subject_status(subject.id)
    
    assert status["subject"].id == subject.id
    assert status["enrollment"].id == enrollment.id
    assert len(status["grades"]) == 2
    assert "average" in status


@pytest.mark.asyncio
async def test_estudiante_service_get_subject_status_without_grades(async_db_session: AsyncSession):
    """Test EstudianteService get_subject_status handles enrollment without grades (covers lines 101-102)."""
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="est_no_grades@example.com",
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
    
    # No grades created - calculate_average will raise ValueError
    
    service = EstudianteService(async_db_session, estudiante)
    status = await service.get_subject_status(subject.id)
    
    # Should return status with average = None (ValueError caught, líneas 101-102)
    assert status["subject"].id == subject.id
    assert status["enrollment"].id == enrollment.id
    assert len(status["grades"]) == 0
    assert status["average"] is None


@pytest.mark.asyncio
async def test_estudiante_service_cannot_access_other_student_grades(async_db_session: AsyncSession):
    """Test EstudianteService cannot access other student's grades."""
    codigo_est1 = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante1 = User(
        email="est1@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est1",
        apellido="Test",
        codigo_institucional=codigo_est1,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante1)
    
    codigo_est2 = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante2 = User(
        email="est2@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est2",
        apellido="Test",
        codigo_institucional=codigo_est2,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante2)
    
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
    await async_db_session.refresh(estudiante1)
    await async_db_session.refresh(estudiante2)
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
    
    # Only estudiante2 is enrolled
    enrollment = Enrollment(
        estudiante_id=estudiante2.id,
        subject_id=subject.id,
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment)
    
    service = EstudianteService(async_db_session, estudiante1)  # estudiante1 trying to access
    
    # Should fail because estudiante1 is not enrolled (covers línea 68 y 90)
    with pytest.raises(ValueError, match="Estudiante is not enrolled"):
        await service.get_grades_by_subject(subject.id)
    
    with pytest.raises(ValueError, match="Estudiante is not enrolled"):
        await service.get_subject_status(subject.id)


@pytest.mark.asyncio
async def test_estudiante_service_update_profile(async_db_session: AsyncSession):
    """Test EstudianteService can update own profile."""
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Original",
        apellido="Name",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería",
        ciudad_residencia="Bogotá",
        numero_contacto="1234567890",
    )
    async_db_session.add(estudiante)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    
    service = EstudianteService(async_db_session, estudiante)
    
    from app.schemas.user import UserUpdate
    update_data = UserUpdate(
        nombre="Updated",
        programa_academico="Medicina",
        ciudad_residencia="Medellín",
        numero_contacto="0987654321",
    )
    
    updated = await service.update_profile(update_data)
    
    assert updated.nombre == "Updated"
    assert updated.programa_academico == "Medicina"
    assert updated.ciudad_residencia == "Medellín"
    assert updated.numero_contacto == "0987654321"


