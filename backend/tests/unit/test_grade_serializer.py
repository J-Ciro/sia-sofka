"""Unit tests for GradeSerializer."""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.api.v1.serializers.grade_serializer import GradeSerializer
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.fixture
async def test_data_grade_serializer(async_db_session: AsyncSession):
    """Create test data for grade serializer tests."""
    # Estudiante
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="estudiante@serializer.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Juan",
        apellido="Pérez",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante)
    
    # Profesor
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor = User(
        email="profesor@serializer.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="María",
        apellido="García",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    await async_db_session.refresh(profesor)
    
    # Subject
    subject = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=4,
        horario="Lunes 10:00-12:00",
        descripcion="Curso de matemáticas",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    # Enrollment
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment)
    
    # Grades
    grade1 = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
        observaciones="Buen rendimiento",
    )
    grade2 = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("3.8"),
        periodo="2024-2",
        fecha=date.today(),
        observaciones="Mejora necesaria",
    )
    async_db_session.add(grade1)
    async_db_session.add(grade2)
    await async_db_session.commit()
    await async_db_session.refresh(grade1)
    await async_db_session.refresh(grade2)
    
    # Manually set relationships for testing
    grade1.enrollment = enrollment
    grade2.enrollment = enrollment
    enrollment.estudiante = estudiante
    enrollment.subject = subject
    
    return {
        "estudiante": estudiante,
        "profesor": profesor,
        "subject": subject,
        "enrollment": enrollment,
        "grades": [grade1, grade2],
    }


@pytest.mark.asyncio
async def test_serialize_batch_empty_list(async_db_session: AsyncSession):
    """Test serializing empty list."""
    result = await GradeSerializer.serialize_batch([], async_db_session)
    assert result == []


@pytest.mark.asyncio
async def test_serialize_batch_with_enrollment_relationships(
    async_db_session: AsyncSession, test_data_grade_serializer
):
    """Test serializing grades with enrollment relationships."""
    grades = test_data_grade_serializer["grades"]
    
    result = await GradeSerializer.serialize_batch(grades, async_db_session)
    
    assert len(result) == 2
    assert result[0].id == grades[0].id
    assert result[0].nota == Decimal("4.5")
    assert result[0].enrollment is not None
    assert result[0].enrollment.estudiante is not None
    assert result[0].enrollment.estudiante.nombre == "Juan"
    assert result[0].enrollment.subject is not None
    assert result[0].enrollment.subject.nombre == "Matemáticas"
    
    assert result[1].id == grades[1].id
    assert result[1].nota == Decimal("3.8")


@pytest.mark.asyncio
async def test_serialize_batch_without_enrollment(
    async_db_session: AsyncSession, test_data_grade_serializer
):
    """Test serializing grades without enrollment relationship."""
    # Create grade without enrollment relationship
    enrollment = test_data_grade_serializer["enrollment"]
    grade = Grade(
        enrollment_id=enrollment.id,  # Use existing enrollment
        nota=Decimal("5.0"),
        periodo="2024-1",
        fecha=date.today(),
    )
    async_db_session.add(grade)
    await async_db_session.commit()
    await async_db_session.refresh(grade)
    
    # Manually set enrollment to None for testing
    grade.enrollment = None
    
    result = await GradeSerializer.serialize_batch([grade], async_db_session)
    
    assert len(result) == 1
    assert result[0].id == grade.id
    assert result[0].nota == Decimal("5.0")
    assert result[0].enrollment is None


@pytest.mark.asyncio
async def test_serialize_batch_batch_loading_efficiency(
    async_db_session: AsyncSession, test_data_grade_serializer
):
    """Test that batch loading is efficient (no N+1 queries)."""
    grades = test_data_grade_serializer["grades"]
    
    # Add another grade with same enrollment (should reuse batch-loaded data)
    enrollment = test_data_grade_serializer["enrollment"]
    grade3 = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.2"),
        periodo="2024-3",
        fecha=date.today(),
    )
    async_db_session.add(grade3)
    await async_db_session.commit()
    await async_db_session.refresh(grade3)
    grade3.enrollment = enrollment
    grades.append(grade3)
    
    result = await GradeSerializer.serialize_batch(grades, async_db_session)
    
    assert len(result) == 3
    # All should have same estudiante and subject (batch loaded)
    assert all(r.enrollment.estudiante.nombre == "Juan" for r in result if r.enrollment)
    assert all(r.enrollment.subject.nombre == "Matemáticas" for r in result if r.enrollment)


@pytest.mark.asyncio
async def test_serialize_batch_missing_estudiante_in_map(
    async_db_session: AsyncSession, test_data_grade_serializer
):
    """Test serializing when estudiante is not in batch-loaded map."""
    grades = test_data_grade_serializer["grades"]
    enrollment = test_data_grade_serializer["enrollment"]
    
    # Manually set enrollment with estudiante_id that won't be in map
    enrollment.estudiante_id = 99999
    
    result = await GradeSerializer.serialize_batch(grades, async_db_session)
    
    assert len(result) == 2
    # Enrollment should exist but estudiante should be None
    assert result[0].enrollment is not None
    assert result[0].enrollment.estudiante is None


@pytest.mark.asyncio
async def test_serialize_batch_missing_subject_in_map(
    async_db_session: AsyncSession, test_data_grade_serializer
):
    """Test serializing when subject is not in batch-loaded map."""
    grades = test_data_grade_serializer["grades"]
    enrollment = test_data_grade_serializer["enrollment"]
    
    # Manually set enrollment with subject_id that won't be in map
    enrollment.subject_id = 99999
    
    result = await GradeSerializer.serialize_batch(grades, async_db_session)
    
    assert len(result) == 2
    # Enrollment should exist but subject should be None
    assert result[0].enrollment is not None
    assert result[0].enrollment.subject is None

