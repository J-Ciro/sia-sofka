"""Attendance validation utilities following SOLID principles."""

from datetime import date, datetime
from typing import Optional

from app.core.exceptions import ValidationError


class SessionValidator:
    """Validator for attendance session creation (SRP)."""
    
    @staticmethod
    def validate_date(session_date: date) -> None:
        """Validate session date is not in the future.
        
        Args:
            session_date: Date to validate
            
        Raises:
            ValidationError: If date is in the future
        """
        if session_date > date.today():
            raise ValidationError("No se puede crear asistencia para fechas futuras")
    
    @staticmethod
    def validate_time_range(hora_inicio: datetime, hora_fin: datetime) -> None:
        """Validate that end time is after start time.
        
        Args:
            hora_inicio: Start time
            hora_fin: End time
            
        Raises:
            ValidationError: If end time is not after start time
        """
        if hora_fin <= hora_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la hora de inicio")
    
    @staticmethod
    def validate_duplicate_session(
        existing_session: Optional[object],
        subject_id: int,
        fecha: date
    ) -> None:
        """Validate no duplicate session exists.
        
        Args:
            existing_session: Existing session object if found
            subject_id: Subject ID
            fecha: Session date
            
        Raises:
            ValidationError: If duplicate session exists
        """
        if existing_session:
            raise ValidationError(
                f"Ya existe una sesión para esta materia en la fecha {fecha}. "
                f"ID de sesión existente: {existing_session.id}"
            )


class AttendanceCalculator:
    """Calculator for attendance statistics (SRP)."""
    
    @staticmethod
    def calculate_attendance_percentage(presente: int, tardanza: int, total: int) -> float:
        """Calculate attendance percentage.
        
        Formula: (Present + Late) / Total * 100
        
        Args:
            presente: Number of present students
            tardanza: Number of late students
            total: Total number of students
            
        Returns:
            Attendance percentage (0-100)
        """
        if total == 0:
            return 0.0
        return round((presente + tardanza) / total * 100, 2)
    
    @staticmethod
    def get_alert_level(percentage: float) -> str:
        """Determine alert level based on attendance percentage.
        
        Args:
            percentage: Attendance percentage
            
        Returns:
            Alert level: 'critical', 'warning', or 'success'
        """
        if percentage < 70:
            return 'critical'
        elif percentage < 80:
            return 'warning'
        return 'success'
