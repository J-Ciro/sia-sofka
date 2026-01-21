"""Unit tests for BulkImportService (TDD - Fase 2 y 3)."""

import pytest
from io import BytesIO
from datetime import date

import pandas as pd

from app.schemas.bulk_import import EstudianteImportRow, BulkImportError
from app.services.bulk_import_service import BulkImportService


def _excel_bytes(rows: list[dict]) -> BytesIO:
    """Build .xlsx in memory from list of dicts."""
    df = pd.DataFrame(rows)
    buf = BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    return buf


class TestParseExcel:
    """Tests for parse_excel."""

    def test_parse_valid_excel_returns_list_of_dicts(self):
        """parse_excel returns list of dicts with required columns."""
        data = [
            {
                "email": "a@sofka.edu",
                "password": "Password123!",
                "nombre": "A",
                "apellido": "B",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2000, 1, 15),
                "numero_contacto": "3001234567",
                "programa_academico": "Ingeniería",
                "ciudad_residencia": "Cali",
            },
        ]
        buf = _excel_bytes(data)
        svc = BulkImportService(None)  # db not needed for parse
        got = svc.parse_excel(buf)
        assert isinstance(got, list)
        assert len(got) == 1
        assert got[0]["email"] == "a@sofka.edu"
        assert got[0]["rol"] == "Estudiante"

    def test_parse_excel_missing_column_raises(self):
        """Missing required column raises ValueError."""
        data = [{"email": "a@sofka.edu", "nombre": "A"}]  # missing password, etc.
        buf = _excel_bytes(data)
        svc = BulkImportService(None)
        with pytest.raises(ValueError, match="columnas|requeridas|faltan"):
            svc.parse_excel(buf)

    def test_parse_excel_more_than_1000_rows_raises(self):
        """More than 1000 data rows raises ValueError."""
        row = {
            "email": "a@sofka.edu",
            "password": "Password123!",
            "nombre": "A",
            "apellido": "B",
            "rol": "Estudiante",
            "fecha_nacimiento": date(2000, 1, 15),
            "numero_contacto": "3001234567",
            "programa_academico": "Ing",
            "ciudad_residencia": "Cali",
        }
        data = [dict(row, email=f"u{i}@sofka.edu") for i in range(1001)]
        buf = _excel_bytes(data)
        svc = BulkImportService(None)
        with pytest.raises(ValueError, match="1000|límite"):
            svc.parse_excel(buf)


class TestValidateRows:
    """Tests for validate_rows."""

    def test_validate_rows_all_valid_returns_no_errors(self):
        """All valid rows -> valid list, empty errors."""
        rows = [
            {
                "email": "a@sofka.edu",
                "password": "Password123!",
                "nombre": "A",
                "apellido": "B",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2000, 1, 15),
                "numero_contacto": "3001234567",
                "programa_academico": "Ing",
                "ciudad_residencia": "Cali",
            },
        ]
        svc = BulkImportService(None)
        valid, errs = svc.validate_rows(rows)
        assert len(valid) == 1
        assert isinstance(valid[0], EstudianteImportRow)
        assert len(errs) == 0

    def test_validate_rows_invalid_email_adds_error(self):
        """Invalid email adds BulkImportError."""
        rows = [
            {
                "email": "invalid",
                "password": "Password123!",
                "nombre": "A",
                "apellido": "B",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2000, 1, 15),
                "numero_contacto": "3001234567",
                "programa_academico": "Ing",
                "ciudad_residencia": "Cali",
            },
        ]
        svc = BulkImportService(None)
        valid, errs = svc.validate_rows(rows)
        assert len(valid) == 0
        assert len(errs) == 1
        assert errs[0].field == "email" or "email" in errs[0].message.lower()

    def test_validate_rows_duplicate_emails_in_file_adds_errors(self):
        """Duplicate emails within file add errors."""
        rows = [
            {
                "email": "same@sofka.edu",
                "password": "Password123!",
                "nombre": "A",
                "apellido": "B",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2000, 1, 15),
                "numero_contacto": "3001234567",
                "programa_academico": "Ing",
                "ciudad_residencia": "Cali",
            },
            {
                "email": "same@sofka.edu",
                "password": "Password123!",
                "nombre": "C",
                "apellido": "D",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2001, 2, 20),
                "numero_contacto": "3009876543",
                "programa_academico": "Medicina",
                "ciudad_residencia": "Bogotá",
            },
        ]
        svc = BulkImportService(None)
        valid, errs = svc.validate_rows(rows)
        assert len(valid) == 0
        assert len(errs) >= 1
        dup = [e for e in errs if "duplicad" in e.message.lower() or e.field == "email"]
        assert len(dup) >= 1


class TestExportUsersToExcel:
    """Tests for export_users_to_excel (Fase 3)."""

    @pytest.mark.asyncio
    async def test_export_generates_valid_excel(self, async_db_session):
        """export_users_to_excel returns BytesIO with valid .xlsx content."""
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash

        u = User(
            email="exp@sofka.edu",
            password_hash=get_password_hash("Secret1!"),
            role=UserRole.ESTUDIANTE,
            nombre="Export",
            apellido="User",
            codigo_institucional="EST-2026-0099",
            fecha_nacimiento=date(2001, 3, 10),
            numero_contacto="3001234567",
            programa_academico="Sistemas",
            ciudad_residencia="Cali",
        )
        async_db_session.add(u)
        await async_db_session.commit()

        svc = BulkImportService(async_db_session)
        buf = await svc.export_users_to_excel(role="Estudiante")
        assert buf is not None
        content = buf.getvalue()
        assert len(content) > 0
        assert b"PK" in content[:10] or b"xl/" in content  # xlsx is zip

    @pytest.mark.asyncio
    async def test_export_excludes_passwords(self, async_db_session):
        """Exported Excel must NOT contain password or password_hash column."""
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash

        u = User(
            email="no-pass@sofka.edu",
            password_hash=get_password_hash("Secret1!"),
            role=UserRole.ESTUDIANTE,
            nombre="No",
            apellido="Pass",
            codigo_institucional="EST-2026-0098",
            fecha_nacimiento=date(2001, 1, 1),
            numero_contacto="3001111111",
            programa_academico="Ing",
            ciudad_residencia="Bogotá",
        )
        async_db_session.add(u)
        await async_db_session.commit()

        svc = BulkImportService(async_db_session)
        buf = await svc.export_users_to_excel(role="Estudiante")
        df = pd.read_excel(buf, engine="openpyxl")
        cols = [c.lower() for c in df.columns]
        assert "password" not in cols
        assert "password_hash" not in cols


@pytest.mark.asyncio
class TestBulkImportStudents:
    """Tests for bulk_import_students (require async DB)."""

    async def test_import_creates_new_users(self, async_db_session):
        """bulk_import_students creates new users and returns created count."""
        rows = [
            EstudianteImportRow(
                email="new1@sofka.edu",
                password="Password123!",
                nombre="New",
                apellido="One",
                rol="Estudiante",
                fecha_nacimiento=date(2000, 5, 15),
                numero_contacto="3001111111",
                programa_academico="Ingeniería",
                ciudad_residencia="Cali",
            ),
        ]
        svc = BulkImportService(async_db_session)
        result = await svc.bulk_import_students(rows)
        assert result.created == 1
        assert result.updated == 0
        assert len(result.errors) == 0

    async def test_import_updates_existing_without_changing_password(self, async_db_session):
        """Upsert: existing user is updated; password and codigo_institucional unchanged."""
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash

        orig_hash = get_password_hash("OriginalPass1!")
        u = User(
            email="exist@sofka.edu",
            password_hash=orig_hash,
            role=UserRole.ESTUDIANTE,
            nombre="Old",
            apellido="Name",
            codigo_institucional="EST-2026-0001",
            fecha_nacimiento=date(1999, 1, 1),
            numero_contacto="3000000000",
            programa_academico="OldProg",
            ciudad_residencia="Bogotá",
        )
        async_db_session.add(u)
        await async_db_session.commit()
        await async_db_session.refresh(u)

        rows = [
            EstudianteImportRow(
                email="exist@sofka.edu",
                password="NewPassword999!",  # must not overwrite
                nombre="Updated",
                apellido="Surname",
                rol="Estudiante",
                fecha_nacimiento=date(2000, 6, 20),
                numero_contacto="3009999999",
                programa_academico="NewProg",
                ciudad_residencia="Medellín",
            ),
        ]
        svc = BulkImportService(async_db_session)
        result = await svc.bulk_import_students(rows)
        assert result.created == 0
        assert result.updated == 1

        # password and codigo must be unchanged
        from sqlalchemy import select
        from app.models.user import User as U

        stmt = select(U).where(U.email == "exist@sofka.edu")
        r = await async_db_session.execute(stmt)
        user = r.scalar_one()
        assert user.password_hash == orig_hash
        assert user.codigo_institucional == "EST-2026-0001"
        assert user.nombre == "Updated"
        assert user.ciudad_residencia == "Medellín"
