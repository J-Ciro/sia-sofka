"""Unit tests for enhanced Schedule schemas with fecha_especifica support.

Tests for Task 2.3: Extend ScheduleBase schema validation and computed fields.
"""

import pytest
from datetime import date, time
from pydantic import ValidationError

from app.schemas.schedule import ScheduleBase, ScheduleCreate, ScheduleUpdate, ScheduleResponse


class TestScheduleBaseSchema:
    """Tests for enhanced ScheduleBase schema with fecha_especifica support."""

    @pytest.mark.unit
    def test_schedule_base_with_fecha_especifica_valid(self):
        """Valid date-specific schedule should pass validation."""
        data = {
            "subject_id": 1,
            "classroom_id": 1,
            "dia_semana": 1,  # Monday
            "hora_inicio": time(8, 0),
            "hora_fin": time(10, 0),
            "fecha_especifica": date(2024, 1, 15)  # This is a Monday
        }
        schedule = ScheduleBase(**data)
        
        assert schedule.subject_id == 1
        assert schedule.classroom_id == 1
        assert schedule.dia_semana == 1
        assert schedule.hora_inicio == time(8, 0)
        assert schedule.hora_fin == time(10, 0)
        assert schedule.fecha_especifica == date(2024, 1, 15)
        assert schedule.es_fecha_especifica is True

    @pytest.mark.unit
    def test_schedule_base_without_fecha_especifica(self):
        """Weekly schedule without fecha_especifica should work as before."""
        data = {
            "subject_id": 1,
            "classroom_id": 1,
            "dia_semana": 3,  # Wednesday
            "hora_inicio": time(14, 0),
            "hora_fin": time(16, 0)
            # No fecha_especifica
        }
        schedule = ScheduleBase(**data)
        
        assert schedule.subject_id == 1
        assert schedule.classroom_id == 1
        assert schedule.dia_semana == 3
        assert schedule.hora_inicio == time(14, 0)
        assert schedule.hora_fin == time(16, 0)
        assert schedule.fecha_especifica is None
        assert schedule.es_fecha_especifica is False

    @pytest.mark.unit
    def test_schedule_base_date_day_mismatch_raises_error(self):
        """Date-day mismatch should raise ValidationError."""
        data = {
            "subject_id": 1,
            "classroom_id": 1,
            "dia_semana": 1,  # Monday
            "hora_inicio": time(8, 0),
            "hora_fin": time(10, 0),
            "fecha_especifica": date(2024, 1, 16)  # This is a Tuesday
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**data)
        
        error = exc_info.value
        assert "dia_semana" in str(error)
        assert "debe coincidir" in str(error)
        assert "Lunes" in str(error)
        assert "Martes" in str(error)

    @pytest.mark.unit
    def test_schedule_base_sunday_rejection(self):
        """Sunday dates should be rejected."""
        data = {
            "subject_id": 1,
            "classroom_id": 1,
            "dia_semana": 1,  # Monday (but date is Sunday)
            "hora_inicio": time(8, 0),
            "hora_fin": time(10, 0),
            "fecha_especifica": date(2024, 1, 14)  # This is a Sunday
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**data)
        
        error = exc_info.value
        assert "No se permiten horarios los domingos" in str(error)

    @pytest.mark.unit
    def test_schedule_base_all_weekdays_valid(self):
        """All weekdays (Monday-Saturday) should be valid."""
        weekdays = [
            (1, date(2024, 1, 15)),  # Monday
            (2, date(2024, 1, 16)),  # Tuesday
            (3, date(2024, 1, 17)),  # Wednesday
            (4, date(2024, 1, 18)),  # Thursday
            (5, date(2024, 1, 19)),  # Friday
            (6, date(2024, 1, 20)),  # Saturday
        ]
        
        for dia_semana, fecha in weekdays:
            data = {
                "subject_id": 1,
                "classroom_id": 1,
                "dia_semana": dia_semana,
                "hora_inicio": time(8, 0),
                "hora_fin": time(10, 0),
                "fecha_especifica": fecha
            }
            schedule = ScheduleBase(**data)
            assert schedule.dia_semana == dia_semana
            assert schedule.fecha_especifica == fecha
            assert schedule.es_fecha_especifica is True

    @pytest.mark.unit
    def test_schedule_base_existing_validations_still_work(self):
        """Existing validations (time range, duration) should still work."""
        # Test invalid time range
        with pytest.raises(ValidationError):
            ScheduleBase(
                subject_id=1,
                classroom_id=1,
                dia_semana=1,
                hora_inicio=time(10, 0),
                hora_fin=time(8, 0),  # End before start
            )
        
        # Test invalid duration (too short)
        with pytest.raises(ValidationError):
            ScheduleBase(
                subject_id=1,
                classroom_id=1,
                dia_semana=1,
                hora_inicio=time(8, 0),
                hora_fin=time(8, 30),  # Only 30 minutes
            )
        
        # Test invalid time outside range
        with pytest.raises(ValidationError):
            ScheduleBase(
                subject_id=1,
                classroom_id=1,
                dia_semana=1,
                hora_inicio=time(5, 0),  # Before 6:00 AM
                hora_fin=time(7, 0),
            )


class TestScheduleCreateSchema:
    """Tests for ScheduleCreate schema (inherits from ScheduleBase)."""

    @pytest.mark.unit
    def test_schedule_create_inherits_fecha_especifica_validation(self):
        """ScheduleCreate should inherit fecha_especifica validation."""
        data = {
            "subject_id": 1,
            "classroom_id": 1,
            "dia_semana": 5,  # Friday
            "hora_inicio": time(9, 0),
            "hora_fin": time(11, 0),
            "fecha_especifica": date(2024, 1, 19)  # This is a Friday
        }
        schedule = ScheduleCreate(**data)
        
        assert schedule.es_fecha_especifica is True
        assert schedule.fecha_especifica == date(2024, 1, 19)


class TestScheduleUpdateSchema:
    """Tests for ScheduleUpdate schema with fecha_especifica support."""

    @pytest.mark.unit
    def test_schedule_update_with_fecha_especifica(self):
        """ScheduleUpdate should support fecha_especifica field."""
        data = {
            "fecha_especifica": date(2024, 2, 15),
            "hora_inicio": time(10, 0),
            "hora_fin": time(12, 0)
        }
        update = ScheduleUpdate(**data)
        
        assert update.fecha_especifica == date(2024, 2, 15)
        assert update.hora_inicio == time(10, 0)
        assert update.hora_fin == time(12, 0)

    @pytest.mark.unit
    def test_schedule_update_all_fields_optional(self):
        """All fields in ScheduleUpdate should be optional."""
        update = ScheduleUpdate()
        
        assert update.subject_id is None
        assert update.classroom_id is None
        assert update.dia_semana is None
        assert update.hora_inicio is None
        assert update.hora_fin is None
        assert update.fecha_especifica is None


class TestScheduleResponseSchema:
    """Tests for ScheduleResponse schema with computed field."""

    @pytest.mark.unit
    def test_schedule_response_with_fecha_especifica(self):
        """ScheduleResponse should include fecha_especifica and computed field."""
        data = {
            "id": 1,
            "codigo": "HOR-TEST123",
            "subject_id": 1,
            "classroom_id": 1,
            "dia_semana": 2,  # Tuesday
            "hora_inicio": time(10, 0),
            "hora_fin": time(12, 0),
            "fecha_especifica": date(2024, 1, 16)  # Tuesday
        }
        response = ScheduleResponse(**data)
        
        assert response.id == 1
        assert response.codigo == "HOR-TEST123"
        assert response.fecha_especifica == date(2024, 1, 16)
        assert response.es_fecha_especifica is True

    @pytest.mark.unit
    def test_schedule_response_without_fecha_especifica(self):
        """ScheduleResponse should work without fecha_especifica (weekly schedule)."""
        data = {
            "id": 2,
            "codigo": "HOR-TEST456",
            "subject_id": 1,
            "classroom_id": 1,
            "dia_semana": 3,  # Wednesday
            "hora_inicio": time(14, 0),
            "hora_fin": time(16, 0)
            # No fecha_especifica
        }
        response = ScheduleResponse(**data)
        
        assert response.id == 2
        assert response.codigo == "HOR-TEST456"
        assert response.fecha_especifica is None
        assert response.es_fecha_especifica is False

    @pytest.mark.unit
    def test_schedule_response_computed_field_consistency(self):
        """Computed field es_fecha_especifica should be consistent."""
        # Test with fecha_especifica
        data_with_date = {
            "id": 1,
            "codigo": "HOR-1",
            "subject_id": 1,
            "classroom_id": 1,
            "dia_semana": 1,
            "hora_inicio": time(8, 0),
            "hora_fin": time(10, 0),
            "fecha_especifica": date(2024, 1, 15)
        }
        response_with_date = ScheduleResponse(**data_with_date)
        assert response_with_date.es_fecha_especifica is True
        
        # Test without fecha_especifica
        data_without_date = {
            "id": 2,
            "codigo": "HOR-2",
            "subject_id": 1,
            "classroom_id": 1,
            "dia_semana": 1,
            "hora_inicio": time(8, 0),
            "hora_fin": time(10, 0),
            "fecha_especifica": None
        }
        response_without_date = ScheduleResponse(**data_without_date)
        assert response_without_date.es_fecha_especifica is False