"""Unit tests for GradeValidator."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.api.v1.validators.grade_validator import GradeValidator
from app.core.exceptions import NotFoundError, ForbiddenError
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.fixture
async def test_data_grade_validator(async_db_session: AsyncSession):
    """Create test data for grade validator tests."""
    # Profesor 1
    codigo_prof1 = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor1 = User(
        email="profesor1@validator.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Uno",
        codigo_institucional=codigo_prof1,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor1)
    
    # Profesor 2
    codigo_prof2 = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor2 = User(
        email="profesor2@validator.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Dos",
        codigo_institucional=codigo_prof2,
        fecha_nacimiento=date(1985, 1, 1),
    )
    async_db_session.add(profesor2)
    
    await async_db_session.commit()
    await async_db_session.refresh(profesor1)
    await async_db_session.refresh(profesor2)
    
    # Subject assigned to profesor1
    subject1 = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=4,
        horario="Lunes 10:00-12:00",
        descripcion="Curso de matemáticas",
        profesor_id=profesor1.id,
    )
    async_db_session.add(subject1)
    await async_db_session.commit()
    await async_db_session.refresh(subject1)
    
    # Estudiante
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="estudiante@validator.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    
    # Enrollment
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject1.id,
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment)
    
    return {
        "profesor1": profesor1,
        "profesor2": profesor2,
        "subject1": subject1,
        "estudiante": estudiante,
        "enrollment": enrollment,
    }


@pytest.mark.asyncio
async def test_verify_profesor_subject_permission_success(
    async_db_session: AsyncSession, test_data_grade_validator
):
    """Test successful verification when profesor has permission."""
    profesor1 = test_data_grade_validator["profesor1"]
    enrollment = test_data_grade_validator["enrollment"]
    
    # Should not raise any exception
    await GradeValidator.verify_profesor_subject_permission(
        async_db_session, profesor1, enrollment.id
    )


@pytest.mark.asyncio
async def test_verify_profesor_subject_permission_enrollment_not_found(
    async_db_session: AsyncSession, test_data_grade_validator
):
    """Test verification fails when enrollment not found."""
    profesor1 = test_data_grade_validator["profesor1"]
    
    with pytest.raises(NotFoundError) as exc_info:
        await GradeValidator.verify_profesor_subject_permission(
            async_db_session, profesor1, 99999
        )
    
    assert "Enrollment" in str(exc_info.value)


@pytest.mark.asyncio
async def test_verify_profesor_subject_permission_subject_not_assigned(
    async_db_session: AsyncSession, test_data_grade_validator
):
    """Test verification fails when subject not assigned to profesor."""
    profesor2 = test_data_grade_validator["profesor2"]  # Different profesor
    enrollment = test_data_grade_validator["enrollment"]  # Subject assigned to profesor1
    
    with pytest.raises(ForbiddenError) as exc_info:
        await GradeValidator.verify_profesor_subject_permission(
            async_db_session, profesor2, enrollment.id
        )
    
    assert "unassigned subject" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_verify_profesor_subject_permission_subject_not_found(
    async_db_session: AsyncSession, test_data_grade_validator
):
    """Test verification fails when subject not found."""
    profesor1 = test_data_grade_validator["profesor1"]
    
    # Create enrollment with non-existent subject
    enrollment = Enrollment(
        estudiante_id=test_data_grade_validator["estudiante"].id,
        subject_id=99999,
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment)
    
    with pytest.raises(ForbiddenError) as exc_info:
        await GradeValidator.verify_profesor_subject_permission(
            async_db_session, profesor1, enrollment.id
        )
    
    assert "unassigned subject" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_verify_profesor_can_access_subject_success(
    async_db_session: AsyncSession, test_data_grade_validator
):
    """Test successful verification when profesor can access subject."""
    profesor1 = test_data_grade_validator["profesor1"]
    subject1 = test_data_grade_validator["subject1"]
    
    # Should not raise any exception
    await GradeValidator.verify_profesor_can_access_subject(
        async_db_session, profesor1, subject1.id
    )


@pytest.mark.asyncio
async def test_verify_profesor_can_access_subject_not_assigned(
    async_db_session: AsyncSession, test_data_grade_validator
):
    """Test verification fails when subject not assigned to profesor."""
    profesor2 = test_data_grade_validator["profesor2"]  # Different profesor
    subject1 = test_data_grade_validator["subject1"]  # Assigned to profesor1
    
    with pytest.raises(ForbiddenError) as exc_info:
        await GradeValidator.verify_profesor_can_access_subject(
            async_db_session, profesor2, subject1.id
        )
    
    assert "not assigned" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_verify_profesor_can_access_subject_not_found(
    async_db_session: AsyncSession, test_data_grade_validator
):
    """Test verification fails when subject doesn't exist."""
    profesor1 = test_data_grade_validator["profesor1"]
    
    with pytest.raises(ForbiddenError) as exc_info:
        await GradeValidator.verify_profesor_can_access_subject(
            async_db_session, profesor1, 99999
        )
    
    assert "not assigned" in str(exc_info.value).lower()

