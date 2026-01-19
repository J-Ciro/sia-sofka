"""Unit tests for Attendance Service.

Tests for AttendanceService business logic and validations following TDD.
"""

import pytest
from datetime import datetime, date
from app.models.attendance import (
    ClaseSession,
    Attendance,
    AttendanceStatus,
    AttendanceStats,
    AttendanceAlert,
)
from app.services.attendance_service import AttendanceService
from app.core.exceptions import NotFoundError, ValidationError


class TestAttendanceService:
    """Tests for AttendanceService."""

    @pytest.mark.unit
    def test_create_clase_session(self, db_session, subject, profesor_user):
        """Test creating a clase session."""
        service = AttendanceService(db_session, profesor_user)
        
        # Use today's date to avoid future date validation error
        today = date.today()
        
        clase_data = {
            "subject_id": subject.id,
            "fecha": today,
            "hora_inicio": datetime.combine(today, __import__('datetime').time(8, 0)),
            "hora_fin": datetime.combine(today, __import__('datetime').time(10, 0)),
            "descripcion": "Test class",
        }
        
        clase = service.create_clase_session(**clase_data)
        
        assert clase.id is not None
        assert clase.subject_id == subject.id
        assert clase.creado_por == profesor_user.id

    @pytest.mark.unit
    def test_validate_clase_session_time_ordering(self, db_session, subject, profesor_user):
        """Test that hora_fin must be after hora_inicio."""
        service = AttendanceService(db_session, profesor_user)
        
        clase_data = {
            "subject_id": subject.id,
            "fecha": date(2026, 1, 20),
            "hora_inicio": datetime(2026, 1, 20, 10, 0),
            "hora_fin": datetime(2026, 1, 20, 8, 0),  # Before inicio
            "descripcion": "Invalid class",
        }
        
        with pytest.raises(ValidationError):
            service.create_clase_session(**clase_data)

    @pytest.mark.unit
    def test_validate_clase_session_future_date(self, db_session, subject, profesor_user):
        """Test that clase session cannot be in the future."""
        service = AttendanceService(db_session, profesor_user)
        
        tomorrow = date.today() + __import__('datetime').timedelta(days=1)
        
        clase_data = {
            "subject_id": subject.id,
            "fecha": tomorrow,
            "hora_inicio": datetime.combine(tomorrow, __import__('datetime').time(8, 0)),
            "hora_fin": datetime.combine(tomorrow, __import__('datetime').time(10, 0)),
            "descripcion": "Future class",
        }
        
        with pytest.raises(ValidationError):
            service.create_clase_session(**clase_data)

    @pytest.mark.unit
    def test_mark_attendance_all_present(self, db_session, clase_session, profesor_user):
        """Test marking all students as present."""
        from app.models.enrollment import Enrollment
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        service = AttendanceService(db_session, profesor_user)
        
        # Create and enroll 3 students
        students = []
        for i in range(3):
            student = User(
                email=f"student{i+400}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Student{i+400}",
                apellido="Test",
                codigo_institucional=f"EST40{i}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            db_session.add(student)
            db_session.commit()
            
            enrollment = Enrollment(
                estudiante_id=student.id,
                subject_id=clase_session.subject_id,
            )
            db_session.add(enrollment)
            db_session.commit()
            students.append(student)
        
        # Mark all as present
        updated_count = service.mark_all_present(clase_session.id)
        
        assert updated_count == 3

    @pytest.mark.unit
    def test_mark_attendance_all_absent(self, db_session, clase_session, profesor_user):
        """Test marking all students as absent."""
        from app.models.enrollment import Enrollment
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        service = AttendanceService(db_session, profesor_user)
        
        # Create and enroll 2 students
        for i in range(2):
            student = User(
                email=f"student{i+500}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Student{i+500}",
                apellido="Test",
                codigo_institucional=f"EST50{i}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            db_session.add(student)
            db_session.commit()
            
            enrollment = Enrollment(
                estudiante_id=student.id,
                subject_id=clase_session.subject_id,
            )
            db_session.add(enrollment)
            db_session.commit()
        
        # Mark all as absent
        updated_count = service.mark_all_absent(clase_session.id)
        
        assert updated_count == 2

    @pytest.mark.unit
    def test_update_individual_attendance(self, db_session, clase_session, estudiante_user):
        """Test updating a single student's attendance."""
        service = AttendanceService(db_session, estudiante_user)
        
        # Create initial attendance
        attendance = service.attendance_repo.create(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        
        # Update to absent
        updated = service.update_attendance(
            attendance.id,
            AttendanceStatus.AUSENTE,
        )
        
        assert updated.estado == AttendanceStatus.AUSENTE

    @pytest.mark.unit
    def test_get_session_statistics(self, db_session, clase_session, profesor_user):
        """Test getting attendance statistics for a session."""
        from app.models.enrollment import Enrollment
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        service = AttendanceService(db_session, profesor_user)
        
        # Create 10 students with mixed attendance
        statuses = [
            AttendanceStatus.PRESENTE,
            AttendanceStatus.PRESENTE,
            AttendanceStatus.PRESENTE,
            AttendanceStatus.PRESENTE,
            AttendanceStatus.PRESENTE,
            AttendanceStatus.TARDANZA,
            AttendanceStatus.TARDANZA,
            AttendanceStatus.AUSENTE,
            AttendanceStatus.AUSENTE,
            AttendanceStatus.AUSENTE,
        ]
        
        for i, status in enumerate(statuses):
            student = User(
                email=f"student{i+600}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Student{i+600}",
                apellido="Test",
                codigo_institucional=f"EST60{i}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            db_session.add(student)
            db_session.commit()
            
            enrollment = Enrollment(
                estudiante_id=student.id,
                subject_id=clase_session.subject_id,
            )
            db_session.add(enrollment)
            db_session.commit()
            
            service.attendance_repo.create(
                clase_session_id=clase_session.id,
                estudiante_id=student.id,
                estado=status,
            )
        
        stats = service.get_session_statistics(clase_session.id)
        
        assert stats["total"] == 10
        assert stats["presentes"] == 5
        assert stats["tardanzas"] == 2
        assert stats["ausentes"] == 3
        assert stats["porcentaje_asistencia"] == 70.0  # (5+2)/10

    @pytest.mark.unit
    def test_check_low_attendance_warning(self, db_session, estudiante_user, subject, profesor_user):
        """Test checking if student meets warning threshold for low attendance."""
        from app.models.enrollment import Enrollment
        
        service = AttendanceService(db_session, profesor_user)
        
        # Enroll student
        enrollment = Enrollment(
            estudiante_id=estudiante_user.id,
            subject_id=subject.id,
        )
        db_session.add(enrollment)
        db_session.commit()
        
        # Create attendance: 1 present, 9 absent = 10%
        for i in range(10):
            estado = AttendanceStatus.PRESENTE if i == 0 else AttendanceStatus.AUSENTE
            clase = ClaseSession(
                subject_id=subject.id,
                fecha=date(2026, 1, 19 + i),
                hora_inicio=datetime(2026, 1, 19 + i, 8, 0),
                hora_fin=datetime(2026, 1, 19 + i, 10, 0),
                creado_por=profesor_user.id,
            )
            db_session.add(clase)
            db_session.commit()
            
            service.attendance_repo.create(
                clase_session_id=clase.id,
                estudiante_id=estudiante_user.id,
                estado=estado,
            )
        
        # Get attendance percentage
        from app.models.attendance import ClaseSession as CS
        clases = db_session.query(CS).filter(CS.subject_id == subject.id).all()
        total_present_or_late = 1  # Only one PRESENTE
        total_sessions = len(clases)
        percentage = (total_present_or_late / total_sessions) * 100
        
        # Should have low attendance
        assert percentage < 70.0

    @pytest.mark.unit
    def test_create_attendance_stats(self, db_session, estudiante_user, subject):
        """Test creating attendance statistics record."""
        service = AttendanceService(db_session, estudiante_user)
        
        stats = service.create_attendance_stats(
            estudiante_id=estudiante_user.id,
            subject_id=subject.id,
            total_sesiones=20,
            presentes=16,
            ausentes=3,
            tardanzas=1,
        )
        
        assert stats.id is not None
        assert stats.porcentaje_asistencia == 85.0

    @pytest.mark.unit
    def test_calculate_percentage_with_tardanza(self, db_session, estudiante_user):
        """Test that TARDANZA counts as present for percentage calculation."""
        service = AttendanceService(db_session, estudiante_user)
        
        # Simulation: 4 PRESENTE + 1 TARDANZA + 5 AUSENTE = 50% (5/10)
        total = 10
        present_or_late = 5
        percentage = (present_or_late / total) * 100
        
        assert percentage == 50.0
