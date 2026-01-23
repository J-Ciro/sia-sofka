"""Attendance validation utilities following SOLID principles."""

from datetime import date, datetime
from typing import List

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
    def validate_no_overlapping_session(
        overlapping: List[object],
        subject_id: int,
        fecha: date,
        hora_inicio: datetime,
        hora_fin: datetime,
    ) -> None:
        """Comprueba que no exista una sesión de la misma materia en la misma fecha
        con horario solapado. El profesor puede crear varias sesiones al día en materias
        distintas o en la misma materia en horarios que no se solapan; debe editar la existente
        si quiere modificar una ya creada.

        Args:
            overlapping: Lista de ClaseSession que solapan
            subject_id: ID de la materia
            fecha: Fecha
            hora_inicio: Hora inicio de la nueva
            hora_fin: Hora fin de la nueva

        Raises:
            ValidationError: Si hay sesiones solapadas
        """
        if not overlapping:
            return
        # Extract IDs from overlapping sessions (works with both ClaseSession and mock objects)
        ids = [str(s.id) for s in overlapping if hasattr(s, 'id') and s.id is not None]
        session_ids = ", ".join(ids) if ids else "N/A"
        raise ValidationError(
            f"Ya existe una sesión de esta materia en la misma fecha con horario que se solapa (ID: {session_ids}). "
            "Use editar la sesión existente en lugar de crear otra."
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
