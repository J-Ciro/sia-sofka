"""Unit tests for Attendance Repository.

Tests for AttendanceRepository CRUD operations following TDD methodology.
"""

import pytest
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError

from app.models.attendance import (
    ClaseSession,
    Attendance,
    AttendanceStatus,
    AttendanceStats,
)
from app.repositories.attendance_repository import AttendanceRepository
from app.core.exceptions import NotFoundError


class TestAttendanceRepository:
    """Tests for AttendanceRepository."""

    @pytest.mark.unit
    def test_create_attendance(self, db_session, clase_session, estudiante_user):
        """Test creating an attendance record."""
        repo = AttendanceRepository(db_session)
        
        attendance = repo.create(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        
        assert attendance.id is not None
        assert attendance.estado == AttendanceStatus.PRESENTE

    @pytest.mark.unit
    def test_get_attendance_by_id(self, db_session, clase_session, estudiante_user):
        """Test retrieving an attendance record by ID."""
        repo = AttendanceRepository(db_session)
        
        # Create attendance
        created = repo.create(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        
        # Retrieve it
        retrieved = repo.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.estado == AttendanceStatus.PRESENTE

    @pytest.mark.unit
    def test_update_attendance_status(self, db_session, clase_session, estudiante_user):
        """Test updating attendance status."""
        repo = AttendanceRepository(db_session)
        
        # Create with PRESENTE
        attendance = repo.create(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        
        # Update to AUSENTE
        updated = repo.update(
            attendance.id,
            estado=AttendanceStatus.AUSENTE,
        )
        
        assert updated.estado == AttendanceStatus.AUSENTE

    @pytest.mark.unit
    def test_get_attendance_by_session_and_student(self, db_session, clase_session, estudiante_user):
        """Test retrieving attendance by session and student."""
        repo = AttendanceRepository(db_session)
        
        created = repo.create(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        
        retrieved = repo.get_by_session_and_student(
            clase_session.id,
            estudiante_user.id,
        )
        
        assert retrieved is not None
        assert retrieved.id == created.id

    @pytest.mark.unit
    def test_get_attendance_by_session_and_student_not_found(self, db_session, clase_session, estudiante_user):
        """Test retrieving non-existent attendance returns None."""
        repo = AttendanceRepository(db_session)
        
        retrieved = repo.get_by_session_and_student(
            clase_session.id,
            999,  # Non-existent student
        )
        
        assert retrieved is None

    @pytest.mark.unit
    def test_get_all_attendance_by_session(self, db_session, clase_session, profesor_user):
        """Test retrieving all attendance records for a session."""
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        repo = AttendanceRepository(db_session)
        
        # Create 3 students
        students = []
        for i in range(3):
            student = User(
                email=f"student{i}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Student{i}",
                apellido="Test",
                codigo_institucional=f"EST10{i}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            db_session.add(student)
            db_session.commit()
            students.append(student)
        
        # Create attendance for all 3 students
        for student in students:
            repo.create(
                clase_session_id=clase_session.id,
                estudiante_id=student.id,
                estado=AttendanceStatus.PRESENTE,
            )
        
        # Retrieve all attendance for this session
        attendances = repo.get_all_by_session(clase_session.id)
        
        assert len(attendances) == 3
        assert all(a.clase_session_id == clase_session.id for a in attendances)

    @pytest.mark.unit
    def test_get_attendance_by_student_and_subject(self, db_session, subject, estudiante_user, profesor_user):
        """Test retrieving attendance for a student in a specific subject."""
        from app.models.enrollment import Enrollment
        
        repo = AttendanceRepository(db_session)
        
        # Create enrollment
        enrollment = Enrollment(
            estudiante_id=estudiante_user.id,
            subject_id=subject.id,
        )
        db_session.add(enrollment)
        db_session.commit()
        
        # Create multiple sessions for the subject
        clase1 = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 19),
            hora_inicio=datetime(2026, 1, 19, 8, 0),
            hora_fin=datetime(2026, 1, 19, 10, 0),
            creado_por=profesor_user.id,
        )
        db_session.add(clase1)
        db_session.commit()
        
        clase2 = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 20),
            hora_inicio=datetime(2026, 1, 20, 8, 0),
            hora_fin=datetime(2026, 1, 20, 10, 0),
            creado_por=profesor_user.id,
        )
        db_session.add(clase2)
        db_session.commit()
        
        # Create attendance records
        repo.create(
            clase_session_id=clase1.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        repo.create(
            clase_session_id=clase2.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.AUSENTE,
        )
        
        # Retrieve by student and subject
        attendances = repo.get_by_student_and_subject(
            estudiante_user.id,
            subject.id,
        )
        
        assert len(attendances) == 2

    @pytest.mark.unit
    def test_calculate_attendance_percentage(self, db_session, clase_session, profesor_user):
        """Test calculating attendance percentage."""
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        repo = AttendanceRepository(db_session)
        
        # Create 10 students with different statuses
        # 6 PRESENTE, 2 AUSENTE, 2 TARDANZA
        students = []
        statuses = (
            [AttendanceStatus.PRESENTE] * 6 +
            [AttendanceStatus.AUSENTE] * 2 +
            [AttendanceStatus.TARDANZA] * 2
        )
        
        for i, status in enumerate(statuses):
            student = User(
                email=f"student{i+100}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Student{i+100}",
                apellido="Test",
                codigo_institucional=f"EST20{i}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            db_session.add(student)
            db_session.commit()
            
            repo.create(
                clase_session_id=clase_session.id,
                estudiante_id=student.id,
                estado=status,
            )
        
        # Calculate percentage (PRESENTE + TARDANZA) / TOTAL
        # (6 + 2) / 10 = 80%
        percentage = repo.calculate_attendance_percentage(
            clase_session.id,
        )
        
        assert percentage == 80.0

    @pytest.mark.unit
    def test_count_by_status(self, db_session, clase_session, profesor_user):
        """Test counting attendance records by status."""
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        repo = AttendanceRepository(db_session)
        
        # Create students with different statuses
        statuses = [
            AttendanceStatus.PRESENTE,
            AttendanceStatus.PRESENTE,
            AttendanceStatus.AUSENTE,
            AttendanceStatus.TARDANZA,
        ]
        
        for i, status in enumerate(statuses):
            student = User(
                email=f"student{i+200}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Student{i+200}",
                apellido="Test",
                codigo_institucional=f"EST30{i}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            db_session.add(student)
            db_session.commit()
            
            repo.create(
                clase_session_id=clase_session.id,
                estudiante_id=student.id,
                estado=status,
            )
        
        # Count by status
        counts = repo.count_by_status(clase_session.id)
        
        assert counts[AttendanceStatus.PRESENTE] == 2
        assert counts[AttendanceStatus.AUSENTE] == 1
        assert counts[AttendanceStatus.TARDANZA] == 1

    @pytest.mark.unit
    def test_delete_attendance(self, db_session, clase_session, estudiante_user):
        """Test deleting an attendance record."""
        repo = AttendanceRepository(db_session)
        
        created = repo.create(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        
        repo.delete(created.id)
        
        retrieved = repo.get_by_id(created.id)
        assert retrieved is None
