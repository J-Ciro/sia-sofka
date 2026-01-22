"""Unit tests for Attendance Service.

Tests for AttendanceService business logic and validations following TDD.
Uses synchronous repository methods for unit testing without async complexity.
"""

import pytest
from datetime import datetime, date, timedelta
from app.models.attendance import (
    ClaseSession,
    Attendance,
    AttendanceStatus,
    AttendanceStats,
    AttendanceAlert,
)
from app.services.attendance_service import AttendanceService
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.attendance_validators import SessionValidator, AttendanceCalculator


class TestAttendanceService:
    """Tests for AttendanceService."""

    @pytest.mark.unit
    def test_validate_clase_session_time_ordering(self, db_session, subject, profesor_user):
        """Test that hora_fin must be after hora_inicio using validators directly."""
        # Test validation directly (validators are synchronous)
        hora_inicio = datetime(2026, 1, 20, 10, 0)
        hora_fin = datetime(2026, 1, 20, 8, 0)  # Before inicio
        
        with pytest.raises(ValidationError) as exc_info:
            SessionValidator.validate_time_range(hora_inicio, hora_fin)
        
        assert "La hora de fin debe ser posterior a la hora de inicio" in str(exc_info.value.detail)

    @pytest.mark.unit
    def test_validate_clase_session_future_date(self, db_session, subject, profesor_user):
        """Test that clase session cannot be in the future using validators."""
        tomorrow = date.today() + timedelta(days=1)
        
        with pytest.raises(ValidationError) as exc_info:
            SessionValidator.validate_date(tomorrow)
        
        assert "No se puede crear asistencia para fechas futuras" in str(exc_info.value.detail)

    @pytest.mark.unit
    def test_validate_clase_session_today_is_valid(self, db_session, subject, profesor_user):
        """Test that today's date is valid for session creation."""
        today = date.today()
        
        # Should not raise
        SessionValidator.validate_date(today)

    @pytest.mark.unit
    def test_validate_time_range_valid(self, db_session, subject, profesor_user):
        """Test that valid time range passes validation."""
        hora_inicio = datetime(2026, 1, 20, 8, 0)
        hora_fin = datetime(2026, 1, 20, 10, 0)
        
        # Should not raise
        SessionValidator.validate_time_range(hora_inicio, hora_fin)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mark_attendance_all_present_async(self, async_db_session, async_clase_session, async_profesor_user):
        """Test marking all students as present using async repository methods."""
        from app.models.enrollment import Enrollment
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        from app.repositories.attendance_repository import AttendanceRepository
        
        repo = AttendanceRepository(async_db_session)
        
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
            async_db_session.add(student)
            await async_db_session.commit()
            await async_db_session.refresh(student)
            
            enrollment = Enrollment(
                estudiante_id=student.id,
                subject_id=async_clase_session.subject_id,
            )
            async_db_session.add(enrollment)
            await async_db_session.commit()
            students.append(student)
        
        # Create attendance records for each student using async repo
        for student in students:
            await repo.create({
                "clase_session_id": async_clase_session.id,
                "estudiante_id": student.id,
                "estado": AttendanceStatus.PRESENTE,
            })
        
        # Verify all are present
        attendances = await repo.get_all_by_session(async_clase_session.id)
        present_count = sum(1 for a in attendances if a.estado == AttendanceStatus.PRESENTE)
        
        assert present_count == 3

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mark_attendance_all_absent_async(self, async_db_session, async_clase_session, async_profesor_user):
        """Test marking all students as absent using async repository methods."""
        from app.models.enrollment import Enrollment
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        from app.repositories.attendance_repository import AttendanceRepository
        
        repo = AttendanceRepository(async_db_session)
        
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
            async_db_session.add(student)
            await async_db_session.commit()
            await async_db_session.refresh(student)
            
            enrollment = Enrollment(
                estudiante_id=student.id,
                subject_id=async_clase_session.subject_id,
            )
            async_db_session.add(enrollment)
            await async_db_session.commit()
            
            # Create attendance as absent
            await repo.create({
                "clase_session_id": async_clase_session.id,
                "estudiante_id": student.id,
                "estado": AttendanceStatus.AUSENTE,
            })
        
        # Verify all are absent
        attendances = await repo.get_all_by_session(async_clase_session.id)
        absent_count = sum(1 for a in attendances if a.estado == AttendanceStatus.AUSENTE)
        
        assert absent_count == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_individual_attendance_async(self, async_db_session, async_clase_session, async_estudiante_user):
        """Test updating a single student's attendance using async repo."""
        from app.repositories.attendance_repository import AttendanceRepository
        
        repo = AttendanceRepository(async_db_session)
        
        # Create initial attendance as PRESENTE
        attendance = await repo.create({
            "clase_session_id": async_clase_session.id,
            "estudiante_id": async_estudiante_user.id,
            "estado": AttendanceStatus.PRESENTE,
        })
        
        # Update to AUSENTE
        updated = await repo.update(attendance.id, {"estado": AttendanceStatus.AUSENTE})
        
        assert updated is not None
        assert updated.estado == AttendanceStatus.AUSENTE
        
        # Update to TARDANZA
        updated = await repo.update(attendance.id, {"estado": AttendanceStatus.TARDANZA})
        
        assert updated is not None
        assert updated.estado == AttendanceStatus.TARDANZA

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_session_statistics_async(self, async_db_session, async_clase_session, async_profesor_user):
        """Test getting attendance statistics for a session using async methods."""
        from app.models.enrollment import Enrollment
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        from app.repositories.attendance_repository import AttendanceRepository
        
        repo = AttendanceRepository(async_db_session)
        
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
            async_db_session.add(student)
            await async_db_session.commit()
            await async_db_session.refresh(student)
            
            enrollment = Enrollment(
                estudiante_id=student.id,
                subject_id=async_clase_session.subject_id,
            )
            async_db_session.add(enrollment)
            await async_db_session.commit()
            
            await repo.create({
                "clase_session_id": async_clase_session.id,
                "estudiante_id": student.id,
                "estado": status,
            })
        
        # Get statistics using async repo methods
        counts = await repo.count_by_status_async(async_clase_session.id)
        percentage = await repo.calculate_attendance_percentage_async(async_clase_session.id)
        
        total = sum(counts.values())
        
        assert total == 10
        assert counts[AttendanceStatus.PRESENTE] == 5
        assert counts[AttendanceStatus.TARDANZA] == 2
        assert counts[AttendanceStatus.AUSENTE] == 3
        assert percentage == 70.0  # (5+2)/10 * 100

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_low_attendance_warning_async(self, async_db_session, async_estudiante_user, async_subject, async_profesor_user):
        """Test checking if student meets warning threshold for low attendance (async)."""
        from app.models.enrollment import Enrollment
        from app.repositories.attendance_repository import AttendanceRepository
        
        repo = AttendanceRepository(async_db_session)
        
        # Enroll student
        enrollment = Enrollment(
            estudiante_id=async_estudiante_user.id,
            subject_id=async_subject.id,
        )
        async_db_session.add(enrollment)
        await async_db_session.commit()
        
        # Create 10 sessions: 1 present, 9 absent = 10% attendance
        today = date.today()
        for i in range(10):
            estado = AttendanceStatus.PRESENTE if i == 0 else AttendanceStatus.AUSENTE
            clase = ClaseSession(
                subject_id=async_subject.id,
                fecha=date(today.year, today.month, today.day - (10 - i)),  # Use past dates
                hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
                hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
                creado_por=async_profesor_user.id,
            )
            async_db_session.add(clase)
            await async_db_session.commit()
            await async_db_session.refresh(clase)
            
            await repo.create({
                "clase_session_id": clase.id,
                "estudiante_id": async_estudiante_user.id,
                "estado": estado,
            })
        
        # Get all attendance for this student in this subject
        attendances = await repo.get_by_student_and_subject(async_estudiante_user.id, async_subject.id)
        
        total_present_or_late = sum(
            1 for a in attendances 
            if a.estado in (AttendanceStatus.PRESENTE, AttendanceStatus.TARDANZA)
        )
        total_sessions = len(attendances)
        percentage = (total_present_or_late / total_sessions) * 100 if total_sessions > 0 else 0.0
        
        # Should have low attendance (10%)
        assert percentage == 10.0
        assert percentage < 70.0
        assert AttendanceCalculator.get_alert_level(percentage) == 'critical'

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_attendance_stats_async(self, async_db_session, async_estudiante_user, async_subject):
        """Test creating attendance statistics record (async)."""
        service = AttendanceService(async_db_session, async_estudiante_user)
        
        stats = await service.create_attendance_stats(
            estudiante_id=async_estudiante_user.id,
            subject_id=async_subject.id,
            total_sesiones=20,
            presentes=16,
            ausentes=3,
            tardanzas=1,
        )
        
        assert stats.id is not None
        assert stats.porcentaje_asistencia == 85.0
        assert stats.total_sesiones == 20
        assert stats.presentes == 16

    @pytest.mark.unit
    def test_calculate_percentage_with_tardanza(self, db_session, estudiante_user):
        """Test that TARDANZA counts as present for percentage calculation."""
        # Use AttendanceCalculator directly for this unit test
        percentage = AttendanceCalculator.calculate_attendance_percentage(
            presente=4,
            tardanza=1,
            total=10
        )
        
        # (4 + 1) / 10 * 100 = 50%
        assert percentage == 50.0

    @pytest.mark.unit
    def test_attendance_percentage_all_present(self, db_session):
        """Test percentage calculation with all students present."""
        percentage = AttendanceCalculator.calculate_attendance_percentage(
            presente=10,
            tardanza=0,
            total=10
        )
        
        assert percentage == 100.0

    @pytest.mark.unit
    def test_attendance_percentage_zero_total(self, db_session):
        """Test percentage calculation with zero students."""
        percentage = AttendanceCalculator.calculate_attendance_percentage(
            presente=0,
            tardanza=0,
            total=0
        )
        
        assert percentage == 0.0

    @pytest.mark.unit
    def test_alert_level_critical(self, db_session):
        """Test alert level for attendance below 70%."""
        assert AttendanceCalculator.get_alert_level(69.9) == 'critical'
        assert AttendanceCalculator.get_alert_level(50.0) == 'critical'
        assert AttendanceCalculator.get_alert_level(0.0) == 'critical'

    @pytest.mark.unit
    def test_alert_level_warning(self, db_session):
        """Test alert level for attendance between 70% and 80%."""
        assert AttendanceCalculator.get_alert_level(70.0) == 'warning'
        assert AttendanceCalculator.get_alert_level(75.0) == 'warning'
        assert AttendanceCalculator.get_alert_level(79.9) == 'warning'

    @pytest.mark.unit
    def test_alert_level_success(self, db_session):
        """Test alert level for attendance 80% or above."""
        assert AttendanceCalculator.get_alert_level(80.0) == 'success'
        assert AttendanceCalculator.get_alert_level(90.0) == 'success'
        assert AttendanceCalculator.get_alert_level(100.0) == 'success'
