"""Integration tests for bulk import/export API (TDD - Fase 4 y 8)."""

import pytest
from datetime import date
from io import BytesIO

import pandas as pd

from app.models.user import User, UserRole
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash, create_access_token

EXCEL_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _make_excel(rows: list[dict]) -> bytes:
    df = pd.DataFrame(rows)
    buf = BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    return buf.getvalue()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_excel_creates_users(client, db_session):
    """POST /api/v1/users/bulk-import with valid .xlsx creates users."""
    codigo = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@bulk.com",
        password_hash=get_password_hash("admin1"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Bulk",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    token = create_access_token({"sub": admin.email, "role": admin.role.value})

    data = [
        {
            "email": "bulk1@sofka.edu",
            "password": "Password123!",
            "nombre": "Bulk",
            "apellido": "One",
            "rol": "Estudiante",
            "fecha_nacimiento": date(2000, 5, 15),
            "numero_contacto": "3001234567",
            "programa_academico": "Ingeniería",
            "ciudad_residencia": "Cali",
        },
    ]
    excel = _make_excel(data)
    resp = await client.post(
        "/api/v1/users/bulk-import",
        files={"file": ("estudiantes.xlsx", excel, EXCEL_TYPE)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    j = resp.json()
    assert j["created"] == 1
    assert j["updated"] == 0
    assert len(j["errors"]) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_invalid_excel_rejects(client, db_session):
    """POST /api/v1/users/bulk-import with invalid data returns 400 and errors."""
    codigo = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin2@bulk.com",
        password_hash=get_password_hash("admin2"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Bulk",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    token = create_access_token({"sub": admin.email, "role": admin.role.value})

    data = [
        {
            "email": "invalid-email",
            "password": "Password123!",
            "nombre": "X",
            "apellido": "Y",
            "rol": "Estudiante",
            "fecha_nacimiento": date(2000, 1, 1),
            "numero_contacto": "3001234567",
            "programa_academico": "Ing",
            "ciudad_residencia": "Cali",
        },
    ]
    excel = _make_excel(data)
    resp = await client.post(
        "/api/v1/users/bulk-import",
        files={"file": ("bad.xlsx", excel, EXCEL_TYPE)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    j = resp.json()
    assert "errors" in j or "detail" in j
    assert j.get("created", 0) == 0 and j.get("updated", 0) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_export_users_endpoint(client, db_session):
    """GET /api/v1/users/export?role=Estudiante returns Excel file."""
    codigo = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin3@bulk.com",
        password_hash=get_password_hash("admin3"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Bulk",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    token = create_access_token({"sub": admin.email, "role": admin.role.value})

    resp = await client.get(
        "/api/v1/users/export",
        params={"role": "Estudiante"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "application/vnd.openxmlformats" in resp.headers.get("content-type", "")
    assert len(resp.content) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unauthorized_user_cannot_import(client, db_session):
    """Non-admin gets 403 on POST /api/v1/users/bulk-import."""
    codigo = await generar_codigo_institucional(db_session, "Estudiante")
    est = User(
        email="est@bulk.com",
        password_hash=get_password_hash("est1"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Bulk",
        codigo_institucional=codigo,
        fecha_nacimiento=date(2000, 1, 1),
    )
    db_session.add(est)
    await db_session.commit()
    await db_session.refresh(est)
    token = create_access_token({"sub": est.email, "role": est.role.value})

    data = [{"email": "a@b.com", "password": "Pass1234!", "nombre": "A", "apellido": "B",
             "rol": "Estudiante", "fecha_nacimiento": date(2000,1,1),
             "numero_contacto": "3001234567", "programa_academico": "Ing", "ciudad_residencia": "C"}]
    excel = _make_excel(data)
    resp = await client.post(
        "/api/v1/users/bulk-import",
        files={"file": ("x.xlsx", excel, EXCEL_TYPE)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.integration
@pytest.mark.asyncio
async def test_template_endpoint(client, db_session):
    """GET /api/v1/users/template returns Excel template."""
    codigo = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin4@bulk.com",
        password_hash=get_password_hash("admin4"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Bulk",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    token = create_access_token({"sub": admin.email, "role": admin.role.value})

    resp = await client.get(
        "/api/v1/users/template",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "application/vnd.openxmlformats" in resp.headers.get("content-type", "")
    # Template must contain required columns
    df = pd.read_excel(BytesIO(resp.content), engine="openpyxl")
    for col in ["email", "password", "nombre", "apellido", "rol", "fecha_nacimiento",
                "numero_contacto", "programa_academico", "ciudad_residencia"]:
        assert col in df.columns
