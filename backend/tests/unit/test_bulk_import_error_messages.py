"""Unit tests for specific error messages in BulkImportService."""

import pytest
from io import BytesIO
from datetime import date

import pandas as pd

from app.services.bulk_import_service import BulkImportService
from app.core.exceptions import (
    FileFormatError,
    FileSizeError,
    FileCorruptedError,
    EmptyFileError,
    MissingColumnsError,
    TooManyRowsError,
    DatabaseOperationError,
)


def _excel_bytes(rows: list[dict]) -> BytesIO:
    """Build .xlsx in memory from list of dicts."""
    df = pd.DataFrame(rows)
    buf = BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    return buf


class TestSpecificErrorMessages:
    """Tests that verify specific error messages are user-friendly and informative."""

    def test_missing_columns_error_lists_specific_columns(self):
        """MissingColumnsError should list the specific missing columns."""
        data = [{"email": "test@sofka.edu", "nombre": "Test"}]  # Missing many columns
        buf = _excel_bytes(data)
        svc = BulkImportService(None)
        
        with pytest.raises(MissingColumnsError) as exc_info:
            svc.parse_excel(buf)
        
        error_message = str(exc_info.value.detail)
        # Should mention specific missing columns
        assert "password" in error_message
        assert "apellido" in error_message
        assert "Faltan las siguientes columnas obligatorias" in error_message

    def test_too_many_rows_error_shows_actual_and_limit(self):
        """TooManyRowsError should show both actual count and limit."""
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
        # Create 1001 rows
        data = [dict(base_row, email=f"test{i}@sofka.edu") for i in range(1001)]
        buf = _excel_bytes(data)
        svc = BulkImportService(None)
        
        with pytest.raises(TooManyRowsError) as exc_info:
            svc.parse_excel(buf)
        
        error_message = str(exc_info.value.detail)
        assert "1001" in error_message  # Actual count
        assert "1000" in error_message  # Limit
        assert "filas" in error_message

    def test_empty_file_error_is_descriptive(self):
        """EmptyFileError should provide clear guidance."""
        data = []  # Empty file
        buf = _excel_bytes(data)
        svc = BulkImportService(None)
        
        with pytest.raises(EmptyFileError) as exc_info:
            svc.parse_excel(buf)
        
        error_message = str(exc_info.value.detail)
        assert "vacío" in error_message or "no contiene datos" in error_message

    def test_corrupted_file_error_suggests_verification(self):
        """FileCorruptedError should suggest file verification."""
        buf = BytesIO(b"This is not an Excel file")
        svc = BulkImportService(None)
        
        with pytest.raises(FileCorruptedError) as exc_info:
            svc.parse_excel(buf)
        
        error_message = str(exc_info.value.detail)
        assert "corrupto" in error_message or "no se puede leer" in error_message
        assert "Excel válido" in error_message

    @pytest.mark.asyncio
    async def test_database_operation_error_includes_context(self):
        """DatabaseOperationError should include operation context."""
        svc = BulkImportService(None)  # No database connection
        
        with pytest.raises(DatabaseOperationError) as exc_info:
            await svc.export_users_to_excel()
        
        error_message = str(exc_info.value.detail)
        assert "database" in error_message.lower() or "base de datos" in error_message
        assert "connection" in error_message.lower() or "conexión" in error_message


class TestErrorMessageConsistency:
    """Tests that verify error messages are consistent and follow patterns."""

    def test_all_custom_exceptions_have_spanish_messages(self):
        """All custom exceptions should have Spanish error messages."""
        # Test FileFormatError
        error = FileFormatError("test.txt")
        assert "válido" in error.detail and "xlsx" in error.detail
        
        # Test FileSizeError
        error = FileSizeError(7.5, 5)
        assert "MB" in error.detail and "límite" in error.detail
        
        # Test FileCorruptedError
        error = FileCorruptedError("test.xlsx")
        assert "corrupto" in error.detail or "no se puede leer" in error.detail
        
        # Test EmptyFileError
        error = EmptyFileError()
        assert "vacío" in error.detail or "no contiene datos" in error.detail
        
        # Test MissingColumnsError
        error = MissingColumnsError(["email", "password"])
        assert "Faltan" in error.detail and "columnas" in error.detail
        
        # Test TooManyRowsError
        error = TooManyRowsError(1500, 1000)
        assert "1500" in error.detail and "1000" in error.detail
        
        # Test DatabaseOperationError
        error = DatabaseOperationError("importación", "Connection failed")
        assert "base de datos" in error.detail or "database" in error.detail.lower()

    def test_error_messages_are_actionable(self):
        """Error messages should provide actionable guidance."""
        # FileFormatError should specify what format is expected
        error = FileFormatError("test.doc")
        assert ".xlsx" in error.detail
        
        # FileSizeError should specify the exact limit
        error = FileSizeError(10.0, 5)
        assert "5 MB" in error.detail
        
        # MissingColumnsError should list what's missing
        error = MissingColumnsError(["email", "nombre"])
        assert "email" in error.detail and "nombre" in error.detail
        
        # FileCorruptedError should suggest verification
        error = FileCorruptedError()
        assert "Verifique" in error.detail or "válido" in error.detail

    def test_error_status_codes_are_appropriate(self):
        """Error status codes should match HTTP standards."""
        # Client errors should be 4xx
        assert FileFormatError().status_code == 400
        assert FileSizeError(10, 5).status_code == 400
        assert EmptyFileError().status_code == 400
        assert MissingColumnsError(["email"]).status_code == 400
        assert TooManyRowsError(1500, 1000).status_code == 400
        
        # Server errors should be 5xx
        assert DatabaseOperationError("test", "error").status_code == 500


class TestErrorMessageForQA:
    """Tests that verify error messages provide sufficient information for QA."""

    def test_validation_errors_include_row_and_field_info(self):
        """Validation errors should include row number and field name for QA."""
        rows = [
            {
                "email": "invalid-email",  # Invalid email
                "password": "Password123!",
                "nombre": "Test",
                "apellido": "User",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2000, 1, 1),
                "numero_contacto": "3001234567",
                "programa_academico": "Test",
                "ciudad_residencia": "Test",
            },
        ]
        svc = BulkImportService(None)
        valid, errors = svc.validate_rows(rows)
        
        assert len(errors) > 0
        error = errors[0]
        assert error.row == 2  # Excel row number (1-based, with header)
        assert error.field == "email"
        assert error.value == "invalid-email"
        assert "email" in error.message.lower() or "inválido" in error.message.lower()

    def test_duplicate_email_errors_show_specific_email(self):
        """Duplicate email errors should show the specific email for QA."""
        rows = [
            {
                "email": "duplicate@sofka.edu",
                "password": "Password123!",
                "nombre": "User1",
                "apellido": "Test",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2000, 1, 1),
                "numero_contacto": "3001234567",
                "programa_academico": "Test",
                "ciudad_residencia": "Test",
            },
            {
                "email": "duplicate@sofka.edu",  # Duplicate
                "password": "Password123!",
                "nombre": "User2",
                "apellido": "Test",
                "rol": "Estudiante",
                "fecha_nacimiento": date(2000, 1, 1),
                "numero_contacto": "3001234567",
                "programa_academico": "Test",
                "ciudad_residencia": "Test",
            },
        ]
        svc = BulkImportService(None)
        valid, errors = svc.validate_rows(rows)
        
        duplicate_errors = [e for e in errors if "duplicad" in e.message.lower()]
        assert len(duplicate_errors) >= 1
        
        for error in duplicate_errors:
            assert error.value == "duplicate@sofka.edu"
            assert error.field == "email"
            assert "duplicado" in error.message.lower()