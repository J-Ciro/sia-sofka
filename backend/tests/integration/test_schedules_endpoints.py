"""Integration tests for schedules endpoints (Fase 4)."""

import pytest
from datetime import date

from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.schedule import Classroom
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash, create_access_token


@pytest.fixture
async def test_data_schedules(db_session):
    """Admin, profesor, subject, subject2, classroom para schedules."""
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@schedules.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)

    codigo_prof = await generar_codigo_institucional(db_session, "Profesor")
    profesor = User(
        email="profesor@schedules.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor)

    await db_session.commit()
    await db_session.refresh(admin)
    await db_session.refresh(profesor)

    subject = Subject(
        nombre="Cálculo",
        codigo_institucional="CAL-101",
        numero_creditos=4,
        profesor_id=profesor.id,
    )
    subject2 = Subject(
        nombre="Física",
        codigo_institucional="FIS-101",
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    db_session.add_all([subject, subject2])
    classroom = Classroom(codigo="AULA-101", nombre="Aula 101", capacidad=40)
    db_session.add(classroom)
    await db_session.commit()
    await db_session.refresh(subject)
    await db_session.refresh(subject2)
    await db_session.refresh(classroom)

    return {
        "admin": admin,
        "profesor": profesor,
        "subject": subject,
        "subject2": subject2,
        "classroom": classroom,
    }


@pytest.mark.asyncio
async def test_create_schedule_as_admin(client, test_data_schedules):
    """Admin crea horario -> 201."""
    admin = test_data_schedules["admin"]
    subject = test_data_schedules["subject"]
    classroom = test_data_schedules["classroom"]
    token = create_access_token({"sub": admin.email, "role": admin.role.value})

    response = await client.post(
        "/api/v1/schedules",
        json={
            "subject_id": subject.id,
            "classroom_id": classroom.id,
            "dia_semana": 1,
            "hora_inicio": "08:00:00",
            "hora_fin": "10:00:00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["codigo"] is not None
    assert data["subject_id"] == subject.id
    assert data["classroom_id"] == classroom.id
    assert data["dia_semana"] == 1


@pytest.mark.asyncio
async def test_create_schedule_conflict_returns_422(client, test_data_schedules):
    """Crear horario con conflicto de aula -> 422 con conflicts."""
    admin = test_data_schedules["admin"]
    subject = test_data_schedules["subject"]
    subject2 = test_data_schedules["subject2"]
    classroom = test_data_schedules["classroom"]
    token = create_access_token({"sub": admin.email, "role": admin.role.value})

    # Primero: 8-10
    await client.post(
        "/api/v1/schedules",
        json={
            "subject_id": subject.id,
            "classroom_id": classroom.id,
            "dia_semana": 1,
            "hora_inicio": "08:00:00",
            "hora_fin": "10:00:00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # Segundo: 9-11 misma aula, otra materia -> conflicto
    response = await client.post(
        "/api/v1/schedules",
        json={
            "subject_id": subject2.id,
            "classroom_id": classroom.id,
            "dia_semana": 1,
            "hora_inicio": "09:00:00",
            "hora_fin": "11:00:00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "conflicts" in data.get("detail", {})


@pytest.mark.asyncio
async def test_get_weekly_as_profesor(client, test_data_schedules):
    """Profesor ve su horario semanal tras crear uno."""
    admin = test_data_schedules["admin"]
    profesor = test_data_schedules["profesor"]
    subject = test_data_schedules["subject"]
    classroom = test_data_schedules["classroom"]
    token_admin = create_access_token({"sub": admin.email, "role": admin.role.value})
    token_prof = create_access_token({"sub": profesor.email, "role": profesor.role.value})

    # Admin crea horario
    await client.post(
        "/api/v1/schedules",
        json={
            "subject_id": subject.id,
            "classroom_id": classroom.id,
            "dia_semana": 1,
            "hora_inicio": "08:00:00",
            "hora_fin": "10:00:00",
        },
        headers={"Authorization": f"Bearer {token_admin}"},
    )

    # Profesor pide su horario
    response = await client.get(
        "/api/v1/schedules/weekly",
        headers={"Authorization": f"Bearer {token_prof}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["subject_id"] == subject.id
    assert data[0]["dia_semana"] == 1


@pytest.mark.asyncio
async def test_create_schedule_as_profesor_forbidden(client, test_data_schedules):
    """Profesor no puede crear horario -> 403."""
    profesor = test_data_schedules["profesor"]
    subject = test_data_schedules["subject"]
    classroom = test_data_schedules["classroom"]
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})

    response = await client.post(
        "/api/v1/schedules",
        json={
            "subject_id": subject.id,
            "classroom_id": classroom.id,
            "dia_semana": 1,
            "hora_inicio": "08:00:00",
            "hora_fin": "10:00:00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
