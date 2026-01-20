"""Unit tests for EnrollmentSerializer."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.api.v1.serializers.enrollment_serializer import EnrollmentSerializer
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.fixture
async def test_data_enrollment_serializer(async_db_session: AsyncSession):
    """Create test data for enrollment serializer tests."""
    # Estudiante
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="estudiante@enrollment-serializer.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Carlos",
        apellido="Rodríguez",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante)
    
    # Profesor
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor = User(
        email="profesor@enrollment-serializer.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Ana",
        apellido="López",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    await async_db_session.refresh(profesor)
    
    # Subjects
    subject1 = Subject(
        nombre="Física",
        codigo_institucional="FIS-101",
        numero_creditos=3,
        horario="Martes 14:00-16:00",
        descripcion="Curso de física",
        profesor_id=profesor.id,
    )
    subject2 = Subject(
        nombre="Química",
        codigo_institucional="QUI-101",
        numero_creditos=3,
        horario="Miércoles 10:00-12:00",
        descripcion="Curso de química",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject1)
    async_db_session.add(subject2)
    await async_db_session.commit()
    await async_db_session.refresh(subject1)
    await async_db_session.refresh(subject2)
    
    # Enrollments
    enrollment1 = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject1.id,
    )
    enrollment2 = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject2.id,
    )
    async_db_session.add(enrollment1)
    async_db_session.add(enrollment2)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment1)
    await async_db_session.refresh(enrollment2)
    
    return {
        "estudiante": estudiante,
        "profesor": profesor,
        "subjects": [subject1, subject2],
        "enrollments": [enrollment1, enrollment2],
    }


@pytest.mark.asyncio
async def test_serialize_batch_empty_list(async_db_session: AsyncSession):
    """Test serializing empty list."""
    result = await EnrollmentSerializer.serialize_batch([], async_db_session)
    assert result == []


@pytest.mark.asyncio
async def test_serialize_batch_with_relationships(
    async_db_session: AsyncSession, test_data_enrollment_serializer
):
    """Test serializing enrollments with estudiante and subject relationships."""
    enrollments = test_data_enrollment_serializer["enrollments"]
    
    result = await EnrollmentSerializer.serialize_batch(enrollments, async_db_session)
    
    assert len(result) == 2
    assert result[0].id == enrollments[0].id
    assert result[0].estudiante is not None
    assert result[0].estudiante.nombre == "Carlos"
    assert result[0].subject is not None
    assert result[0].subject.nombre == "Física"
    
    assert result[1].id == enrollments[1].id
    assert result[1].estudiante.nombre == "Carlos"  # Same estudiante
    assert result[1].subject.nombre == "Química"


@pytest.mark.asyncio
async def test_serialize_batch_batch_loading_efficiency(
    async_db_session: AsyncSession, test_data_enrollment_serializer
):
    """Test that batch loading is efficient (no N+1 queries)."""
    enrollments = test_data_enrollment_serializer["enrollments"]
    
    result = await EnrollmentSerializer.serialize_batch(enrollments, async_db_session)
    
    assert len(result) == 2
    # Both should have same estudiante (batch loaded once)
    assert result[0].estudiante.id == result[1].estudiante.id
    assert result[0].estudiante.nombre == "Carlos"
    assert result[1].estudiante.nombre == "Carlos"


@pytest.mark.asyncio
async def test_serialize_batch_missing_estudiante_in_map(
    async_db_session: AsyncSession, test_data_enrollment_serializer
):
    """Test serializing when estudiante is not in batch-loaded map."""
    enrollments = test_data_enrollment_serializer["enrollments"]
    
    # Manually set estudiante_id that won't be in map
    enrollments[0].estudiante_id = 99999
    
    result = await EnrollmentSerializer.serialize_batch(enrollments, async_db_session)
    
    assert len(result) == 2
    # First enrollment should have None estudiante
    assert result[0].estudiante is None
    # Second enrollment should still have estudiante
    assert result[1].estudiante is not None


@pytest.mark.asyncio
async def test_serialize_batch_missing_subject_in_map(
    async_db_session: AsyncSession, test_data_enrollment_serializer
):
    """Test serializing when subject is not in batch-loaded map."""
    enrollments = test_data_enrollment_serializer["enrollments"]
    
    # Manually set subject_id that won't be in map
    enrollments[0].subject_id = 99999
    
    result = await EnrollmentSerializer.serialize_batch(enrollments, async_db_session)
    
    assert len(result) == 2
    # First enrollment should have None subject
    assert result[0].subject is None
    # Second enrollment should still have subject
    assert result[1].subject is not None

