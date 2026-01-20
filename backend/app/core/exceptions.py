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

