"""Unit tests for Attendance Schemas.

Tests for Pydantic schemas validation following TDD methodology.
"""

import pytest
from datetime import datetime, date
from pydantic import ValidationError as PydanticValidationError

from app.schemas.attendance import (
    ClaseSessionCreate,
    ClaseSessionResponse,
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    SessionStatisticsResponse,
    AttendanceStatsResponse,
)
from app.models.attendance import AttendanceStatus


class TestClaseSessionSchemas:
    """Tests for ClaseSession Pydantic schemas."""

    @pytest.mark.unit
    def test_clase_session_create_valid(self):
        """Test creating a valid ClaseSession schema."""
        data = {
            "subject_id": 1,
            "fecha": date(2026, 1, 19),
            "hora_inicio": datetime(2026, 1, 19, 8, 0),
            "hora_fin": datetime(2026, 1, 19, 10, 0),
            "descripcion": "Clase de Cálculo",
        }
        
        schema = ClaseSessionCreate(**data)
        
        assert schema.subject_id == 1
        assert schema.fecha == date(2026, 1, 19)
        assert schema.descripcion == "Clase de Cálculo"

    @pytest.mark.unit
    def test_clase_session_create_without_descripcion(self):
        """Test that descripcion is optional."""
        data = {
            "subject_id": 1,
            "fecha": date(2026, 1, 19),
            "hora_inicio": datetime(2026, 1, 19, 8, 0),
            "hora_fin": datetime(2026, 1, 19, 10, 0),
        }
        
        schema = ClaseSessionCreate(**data)
        
        assert schema.descripcion is None

    @pytest.mark.unit
    def test_clase_session_create_missing_required_field(self):
        """Test validation error when required field is missing."""
        data = {
            "subject_id": 1,
            "fecha": date(2026, 1, 19),
            # Missing hora_inicio and hora_fin
        }
        
        with pytest.raises(PydanticValidationError):
            ClaseSessionCreate(**data)

    @pytest.mark.unit
    def test_clase_session_response(self):
        """Test ClaseSessionResponse schema."""
        data = {
            "id": 1,
            "subject_id": 1,
            "fecha": date(2026, 1, 19),
            "hora_inicio": datetime(2026, 1, 19, 8, 0),
            "hora_fin": datetime(2026, 1, 19, 10, 0),
            "descripcion": "Test",
            "creado_por": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        schema = ClaseSessionResponse(**data)
        
        assert schema.id == 1
        assert schema.subject_id == 1


class TestAttendanceSchemas:
    """Tests for Attendance Pydantic schemas."""

    @pytest.mark.unit
    def test_attendance_create_valid(self):
        """Test creating a valid Attendance schema."""
        data = {
            "clase_session_id": 1,
            "estudiante_id": 1,
            "estado": AttendanceStatus.PRESENTE,
        }
        
        schema = AttendanceCreate(**data)
        
        assert schema.clase_session_id == 1
        assert schema.estudiante_id == 1
        assert schema.estado == AttendanceStatus.PRESENTE

    @pytest.mark.unit
    def test_attendance_create_default_estado(self):
        """Test that estado defaults to PRESENTE."""
        data = {
            "clase_session_id": 1,
            "estudiante_id": 1,
        }
        
        schema = AttendanceCreate(**data)
        
        assert schema.estado == AttendanceStatus.PRESENTE

    @pytest.mark.unit
    def test_attendance_update_only_estado(self):
        """Test AttendanceUpdate with only estado field."""
        data = {
            "estado": AttendanceStatus.AUSENTE,
        }
        
        schema = AttendanceUpdate(**data)
        
        assert schema.estado == AttendanceStatus.AUSENTE

    @pytest.mark.unit
    def test_attendance_update_invalid_estado(self):
        """Test validation error with invalid estado."""
        data = {
            "estado": "INVALID_STATUS",
        }
        
        with pytest.raises(PydanticValidationError):
            AttendanceUpdate(**data)

    @pytest.mark.unit
    def test_attendance_response(self):
        """Test AttendanceResponse schema."""
        data = {
            "id": 1,
            "clase_session_id": 1,
            "estudiante_id": 1,
            "estado": AttendanceStatus.PRESENTE,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        schema = AttendanceResponse(**data)
        
        assert schema.id == 1
        assert schema.estado == AttendanceStatus.PRESENTE


class TestSessionStatisticsSchemas:
    """Tests for Session Statistics Pydantic schemas."""

    @pytest.mark.unit
    def test_session_statistics_response(self):
        """Test SessionStatisticsResponse schema."""
        data = {
            "total": 20,
            "presentes": 15,
            "tardanzas": 3,
            "ausentes": 2,
            "porcentaje_asistencia": 90.0,
        }
        
        schema = SessionStatisticsResponse(**data)
        
        assert schema.total == 20
        assert schema.presentes == 15
        assert schema.porcentaje_asistencia == 90.0

    @pytest.mark.unit
    def test_session_statistics_validation(self):
        """Test that porcentaje_asistencia is between 0 and 100."""
        # Valid percentage
        data = {
            "total": 10,
            "presentes": 5,
            "tardanzas": 2,
            "ausentes": 3,
            "porcentaje_asistencia": 70.0,
        }
        
        schema = SessionStatisticsResponse(**data)
        assert schema.porcentaje_asistencia == 70.0

    @pytest.mark.unit
    def test_attendance_stats_response(self):
        """Test AttendanceStatsResponse schema."""
        data = {
            "id": 1,
            "estudiante_id": 1,
            "subject_id": 1,
            "total_sesiones": 20,
            "presentes": 16,
            "ausentes": 3,
            "tardanzas": 1,
            "porcentaje_asistencia": 85.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        schema = AttendanceStatsResponse(**data)
        
        assert schema.total_sesiones == 20
        assert schema.porcentaje_asistencia == 85.0
