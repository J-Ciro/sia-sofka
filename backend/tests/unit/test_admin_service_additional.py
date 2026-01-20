"""Additional unit tests for AdminService to increase coverage."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.services.admin_service import AdminService
from app.schemas.subject import SubjectUpdate
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_admin_service_update_subject(async_db_session: AsyncSession):
    """Test AdminService can update subject."""
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
    
    service = AdminService(async_db_session, admin)
    update_data = SubjectUpdate(
        nombre="Updated",
        numero_creditos=4,
    )
    
    updated = await service.update_subject(subject.id, update_data)
    
    assert updated is not None
    assert updated.nombre == "Updated"
    assert updated.numero_creditos == 4


@pytest.mark.asyncio
async def test_admin_service_delete_subject(async_db_session: AsyncSession):
    """Test AdminService can delete subject."""
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
    result = await service.delete_subject(subject.id)
    
    assert result is True


@pytest.mark.asyncio
async def test_admin_service_generate_student_report_not_found(async_db_session: AsyncSession):
    """Test AdminService raises error when estudiante not found."""
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
    
    # Should raise error because estudiante doesn't exist
    with pytest.raises(ValueError):
        await service.generate_student_report(99999, "json")

