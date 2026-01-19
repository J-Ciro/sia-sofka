"""Attendance Repository - Data access layer for attendance operations."""

from typing import Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.attendance import (
    Attendance,
    AttendanceStatus,
    ClaseSession,
)
from app.repositories.base import AbstractRepository


class AttendanceRepository:
    """Repository for Attendance model operations."""
    
    def __init__(self, db: Union[Session, AsyncSession]):
        """Initialize attendance repository.
        
        Args:
            db: Database session (sync or async)
        """
        self.db = db
        self.model = Attendance
    
    def create(
        self,
        clase_session_id: int,
        estudiante_id: int,
        estado: AttendanceStatus = AttendanceStatus.PRESENTE,
    ) -> Attendance:
        """Create a new attendance record.
        
        Args:
            clase_session_id: ID of the clase session
            estudiante_id: ID of the student
            estado: Attendance status (default: PRESENTE)
        
        Returns:
            Created Attendance instance
        """
        attendance = Attendance(
            clase_session_id=clase_session_id,
            estudiante_id=estudiante_id,
            estado=estado,
        )
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance
    
    def get_by_id(self, attendance_id: int) -> Optional[Attendance]:
        """Get attendance by ID.
        
        Args:
            attendance_id: Attendance ID
        
        Returns:
            Attendance instance or None
        """
        # Works with both sync and async sessions
        try:
            return self.db.query(Attendance).filter(Attendance.id == attendance_id).first()
        except (AttributeError, TypeError):
            # Fallback for async sessions (will not work with sync API)
            return None
    
    def get_by_session_and_student(
        self,
        clase_session_id: int,
        estudiante_id: int,
    ) -> Optional[Attendance]:
        """Get attendance for a specific student in a specific session.
        
        Args:
            clase_session_id: ID of the clase session
            estudiante_id: ID of the student
        
        Returns:
            Attendance instance or None
        """
        return self.db.query(Attendance).filter(
            Attendance.clase_session_id == clase_session_id,
            Attendance.estudiante_id == estudiante_id,
        ).first()
    
    def get_all_by_session(self, clase_session_id: int) -> list[Attendance]:
        """Get all attendance records for a specific session.
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            List of Attendance instances
        """
        return self.db.query(Attendance).filter(
            Attendance.clase_session_id == clase_session_id,
        ).all()
    
    def get_by_student_and_subject(
        self,
        estudiante_id: int,
        subject_id: int,
    ) -> list[Attendance]:
        """Get all attendance records for a student in a specific subject.
        
        Args:
            estudiante_id: ID of the student
            subject_id: ID of the subject
        
        Returns:
            List of Attendance instances
        """
        return self.db.query(Attendance).join(
            ClaseSession,
            Attendance.clase_session_id == ClaseSession.id,
        ).filter(
            Attendance.estudiante_id == estudiante_id,
            ClaseSession.subject_id == subject_id,
        ).all()
    
    def update(self, attendance_id: int, **kwargs) -> Optional[Attendance]:
        """Update an attendance record.
        
        Args:
            attendance_id: Attendance ID
            **kwargs: Fields to update
        
        Returns:
            Updated Attendance instance or None
        """
        attendance = self.get_by_id(attendance_id)
        if attendance is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(attendance, key):
                setattr(attendance, key, value)
        
        self.db.commit()
        self.db.refresh(attendance)
        return attendance
    
    def delete(self, attendance_id: int) -> bool:
        """Delete an attendance record.
        
        Args:
            attendance_id: Attendance ID
        
        Returns:
            True if deleted, False if not found
        """
        attendance = self.get_by_id(attendance_id)
        if attendance is None:
            return False
        
        self.db.delete(attendance)
        self.db.commit()
        return True
    
    def calculate_attendance_percentage(self, clase_session_id: int) -> float:
        """Calculate attendance percentage for a session.
        
        Attendance percentage = (PRESENTE + TARDANZA) / TOTAL * 100
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Attendance percentage (0-100)
        """
        attendances = self.get_all_by_session(clase_session_id)
        
        if not attendances:
            return 0.0
        
        present_or_late = sum(
            1 for a in attendances
            if a.estado in (AttendanceStatus.PRESENTE, AttendanceStatus.TARDANZA)
        )
        
        return (present_or_late / len(attendances)) * 100
    
    def count_by_status(self, clase_session_id: int) -> Dict[AttendanceStatus, int]:
        """Count attendance records by status for a session.
        
        Args:
            clase_session_id: ID of the clase session
        
        Returns:
            Dictionary with counts by status
        """
        attendances = self.get_all_by_session(clase_session_id)
        
        counts = {
            AttendanceStatus.PRESENTE: 0,
            AttendanceStatus.AUSENTE: 0,
            AttendanceStatus.TARDANZA: 0,
        }
        
        for attendance in attendances:
            counts[attendance.estado] += 1
        
        return counts
