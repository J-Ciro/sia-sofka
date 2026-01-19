"""Unit tests for report generation."""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.services.admin_service import AdminService
from app.services.profesor_service import ProfesorService
from app.services.estudiante_service import EstudianteService
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_admin_service_generate_student_report_json(async_db_session: AsyncSession):
    """Test AdminService can generate student report in JSON format."""
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
        programa_academico="Ingeniería",
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
    
    grade = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    async_db_session.add(grade)
    await async_db_session.commit()
    
    service = AdminService(async_db_session, admin)
    report = await service.generate_student_report(estudiante.id, "json")
    
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "application/json"


@pytest.mark.asyncio
async def test_admin_service_generate_student_report_pdf(async_db_session: AsyncSession):
    """Test AdminService can generate student report in PDF format."""
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
        programa_academico="Ingeniería",
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
    
    service = AdminService(async_db_session, admin)
    report = await service.generate_student_report(estudiante.id, "pdf")
    
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "application/pdf"


@pytest.mark.asyncio
async def test_admin_service_generate_student_report_html(async_db_session: AsyncSession):
    """Test AdminService can generate student report in HTML format."""
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
        programa_academico="Ingeniería",
    )
    async_db_session.add(estudiante)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    
    service = AdminService(async_db_session, admin)
    report = await service.generate_student_report(estudiante.id, "html")
    
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "text/html"


@pytest.mark.asyncio
async def test_profesor_service_generate_subject_report_json(async_db_session: AsyncSession):
    """Test ProfesorService can generate subject report in JSON format."""
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
    
    grade = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    async_db_session.add(grade)
    await async_db_session.commit()
    
    service = ProfesorService(async_db_session, profesor)
    report = await service.generate_subject_report(subject.id, "json")
    
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "application/json"


@pytest.mark.asyncio
async def test_profesor_service_generate_subject_report_pdf(async_db_session: AsyncSession):
    """Test ProfesorService can generate subject report in PDF format."""
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
    
    service = ProfesorService(async_db_session, profesor)
    report = await service.generate_subject_report(subject.id, "pdf")
    
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "application/pdf"


@pytest.mark.asyncio
async def test_profesor_service_get_subject_with_students(async_db_session: AsyncSession):
    """Test ProfesorService can get subject with students."""
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
    
    service = ProfesorService(async_db_session, profesor)
    result = await service.get_subject_with_students(subject.id)
    
    assert "subject" in result
    assert "students" in result
    assert result["subject"].id == subject.id
    assert len(result["students"]) == 1


@pytest.mark.asyncio
async def test_estudiante_service_generate_general_report_json(async_db_session: AsyncSession):
    """Test EstudianteService can generate general report in JSON format."""
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería",
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
    
    grade = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    async_db_session.add(grade)
    await async_db_session.commit()
    
    service = EstudianteService(async_db_session, estudiante)
    report = await service.generate_general_report("json")
    
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "application/json"


@pytest.mark.asyncio
async def test_estudiante_service_generate_general_report_pdf(async_db_session: AsyncSession):
    """Test EstudianteService can generate general report in PDF format."""
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería",
    )
    async_db_session.add(estudiante)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    
    service = EstudianteService(async_db_session, estudiante)
    report = await service.generate_general_report("pdf")
    
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "application/pdf"


@pytest.mark.asyncio
async def test_admin_service_generate_average_error_case(async_db_session: AsyncSession):
    """Test AdminService raises error when enrollment not found."""
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
    
    service = AdminService(async_db_session, admin)
    
    # Should raise error because estudiante is not enrolled
    with pytest.raises(ValueError):
        await service.generate_average(estudiante.id, subject.id)


@pytest.mark.asyncio
async def test_profesor_service_generate_subject_report_error(async_db_session: AsyncSession):
    """Test ProfesorService raises error for unassigned subject."""
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
    await async_db_session.commit()
    await async_db_session.refresh(profesor1)
    await async_db_session.refresh(profesor2)
    
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
    
    service = ProfesorService(async_db_session, profesor1)  # profesor1 trying to access
    
    # Should raise error because profesor1 is not assigned
    with pytest.raises(ValueError):
        await service.generate_subject_report(subject.id, "json")

