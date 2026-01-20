"""Unit tests for Attendance models.

Tests for ClaseSession, Attendance, AttendanceStats, and AttendanceAlert models.
Following TDD: RED phase - these tests will fail until models are implemented.
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.exc import IntegrityError
from app.models.attendance import (
    ClaseSession,
    Attendance,
    AttendanceStats,
    AttendanceAlert,
    AttendanceStatus,
)
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment


class TestClaseSessionModel:
    """Tests for ClaseSession model."""

    @pytest.mark.unit
    def test_create_clase_session(self, db_session, profesor_user, subject):
        """Test creating a valid ClaseSession."""
        clase_session = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 19),
            hora_inicio=datetime(2026, 1, 19, 8, 0),
            hora_fin=datetime(2026, 1, 19, 10, 0),
            descripcion="Clase de Cálculo Diferencial",
            creado_por=profesor_user.id,
        )
        db_session.add(clase_session)
        db_session.commit()

        assert clase_session.id is not None
        assert clase_session.subject_id == subject.id
        assert clase_session.fecha == date(2026, 1, 19)
        assert clase_session.creado_por == profesor_user.id

    @pytest.mark.unit
    def test_clase_session_timestamps(self, db_session, profesor_user, subject):
        """Test that ClaseSession has created_at and updated_at timestamps."""
        clase_session = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 19),
            hora_inicio=datetime(2026, 1, 19, 8, 0),
            hora_fin=datetime(2026, 1, 19, 10, 0),
            creado_por=profesor_user.id,
        )
        db_session.add(clase_session)
        db_session.commit()

        assert clase_session.created_at is not None
        assert clase_session.updated_at is not None
        assert isinstance(clase_session.created_at, datetime)

    @pytest.mark.unit
    def test_clase_session_subject_relationship(self, db_session, profesor_user, subject):
        """Test ClaseSession relationship with Subject."""
        clase_session = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 19),
            hora_inicio=datetime(2026, 1, 19, 8, 0),
            hora_fin=datetime(2026, 1, 19, 10, 0),
            creado_por=profesor_user.id,
        )
        db_session.add(clase_session)
        db_session.commit()

        assert clase_session.subject.id == subject.id

    @pytest.mark.unit
    def test_clase_session_created_by_relationship(self, db_session, profesor_user, subject):
        """Test ClaseSession relationship with User (created_by)."""
        clase_session = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 19),
            hora_inicio=datetime(2026, 1, 19, 8, 0),
            hora_fin=datetime(2026, 1, 19, 10, 0),
            creado_por=profesor_user.id,
        )
        db_session.add(clase_session)
        db_session.commit()

        assert clase_session.creado_por_user.id == profesor_user.id


class TestAttendanceModel:
    """Tests for Attendance model."""

    @pytest.mark.unit
    def test_create_attendance(self, db_session, clase_session, estudiante_user):
        """Test creating a valid Attendance record."""
        attendance = Attendance(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        db_session.add(attendance)
        db_session.commit()

        assert attendance.id is not None
        assert attendance.estado == AttendanceStatus.PRESENTE

    @pytest.mark.unit
    def test_attendance_status_enum(self, db_session, clase_session, estudiante_user):
        """Test all possible attendance status values."""
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        statuses = [
            AttendanceStatus.PRESENTE,
            AttendanceStatus.AUSENTE,
            AttendanceStatus.TARDANZA,
        ]

        # Create different students for each status
        for i, status in enumerate(statuses):
            # Create a new student
            student = User(
                email=f"estudiante{i}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Estudiante{i}",
                apellido="Test",
                codigo_institucional=f"EST00{i+2}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            db_session.add(student)
            db_session.commit()
            
            # Create attendance for this student
            attendance = Attendance(
                clase_session_id=clase_session.id,
                estudiante_id=student.id,
                estado=status,
            )
            db_session.add(attendance)

        db_session.commit()

        assert db_session.query(Attendance).count() == 3

    @pytest.mark.unit
    def test_attendance_unique_constraint(self, db_session, clase_session, estudiante_user):
        """Test that a student can only have one attendance record per session."""
        attendance1 = Attendance(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        db_session.add(attendance1)
        db_session.commit()

        # Try to create another attendance for same student in same session
        attendance2 = Attendance(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.AUSENTE,
        )
        db_session.add(attendance2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    @pytest.mark.unit
    def test_attendance_timestamps(self, db_session, clase_session, estudiante_user):
        """Test that Attendance has created_at and updated_at."""
        attendance = Attendance(
            clase_session_id=clase_session.id,
            estudiante_id=estudiante_user.id,
            estado=AttendanceStatus.PRESENTE,
        )
        db_session.add(attendance)
        db_session.commit()

        assert attendance.created_at is not None
        assert attendance.updated_at is not None


class TestAttendanceStatsModel:
    """Tests for AttendanceStats model."""

    @pytest.mark.unit
    def test_create_attendance_stats(self, db_session, estudiante_user, subject):
        """Test creating AttendanceStats record."""
        stats = AttendanceStats(
            estudiante_id=estudiante_user.id,
            subject_id=subject.id,
            total_sesiones=20,
            presentes=16,
            ausentes=3,
            tardanzas=1,
            porcentaje_asistencia=85.0,
        )
        db_session.add(stats)
        db_session.commit()

        assert stats.id is not None
        assert stats.porcentaje_asistencia == 85.0

    @pytest.mark.unit
    def test_attendance_stats_unique_constraint(self, db_session, estudiante_user, subject):
        """Test that stats are unique per student per subject."""
        stats1 = AttendanceStats(
            estudiante_id=estudiante_user.id,
            subject_id=subject.id,
            total_sesiones=20,
            presentes=16,
            ausentes=3,
            tardanzas=1,
            porcentaje_asistencia=85.0,
        )
        db_session.add(stats1)
        db_session.commit()

        stats2 = AttendanceStats(
            estudiante_id=estudiante_user.id,
            subject_id=subject.id,
            total_sesiones=21,
            presentes=17,
            ausentes=3,
            tardanzas=1,
            porcentaje_asistencia=85.7,
        )
        db_session.add(stats2)

        with pytest.raises(IntegrityError):
            db_session.commit()


class TestAttendanceAlertModel:
    """Tests for AttendanceAlert model."""

    @pytest.mark.unit
    def test_create_attendance_alert(self, db_session, estudiante_user, subject):
        """Test creating an AttendanceAlert."""
        alert = AttendanceAlert(
            estudiante_id=estudiante_user.id,
            subject_id=subject.id,
            nivel="critical",
            porcentaje_asistencia=65.0,
            descripcion="Asistencia crítica: 65%",
        )
        db_session.add(alert)
        db_session.commit()

        assert alert.id is not None
        assert alert.nivel == "critical"
        assert alert.resuelta_en is None

    @pytest.mark.unit
    def test_attendance_alert_resolve(self, db_session, estudiante_user, subject):
        """Test resolving an AttendanceAlert."""
        alert = AttendanceAlert(
            estudiante_id=estudiante_user.id,
            subject_id=subject.id,
            nivel="warning",
            porcentaje_asistencia=75.0,
            descripcion="Asistencia baja: 75%",
        )
        db_session.add(alert)
        db_session.commit()

        alert.resuelta_en = datetime.now()
        db_session.commit()

        assert alert.resuelta_en is not None

    @pytest.mark.unit
    def test_attendance_alert_timestamps(self, db_session, estudiante_user, subject):
        """Test that AttendanceAlert has created_at."""
        alert = AttendanceAlert(
            estudiante_id=estudiante_user.id,
            subject_id=subject.id,
            nivel="warning",
            porcentaje_asistencia=75.0,
        )
        db_session.add(alert)
        db_session.commit()

        assert alert.created_at is not None
