"""Unit tests for services edge cases to achieve 100% coverage."""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.services.admin_service import AdminService
from app.services.user_service import UserService
from app.services.grade_service import GradeService
from app.services.enrollment_service import EnrollmentService
from app.services.subject_service import SubjectService
from app.schemas.user import UserCreate
from app.schemas.grade import GradeCreate, GradeUpdate
from app.schemas.enrollment import EnrollmentCreate
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


# ==================== AdminService Edge Cases ====================

@pytest.mark.asyncio
async def test_admin_service_create_estudiante_wrong_role(async_db_session: AsyncSession):
    """Test AdminService.create_estudiante raises ValueError for wrong role (covers línea 47)."""
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
    await async_db_session.refresh(admin)
    
    service = AdminService(async_db_session, admin)
    
    # Try to create estudiante with wrong role (PROFESOR instead of ESTUDIANTE)
    user_data = UserCreate(
        email="wrong@example.com",
        password="password123",
        nombre="Wrong",
        apellido="Role",
        role=UserRole.PROFESOR,  # Wrong role
        fecha_nacimiento=date(2000, 1, 1),
    )
    
    with pytest.raises(ValueError, match="Role must be Estudiante"):
        await service.create_estudiante(user_data)


@pytest.mark.asyncio
async def test_admin_service_create_profesor_wrong_role(async_db_session: AsyncSession):
    """Test AdminService.create_profesor raises ValueError for wrong role (covers línea 63)."""
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
    await async_db_session.refresh(admin)
    
    service = AdminService(async_db_session, admin)
    
    # Try to create profesor with wrong role (ESTUDIANTE instead of PROFESOR)
    user_data = UserCreate(
        email="wrong@example.com",
        password="password123",
        nombre="Wrong",
        apellido="Role",
        role=UserRole.ESTUDIANTE,  # Wrong role
        fecha_nacimiento=date(1980, 1, 1),
    )
    
    with pytest.raises(ValueError, match="Role must be Profesor"):
        await service.create_profesor(user_data)


# ==================== UserService Edge Cases ====================

@pytest.mark.asyncio
async def test_user_service_create_user_duplicate_email(async_db_session: AsyncSession):
    """Test UserService.create_user raises ValueError for duplicate email (covers línea 38)."""
    codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
    existing_user = User(
        email="existing@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Existing",
        apellido="User",
        codigo_institucional=codigo,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(existing_user)
    await async_db_session.commit()
    
    service = UserService(async_db_session)
    
    # Try to create user with duplicate email
    user_data = UserCreate(
        email="existing@example.com",  # Duplicate email
        password="password123",
        nombre="New",
        apellido="User",
        role=UserRole.ESTUDIANTE,
        fecha_nacimiento=date(2001, 1, 1),
    )
    
    with pytest.raises(ValueError, match="Email already registered"):
        await service.create_user(user_data)


@pytest.mark.asyncio
async def test_user_service_get_user_by_email(async_db_session: AsyncSession):
    """Test UserService.get_user_by_email (covers línea 88)."""
    codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Test",
        apellido="User",
        codigo_institucional=codigo,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    service = UserService(async_db_session)
    
    # Get user by email
    found_user = await service.get_user_by_email("test@example.com")
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.email == "test@example.com"
    
    # Get non-existent user
    not_found = await service.get_user_by_email("nonexistent@example.com")
    assert not_found is None


# ==================== GradeService Edge Cases ====================

@pytest.mark.asyncio
async def test_grade_service_create_grade_invalid_range_low(async_db_session: AsyncSession):
    """Test GradeService.create_grade raises ValueError for note < 0.0 (covers línea 38)."""
    service = GradeService(async_db_session)
    
    # Use model_construct to bypass Pydantic validation and test service validation
    grade_data = GradeCreate.model_construct(
        enrollment_id=1,  # Will fail on enrollment check, but we test the range first
        nota=Decimal("-0.1"),  # Invalid: less than 0.0
        periodo="2024-1",
        fecha=date.today(),
    )
    
    with pytest.raises(ValueError, match="Note must be between 0.0 and 5.0"):
        await service.create_grade(grade_data)


@pytest.mark.asyncio
async def test_grade_service_create_grade_invalid_range_high(async_db_session: AsyncSession):
    """Test GradeService.create_grade raises ValueError for note > 5.0 (covers línea 38)."""
    service = GradeService(async_db_session)
    
    # Use model_construct to bypass Pydantic validation and test service validation
    grade_data = GradeCreate.model_construct(
        enrollment_id=1,
        nota=Decimal("5.1"),  # Invalid: greater than 5.0
        periodo="2024-1",
        fecha=date.today(),
    )
    
    with pytest.raises(ValueError, match="Note must be between 0.0 and 5.0"):
        await service.create_grade(grade_data)


@pytest.mark.asyncio
async def test_grade_service_create_grade_enrollment_not_found(async_db_session: AsyncSession):
    """Test GradeService.create_grade raises ValueError when enrollment not found (covers línea 43)."""
    service = GradeService(async_db_session)
    
    grade_data = GradeCreate(
        enrollment_id=99999,  # Non-existent enrollment
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    
    with pytest.raises(ValueError, match="Enrollment not found"):
        await service.create_grade(grade_data)


@pytest.mark.asyncio
async def test_grade_service_get_grade_by_id(async_db_session: AsyncSession):
    """Test GradeService.get_grade_by_id (covers línea 59)."""
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
    
    grade = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    async_db_session.add(grade)
    await async_db_session.commit()
    await async_db_session.refresh(grade)
    
    service = GradeService(async_db_session)
    
    # Get grade by ID
    found_grade = await service.get_grade_by_id(grade.id)
    assert found_grade is not None
    assert found_grade.id == grade.id
    assert found_grade.nota == Decimal("4.5")
    
    # Get non-existent grade
    not_found = await service.get_grade_by_id(99999)
    assert not_found is None


@pytest.mark.asyncio
async def test_grade_service_update_grade_invalid_range(async_db_session: AsyncSession):
    """Test GradeService.update_grade raises ValueError for invalid note range (covers línea 79)."""
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
    
    grade = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.0"),
        periodo="2024-1",
        fecha=date.today(),
    )
    async_db_session.add(grade)
    await async_db_session.commit()
    await async_db_session.refresh(grade)
    
    service = GradeService(async_db_session)
    
    # Try to update with invalid note (> 5.0) - use model_construct to bypass Pydantic validation
    update_data = GradeUpdate.model_construct(nota=Decimal("5.1"))
    with pytest.raises(ValueError, match="Note must be between 0.0 and 5.0"):
        await service.update_grade(grade.id, update_data)
    
    # Try to update with invalid note (< 0.0)
    update_data = GradeUpdate.model_construct(nota=Decimal("-0.1"))
    with pytest.raises(ValueError, match="Note must be between 0.0 and 5.0"):
        await service.update_grade(grade.id, update_data)


# ==================== EnrollmentService Edge Cases ====================

@pytest.mark.asyncio
async def test_enrollment_service_create_enrollment_estudiante_not_found(async_db_session: AsyncSession):
    """Test EnrollmentService.create_enrollment raises ValueError when estudiante not found (covers línea 41)."""
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
    
    service = EnrollmentService(async_db_session)
    
    enrollment_data = EnrollmentCreate(
        estudiante_id=99999,  # Non-existent estudiante
        subject_id=subject.id,
    )
    
    with pytest.raises(ValueError, match="Estudiante not found"):
        await service.create_enrollment(enrollment_data)


@pytest.mark.asyncio
async def test_enrollment_service_create_enrollment_not_estudiante(async_db_session: AsyncSession):
    """Test EnrollmentService.create_enrollment raises ValueError when user is not Estudiante (covers línea 44)."""
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,  # Not ESTUDIANTE
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
    
    service = EnrollmentService(async_db_session)
    
    enrollment_data = EnrollmentCreate(
        estudiante_id=profesor.id,  # Profesor, not Estudiante
        subject_id=subject.id,
    )
    
    with pytest.raises(ValueError, match="User is not an Estudiante"):
        await service.create_enrollment(enrollment_data)


@pytest.mark.asyncio
async def test_enrollment_service_create_enrollment_subject_not_found(async_db_session: AsyncSession):
    """Test EnrollmentService.create_enrollment raises ValueError when subject not found (covers línea 49)."""
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
    await async_db_session.refresh(estudiante)
    
    service = EnrollmentService(async_db_session)
    
    enrollment_data = EnrollmentCreate(
        estudiante_id=estudiante.id,
        subject_id=99999,  # Non-existent subject
    )
    
    with pytest.raises(ValueError, match="Subject not found"):
        await service.create_enrollment(enrollment_data)


@pytest.mark.asyncio
async def test_enrollment_service_get_enrollment_by_id(async_db_session: AsyncSession):
    """Test EnrollmentService.get_enrollment_by_id (covers línea 72)."""
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
    
    service = EnrollmentService(async_db_session)
    
    # Get enrollment by ID
    found_enrollment = await service.get_enrollment_by_id(enrollment.id)
    assert found_enrollment is not None
    assert found_enrollment.id == enrollment.id
    
    # Get non-existent enrollment
    not_found = await service.get_enrollment_by_id(99999)
    assert not_found is None


@pytest.mark.asyncio
async def test_enrollment_service_get_enrollments_by_estudiante(async_db_session: AsyncSession):
    """Test EnrollmentService.get_enrollments_by_estudiante (covers línea 87)."""
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
    
    # Create enrollments
    enrollments = []
    for subject in subjects:
        enrollment = Enrollment(
            estudiante_id=estudiante.id,
            subject_id=subject.id,
        )
        enrollments.append(enrollment)
        async_db_session.add(enrollment)
    await async_db_session.commit()
    
    service = EnrollmentService(async_db_session)
    
    # Get enrollments by estudiante
    found_enrollments = await service.get_enrollments_by_estudiante(estudiante.id)
    assert len(found_enrollments) == 3
    assert all(e.estudiante_id == estudiante.id for e in found_enrollments)
    
    # Get enrollments for non-existent estudiante
    empty_enrollments = await service.get_enrollments_by_estudiante(99999)
    assert len(empty_enrollments) == 0


@pytest.mark.asyncio
async def test_enrollment_service_get_enrollments_by_subject(async_db_session: AsyncSession):
    """Test EnrollmentService.get_enrollments_by_subject (covers línea 102)."""
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
    
    # Create multiple estudiantes
    estudiantes = []
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
        estudiantes.append(estudiante)
        async_db_session.add(estudiante)
    await async_db_session.commit()
    for est in estudiantes:
        await async_db_session.refresh(est)
    
    # Create enrollments
    for estudiante in estudiantes:
        enrollment = Enrollment(
            estudiante_id=estudiante.id,
            subject_id=subject.id,
        )
        async_db_session.add(enrollment)
    await async_db_session.commit()
    
    service = EnrollmentService(async_db_session)
    
    # Get enrollments by subject
    found_enrollments = await service.get_enrollments_by_subject(subject.id)
    assert len(found_enrollments) == 3
    assert all(e.subject_id == subject.id for e in found_enrollments)
    
    # Get enrollments for non-existent subject
    empty_enrollments = await service.get_enrollments_by_subject(99999)
    assert len(empty_enrollments) == 0


# ==================== SubjectService Edge Cases ====================

@pytest.mark.asyncio
async def test_subject_service_create_subject_invalid_credits_low(async_db_session: AsyncSession):
    """Test SubjectService.create_subject raises ValueError for credits <= 0 (covers línea 38)."""
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
    
    # Use model_construct to bypass Pydantic validation and test service validation
    subject_data = SubjectCreate.model_construct(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=0,  # Invalid: <= 0
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    
    with pytest.raises(ValueError, match="Number of credits must be between 1 and 10"):
        await service.create_subject(subject_data)


@pytest.mark.asyncio
async def test_subject_service_create_subject_invalid_credits_high(async_db_session: AsyncSession):
    """Test SubjectService.create_subject raises ValueError for credits > 10 (covers línea 38)."""
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
    
    # Use model_construct to bypass Pydantic validation and test service validation
    subject_data = SubjectCreate.model_construct(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=11,  # Invalid: > 10
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    
    with pytest.raises(ValueError, match="Number of credits must be between 1 and 10"):
        await service.create_subject(subject_data)


@pytest.mark.asyncio
async def test_subject_service_create_subject_profesor_not_found(async_db_session: AsyncSession):
    """Test SubjectService.create_subject raises ValueError when profesor not found (covers línea 43)."""
    service = SubjectService(async_db_session)
    
    subject_data = SubjectCreate(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=99999,  # Non-existent profesor
    )
    
    with pytest.raises(ValueError, match="Profesor not found"):
        await service.create_subject(subject_data)


@pytest.mark.asyncio
async def test_subject_service_create_subject_not_profesor(async_db_session: AsyncSession):
    """Test SubjectService.create_subject raises ValueError when user is not Profesor (covers línea 46)."""
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,  # Not PROFESOR
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    
    service = SubjectService(async_db_session)
    
    subject_data = SubjectCreate(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=estudiante.id,  # Estudiante, not Profesor
    )
    
    with pytest.raises(ValueError, match="User is not a Profesor"):
        await service.create_subject(subject_data)


@pytest.mark.asyncio
async def test_subject_service_create_subject_duplicate_code(async_db_session: AsyncSession):
    """Test SubjectService.create_subject raises ValueError for duplicate codigo_institucional (covers línea 53)."""
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
    
    # Create first subject
    subject1 = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject1)
    await async_db_session.commit()
    
    service = SubjectService(async_db_session)
    
    # Try to create subject with duplicate codigo_institucional
    subject_data = SubjectCreate(
        nombre="Matemáticas 2",
        codigo_institucional="MAT-101",  # Duplicate
        numero_creditos=4,
        horario="Martes 8:00",
        profesor_id=profesor.id,
    )
    
    with pytest.raises(ValueError, match="Subject code already exists"):
        await service.create_subject(subject_data)


@pytest.mark.asyncio
async def test_subject_service_update_subject_invalid_credits(async_db_session: AsyncSession):
    """Test SubjectService.update_subject raises ValueError for invalid credits (covers línea 88)."""
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
    
    service = SubjectService(async_db_session)
    
    # Try to update with invalid credits (> 10) - use model_construct to bypass Pydantic validation
    update_data = SubjectUpdate.model_construct(numero_creditos=11)
    with pytest.raises(ValueError, match="Number of credits must be between 1 and 10"):
        await service.update_subject(subject.id, update_data)
    
    # Try to update with invalid credits (<= 0)
    update_data = SubjectUpdate.model_construct(numero_creditos=0)
    with pytest.raises(ValueError, match="Number of credits must be between 1 and 10"):
        await service.update_subject(subject.id, update_data)


@pytest.mark.asyncio
async def test_subject_service_update_subject_invalid_profesor_not_found(async_db_session: AsyncSession):
    """Test SubjectService.update_subject raises ValueError when profesor not found (covers línea 93)."""
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
    
    service = SubjectService(async_db_session)
    
    # Try to update with non-existent profesor
    update_data = SubjectUpdate(profesor_id=99999)
    with pytest.raises(ValueError, match="Profesor not found"):
        await service.update_subject(subject.id, update_data)


@pytest.mark.asyncio
async def test_subject_service_update_subject_invalid_profesor_role(async_db_session: AsyncSession):
    """Test SubjectService.update_subject raises ValueError when user is not Profesor (covers línea 93)."""
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
        role=UserRole.ESTUDIANTE,  # Not PROFESOR
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
    
    service = SubjectService(async_db_session)
    
    # Try to update with estudiante (not profesor)
    update_data = SubjectUpdate(profesor_id=estudiante.id)
    with pytest.raises(ValueError, match="User is not a Profesor"):
        await service.update_subject(subject.id, update_data)


# ==================== Additional AdminService Edge Cases ====================

@pytest.mark.asyncio
async def test_admin_service_update_user(async_db_session: AsyncSession):
    """Test AdminService.update_user (covers línea 76)."""
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
        nombre="Original",
        apellido="Name",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante)
    await async_db_session.commit()
    await async_db_session.refresh(admin)
    await async_db_session.refresh(estudiante)
    
    service = AdminService(async_db_session, admin)
    
    from app.schemas.user import UserUpdate
    update_data = UserUpdate(
        nombre="Updated",
        programa_academico="Medicina",
    )
    
    updated = await service.update_user(estudiante.id, update_data)
    assert updated is not None
    assert updated.nombre == "Updated"
    assert updated.programa_academico == "Medicina"
    
    # Test with non-existent user
    not_found = await service.update_user(99999, update_data)
    assert not_found is None


@pytest.mark.asyncio
async def test_admin_service_delete_user(async_db_session: AsyncSession):
    """Test AdminService.delete_user (covers línea 87)."""
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
    await async_db_session.commit()
    await async_db_session.refresh(admin)
    await async_db_session.refresh(estudiante)
    
    service = AdminService(async_db_session, admin)
    
    # Delete user
    result = await service.delete_user(estudiante.id)
    assert result is True
    
    # Try to delete non-existent user
    result = await service.delete_user(99999)
    assert result is False


@pytest.mark.asyncio
async def test_admin_service_generate_average_enrollment_not_found(async_db_session: AsyncSession):
    """Test AdminService.generate_average raises ValueError when enrollment not found (covers línea 178)."""
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
    await async_db_session.refresh(admin)
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
    
    # Try to generate average for estudiante not enrolled in subject
    with pytest.raises(ValueError, match="Estudiante is not enrolled in this subject"):
        await service.generate_average(estudiante.id, subject.id)


# ==================== Additional SubjectService Edge Cases ====================

@pytest.mark.asyncio
async def test_subject_service_get_subject_by_id(async_db_session: AsyncSession):
    """Test SubjectService.get_subject_by_id (covers línea 68)."""
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
    
    service = SubjectService(async_db_session)
    
    # Get subject by ID
    found_subject = await service.get_subject_by_id(subject.id)
    assert found_subject is not None
    assert found_subject.id == subject.id
    assert found_subject.nombre == "Matemáticas"
    
    # Get non-existent subject
    not_found = await service.get_subject_by_id(99999)
    assert not_found is None

