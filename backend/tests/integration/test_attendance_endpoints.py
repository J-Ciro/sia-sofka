"""Integration tests for attendance endpoints.

Tests for REST API endpoints following TDD methodology.
Tests authentication, authorization, validation, and business logic.
"""

import pytest
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.attendance import ClaseSession, Attendance, AttendanceStatus
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash, create_access_token


# ==================== Fixtures ====================

@pytest.fixture
async def test_data_attendance(db_session: AsyncSession):
    """Create test data: admin, profesor, estudiante, subject, enrollment."""
    # Admin
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@attendance.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    
    # Profesor
    codigo_prof = await generar_codigo_institucional(db_session, "Profesor")
    profesor = User(
        email="profesor@attendance.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor)
    
    # Estudiante 1
    codigo_est1 = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante1 = User(
        email="estudiante1@attendance.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante",
        apellido="Uno",
        codigo_institucional=codigo_est1,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería",
    )
    db_session.add(estudiante1)
    
    # Estudiante 2
    codigo_est2 = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante2 = User(
        email="estudiante2@attendance.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante",
        apellido="Dos",
        codigo_institucional=codigo_est2,
        fecha_nacimiento=date(2000, 2, 1),
        programa_academico="Ingeniería",
    )
    db_session.add(estudiante2)
    
    await db_session.commit()
    await db_session.refresh(admin)
    await db_session.refresh(profesor)
    await db_session.refresh(estudiante1)
    await db_session.refresh(estudiante2)
    
    # Subject
    subject = Subject(
        nombre="Matemáticas",
        descripcion="Cálculo I",
        numero_creditos=4,
        profesor_id=profesor.id,
    )
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    
    # Enrollments
    enrollment1 = Enrollment(
        estudiante_id=estudiante1.id,
        subject_id=subject.id,
    )
    enrollment2 = Enrollment(
        estudiante_id=estudiante2.id,
        subject_id=subject.id,
    )
    db_session.add_all([enrollment1, enrollment2])
    await db_session.commit()
    
    return {
        "admin": admin,
        "profesor": profesor,
        "estudiante1": estudiante1,
        "estudiante2": estudiante2,
        "subject": subject,
    }


@pytest.fixture
def profesor_token(test_data_attendance):
    """Generate JWT token for profesor."""
    profesor = test_data_attendance["profesor"]
    return create_access_token(data={"sub": profesor.email})


@pytest.fixture
def estudiante_token(test_data_attendance):
    """Generate JWT token for estudiante."""
    estudiante = test_data_attendance["estudiante1"]
    return create_access_token(data={"sub": estudiante.email})


@pytest.fixture
def admin_token(test_data_attendance):
    """Generate JWT token for admin."""
    admin = test_data_attendance["admin"]
    return create_access_token(data={"sub": admin.email})


# ==================== Tests ====================

@pytest.mark.integration
@pytest.mark.asyncio
class TestCreateClaseSession:
    """Tests for POST /api/v1/attendance/sessions endpoint."""
    
    async def test_create_clase_session_success(
        self, client: AsyncClient, profesor_token: str, test_data_attendance: dict
    ):
        """Test creating a class session as profesor."""
        subject_id = test_data_attendance["subject"].id
        
        payload = {
            "subject_id": subject_id,
            "fecha": "2026-01-20",
            "hora_inicio": "2026-01-20T08:00:00",
            "hora_fin": "2026-01-20T10:00:00",
            "descripcion": "Clase de Cálculo",
        }
        
        response = await client.post(
            "/api/v1/attendance/sessions",
            json=payload,
            headers={"Authorization": f"Bearer {profesor_token}"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["subject_id"] == subject_id
        assert data["descripcion"] == "Clase de Cálculo"
        assert "id" in data
    
    async def test_create_clase_session_unauthorized_estudiante(
        self, client: AsyncClient, estudiante_token: str, test_data_attendance: dict
    ):
        """Test that estudiante cannot create sessions."""
        subject_id = test_data_attendance["subject"].id
        
        payload = {
            "subject_id": subject_id,
            "fecha": "2026-01-20",
            "hora_inicio": "2026-01-20T08:00:00",
            "hora_fin": "2026-01-20T10:00:00",
        }
        
        response = await client.post(
            "/api/v1/attendance/sessions",
            json=payload,
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        
        assert response.status_code == 403
    
    async def test_create_clase_session_invalid_times(
        self, client: AsyncClient, profesor_token: str, test_data_attendance: dict
    ):
        """Test validation error when hora_fin < hora_inicio."""
        subject_id = test_data_attendance["subject"].id
        
        payload = {
            "subject_id": subject_id,
            "fecha": "2026-01-20",
            "hora_inicio": "2026-01-20T10:00:00",
            "hora_fin": "2026-01-20T08:00:00",  # Invalid: before start
        }
        
        response = await client.post(
            "/api/v1/attendance/sessions",
            json=payload,
            headers={"Authorization": f"Bearer {profesor_token}"},
        )
        
        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetClaseSession:
    """Tests for GET /api/v1/attendance/sessions/{id} endpoint."""
    
    async def test_get_clase_session_success(
        self, client: AsyncClient, profesor_token: str, test_data_attendance: dict, db_session: AsyncSession
    ):
        """Test getting a class session by id."""
        # Create session in database
        profesor = test_data_attendance["profesor"]
        subject = test_data_attendance["subject"]
        
        session = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 20),
            hora_inicio=datetime(2026, 1, 20, 8, 0),
            hora_fin=datetime(2026, 1, 20, 10, 0),
            creado_por=profesor.id,
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        response = await client.get(
            f"/api/v1/attendance/sessions/{session.id}",
            headers={"Authorization": f"Bearer {profesor_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session.id
        assert data["subject_id"] == subject.id
    
    async def test_get_clase_session_not_found(
        self, client: AsyncClient, profesor_token: str
    ):
        """Test 404 when session doesn't exist."""
        response = await client.get(
            "/api/v1/attendance/sessions/99999",
            headers={"Authorization": f"Bearer {profesor_token}"},
        )
        
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
class TestUpdateAttendance:
    """Tests for PATCH /api/v1/attendance/{id} endpoint."""
    
    async def test_update_attendance_success(
        self, client: AsyncClient, profesor_token: str, test_data_attendance: dict, db_session: AsyncSession
    ):
        """Test updating attendance status as profesor."""
        # Create session and attendance
        profesor = test_data_attendance["profesor"]
        subject = test_data_attendance["subject"]
        estudiante = test_data_attendance["estudiante1"]
        
        session = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 20),
            hora_inicio=datetime(2026, 1, 20, 8, 0),
            hora_fin=datetime(2026, 1, 20, 10, 0),
            creado_por=profesor.id,
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        attendance = Attendance(
            clase_session_id=session.id,
            estudiante_id=estudiante.id,
            estado=AttendanceStatus.PRESENTE,
        )
        db_session.add(attendance)
        await db_session.commit()
        await db_session.refresh(attendance)
        
        payload = {"estado": "AUSENTE"}
        
        response = await client.patch(
            f"/api/v1/attendance/{attendance.id}",
            json=payload,
            headers={"Authorization": f"Bearer {profesor_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "AUSENTE"
    
    async def test_update_attendance_unauthorized_estudiante(
        self, client: AsyncClient, estudiante_token: str, test_data_attendance: dict, db_session: AsyncSession
    ):
        """Test that estudiante cannot update attendance."""
        # Create session and attendance
        profesor = test_data_attendance["profesor"]
        subject = test_data_attendance["subject"]
        estudiante = test_data_attendance["estudiante1"]
        
        session = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 20),
            hora_inicio=datetime(2026, 1, 20, 8, 0),
            hora_fin=datetime(2026, 1, 20, 10, 0),
            creado_por=profesor.id,
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        attendance = Attendance(
            clase_session_id=session.id,
            estudiante_id=estudiante.id,
            estado=AttendanceStatus.PRESENTE,
        )
        db_session.add(attendance)
        await db_session.commit()
        await db_session.refresh(attendance)
        
        payload = {"estado": "AUSENTE"}
        
        response = await client.patch(
            f"/api/v1/attendance/{attendance.id}",
            json=payload,
            headers={"Authorization": f"Bearer {estudiante_token}"},
        )
        
        assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetSessionStatistics:
    """Tests for GET /api/v1/attendance/sessions/{id}/stats endpoint."""
    
    async def test_get_session_statistics_success(
        self, client: AsyncClient, profesor_token: str, test_data_attendance: dict, db_session: AsyncSession
    ):
        """Test getting statistics for a session."""
        # Create session and attendances
        profesor = test_data_attendance["profesor"]
        subject = test_data_attendance["subject"]
        estudiante1 = test_data_attendance["estudiante1"]
        estudiante2 = test_data_attendance["estudiante2"]
        
        session = ClaseSession(
            subject_id=subject.id,
            fecha=date(2026, 1, 20),
            hora_inicio=datetime(2026, 1, 20, 8, 0),
            hora_fin=datetime(2026, 1, 20, 10, 0),
            creado_por=profesor.id,
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        # Create attendances
        att1 = Attendance(
            clase_session_id=session.id,
            estudiante_id=estudiante1.id,
            estado=AttendanceStatus.PRESENTE,
        )
        att2 = Attendance(
            clase_session_id=session.id,
            estudiante_id=estudiante2.id,
            estado=AttendanceStatus.AUSENTE,
        )
        db_session.add_all([att1, att2])
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/attendance/sessions/{session.id}/stats",
            headers={"Authorization": f"Bearer {profesor_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["presentes"] == 1
        assert data["ausentes"] == 1
        assert data["tardanzas"] == 0
        assert data["porcentaje_asistencia"] == 50.0
    
    async def test_get_session_statistics_not_found(
        self, client: AsyncClient, profesor_token: str
    ):
        """Test 404 when session doesn't exist."""
        response = await client.get(
            "/api/v1/attendance/sessions/99999/stats",
            headers={"Authorization": f"Bearer {profesor_token}"},
        )
        
        assert response.status_code == 404
