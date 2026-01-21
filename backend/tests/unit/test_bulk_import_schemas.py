"""Unit tests for bulk import schemas (TDD - Fase 1)."""

import pytest
from datetime import date
from pydantic import ValidationError

from app.schemas.bulk_import import (
    EstudianteImportRow,
    BulkImportResult,
    BulkImportError,
)


class TestEstudianteImportRow:
    """Tests for EstudianteImportRow schema."""

    def test_valid_row_creates_instance(self):
        """Valid data creates EstudianteImportRow."""
        row = EstudianteImportRow(
            email="juan@sofka.edu",
            password="Password123!",
            nombre="Juan",
            apellido="Pérez",
            rol="Estudiante",
            fecha_nacimiento=date(2000, 5, 15),
            numero_contacto="3001234567",
            programa_academico="Ingeniería de Sistemas",
            ciudad_residencia="Cali",
        )
        assert row.email == "juan@sofka.edu"
        assert row.rol == "Estudiante"
        assert row.fecha_nacimiento == date(2000, 5, 15)

    def test_rol_must_be_estudiante(self):
        """Rol must be 'Estudiante' only."""
        with pytest.raises(ValidationError) as exc_info:
            EstudianteImportRow(
                email="juan@sofka.edu",
                password="Password123!",
                nombre="Juan",
                apellido="Pérez",
                rol="Profesor",
                fecha_nacimiento=date(2000, 5, 15),
                numero_contacto="3001234567",
                programa_academico="Ingeniería",
                ciudad_residencia="Cali",
            )
        assert "rol" in str(exc_info.value).lower() or "Estudiante" in str(exc_info.value)

    def test_email_validated(self):
        """Invalid email raises ValidationError."""
        with pytest.raises(ValidationError):
            EstudianteImportRow(
                email="invalid-email",
                password="Password123!",
                nombre="Juan",
                apellido="Pérez",
                rol="Estudiante",
                fecha_nacimiento=date(2000, 5, 15),
                numero_contacto="3001234567",
                programa_academico="Ingeniería",
                ciudad_residencia="Cali",
            )

    def test_password_min_length_8(self):
        """Password must be at least 8 characters."""
        with pytest.raises(ValidationError):
            EstudianteImportRow(
                email="juan@sofka.edu",
                password="Short1!",
                nombre="Juan",
                apellido="Pérez",
                rol="Estudiante",
                fecha_nacimiento=date(2000, 5, 15),
                numero_contacto="3001234567",
                programa_academico="Ingeniería",
                ciudad_residencia="Cali",
            )

    def test_fecha_nacimiento_not_future(self):
        """fecha_nacimiento cannot be in the future."""
        with pytest.raises(ValidationError):
            EstudianteImportRow(
                email="juan@sofka.edu",
                password="Password123!",
                nombre="Juan",
                apellido="Pérez",
                rol="Estudiante",
                fecha_nacimiento=date(2030, 1, 1),
                numero_contacto="3001234567",
                programa_academico="Ingeniería",
                ciudad_residencia="Cali",
            )

    def test_numero_contacto_length_10_20(self):
        """numero_contacto must be 10-20 characters."""
        with pytest.raises(ValidationError):
            EstudianteImportRow(
                email="juan@sofka.edu",
                password="Password123!",
                nombre="Juan",
                apellido="Pérez",
                rol="Estudiante",
                fecha_nacimiento=date(2000, 5, 15),
                numero_contacto="123",
                programa_academico="Ingeniería",
                ciudad_residencia="Cali",
            )


class TestBulkImportResult:
    """Tests for BulkImportResult schema."""

    def test_valid_result(self):
        """BulkImportResult with created, updated, errors."""
        result = BulkImportResult(
            created=5,
            updated=2,
            errors=[BulkImportError(row=3, field="email", message="Email inválido", value="bad")],
        )
        assert result.created == 5
        assert result.updated == 2
        assert len(result.errors) == 1
        assert result.errors[0].row == 3


class TestBulkImportError:
    """Tests for BulkImportError schema."""

    def test_error_instance(self):
        """BulkImportError has row, field, message, value."""
        err = BulkImportError(row=2, field="email", message="Formato inválido", value="x")
        assert err.row == 2
        assert err.field == "email"
        assert err.message == "Formato inválido"
        assert err.value == "x"
