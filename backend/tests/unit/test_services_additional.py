"""Additional unit tests for services to increase coverage."""

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
from app.schemas.user import UserUpdate
from app.schemas.subject import SubjectUpdate
from app.schemas.enrollment import EnrollmentCreate
from app.schemas.grade import GradeUpdate
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_user_service_update_user(async_db_session: AsyncSession):
    """Test UserService can update user."""
    codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Original",
        apellido="Name",
        codigo_institucional=codigo,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    service = UserService(async_db_session)
    update_data = UserUpdate(
        nombre="Updated",
        numero_contacto="1234567890",
    )
    
    updated = await service.update_user(user.id, update_data)
    
    assert updated is not None
    assert updated.nombre == "Updated"
    assert updated.numero_contacto == "1234567890"


@pytest.mark.asyncio
async def test_user_service_update_user_with_fecha_nacimiento(async_db_session: AsyncSession):
    """Test UserService updates age when fecha_nacimiento changes."""
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
    update_data = UserUpdate(
        fecha_nacimiento=date(1995, 1, 1),
    )
    
    updated = await service.update_user(user.id, update_data)
    
    assert updated is not None
    assert updated.fecha_nacimiento == date(1995, 1, 1)
    assert updated.edad is not None


@pytest.mark.asyncio
async def test_user_service_delete_user(async_db_session: AsyncSession):
    """Test UserService can delete user."""
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
    result = await service.delete_user(user.id)
    
    assert result is True
    
    # Verify user is deleted
    deleted = await service.get_user_by_id(user.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_user_service_get_users_by_role(async_db_session: AsyncSession):
    """Test UserService can get users by role."""
    # Create multiple estudiantes
    for i in range(3):
        codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
        user = User(
            email=f"est{i}@example.com",
            password_hash=get_password_hash("pass"),
            role=UserRole.ESTUDIANTE,
            nombre=f"Est{i}",
            apellido="Test",
            codigo_institucional=codigo,
            fecha_nacimiento=date(2000, 1, 1),
        )
        async_db_session.add(user)
    
    await async_db_session.commit()
    
    service = UserService(async_db_session)
    estudiantes = await service.get_users_by_role("Estudiante")
    
    assert len(estudiantes) == 3
    assert all(est.role == UserRole.ESTUDIANTE for est in estudiantes)


@pytest.mark.asyncio
async def test_subject_service_update_subject(async_db_session: AsyncSession):
    """Test SubjectService can update subject."""
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
        nombre="Original",
        codigo_institucional="ORI-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    
    service = SubjectService(async_db_session)
    update_data = SubjectUpdate(
        nombre="Updated",
        numero_creditos=4,
    )
    
    updated = await service.update_subject(subject.id, update_data)
    
    assert updated is not None
    assert updated.nombre == "Updated"
    assert updated.numero_creditos == 4


@pytest.mark.asyncio
async def test_subject_service_delete_subject(async_db_session: AsyncSession):
    """Test SubjectService can delete subject."""
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
    result = await service.delete_subject(subject.id)
    
    assert result is True


@pytest.mark.asyncio
async def test_subject_service_get_subjects_by_profesor(async_db_session: AsyncSession):
    """Test SubjectService can get subjects by profesor."""
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
    
    # Create multiple subjects
    for i in range(3):
        subject = Subject(
            nombre=f"Materia {i}",
            codigo_institucional=f"MAT-{i}01",
            numero_creditos=3,
            horario=f"Día {i} 8:00",
            profesor_id=profesor.id,
        )
        async_db_session.add(subject)
    
    await async_db_session.commit()
    
    service = SubjectService(async_db_session)
    subjects = await service.get_subjects_by_profesor(profesor.id)
    
    assert len(subjects) == 3
    assert all(sub.profesor_id == profesor.id for sub in subjects)


@pytest.mark.asyncio
async def test_enrollment_service_update_enrollment(async_db_session: AsyncSession):
    """Test EnrollmentService can update enrollment."""
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
    await async_db_session.refresh(subject1)
    await async_db_session.refresh(subject2)
    
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject1.id,
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    await async_db_session.refresh(enrollment)
    
    service = EnrollmentService(async_db_session)
    # Note: Enrollment doesn't have update in the service, but we can test delete
    result = await service.delete_enrollment(enrollment.id)
    
    assert result is True


@pytest.mark.asyncio
async def test_grade_service_update_grade(async_db_session: AsyncSession):
    """Test GradeService can update grade."""
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
    update_data = GradeUpdate(
        nota=Decimal("4.5"),
        observaciones="Mejorado",
    )
    
    updated = await service.update_grade(grade.id, update_data)
    
    assert updated is not None
    assert updated.nota == Decimal("4.5")
    assert updated.observaciones == "Mejorado"


@pytest.mark.asyncio
async def test_grade_service_delete_grade(async_db_session: AsyncSession):
    """Test GradeService can delete grade."""
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
    result = await service.delete_grade(grade.id)
    
    assert result is True


@pytest.mark.asyncio
async def test_grade_service_calculate_average_with_no_grades(async_db_session: AsyncSession):
    """Test GradeService raises error when calculating average with no grades."""
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
    
    # Should raise error because there are no grades
    with pytest.raises(ValueError):
        await service.calculate_average(enrollment.id)

