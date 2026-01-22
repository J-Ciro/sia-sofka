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
    # Should return BulkImportResult with validation errors
    assert "errors" in j
    assert j.get("created", 0) == 0 and j.get("updated", 0) == 0
    assert len(j["errors"]) > 0
    # Check that error contains email validation message
    email_errors = [e for e in j["errors"] if "email" in e.get("field", "").lower()]
    assert len(email_errors) > 0


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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_non_xlsx_file_rejects(client, db_session):
    """POST /api/v1/users/bulk-import with non-.xlsx file returns 400 with specific error."""
    codigo = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin5@bulk.com",
        password_hash=get_password_hash("admin5"),
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

    # Upload a text file instead of Excel
    resp = await client.post(
        "/api/v1/users/bulk-import",
        files={"file": ("test.txt", b"This is not an Excel file", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    j = resp.json()
    assert "detail" in j
    assert "Solo se aceptan archivos" in j["detail"] or ".xlsx" in j["detail"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_missing_columns_rejects(client, db_session):
    """POST /api/v1/users/bulk-import with missing required columns returns 400."""
    codigo = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin6@bulk.com",
        password_hash=get_password_hash("admin6"),
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

    # Excel with missing required columns
    data = [{"email": "test@sofka.edu", "nombre": "Test"}]  # Missing many required columns
    excel = _make_excel(data)
    resp = await client.post(
        "/api/v1/users/bulk-import",
        files={"file": ("missing_cols.xlsx", excel, EXCEL_TYPE)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    j = resp.json()
    assert "detail" in j
    assert "Faltan" in j["detail"] and "columnas" in j["detail"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_empty_excel_rejects(client, db_session):
    """POST /api/v1/users/bulk-import with empty Excel returns 400."""
    codigo = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin7@bulk.com",
        password_hash=get_password_hash("admin7"),
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

    # Empty Excel file
    data = []  # No data rows
    excel = _make_excel(data)
    resp = await client.post(
        "/api/v1/users/bulk-import",
        files={"file": ("empty.xlsx", excel, EXCEL_TYPE)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    j = resp.json()
    assert "detail" in j
    assert "vacío" in j["detail"] or "no contiene datos" in j["detail"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_too_many_rows_rejects(client, db_session):
    """POST /api/v1/users/bulk-import with >1000 rows returns 400."""
    codigo = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin8@bulk.com",
        password_hash=get_password_hash("admin8"),
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

    # Create Excel with 1001 rows
    base_row = {
        "email": "test@sofka.edu",
        "password": "Password123!",
        "nombre": "Test",
        "apellido": "User",
        "rol": "Estudiante",
        "fecha_nacimiento": date(2000, 1, 1),
        "numero_contacto": "3001234567",
        "programa_academico": "Test",
        "ciudad_residencia": "Test",
    }
    data = [dict(base_row, email=f"test{i}@sofka.edu") for i in range(1001)]
    excel = _make_excel(data)
    
    resp = await client.post(
        "/api/v1/users/bulk-import",
        files={"file": ("too_many.xlsx", excel, EXCEL_TYPE)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    j = resp.json()
    assert "detail" in j
    assert "1001" in j["detail"] and "1000" in j["detail"]
