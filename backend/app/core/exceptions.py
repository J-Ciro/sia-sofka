"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Base exception for application errors."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)
        self.detail = detail
        self.status_code = status_code


class NotFoundError(BaseAppException):
    """Exception for resource not found."""
    
    def __init__(self, resource: str, identifier: str | int):
        detail = f"{resource} with id {identifier} not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(BaseAppException):
    """Exception for validation errors."""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedError(BaseAppException):
    """Exception for unauthorized access."""
    
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(BaseAppException):
    """Exception for forbidden access."""
    
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ConflictError(BaseAppException):
    """Exception for resource conflicts."""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class ScheduleConflictError(HTTPException):
    """Conflictos de horario (aula o profesor). status 422 con listado de conflictos."""

    def __init__(self, conflicts: list):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Conflictos de horario", "conflicts": conflicts},
        )


# ==================== BULK IMPORT SPECIFIC EXCEPTIONS ====================

class BulkImportError(BaseAppException):
    """Base exception for bulk import operations."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail=detail, status_code=status_code)


class FileFormatError(BulkImportError):
    """Exception for invalid file format."""
    
    def __init__(self, filename: str = None, expected_format: str = ".xlsx"):
        if filename:
            detail = f"Archivo '{filename}' no es válido. Solo se aceptan archivos {expected_format}"
        else:
            detail = f"Formato de archivo no válido. Solo se aceptan archivos {expected_format}"
        super().__init__(detail=detail)


class FileSizeError(BulkImportError):
    """Exception for file size exceeding limits."""
    
    def __init__(self, size_mb: float, max_size_mb: int = 5):
        detail = f"El archivo ({size_mb:.1f} MB) supera el límite máximo de {max_size_mb} MB"
        super().__init__(detail=detail)


class FileCorruptedError(BulkImportError):
    """Exception for corrupted or unreadable files."""
    
    def __init__(self, filename: str = None, context: str = None):
        if context:
            detail = f"Error al {context}. El archivo está corrupto o no se puede procesar correctamente"
        elif filename:
            detail = f"El archivo '{filename}' está corrupto o no se puede leer. Verifique que sea un archivo Excel válido"
        else:
            detail = "El archivo está corrupto o no se puede leer. Verifique que sea un archivo Excel válido"
        super().__init__(detail=detail)


class EmptyFileError(BulkImportError):
    """Exception for empty files or files without data."""
    
    def __init__(self):
        detail = "El archivo está vacío o no contiene datos para importar"
        super().__init__(detail=detail)


class MissingColumnsError(BulkImportError):
    """Exception for missing required columns."""
    
    def __init__(self, missing_columns: list[str]):
        columns_str = ", ".join(missing_columns)
        detail = f"Faltan las siguientes columnas obligatorias: {columns_str}"
        super().__init__(detail=detail)


class TooManyRowsError(BulkImportError):
    """Exception for files exceeding row limits."""
    
    def __init__(self, row_count: int, max_rows: int = 1000):
        detail = f"El archivo contiene {row_count} filas, pero el límite máximo es {max_rows} filas por importación"
        super().__init__(detail=detail)


class DatabaseOperationError(BulkImportError):
    """Exception for database operation failures during bulk import."""
    
    def __init__(self, operation: str, details: str = None):
        if details:
            detail = f"Error en operación de base de datos ({operation}): {details}"
        else:
            detail = f"Error en operación de base de datos durante {operation}"
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NetworkTimeoutError(BulkImportError):
    """Exception for network timeouts during file processing."""
    
    def __init__(self):
        detail = "Tiempo de espera agotado durante el procesamiento. El archivo puede ser muy grande o el servidor está ocupado"
        super().__init__(detail=detail, status_code=status.HTTP_408_REQUEST_TIMEOUT)


class InsufficientPermissionsError(BulkImportError):
    """Exception for insufficient permissions for bulk operations."""
    
    def __init__(self, operation: str = "importación masiva"):
        detail = f"No tiene permisos suficientes para realizar {operation}"
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)

