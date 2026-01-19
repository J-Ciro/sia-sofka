"""Unit tests for EstudianteService report generation methods."""

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


# ==================== Fixtures ====================

@pytest.fixture
async def test_data_estudiante_reports(async_db_session: AsyncSession):
    """Create comprehensive test data for estudiante report generation."""
    # Profesor
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor = User(
        email="profesor@reports.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Reports",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    
    # Estudiante
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="estudiante@reports.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="María",
        apellido="González",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería de Sistemas",
    )
    async_db_session.add(estudiante)
    
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    await async_db_session.refresh(estudiante)
    
    # Subject 1 (with credits = 4)
    subject1 = Subject(
        nombre="Cálculo Diferencial",
        codigo_institucional="CAL-101",
        numero_creditos=4,
        horario="Lunes 8:00-10:00",
        descripcion="Curso de cálculo",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject1)
    
    # Subject 2 (with credits = 3)
    subject2 = Subject(
        nombre="Programación I",
        codigo_institucional="PRO-101",
        numero_creditos=3,
        horario="Martes 10:00-12:00",
        descripcion="Curso de programación",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject2)
    
    await async_db_session.commit()
    await async_db_session.refresh(subject1)
    await async_db_session.refresh(subject2)
    
    # Enrollment 1
    enrollment1 = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject1.id,
    )
    async_db_session.add(enrollment1)
    
    # Enrollment 2
    enrollment2 = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject2.id,
    )
    async_db_session.add(enrollment2)
    
    await async_db_session.commit()
    await async_db_session.refresh(enrollment1)
    await async_db_session.refresh(enrollment2)
    
    # Grades for enrollment 1 (average = 4.0)
    grade1_1 = Grade(
        enrollment_id=enrollment1.id,
        nota=Decimal("3.5"),
        periodo="2024-1",
        fecha=date(2024, 1, 15),
        observaciones="Primera evaluación",
    )
    grade1_2 = Grade(
        enrollment_id=enrollment1.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date(2024, 2, 15),
        observaciones="Segunda evaluación",
    )
    async_db_session.add_all([grade1_1, grade1_2])
    
    # Grades for enrollment 2 (average = 5.0)
    grade2_1 = Grade(
        enrollment_id=enrollment2.id,
        nota=Decimal("5.0"),
        periodo="2024-1",
        fecha=date(2024, 1, 20),
        observaciones="Primera evaluación",
    )
    grade2_2 = Grade(
        enrollment_id=enrollment2.id,
        nota=Decimal("5.0"),
        periodo="2024-1",
        fecha=date(2024, 2, 20),
        observaciones="Segunda evaluación",
    )
    async_db_session.add_all([grade2_1, grade2_2])
    
    await async_db_session.commit()
    for grade in [grade1_1, grade1_2, grade2_1, grade2_2]:
        await async_db_session.refresh(grade)
    
    return {
        "profesor": profesor,
        "estudiante": estudiante,
        "subjects": [subject1, subject2],
        "enrollments": [enrollment1, enrollment2],
        "grades": [grade1_1, grade1_2, grade2_1, grade2_2],
    }


# ==================== generate_general_report Tests ====================

@pytest.mark.asyncio
async def test_generate_general_report_json_format_complete_data(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report in JSON format with complete data (covers lines 111-178)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("json")
    
    # Verify report structure
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "application/json"
    assert "json" in report["filename"].lower()
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Verify estudiante data
    assert "estudiante" in content
    assert content["estudiante"]["id"] == estudiante.id
    assert content["estudiante"]["nombre"] == "María"
    assert content["estudiante"]["apellido"] == "González"
    assert content["estudiante"]["codigo_institucional"] == estudiante.codigo_institucional
    assert content["estudiante"]["programa_academico"] == "Ingeniería de Sistemas"
    
    # Verify subjects data
    assert "subjects" in content
    assert len(content["subjects"]) == 2
    
    # Verify first subject
    subject1_data = next((s for s in content["subjects"] if s["subject"]["nombre"] == "Cálculo Diferencial"), None)
    assert subject1_data is not None
    assert subject1_data["subject"]["numero_creditos"] == 4
    assert len(subject1_data["grades"]) == 2
    assert subject1_data["average"] == 4.0  # (3.5 + 4.5) / 2
    
    # Verify second subject
    subject2_data = next((s for s in content["subjects"] if s["subject"]["nombre"] == "Programación I"), None)
    assert subject2_data is not None
    assert subject2_data["subject"]["numero_creditos"] == 3
    assert len(subject2_data["grades"]) == 2
    assert subject2_data["average"] == 5.0  # (5.0 + 5.0) / 2
    
    # Verify general average (weighted by credits)
    # (4.0 * 4 + 5.0 * 3) / (4 + 3) = (16.0 + 15.0) / 7 = 31.0 / 7 ≈ 4.43
    assert "general_average" in content
    assert content["general_average"] == round((4.0 * 4 + 5.0 * 3) / 7, 2)


@pytest.mark.asyncio
async def test_generate_general_report_pdf_format(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report in PDF format (covers lines 176-178)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("pdf")
    
    # Verify report structure
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "application/pdf"
    assert "pdf" in report["filename"].lower()
    
    # Verify PDF content is bytes
    assert isinstance(report["content"], bytes)
    assert len(report["content"]) > 0
    assert report["content"].startswith(b"%PDF")


@pytest.mark.asyncio
async def test_generate_general_report_html_format(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report in HTML format (covers lines 176-178)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("html")
    
    # Verify report structure
    assert "content" in report
    assert "filename" in report
    assert "content_type" in report
    assert report["content_type"] == "text/html"
    assert "html" in report["filename"].lower()
    
    # Verify HTML content
    content = report["content"]
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    assert "<html" in content.lower() or "<!doctype" in content.lower()


@pytest.mark.asyncio
async def test_generate_general_report_no_enrollments(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report with estudiante that has no enrollments (covers lines 122-124, 134-135, 174)."""
    # Create estudiante without enrollments
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="est_no_enrollments@reports.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Sin",
        apellido="Enrollments",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería",
    )
    async_db_session.add(estudiante)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("json")
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Verify structure
    assert "estudiante" in content
    assert "subjects" in content
    assert len(content["subjects"]) == 0  # No enrollments
    assert content["general_average"] is None  # No credits, so no average (línea 174)


@pytest.mark.asyncio
async def test_generate_general_report_enrollment_without_grades(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report with enrollment that has no grades (covers lines 142-146)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    profesor = test_data_estudiante_reports["profesor"]
    
    # Create subject and enrollment without grades
    subject = Subject(
        nombre="Química",
        codigo_institucional="QUI-101",
        numero_creditos=2,
        horario="Jueves 8:00",
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
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("json")
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Find subject without grades
    subject_no_grades = next((s for s in content["subjects"] if s["subject"]["nombre"] == "Química"), None)
    assert subject_no_grades is not None
    assert len(subject_no_grades["grades"]) == 0
    assert subject_no_grades["average"] is None  # No grades, so no average (línea 146)


@pytest.mark.asyncio
async def test_generate_general_report_subject_not_found_skipped(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report skips enrollment when subject not found (covers lines 138-140)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    
    # Create enrollment with non-existent subject_id (edge case)
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=99999,  # Non-existent subject
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment)
    
    service = EstudianteService(async_db_session, estudiante)
    
    # Should not raise error, but skip the enrollment with non-existent subject
    report = await service.generate_general_report("json")
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Should still include the valid subjects (2 subjects)
    assert "subjects" in content
    assert len([s for s in content["subjects"] if s["subject"]["id"] != 99999]) == 2


@pytest.mark.asyncio
async def test_generate_general_report_general_average_calculation(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report calculates general average correctly (covers lines 159-172)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("json")
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Verify general average calculation
    # Subject 1: average = 4.0, credits = 4
    # Subject 2: average = 5.0, credits = 3
    # General average = (4.0 * 4 + 5.0 * 3) / (4 + 3) = 31.0 / 7 ≈ 4.43
    expected_average = round((4.0 * 4 + 5.0 * 3) / 7, 2)
    assert content["general_average"] == expected_average


@pytest.mark.asyncio
async def test_generate_general_report_general_average_none_when_no_valid_averages(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report sets general_average to None when no valid averages (covers lines 173-174)."""
    # Create estudiante with enrollments but no grades
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="est_no_grades@reports.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Sin",
        apellido="Grades",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante)
    
    profesor = test_data_estudiante_reports["profesor"]
    subject = Subject(
        nombre="Test",
        codigo_institucional="TEST-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    await async_db_session.refresh(subject)
    
    # Enrollment without grades
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("json")
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Should have subject but no average
    assert len(content["subjects"]) == 1
    assert content["subjects"][0]["average"] is None
    assert content["general_average"] is None  # total_credits = 0, so general_average = None (línea 174)


@pytest.mark.asyncio
async def test_generate_general_report_grades_serialization(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report correctly serializes grades (covers línea 155)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("json")
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Verify grades structure
    subject1_data = next((s for s in content["subjects"] if s["subject"]["nombre"] == "Cálculo Diferencial"), None)
    assert subject1_data is not None
    assert len(subject1_data["grades"]) == 2
    
    # Verify grade structure
    grade = subject1_data["grades"][0]
    assert "nota" in grade
    assert "periodo" in grade
    assert "fecha" in grade
    assert grade["nota"] == 3.5 or grade["nota"] == 4.5
    assert grade["periodo"] == "2024-1"
    assert isinstance(grade["fecha"], str)  # Should be serialized as string


@pytest.mark.asyncio
async def test_generate_general_report_calculates_average_exception_handling(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report handles ValueError from calculate_average (covers lines 143-146)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    profesor = test_data_estudiante_reports["profesor"]
    
    # Create subject with enrollment but no grades
    # calculate_average will raise ValueError
    subject = Subject(
        nombre="Sin Grades",
        codigo_institucional="NOG-101",
        numero_creditos=3,
        horario="Viernes 8:00",
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
    
    service = EstudianteService(async_db_session, estudiante)
    
    # Should not raise error, but set average to None
    report = await service.generate_general_report("json")
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Find subject without grades
    subject_no_grades = next((s for s in content["subjects"] if s["subject"]["nombre"] == "Sin Grades"), None)
    assert subject_no_grades is not None
    assert subject_no_grades["average"] is None  # ValueError caught, average = None (línea 146)


@pytest.mark.asyncio
async def test_generate_general_report_multiple_subjects_weighted_average(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report calculates weighted average correctly with multiple subjects (covers lines 163-168)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    profesor = test_data_estudiante_reports["profesor"]
    
    # Add third subject with different credits and average
    subject3 = Subject(
        nombre="Base de Datos",
        codigo_institucional="BD-201",
        numero_creditos=5,  # More credits
        horario="Jueves 14:00",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject3)
    await async_db_session.commit()
    await async_db_session.refresh(subject3)
    
    enrollment3 = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject3.id,
    )
    async_db_session.add(enrollment3)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment3)
    
    # Add grades with average = 4.5
    grade3_1 = Grade(
        enrollment_id=enrollment3.id,
        nota=Decimal("4.0"),
        periodo="2024-1",
        fecha=date(2024, 1, 25),
    )
    grade3_2 = Grade(
        enrollment_id=enrollment3.id,
        nota=Decimal("5.0"),
        periodo="2024-1",
        fecha=date(2024, 2, 25),
    )
    async_db_session.add_all([grade3_1, grade3_2])
    await async_db_session.commit()
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("json")
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Verify general average with weighted calculation
    # Subject 1: 4.0 * 4 = 16.0
    # Subject 2: 5.0 * 3 = 15.0
    # Subject 3: 4.5 * 5 = 22.5
    # Total: (16.0 + 15.0 + 22.5) / (4 + 3 + 5) = 53.5 / 12 ≈ 4.46
    expected_average = round((4.0 * 4 + 5.0 * 3 + 4.5 * 5) / 12, 2)
    assert content["general_average"] == expected_average
    
    # Verify all 3 subjects are included
    assert len(content["subjects"]) == 3


# ==================== Additional Edge Cases ====================

@pytest.mark.asyncio
async def test_generate_general_report_estudiante_data_correct(async_db_session: AsyncSession, test_data_estudiante_reports):
    """Test generate_general_report includes correct estudiante data (covers lines 126-133)."""
    estudiante = test_data_estudiante_reports["estudiante"]
    
    service = EstudianteService(async_db_session, estudiante)
    
    report = await service.generate_general_report("json")
    
    # Parse JSON content
    import json
    if isinstance(report["content"], bytes):
        content = json.loads(report["content"].decode("utf-8"))
    else:
        content = json.loads(report["content"])
    
    # Verify estudiante data matches
    assert content["estudiante"]["id"] == estudiante.id
    assert content["estudiante"]["nombre"] == estudiante.nombre
    assert content["estudiante"]["apellido"] == estudiante.apellido
    assert content["estudiante"]["codigo_institucional"] == estudiante.codigo_institucional
    assert content["estudiante"]["programa_academico"] == estudiante.programa_academico

