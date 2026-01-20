"""Unit tests for attendance validators following SOLID principles."""

import pytest
from datetime import date, datetime, timedelta
from app.utils.attendance_validators import SessionValidator, AttendanceCalculator
from app.core.exceptions import ValidationError


class TestSessionValidator:
    """Tests for SessionValidator utility class."""
    
    def test_validate_date_today_is_valid(self):
        """Test that today's date is valid."""
        today = date.today()
        # Should not raise
        SessionValidator.validate_date(today)
    
    def test_validate_date_past_is_valid(self):
        """Test that past dates are valid."""
        yesterday = date.today() - timedelta(days=1)
        # Should not raise
        SessionValidator.validate_date(yesterday)
    
    def test_validate_date_future_raises_error(self):
        """Test that future dates raise ValidationError."""
        tomorrow = date.today() + timedelta(days=1)
        
        with pytest.raises(ValidationError) as exc_info:
            SessionValidator.validate_date(tomorrow)
        
        assert "No se puede crear asistencia para fechas futuras" in str(exc_info.value.detail)
    
    def test_validate_time_range_valid(self):
        """Test valid time range (end after start)."""
        start = datetime(2026, 1, 19, 8, 0)
        end = datetime(2026, 1, 19, 10, 0)
        
        # Should not raise
        SessionValidator.validate_time_range(start, end)
    
    def test_validate_time_range_same_time_raises_error(self):
        """Test that same start and end time raises error."""
        same_time = datetime(2026, 1, 19, 8, 0)
        
        with pytest.raises(ValidationError) as exc_info:
            SessionValidator.validate_time_range(same_time, same_time)
        
        assert "La hora de fin debe ser posterior a la hora de inicio" in str(exc_info.value.detail)
    
    def test_validate_time_range_end_before_start_raises_error(self):
        """Test that end before start raises error."""
        start = datetime(2026, 1, 19, 10, 0)
        end = datetime(2026, 1, 19, 8, 0)
        
        with pytest.raises(ValidationError) as exc_info:
            SessionValidator.validate_time_range(start, end)
        
        assert "La hora de fin debe ser posterior a la hora de inicio" in str(exc_info.value.detail)
    
    def test_validate_duplicate_session_none_is_valid(self):
        """Test that no existing session is valid."""
        # Should not raise
        SessionValidator.validate_duplicate_session(None, 1, date.today())
    
    def test_validate_duplicate_session_existing_raises_error(self):
        """Test that existing session raises ValidationError."""
        
        class MockSession:
            id = 123
        
        existing = MockSession()
        subject_id = 1
        fecha = date.today()
        
        with pytest.raises(ValidationError) as exc_info:
            SessionValidator.validate_duplicate_session(existing, subject_id, fecha)
        
        assert "Ya existe una sesión" in str(exc_info.value.detail)
        assert str(existing.id) in str(exc_info.value.detail)


class TestAttendanceCalculator:
    """Tests for AttendanceCalculator utility class."""
    
    def test_calculate_attendance_percentage_all_present(self):
        """Test percentage calculation with all students present."""
        presente = 10
        tardanza = 0
        total = 10
        
        percentage = AttendanceCalculator.calculate_attendance_percentage(presente, tardanza, total)
        
        assert percentage == 100.0
    
    def test_calculate_attendance_percentage_half_present(self):
        """Test percentage calculation with half students present."""
        presente = 5
        tardanza = 0
        total = 10
        
        percentage = AttendanceCalculator.calculate_attendance_percentage(presente, tardanza, total)
        
        assert percentage == 50.0
    
    def test_calculate_attendance_percentage_with_late_students(self):
        """Test that late students count toward attendance."""
        presente = 5
        tardanza = 3
        total = 10
        
        percentage = AttendanceCalculator.calculate_attendance_percentage(presente, tardanza, total)
        
        assert percentage == 80.0  # (5 + 3) / 10 * 100
    
    def test_calculate_attendance_percentage_zero_total(self):
        """Test percentage with zero total students."""
        percentage = AttendanceCalculator.calculate_attendance_percentage(0, 0, 0)
        
        assert percentage == 0.0
    
    def test_calculate_attendance_percentage_rounding(self):
        """Test that percentage is rounded to 2 decimals."""
        presente = 2
        tardanza = 1
        total = 7
        
        percentage = AttendanceCalculator.calculate_attendance_percentage(presente, tardanza, total)
        
        # (2 + 1) / 7 * 100 = 42.857142... should round to 42.86
        assert percentage == 42.86
    
    def test_get_alert_level_critical(self):
        """Test alert level for attendance below 70%."""
        assert AttendanceCalculator.get_alert_level(69.9) == 'critical'
        assert AttendanceCalculator.get_alert_level(50.0) == 'critical'
        assert AttendanceCalculator.get_alert_level(0.0) == 'critical'
    
    def test_get_alert_level_warning(self):
        """Test alert level for attendance between 70% and 80%."""
        assert AttendanceCalculator.get_alert_level(70.0) == 'warning'
        assert AttendanceCalculator.get_alert_level(75.0) == 'warning'
        assert AttendanceCalculator.get_alert_level(79.9) == 'warning'
    
    def test_get_alert_level_success(self):
        """Test alert level for attendance 80% or above."""
        assert AttendanceCalculator.get_alert_level(80.0) == 'success'
        assert AttendanceCalculator.get_alert_level(90.0) == 'success'
        assert AttendanceCalculator.get_alert_level(100.0) == 'success'
